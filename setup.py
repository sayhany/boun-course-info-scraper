from setuptools import setup, find_packages

setup(
    name="boun-course-info",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
    ],
    entry_points={
        "console_scripts": [
            "get-boun-course-info=boun_course_info.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Sayhan",
    description="A tool to scrape course information from Boğaziçi University's registration website",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
