import pandas as pd
from pathlib import Path

def buildTechSkillLibrary():

    #setup paths
    baseDirectory = Path(__file__).parents[2]
    escoSourceDataFolder = baseDirectory/"data"/"ESCO"/"Used"
    outputFile = baseDirectory/"data"/"processed"/"job_skills_library.parquet"

    print("Building ESCO tech library...")

    # load data

    allOccupationsDF = pd.read_csv(escoSourceDataFolder/"occupations_en.csv")   # dataset for ESCO job roles
    allSkillsDf = pd.read_csv(escoSourceDataFolder / 'skills_en.csv')   # dataset for ESCO skill sets
    jobToSkillsLinksDF = pd.read_csv(escoSourceDataFolder/"OccupationSkillRelations_en.csv")    # dataset for ESCO job role and their related skill requirements


    #merge jobs with their skill links
    jobsWithSkillIdsDf = pd.merge(
        allOccupationsDF[['conceptUri', 'preferredLabel']], 
        jobToSkillsLinksDF[['occupationUri', 'skillUri', 'relationType',"skillType"]], 
        left_on='conceptUri',  
        right_on='occupationUri'
    )

    # Attach skill names
    libraryWithNamesDF = pd.merge(
        jobsWithSkillIdsDf,
        allSkillsDf[['conceptUri', 'preferredLabel']],
        left_on="skillUri",
        right_on="conceptUri",
        suffixes = ("_job","_skill")
    )

    # Filter to only include "knowledge" skills as "skill/competence" types are too vague
    knowledgeLibraryDF = libraryWithNamesDF[libraryWithNamesDF["skillType"]=="knowledge"]

    
    #Cleanup and export
    #Selerct the 3 columns we need for final library
    finalLibraryDF = knowledgeLibraryDF[["preferredLabel_job","preferredLabel_skill","relationType","skillType"]]

    
    finalLibraryDF.to_parquet(outputFile, index=False)
    print("file exported")

# Only run if called , not when this script imported into another file
if __name__ == "buildTechSkillLibrary":
    buildTechSkillLibrary()