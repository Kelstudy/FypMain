import streamlit as st
import pandas as pd
import pydeck as pdk
from pathlib import Path
import sys

#Setup Streamlit page config
st.set_page_config(page_title="Job Skill Matcher", layout="wide") 

#Set project root folder
rootPath = Path(__file__).resolve().parents[1]  # FypMain/

#add root folder to pythons search list and set to search there first for imports below
sys.path.insert(0, str(rootPath))

#Import data pipeline functions
from src.data_pipeline.data_pull import main as adzunaPull
from src.data_pipeline.ESCO_combine import buildTechSkillLibrary
from src.data_pipeline.job_skill_assignment import main as assignSkills

# Function to check if the ESCO library exists and create it if not
def ensureEscoLibraryExists():
    escoFile = rootPath / "data" / "processed" / "job_skills_library.parquet"
    if not escoFile.exists():
        print("Setup: Building ESCO library for the first time...")
        buildTechSkillLibrary()
    return True

ensureEscoLibraryExists()

#Define format to show salary in for later
def formatSalary(value):
    if pd.notnull(value):
        return f"{value:,.0f}"
    else:
        return "N/A"

#Streamlit header
st.title("SkillSignal UK Job Posting Dashboard")

#Streamlit sidebar controls
with st.sidebar:
    st.header("Search Parameters")
    jobTitleInput = st.text_input("Enter a Job Title", placeholder="e.g. Python Developer")
    recordLimit = st.slider("Number of Records to Fetch",50,350,50,50) #min, max, default, increment size
    runPipelineButton = st.button("Run Full Pipeline",type="primary") # primary type sets button type to highlighted
    resetDataButton = st.button ("Reset/Clear Data")

    #Clear data when clear button clicked
    if resetDataButton:
        #define location of files to delete
        processedFile = rootPath / "data" / "processed" / "job_skills_extracted.xlsx"
        rawFile = rootPath / "data" / "raw" / "adzuna_raw.xlsx"
        #if files exist, then unlink/delete them
        if processedFile.exists(): processedFile.unlink()
        if rawFile.exists(): rawFile.unlink()
        #rerun streamlit appliction from scratch
        st.rerun()

#Pipeline button execution
if runPipelineButton:
    if jobTitleInput == "":
        st.error("ERROR: Please enter a job title in the sidebar")
    else:
        #create status box to show progress
        #expanded as collapsed by default
        with st.status(f"Searching for '{jobTitleInput}'...",expanded=True) as status:  #as status allows referencing of the status to update once complete 
            st.write("Step 1: Fetching Live Job Posting Data...")
            adzunaPull(jobTitleInput,recordLimit)
            st.write("Step 2: Matching jobs postings to skill sets")
            assignSkills()
            #update status label
            status.update(label="Search Complete",state="complete")

#Display pipeline results
processedFile = rootPath /"data"/"processed"/"job_skills_extracted.xlsx"

if processedFile.exists():
    try:
        jobData = pd.read_excel(processedFile)
    except:
        #create an empty data frame if nothing found, used for soft errors later, instead of hard crash now
        jobData = pd.DataFrame()

    #check data is loaded with required columns
    if jobData.empty:
        st.warning(f"No results found for '{jobTitleInput}'. Please try a different search term")
    
    elif "adzuna_title" not in jobData.columns or 'esco_matched_title' not in jobData.columns:
        st.warning("The search returned results but they couldn't be matched to any skills. Try a more common job title")
    
    else:
        #create 3 tabs for each section
        tabMap,tabList,tabSkills = st.tabs(["Map","Job List", "Skill Breakdown"])

        #create map tab contents
        with tabMap:
            st.subheader("Geographic Job Data")
            if "latitude" in jobData.columns and "longitude" in jobData.columns:

                #Calculate counts of total unique jobs pulled from Adzuna
                totalPulled = jobData["job_id"].nunique() #nunique just returns a count

                #filter for map (unique jobs with coordinates)
                mapDF = jobData.drop_duplicates(subset=["job_id"]).dropna(subset=["latitude","longitude"]).copy() #copy creates a new df to prevent overwriting
                mapJobCount = len(mapDF)

                if mapDF.empty:
                    st.warning("No Geographic Coordinates found for these jobs")
                else:
                    #ensure salary columns are formatted for display
                    mapDF["salary_min"] = mapDF['salary_min'].apply(formatSalary)
                    mapDF["salary_max"] = mapDF['salary_max'].apply(formatSalary)

                    #Create PyDeck

                    #This for the data points on the map
                    JobPointsLayer = pdk.Layer(
                        "ScatterplotLayer",
                        mapDF,
                        get_position= "[longitude,latitude]",
                        get_color='[255, 75, 75, 160]',  #Red
                        get_radius=4000,
                        pickable=True,
                        auto_highlight=True                    
                    )

                    #Set initial map view
                    viewState = pdk.ViewState(
                        latitude=mapDF["latitude"].mean(),
                        longitude=mapDF['longitude'].mean(),
                        zoom=5
                    )

                    #Assemble all map components into 1 object
                    jobMapObject = pdk.Deck(
                        map_style=None, #default streamlit map theme
                        initial_view_state=viewState,
                        layers=[JobPointsLayer],
                        tooltip={"text": "Title: {adzuna_title}\n"
                        "ESCO Match: {esco_matched_title}\n"
                        "Min Salary: £{salary_min}\n"
                        "Max Salary: £{salary_max}\n"
                        "Contract: {contract_type}\n"
                        }
                    )

                    #Show the map
                    st.pydeck_chart(jobMapObject)

                    #Show an info box under the map
                    st.info(f"Showing {mapJobCount} unique jobs with geolocation data, out of {totalPulled} total job postings pulled")
                    st.info("**TIP**: Hover over the dots on the map to see specific job details")

            else:
                st.warning("No location data found in results.")


        #create job list tab content
        with tabList:
            if 'job_id' in jobData.columns:
                uniqueJobsDF = jobData.drop_duplicates(subset=['job_id'])
                st.dataframe(uniqueJobsDF)

                st.header("Download:")
                st.download_button(
                    label= "Download as CSV",
                    data=uniqueJobsDF.to_csv(index=False),
                    file_name="UniqueJobResults.csv",
                    mime="text/csv", # mime tells what the file type is
                    type="primary"
                )

        #create skill tab contents
        
        with tabSkills:
            uniquePairs = jobData[["adzuna_title","esco_matched_title"]].drop_duplicates()
            for index,row in uniquePairs.iterrows():
                with st.expander(f"{row["adzuna_title"]} -> skills inferred from {row["esco_matched_title"]} ESCO skill set"):
                    #filter job data to rows matching current title
                    matchingRows = jobData[jobData["adzuna_title"] == row["adzuna_title"]]
                    #select just the skill column and unique skills
                    skillColumn = matchingRows["skill"].unique()

                    #display each skill as a bullet point
                    for skill in skillColumn:
                        st.markdown(f"- {skill}")

else:
    st.divider()
    st.info("Welcome! To begin, enter a job role in the sidebar and click **Run Full Pipeline**.")
    st.markdown("""
    ### How to use this tool:
    1. **Enter a Keyword**: Type a job title into the box on the left.
    2. **Set the Limit**: Choose how many job postings you want to analyze.
    3. **Analyze**: The app will fetch live data from Adzuna and cross-reference it with the ESCO Skill database.
    """)