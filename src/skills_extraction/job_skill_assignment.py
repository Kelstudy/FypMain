import pandas as pd
import re
from pathlib import Path
from rapidfuzz import process,utils,fuzz

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
    escoLibraryDF = pd.read_parquet(escoLibraryIn)

    #get top 500 most common skills of all jobs for later skill extraction from job descriptions
    commonSkills = escoLibraryDF["preferredLabel_skill"].value_counts().head(500).index.tolist()
    # get unique job titles for later use
    escoTitles = escoLibraryDF["preferredLabel_job"].unique()

    #Use to store final results for jobs plus their skills
    results = []

    print (f"Refining matches for {len(adzunaDF)} jobs...")

    #get job information
    for i , row in adzunaDF.itterows():
        jobID = row.get("id","N/A")
        rawTitle = str(row["title"])
        roleGroup = str(row.get("search_keyword", "Unknown")).lower()
        description = str(row["description"]).lower()
        contractType = str(row["contract_type"])
        postingUrl = str(row["redirect_url"])
        salaryMin = float(row["salary_min"])
        salaryMax = float(row["salary_max"])


    # Use FuzzySearch to find closest ESCO job title compared to Adzuna job title
    fuzzyMatchResult = process.extractOne(
        rawTitle,
        escoTitles,
        scorer = fuzz.WRatio, # WRatio chosen as found best for general purpose
        processor = utils.default_process  # remove non-alphanumeric, trim whitespaces, convert to lower case
    )



    


        




    