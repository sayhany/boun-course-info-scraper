"""Command-line interface for the Boğaziçi University Course Information Scraper."""

import argparse
import json
import logging
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .config import DEPARTMENT_MAPPING, SEMESTER_MAPPING
from .scraper import CourseInfoScraper  # Import CourseInfoScraper
from .utils import construct_url, parse_time_slots


def setup_logging(debug: bool = False):
    """Configure logging with a consistent format."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def test_fetch(semester: str, kisaadi: str = "CMPE", save_html: bool = True, debug: bool = False, include_unscheduled: bool = False) -> None:
    """
    Test fetching data for a single department and optionally save the raw HTML.
    
    Args:
        semester: The semester code (e.g., '2024-2025-1')
        kisaadi: The department code to test (default: CMPE)
        save_html: Whether to save the raw HTML to a file
        debug: Enable debug logging
        include_unscheduled: Whether to include courses without scheduled meeting information
    """
    department = DEPARTMENT_MAPPING[kisaadi][0]
    url = construct_url(semester, kisaadi, department)
    
    logging.info(f"Testing URL: {url}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    })
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        logging.info(f"Response status: {response.status_code}")
        logging.info(f"Content type: {response.headers.get('content-type')}")
        logging.info(f"Content length: {len(response.text)} bytes")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Log page title
        title = soup.find('title')
        if title:
            logging.info(f"Page title: {title.string}")
        
        # Log all tables found
        tables = soup.find_all('table')
        logging.info(f"Found {len(tables)} tables")
        for i, table in enumerate(tables):
            logging.info(f"Table {i} attributes: {table.attrs}")
            first_row = table.find('tr')
            if first_row:
                logging.info(f"Table {i} first row: {first_row.get_text()[:100]}...")

        if debug:
            # Parse time slots
            time_slots = parse_time_slots(soup)
            logging.debug(f"Parsed Time Slots in Test Mode: {time_slots}")

            # Initialize scraper and extract course data
            scraper = CourseInfoScraper(semester, include_unscheduled=include_unscheduled)  # Pass include_unscheduled flag
            courses = scraper.extract_course_data(soup, time_slots)  # Call extract_course_data method and pass time_slots
            logging.debug(f"Extracted Course Data in Test Mode:\n{json.dumps(courses, indent=2, ensure_ascii=False)}")

            # Save the HTML content to a file for debugging
            output_file = f"test_response_{kisaadi}_{semester}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logging.info(f"Saved raw HTML to {output_file}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch URL: {e}")


def main():
    """Entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Scrape course information from Boğaziçi University's registration website."
    )
    parser.add_argument(
        "semester",
        help=(
            "Semester code (e.g., '2024-2025-1' for Fall Semester). "
            f"Valid options: {', '.join(SEMESTER_MAPPING.keys())}"
        )
    )
    parser.add_argument(
        "--output",
        default="courses.json",
        help="Output JSON file path (default: courses.json)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (fetch single department and save HTML)"
    )
    parser.add_argument(
        "--department",
        default="CMPE",
        help="Department code to use in test mode (default: CMPE)"
    )
    parser.add_argument(
        "--include-unscheduled",
        action="store_true",
        help="Include courses without scheduled meeting information (default omits these courses)"
    )

    args = parser.parse_args()
    setup_logging(args.debug)

    try:
        if args.test:
            test_fetch(args.semester, args.department, save_html=True, debug=args.debug, include_unscheduled=args.include_unscheduled)
            return

        # Initialize and run the scraper
        scraper = CourseInfoScraper(args.semester, include_unscheduled=args.include_unscheduled)
        logging.info(f"Starting scraper for {SEMESTER_MAPPING[args.semester]}")
        courses = scraper.scrape()

        # Ensure the output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the results to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(courses, f, ensure_ascii=False, indent=2)

        logging.info(f"Successfully scraped {len(courses)} courses")
        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
