# Boğaziçi University Course Information Scraper

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A tool for scraping course information from Boğaziçi University's registration website. This scraper extracts course data including schedules, instructors, rooms, and credit information for all departments across multiple semesters.

## Features

- 📅 **Multi-semester Support**: Can fetch data from multiple academic terms (2021-2022 through 2024-2025)
- 📊 **Rich Course Data**: Extracts detailed information including:
  - Course codes and sections
  - Credit hours and ECTS credits
  - Instructor information
  - Schedule details (days and hours)
  - Room assignments
  - Lab and PS (Problem Solving) sessions
- 🔄 **JSON Output**: Saves data in structured JSON format
- 🛠 **Configurable Options**: Supports various scraping configurations including:
  - Including/excluding unscheduled courses
  - Debug mode for detailed logging
  - Test mode for single department testing
- 🌐 **Robust Handling**: Manages Turkish character encoding and various edge cases

## Installation

1. Ensure you have Python 3.8 or higher installed
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/boun-course-info-scraper.git
   cd boun-course-info-scraper
   ```
3. Install the package:
   ```bash
   pip install .
   ```

## Usage

### Basic Usage

The scraper can be used as a command-line tool:

```bash
get-boun-course-info 2024-2025-1 --output courses.json
```

This will scrape all courses for the Fall 2024 semester and save them to `courses.json`.

### Command-line Options

- `semester`: Required. The semester code (e.g., '2024-2025-1' for Fall Semester)
- `--output`: Output JSON file path (default: courses.json)
- `--debug`: Enable debug logging
- `--test`: Run in test mode (fetch single department)
- `--department`: Department code to use in test mode (default: CMPE)
- `--include-unscheduled`: Include courses without scheduled meeting information

### Example Commands

Test mode for a specific department:
```bash
get-boun-course-info 2024-2025-1 --test --department CMPE
```

Include unscheduled courses:
```bash
get-boun-course-info 2024-2025-1 --include-unscheduled
```

Enable debug logging:
```bash
get-boun-course-info 2024-2025-1 --debug
```

## Output Format

The scraper outputs a JSON file with the following structure:

```json
{
  "CMPE150.01": {
    "code": "CMPE150.01",
    "credits": 3,
    "ects": 6.0,
    "instructor": "JOHN DOE",
    "name": "Introduction to Computing",
    "days": ["M", "W", "F"],
    "hours": [3, 3, 3],
    "rooms": ["M2170", "M2170", "M2170"]
  },
  "CMPE150.01 PS 1": {
    "code": "CMPE150.01 PS 1",
    "credits": 0,
    "ects": 0.0,
    "instructor": "JOHN DOE",
    "name": "Introduction to Computing PS 1",
    "days": ["T"],
    "hours": [5],
    "rooms": ["M2170"]
  }
}
```

## Supported Departments

The scraper supports all departments at Boğaziçi University, including:

- CMPE (Computer Engineering)
- EE (Electrical & Electronics Engineering)
- IE (Industrial Engineering)
- ME (Mechanical Engineering)
- MATH (Mathematics)
- PHYS (Physics)
- ...and many more

For a complete list, check the `DEPARTMENT_MAPPING` in the configuration.

## Semesters

Each academic year is divided into three semesters, identified by a suffix number:

- Fall Semester: Suffix `-1` (e.g., "2024-2025-1")
- Spring Semester: Suffix `-2` (e.g., "2024-2025-2")
- Summer Semester: Suffix `-3` (e.g., "2024-2025-3")

For example, to scrape Fall 2024 courses, you would use the semester code `2024-2025-1`.

## Development

### Requirements

- Python 3.8+
- requests>=2.31.0
- beautifulsoup4>=4.12.2

### Project Structure

```
boun-course-info-scraper/
├── src/
│   └── boun_course_info/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py          # Command-line interface
│       ├── config.py       # Configuration and mappings
│       ├── scraper.py      # Core scraping functionality
│       └── utils.py        # Utility functions
├── setup.py
└── requirements.txt
```

### Running Tests

Currently, the project uses manual testing through the `--test` flag:

```bash
get-boun-course-info 2024-2025-1 --test --department CMPE --debug
```

## Known Limitations

- Rate limiting: Includes a 1-second delay between requests to avoid overwhelming the server
- Some courses might have incomplete or missing data
- Depends on the stability of the registration website's HTML structure

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Boğaziçi University Registration System
- Beautiful Soup library for HTML parsing
- Requests library for HTTP requests

## Contact

For questions and feedback:

- GitHub Issues: [Create an issue](https://github.com/sayhany/boun-course-info-scraper/issues)

## Changelog

### [0.1.0] - 2024
- Initial release
- Basic scraping functionality
- Support for all departments
- JSON output format
- Command-line interface