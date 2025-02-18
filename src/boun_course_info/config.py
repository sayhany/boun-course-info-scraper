"""Configuration for the Boğaziçi University Course Information Scraper."""

# Base URL pattern for course information
BASE_URL = "https://registration.bogazici.edu.tr/scripts/sch.asp?donem={SEMESTER}&kisaadi={KISAADI}&bolum={DEPARTMENT_NAME}"

# Complete department mapping: kisaadi → list of department names
DEPARTMENT_MAPPING = {
    "ASIA": ["ASIAN STUDIES", "ASIAN STUDIES WITH THESIS"],
    "ATA": ["ATATURK INSTITUTE FOR MODERN TURKISH HISTORY"],
    "BM": ["BIOMEDICAL ENGINEERING"],
    "BIS": ["BUSINESS INFORMATION SYSTEMS", "BUSINESS INFORMATION SYSTEMS (WITH THESIS)"],
    "CHE": ["CHEMICAL ENGINEERING"],
    "CHEM": ["CHEMISTRY"],
    "CE": ["CIVIL ENGINEERING"],
    "COGS": ["COGNITIVE SCIENCE"],
    "CSE": ["COMPUTATIONAL SCIENCE & ENGINEERING"],
    "CET": ["COMPUTER EDUCATION & EDUCATIONAL TECHNOLOGY", "EDUCATIONAL TECHNOLOGY"],
    "CMPE": ["COMPUTER ENGINEERING"],
    "INT": ["CONFERENCE INTERPRETING"],
    "CEM": ["CONSTRUCTION ENGINEERING AND MANAGEMENT"],
    "CCS": ["CRITICAL AND CULTURAL STUDIES"],
    "ED": ["CURRICULUM AND INSTRUCTIONAL PROGRAMS", "EDUCATIONAL SCIENCES"],
    "DSAI": ["DATA SCIENCE AND ARTIFICIAL INTELLIGENCE"],
    "PRED": ["EARLY CHILDHOOD EDUCATION"],
    "EQE": ["EARTHQUAKE ENGINEERING"],
    "EC": ["ECONOMICS"],
    "EF": ["ECONOMICS AND FINANCE"],
    "EE": ["ELECTRICAL & ELECTRONICS ENGINEERING"],
    "ETM": ["ENGINEERING AND TECHNOLOGY MANAGEMENT"],
    "LL": ["ENGLISH LITERATURE", "WESTERN LANGUAGES & LITERATURES"],
    "ENV": ["ENVIRONMENTAL SCIENCES"],
    "ENVT": ["ENVIRONMENTAL TECHNOLOGY"],
    "XMBA": ["EXECUTIVE MBA"],
    "FE": ["FINANCIAL ENGINEERING"],
    "PA": ["FINE ARTS"],
    "FLED": ["FOREIGN LANGUAGE EDUCATION"],
    "GED": ["GEODESY"],
    "GPH": ["GEOPHYSICS"],
    "GUID": ["GUIDANCE & PSYCHOLOGICAL COUNSELING"],
    "HIST": ["HISTORY"],
    "HUM": ["HUMANITIES COURSES COORDINATOR"],
    "IE": ["INDUSTRIAL ENGINEERING"],
    "MIR": [
        "INTERNATIONAL RELATIONS:TURKEY, EUROPE AND THE MIDDLE EAST",
        "INTERNATIONAL RELATIONS:TURKEY, EUROPE AND THE MIDDLE EAST WITH THESIS"
    ],
    "INTT": ["INTERNATIONAL TRADE", "INTERNATIONAL TRADE MANAGEMENT"],
    "LAW": ["LAW PR."],
    "LS": ["LEARNING SCIENCES"],
    "LING": ["LINGUISTICS"],
    "AD": ["MANAGEMENT"],
    "MIS": ["MANAGEMENT INFORMATION SYSTEMS"],
    "MATH": ["MATHEMATICS"],
    "SCED": ["MATHEMATICS AND SCIENCE EDUCATION"],
    "ME": ["MECHANICAL ENGINEERING"],
    "MECA": ["MECHATRONICS ENGINEERING (WITH THESIS)"],
    "BIO": ["MOLECULAR BIOLOGY & GENETICS"],
    "PF": ["PEDAGOGICAL FORMATION CERTIFICATE PROGRAM"],
    "PHIL": ["PHILOSOPHY"],
    "PE": ["PHYSICAL EDUCATION"],
    "PHYS": ["PHYSICS"],
    "POLS": ["POLITICAL SCIENCE&INTERNATIONAL RELATIONS"],
    "PSY": ["PSYCHOLOGY"],
    "YADYOK": ["SCHOOL OF FOREIGN LANGUAGES"],
    "SPL": ["SOCIAL POLICY WITH THESIS"],
    "SOC": ["SOCIOLOGY"],
    "SWE": ["SOFTWARE ENGINEERING", "SOFTWARE ENGINEERING WITH THESIS"],
    "TRM": ["SUSTAINABLE TOURISM MANAGEMENT", "TOURISM ADMINISTRATION", "TOURISM MANAGEMENT"],
    "SCO": ["SYSTEMS & CONTROL ENGINEERING"],
    "WTR": ["TRANSLATION"],
    "TR": ["TRANSLATION AND INTERPRETING STUDIES"],
    "TK": ["TURKISH COURSES COORDINATOR"],
    "TKL": ["TURKISH LANGUAGE & LITERATURE"],
    "PRSO": ["UNDERGRADUATE PROGRAM IN PRESCHOOL EDUCATION"]
}

# Semester mapping: donem parameter → human-readable semester
SEMESTER_MAPPING = {
    # 2021-2022
    "2021-2022-2": "Spring Semester",
    "2021-2022-3": "Summer Semester",
    # 2022-2023
    "2022-2023-1": "Fall Semester",
    "2022-2023-2": "Spring Semester",
    "2022-2023-3": "Summer Semester",
    # 2023-2024
    "2023-2024-1": "Fall Semester",
    "2023-2024-2": "Spring Semester",
    "2023-2024-3": "Summer Semester",
    # 2024-2025
    "2024-2025-1": "Fall Semester",
    "2024-2025-2": "Spring Semester",
    "2024-2025-3": "Summer Semester"
}
