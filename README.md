# Job Market Trends Dashboard (UK)

Author: Kelvin Rushbrook  
Degree: BSc (Hons) Data Science and Analytics – University of Westminster  
Module: 6DATA007W – Final Year Project

---

## Project Overview

This work in progress project analyses live UK job posting data to identify trends in roles, skills, and employment data.
The core objective is to build a reproducible data pipeline that collects real job postings, infers required skills using a standardised taxonomy, and prepares the data for analysis and dashboard visualisation.

Rather than relying solely on job description text, which is often truncated or inconsistent, the project maps job titles to standardised occupations and infers skills indirectly, currently by using the ESCO framework.
This improves reliability, scalability, and defensibility.

The final outcome will be an interactive dashboard allowing users to explore trends across roles, skill demand, locations, and salaries within the UK job market.

--- 

## Challenges

This project faced several technical challenges, mainly related to data quality and the reliable extraction of job skills from live job postings. Job descriptions retrieved via the Adzuna API were truncated and lacked skill information, making direct skill extraction from text unreliable. 

To mitigate this, the project inferred skills indirectly by mapping Adzuna job titles to standardised ESCO occupations and assigning skills to the Adzuna job title, based on the ESCO taxonomy, improving consistency and scalability.

Fuzzy matching between Adzuna job titles and ESCO occupations sometimes introduced innacurate matches, highlighting the need for iterative refinement and justifying the use of the CRISP DM methodology.

---

## Key Features

- Live UK job data collection using the Adzuna API
- Automated, repeatable data engineering pipeline
- Skill inference using the ESCO job-skill taxonomy
- Fuzzy job title matching to handle non standard employer titles
- Clear separation of raw, intermediate, and processed data
- Designed for future integration with a Streamlit dashboard

---

## Project contents overview

| Directory | Purpose |
|----------|---------|
| FYPMain/ | Root folder |
| .git/ | Git version control metadata |
| various git folders... | Internal Git files (created by Git) |
| data/ | All datasets are stored here |
| ESCO/ | ESCO source / reference datasets |
| Used/ | ESCO datasets actively used in the pipeline |
| occupations_en.csv | ESCO occupation list file |
| occupationSkillRelations_en.csv | ESCO occupation and skill link list file |
| skills_en.csv | ESCO skill list file |
| processed/ | For datasets that are created by the scripts |
| job_skills_extracted.xlsx | The final output dataset with job titles and their corresponding skills |
| job_skills_library.parquet | A parquet file created to list all ESCO skills against all job titles |
| raw | The output folder for the raw Adzuna file created by data_pull.py |
| src/ | Folder to store all source code |
| data_collection/ | Folder to store data collection/ sourcing scripts |
| data_pull.py | Scripts for pulling job posting data via Adzuna API |
| skills_extraction/ | Folder to store data skill extraction scripts |
| ESCO_combine.py | Script for building ESCO job and skill datasets (job_skills_library.parquet) |
| job_skill_assignment.py | Script for assigning skills to input jobs , and generating the job_skills_extracted.xlsx file |
| .gitignore | Fles/Folders excluded from Git |
| api_template.env | Safe template showing API variable example |
| README.md | Project documentation (setup, structure, execution order |
| requirements.txt | Python dependencies needed to run the project |

## Data Pipeline Overview

### Live Job Data Collection
Script: data_pull.py

- Retrieves live UK job postings via the Adzuna API
- Accepts user defined keywords and record limits
- Handles pagination and duplicate removal
- Outputs raw data to adzuna_raw.xlsx

---

### ESCO Job-Skill Reference Library
Script: ESCO_combine.py

- Combines official ESCO datasets into a single reference file
- Links occupations to associated skills
- Filters to knowledge based skills only
- Outputs job_skills_library.parquet

---

### Job Title Matching and Skill Assignment
Script: job_skill_assignment.py

- Fuzzy matches Adzuna job titles to ESCO occupations
- Assigns essential ESCO skills to each job posting
- Outputs job_skills_extracted.xlsx linking job titles, skills, salary ranges, locations, and match confidence scores

---

## Technologies Used

- Python
  - pandas
  - numpy
  - requests
  - rapidfuzz
  - pyarrow
  - python-dotenv
  - openpyxl
- Data formats
  - Excel (.xlsx)
  - Parquet (.parquet)
- Planned visualisation
  - Streamlit
- Version control
  - Git and GitHub

## Setup Instructions

### Clone the repository
1. git clone https://github.com/Kelstudy/FypMain
2. cd FypMain

### Install dependencies
pip install -r requirements.txt

### Configure API credentials 

1. Edit api_template.env to include your API credentials for Adzuna


## Execution Order
Run scripts in the following order:

1. src/data_collection/data_pull.py
2. src/skills_extraction/ESCO_combine.py
3. src/skills_extraction/job_skill_assignment.py

Each script is rerunnable and designed to overwrite outdated outputs.



## Current Status

- Live data pipeline implemented
- ESCO skill inference working
- Structured outputs generated
- Dashboard development pending
- Final analysis and report pending

---

"Microsite: https://sites.google.com/view/skillsignal/home"

