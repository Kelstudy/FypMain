import pandas as pd
import re
from pathlib import Path
import rapidfuzz

#Setup paths
BaseDir = Path(__file__).parents[2] 
fileIn = BaseDir / "data" / "raw" / "adzuna_raw.xlsx"
escoLibraryIn = BaseDir / "data" /"processed"/ "job_skills_library.parquet"
fileOut = BaseDir / "data" / "processed" / "job_skills_extracted.xlsx"

def main():
    if not fileIn.exists() or not escoLibraryIn.exists():
        print("ERROR - Missing input files")
        return
    
    adzunaDF = pd.read_excel(fileIn)
    escoLibraryDF = pd.read_excel(escoLibraryIn)

    #get top 500 most common skills of all jobs for later skill extraction from job descriptions
    commonSkills = escoLibraryDF["preferredLabel_skill"].value_counts().head(500).index.tolist()
    # get unique job titles for later use
    escoTitles = escoLibraryDF["preferredLabel_job"].unique()

    #Use to store jobs and skills final results
    results = []

    