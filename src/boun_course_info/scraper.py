"""Core scraping functionality for the Boğaziçi University Course Information Scraper."""

import logging
import re # Import the re module
from time import sleep
from typing import Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag

from .config import DEPARTMENT_MAPPING, SEMESTER_MAPPING
from .utils import (
    construct_url,
    normalize_course_code,
    parse_credits,
    parse_days,
    parse_departments,
    parse_ects,
    parse_hours,
    parse_rooms,
    parse_time_slots,
)


class CourseInfoScraper:
    """Scraper for Boğaziçi University course information."""

    def __init__(self, semester: str, include_unscheduled: bool = False):
        """
        Initialize the scraper.

        Args:
            semester: The semester code (e.g., '2024-2025-1')
            include_unscheduled: Whether to include courses without scheduled meeting information

        Raises:
            ValueError: If the semester code is invalid
        """
        self.include_unscheduled = include_unscheduled
        if semester not in SEMESTER_MAPPING:
            raise ValueError(
                f"Invalid semester code: {semester}. "
                f"Valid options are: {', '.join(SEMESTER_MAPPING.keys())}"
            )
        # Convert semester format from 2024-2025-1 to 2024/2025-1
        # First replace only the first hyphen with slash
        parts = semester.split('-', 2)
        if len(parts) == 3:
            self.semester = f"{parts[0]}/{parts[1]}-{parts[2]}"
        else:
            self.semester = semester  # Keep original if format is unexpected
            
        self.session = requests.Session()
        # Add common headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',  # Added Turkish language support
            'Accept-Charset': 'utf-8',  # Explicitly request UTF-8 content
            'Connection': 'keep-alive',
        })

    def fetch_html(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch HTML content from a URL.

        Args:
            url: The URL to fetch

        Returns:
            Tuple of (HTML content, error message if any)
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check if we got an actual HTML response
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                error_msg = f"Unexpected content type: {content_type}"
                logging.error(error_msg)
                return None, error_msg

            # Log original encoding and content type
            logging.debug(f"Original response encoding: {response.encoding}")
            logging.debug(f"Content-Type header: {response.headers.get('content-type')}")
            
            # Try to detect the encoding from the Content-Type header
            charset = None
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[-1].strip()
            
            # If charset not specified in headers, try Windows-1254 (Turkish)
            if not charset:
                charset = 'windows-1254'
            
            # Set the response encoding
            response.encoding = charset
            logging.debug(f"Set encoding to: {charset}")
            
            # Sample some text to check encoding
            sample = response.text[:200]
            logging.debug(f"Sample text after encoding: {sample}")
            
            # Use response.content with the detected charset to decode the bytes:
            try:
                text = response.content.decode(charset)
            except UnicodeDecodeError as e:
                logging.error(f"Decoding error using charset {charset}: {e}")
                return None, f"Decoding error: {e}"

            # Check if the response is too short (might be an error page)
            if len(text) < 1000:  # Arbitrary threshold
                logging.warning(f"Response seems too short: {len(response.text)} bytes")
                logging.debug(f"Response content: {response.text[:200]}...")

            return text, None

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch {url}: {str(e)}"
            logging.error(error_msg)
            return None, error_msg

    def extract_course_data(self, soup: BeautifulSoup, time_slots: Dict[int, int]) -> Dict[str, dict]:
        """
        Extract course data from the HTML content.

        Args:
            soup: BeautifulSoup object of the page HTML
            time_slots: Dictionary mapping slot numbers to start times

        Returns:
            Dictionary mapping normalized course codes to course data
        """
        courses = {}
        course_table = soup.find('table', {'border': '1', 'width': '1300px'})
        if not course_table:
            logging.error("Course schedule table not found.")
            return courses

        # Map header names to their column indices.
        header_row = course_table.find('tr', class_='schtitle')
        headers = [th.get_text(strip=True) for th in header_row.find_all('td')]
        header_indices = {header: idx for idx, header in enumerate(headers)}
        
        # Iterate over each course row.
        for row in course_table.find_all('tr', class_=lambda x: x in ['schtd', 'schtd2']):
            cells = row.find_all('td')
            if len(cells) < len(headers):
                continue  # Skip incomplete rows

            try:
                # Extract and normalize the course code.
                code_cell = cells[header_indices.get('Code.Sec', 0)]
                course_code_section = code_cell.find('font').get_text(strip=True)
                course_code_key = course_code_section.replace(' ', '').upper()
            except Exception as e:
                logging.warning(f"Error extracting course code: {e}")
                continue

            def safe_text_for_row(cells, field, header_indices):
                """Helper function to safely get text from a cell in any row."""
                idx = header_indices.get(field, None)
                if idx is not None and idx < len(cells):
                    text = cells[idx].get_text(strip=True)
                    return text
                return ""

            def safe_text(field):
                """Helper function to safely get text from a cell in the current row."""
                return safe_text_for_row(cells, field, header_indices)

            credits = int(safe_text('Cr.')) if safe_text('Cr.').isdigit() else 0
            try:
                ects = float(safe_text('Ects').replace(',', '.')) if safe_text('Ects') else 0.0
            except ValueError:
                ects = 0.0
            instructor = safe_text('Instr.')
            name = safe_text('Name')

            days_text = safe_text('Days')
            days = re.findall(r'Th|St|Su|[MTWF]', days_text) if days_text else []

            hours_text = safe_text('Hours')
            hours = []
            if hours_text:
                # Extract and validate individual slot numbers
                for char in hours_text:
                    if char.isdigit():
                        slot_num = int(char)
                        # Only include valid slot numbers (1-8)
                        if 1 <= slot_num <= 8:
                            hours.append(slot_num)

            def fix_room_text(text):
                """Helper function to fix Turkish characters in room names."""
                replacements = {
                    'Ý': 'İ',  # Capital I with dot
                    'ý': 'i',  # Lowercase dotless i
                }
                for old, new in replacements.items():
                    text = text.replace(old, new)
                return text

            # Parse rooms, removing separators and empty values
            rooms_cell = cells[header_indices.get('Rooms', 0)]
            rooms = []
            # First try to get rooms from span elements
            span_rooms = [fix_room_text(span.get_text(strip=True)) for span in rooms_cell.find_all('span')]
            if span_rooms:
                rooms = [r for r in span_rooms if r and r != '|']
            else:
                # If no spans, try parsing the text content
                room_text = rooms_cell.get_text(strip=True)
                if room_text:
                    # Split by common separators and clean up
                    rooms = [fix_room_text(r.strip()) for r in re.split(r'[,|]', room_text) if r.strip()]

            # Check if this is a nested session (LAB, P.S., etc.)
            session_type = safe_text('Name').strip()
            is_nested = bool(re.match(r'^(LAB|P\.S\.|PS|REC)\s*\d*$', session_type))

            # If this is a nested session, skip creating a new course object
            if is_nested:
                continue

            # Create main course object with empty lists for schedule data
            course_obj = {
                "code": course_code_section,
                "credits": credits,
                "ects": ects,
                "instructor": instructor,
                "name": name,
                "days": days if days else [],
                "hours": hours if hours else [],
                "rooms": rooms if rooms else []
            }

            # Ensure arrays are of equal length if any of them have data
            if any([course_obj["days"], course_obj["hours"], course_obj["rooms"]]):
                max_len = max(len(course_obj["days"]),
                            len(course_obj["hours"]),
                            len(course_obj["rooms"]))
                
                # Extend arrays to match the longest one
                if course_obj["days"]:
                    last_day = course_obj["days"][-1]
                    course_obj["days"].extend([last_day] * (max_len - len(course_obj["days"])))
                else:
                    course_obj["days"] = []  # Keep as empty list if no days
                
                if course_obj["hours"]:
                    last_hour = course_obj["hours"][-1]
                    course_obj["hours"].extend([last_hour] * (max_len - len(course_obj["hours"])))
                else:
                    course_obj["hours"] = []  # Keep as empty list if no hours
                
                if course_obj["rooms"]:
                    last_room = course_obj["rooms"][-1]
                    course_obj["rooms"].extend([last_room] * (max_len - len(course_obj["rooms"])))
                else:
                    course_obj["rooms"] = []  # Keep as empty list if no rooms

            # Skip unscheduled courses if include_unscheduled is False
            if not self.include_unscheduled:
                if not any([course_obj["days"], course_obj["hours"], course_obj["rooms"]]):
                    logging.debug(f"Skipping unscheduled course: {course_code_key}")
                    continue

            # Add main course to courses dictionary
            if course_code_key not in courses:
                courses[course_code_key] = course_obj
            else:
                logging.info(f"Duplicate course code found: {course_code_key}")

            # Create separate entries for labs and problem sessions
            next_row = row.find_next_sibling('tr')
            session_counter = 1
            while next_row and next_row.get('class') in ['schtd', 'schtd2']:
                next_cells = next_row.find_all('td')
                if len(next_cells) < len(headers):
                    break

                next_name = safe_text_for_row(next_cells, 'Name', header_indices).strip()
                session_match = re.match(r'^(LAB|P\.S\.|PS|REC)\s*\d*$', next_name)
                if not session_match:
                    break

                session_type = session_match.group(1)
                if session_type == "PS":
                    session_type = "P.S."
                elif session_type == "REC":
                    session_type = "LAB"

                # Parse session info
                session_days = re.findall(r'Th|St|Su|[MTWF]', safe_text_for_row(next_cells, 'Days', header_indices))
                
                hours_text = safe_text_for_row(next_cells, 'Hours', header_indices)
                session_hours = []
                if hours_text:
                    # Extract and validate individual slot numbers
                    for char in hours_text:
                        if char.isdigit():
                            slot_num = int(char)
                            # Only include valid slot numbers (1-8)
                            if 1 <= slot_num <= 8:
                                session_hours.append(slot_num)

                session_rooms = []
                rooms_cell = next_cells[header_indices.get('Rooms', 0)]
                span_rooms = [fix_room_text(span.get_text(strip=True)) for span in rooms_cell.find_all('span')]
                if span_rooms:
                    session_rooms = [r for r in span_rooms if r and r != '|']
                else:
                    room_text = rooms_cell.get_text(strip=True)
                    if room_text:
                        session_rooms = [fix_room_text(r.strip()) for r in re.split(r'[,|]', room_text) if r.strip()]

                # Create session entry with its own course code
                session_code_key = f"{course_code_key} {session_type} {session_counter}"
                session_obj = {
                    "code": f"{course_code_section} {session_type} {session_counter}",
                    "credits": 0,  # Labs/PS typically don't have separate credits
                    "ects": 0.0,
                    "instructor": instructor,  # Use same instructor as main course
                    "name": f"{name} {session_type} {session_counter}",
                    "days": session_days if session_days else [],
                    "hours": session_hours if session_hours else [],
                    "rooms": session_rooms if session_rooms else []
                }

                # Ensure arrays are of equal length if any of them have data
                if any([session_obj["days"], session_obj["hours"], session_obj["rooms"]]):
                    max_len = max(len(session_obj["days"]),
                                len(session_obj["hours"]),
                                len(session_obj["rooms"]))
                    
                    # Extend arrays to match the longest one
                    if session_obj["days"]:
                        last_day = session_obj["days"][-1]
                        session_obj["days"].extend([last_day] * (max_len - len(session_obj["days"])))
                    else:
                        session_obj["days"] = []  # Keep as empty list if no days
                    
                    if session_obj["hours"]:
                        last_hour = session_obj["hours"][-1]
                        session_obj["hours"].extend([last_hour] * (max_len - len(session_obj["hours"])))
                    else:
                        session_obj["hours"] = []  # Keep as empty list if no hours
                    
                    if session_obj["rooms"]:
                        last_room = session_obj["rooms"][-1]
                        session_obj["rooms"].extend([last_room] * (max_len - len(session_obj["rooms"])))
                    else:
                        session_obj["rooms"] = []  # Keep as empty list if no rooms

                # Add session to courses dictionary
                courses[session_code_key] = session_obj
                session_counter += 1

                next_row = next_row.find_next_sibling('tr')

        return courses

    def scrape(self) -> Dict[str, dict]:
        """
        Scrape course information for all departments.

        Returns:
            Dictionary mapping normalized course codes to course data
        """
        aggregated_courses = {}
        sem_label = SEMESTER_MAPPING[self.semester.replace('/', '-', 2)]

        for kisaadi, departments in DEPARTMENT_MAPPING.items():
            for department in departments:
                url = construct_url(self.semester, kisaadi, department)
                logging.info(f"Fetching data for {department} ({kisaadi}) - {sem_label}")

                html_content, error = self.fetch_html(url)
                if error:
                    logging.error(f"Error fetching {department}: {error}")
                    continue
                if not html_content:
                    continue

                soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
                
                # Check for error messages on the page
                error_msg = soup.find('div', class_='error')
                if error_msg:
                    logging.error(f"Error message on page: {error_msg.get_text()}")
                    continue

                # Parse time slots and pass to extract_course_data
                time_slots = parse_time_slots(soup)
                if time_slots:
                    courses = self.extract_course_data(soup, time_slots)
                    if courses:
                        aggregated_courses.update(courses)
                        logging.info(f"Found {len(courses)} courses for {department}")
                    else:
                        logging.warning(f"No courses found for {department}")
                else:
                    logging.warning(f"Could not parse time slots for {department}")

                # Respectful delay between requests
                sleep(1)

        if not aggregated_courses:
            logging.warning("No courses were found for any department")
        else:
            logging.info(f"Total courses found: {len(aggregated_courses)}")

        return aggregated_courses
