#!/usr/bin/env python3
"""Script to download course data for all semesters."""

import os
import subprocess
from datetime import datetime

# List of semesters to download (from 2021/2022-2 to 2024/2025-2)
SEMESTERS = [
    "2021-2022-3",
    "2022-2023-1",
    "2022-2023-2",
    "2022-2023-3",
    "2023-2024-1",
    "2023-2024-2",
    "2023-2024-3",
    "2024-2025-1",
    "2024-2025-2"
]

def main():
    """Download course data for all semesters."""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    print(f"Starting download at {datetime.now()}")
    
    for semester in SEMESTERS:
        output_file = f"data/{semester.replace('/', '-')}.json"
        print(f"\nDownloading {semester}...")
        
        try:
            subprocess.run(
                [
                    "python3", "-m", "boun_course_info",
                    semester,
                    "--output", output_file
                ],
                check=True
            )
            print(f"Successfully downloaded {semester} to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {semester}: {e}")
            continue
    
    print(f"\nDownload completed at {datetime.now()}")

if __name__ == "__main__":
    main()
