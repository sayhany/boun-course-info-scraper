"""Utility functions for the Boğaziçi University Course Information Scraper."""

import re
from typing import Dict, List, Optional, Union
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag

from .config import BASE_URL
import logging


def construct_url(semester: str, kisaadi: str, department: str) -> str:
    """
    Construct the URL for fetching course information.

    Args:
        semester: The semester code (e.g., '2024/2025-1')
        kisaadi: The department abbreviation
        department: The full department name

    Returns:
        The constructed URL with properly encoded parameters
    """
    # URL-encode the department name, preserving certain characters
    department_encoded = quote(department, safe='')
    return BASE_URL.format(
        SEMESTER=semester,
        KISAADI=kisaadi,
        DEPARTMENT_NAME=department_encoded
    )


def parse_time_slots(soup: BeautifulSoup) -> Dict[int, int]:
    """
    Parse the time slot legend table to map slot numbers to start times.

    Args:
        soup: BeautifulSoup object of the page HTML

    Returns:
        Dictionary mapping slot numbers to their start times (hour)
    """
    time_slots = {}
    legend_table = soup.find('table', style='margin:20px 0')
    
    if not legend_table:
        logging.debug("Time slots table not found in HTML")
        return time_slots

    logging.debug("Time slots table found")
    logging.debug(f"Table HTML: {legend_table.prettify()}")
    
    # Process each row in the table
    for row in legend_table.find_all('tr'):
        # Skip the header row that contains "The course slots are as follows"
        if row.find('td', colspan=True):
            continue
            
        logging.debug(f"Processing row: {row.prettify()}")
        
        # Find all cells with class="bodygray"
        cells = row.find_all('td', class_='bodygray')
        
        # Process cells in pairs within each row
        for i in range(0, len(cells), 2):
            if i + 1 >= len(cells):
                break
                
            slot_cell = cells[i]
            time_cell = cells[i+1]

            # Check if this is a slot cell by looking for bold text in the HTML
            slot_html = str(slot_cell)
            if '<b>' not in slot_html:
                logging.debug("Skipping non-slot cell (no bold text)")
                continue
                
            slot_text = slot_cell.get_text(strip=True)
            time_text = time_cell.get_text(strip=True)
            
            logging.debug(f"Processing pair - Slot: '{slot_text}', Time: '{time_text}'")
            logging.debug(f"Slot cell HTML: {slot_html}")
            logging.debug(f"Time cell HTML: {time_cell}")
            
            # Extract slot number from text like "Slot 1"
            slot_match = re.search(r'Slot\s*(\d+)', slot_text)
            if not slot_match:
                logging.debug(f"No slot number found in '{slot_text}'")
                continue
                
            slot_number = int(slot_match.group(1))
            logging.debug(f"Found slot number: {slot_number}")
            
            # Extract start hour from text like ": 09:00 - 09:50"
            time_match = re.search(r':\s*(\d{2}):(\d{2})\s*-', time_text)
            if not time_match:
                logging.debug(f"No time found in '{time_text}'")
                continue
                
            start_hour = int(time_match.group(1))
            time_slots[slot_number] = start_hour
            logging.debug(f"Successfully mapped slot {slot_number} to hour {start_hour}")

    logging.debug(f"Found {len(time_slots)} time slots: {time_slots}")
    return time_slots


def parse_days(days_text: str) -> List[str]:
    """
    Parse the days string into a list of day abbreviations.
    Handles repeated patterns like "StStSt" or "MMM".

    Args:
        days_text: String containing day abbreviations

    Returns:
        List of unique day abbreviations
    """
    if not days_text:
        return []

    # Define the possible day patterns
    day_patterns = ['St', 'Th', 'M', 'T', 'W', 'F']
    
    # Initialize the result list
    days = []
    
    # Process the text character by character
    i = 0
    while i < len(days_text):
        # Check for two-character days first
        if i + 1 < len(days_text):
            two_chars = days_text[i:i+2]
            if two_chars in ['St', 'Th']:
                if two_chars not in days:  # Only add if not already present
                    days.append(two_chars)
                i += 2
                continue
        
        # Check for single-character days
        one_char = days_text[i]
        if one_char in ['M', 'T', 'W', 'F']:
            if one_char not in days:  # Only add if not already present
                days.append(one_char)
        i += 1
    
    return days


def parse_hours(hours_text: str, time_slots: Dict[int, int]) -> List[int]:
    """
    Parse the hours string into a list of start times.

    Args:
        hours_text: String containing slot numbers
        time_slots: Dictionary mapping slot numbers to start times

    Returns:
        List of start times (hours)
    """
    if not hours_text:
        return []

    # Extract individual digits, ensuring they're treated as separate slots
    # This will handle cases like "1415" by splitting into ['1', '4', '1', '5']
    hours = []
    for char in hours_text:
        if char.isdigit():
            slot_num = int(char)
            # Only include valid slot numbers (1-8)
            if 1 <= slot_num <= 8:
                hours.append(slot_num)
    
    return sorted(hours)  # Return sorted list of hours


def parse_rooms(rooms_cell: Tag) -> List[str]:
    """
    Parse the rooms cell into a list of room codes.
    Handles rooms separated by red vertical bars.

    Args:
        rooms_cell: BeautifulSoup Tag object of the rooms cell

    Returns:
        List of room codes
    """
    rooms = []
    
    # First try to find span elements
    spans = rooms_cell.find_all('span', onclick=True)  # Only get spans with onclick attribute
    if spans:
        rooms = [span.get_text(strip=True) for span in spans if span.get_text(strip=True)]
    else:
        # If no spans found, try to parse the text directly
        text = rooms_cell.get_text(strip=True)
        if text:
            # Split by the red vertical bar and clean up each room code
            rooms = [room.strip() for room in text.split('|') if room.strip()]
    
    return rooms


def normalize_course_code(code: str) -> str:
    """
    Normalize a course code by removing spaces and converting to uppercase.

    Args:
        code: The course code to normalize (e.g., 'CMPE 150.01')

    Returns:
        Normalized course code (e.g., 'CMPE150.01')
    """
    return code.replace(' ', '').upper()


def parse_credits(credits_text: str) -> int:
    """
    Parse the credits string into an integer.

    Args:
        credits_text: String containing the credits value

    Returns:
        Integer value of credits, or 0 if parsing fails
    """
    try:
        return int(credits_text) if credits_text and credits_text.isdigit() else 0
    except (ValueError, AttributeError):
        return 0


def parse_ects(ects_text: str) -> float:
    """
    Parse the ECTS string into a float.

    Args:
        ects_text: String containing the ECTS value

    Returns:
        Float value of ECTS credits, or 0.0 if parsing fails
    """
    if not ects_text:
        return 0.0
    
    try:
        # Replace comma with dot for decimal point
        ects_text = ects_text.replace(',', '.')
        return float(ects_text)
    except (ValueError, AttributeError):
        return 0.0


def parse_departments(dept_text: str) -> List[str]:
    """
    Parse the departments string into a list of department codes.

    Args:
        dept_text: String containing semicolon-separated department codes

    Returns:
        List of department codes
    """
    if not dept_text:
        return []
    
    # Split by semicolon and clean up each department code
    return [dept.strip() for dept in dept_text.split(';') if dept.strip()]


def extract_course_data(soup: BeautifulSoup, time_slots: Dict[int, int]) -> Dict[str, dict]:
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

        def safe_text(field):
            idx = header_indices.get(field, None)
            return cells[idx].get_text(strip=True) if idx is not None and cells[idx] else ""

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
        if hours_text:
            slot_numbers = re.findall(r'\d', hours_text)  # Changed to parse individual digits
            hours = [time_slots.get(int(slot)) for slot in slot_numbers if slot.isdigit() and int(slot) in time_slots]
        else:
            hours = []

        rooms_cell = cells[header_indices.get('Rooms', 0)]
        rooms = [span.get_text(strip=True) for span in rooms_cell.find_all('span')]
        if not rooms:
            room_text = rooms_cell.get_text(strip=True)
            if room_text:
                rooms = [r.strip() for r in room_text.split('|') if r.strip()]

        # Check if this is a nested session (LAB, P.S., etc.)
        session_type = safe_text('Name').strip()
        is_nested = bool(re.match(r'^(LAB|P\.S\.|PS|REC)\s*\d*$', session_type))

        # If this is a nested session, skip creating a new course object
        if is_nested:
            continue

        # Get all sessions for this course (main + nested)
        all_sessions = []
        current_session = {
            "days": days,
            "hours": hours,
            "rooms": rooms
        }
        all_sessions.append(current_session)

        # Look for nested sessions
        next_row = row.find_next_sibling('tr')
        while next_row and next_row.get('class') in ['schtd', 'schtd2']:
            next_cells = next_row.find_all('td')
            if len(next_cells) < len(headers):
                break

            def safe_text_for_row(cells, field, header_indices):
                idx = header_indices.get(field, None)
                return cells[idx].get_text(strip=True) if idx is not None and idx < len(cells) else ""

            next_name = safe_text_for_row(next_cells, 'Name', header_indices).strip()
            if not re.match(r'^(LAB|P\.S\.|PS|REC)\s*\d*$', next_name):
                break

            # Parse session info
            session_days = re.findall(r'Th|St|Su|[MTWF]', safe_text_for_row(next_cells, 'Days', header_indices))
            
            session_hours = []
            hours_text = safe_text_for_row(next_cells, 'Hours', header_indices)
            if hours_text:
                slot_numbers = re.findall(r'\d', hours_text)  # Changed to parse individual digits
                session_hours = [time_slots.get(int(slot)) for slot in slot_numbers if slot.isdigit() and int(slot) in time_slots]

            session_rooms = []
            rooms_cell = next_cells[header_indices.get('Rooms', 0)]
            span_rooms = [span.get_text(strip=True) for span in rooms_cell.find_all('span')]
            if span_rooms:
                session_rooms = [r for r in span_rooms if r and r != '|']
            else:
                room_text = rooms_cell.get_text(strip=True)
                if room_text:
                    session_rooms = [r.strip() for r in re.split(r'[,|]', room_text) if r.strip()]

            if session_days or session_hours or session_rooms:
                all_sessions.append({
                    "days": session_days,
                    "hours": session_hours,
                    "rooms": session_rooms
                })

            next_row = next_row.find_next_sibling('tr')

        # Combine all sessions into single arrays
        combined_days = []
        combined_hours = []
        combined_rooms = []
        for session in all_sessions:
            if session["days"]: combined_days.extend(session["days"])
            if session["hours"]: combined_hours.extend(session["hours"])
            if session["rooms"]: combined_rooms.extend(session["rooms"])

        # Create course object with only the required fields
        course_obj = {
            "code": course_code_section,
            "credits": credits,
            "ects": ects,
            "instructor": instructor,
            "name": name,
            "days": combined_days,
            "hours": combined_hours,
            "rooms": combined_rooms
        }

        # Ensure arrays are of equal length
        if course_obj["days"] or course_obj["hours"] or course_obj["rooms"]:
            max_len = max(len(course_obj["days"] or []),
                         len(course_obj["hours"] or []),
                         len(course_obj["rooms"] or []))
            
            # Extend arrays to match the longest one by repeating the last element
            if course_obj["days"]:
                last_day = course_obj["days"][-1]
                course_obj["days"].extend([last_day] * (max_len - len(course_obj["days"])))
            if course_obj["hours"]:
                last_hour = course_obj["hours"][-1]
                course_obj["hours"].extend([last_hour] * (max_len - len(course_obj["hours"])))
            if course_obj["rooms"]:
                last_room = course_obj["rooms"][-1]
                course_obj["rooms"].extend([last_room] * (max_len - len(course_obj["rooms"])))

        if course_code_key not in courses:
            courses[course_code_key] = course_obj
        else:
            logging.info(f"Duplicate course code found: {course_code_key}")

    return courses
