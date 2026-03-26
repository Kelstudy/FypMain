import os
import requests
import pandas as pd
from pathlib import Path
import streamlit as st


def loadApiCredentials():   #Setup API key and ID

    try:
        apiId = st.secrets["ADZUNA_APP_ID"]
        apiKey = st.secrets["ADZUNA_API_KEY"]
    except:
        
        from dotenv import load_dotenv
        envPath = Path(__file__).parents[2]/"api.env"
        #load api.env file 
        load_dotenv(envPath)
        load_dotenv("api.env")
        apiId = os.getenv("ADZUNA_APP_ID")
        apiKey = os.getenv("ADZUNA_APP_KEY")

    # API ID and key Error check
    print(f"apiId: {apiId}")
    print(f"apiKey: {apiKey}")
    if not apiId or not apiKey:
        raise ValueError(f"Missing Adzuna API information , check {envPath}")
    
    return apiId,apiKey



def callApiForKeywords(searchKeyword,targetCount,adzunaID,adzunaKey):
    # Call Adzuna API to get job listings for one keyword

    apiBaseUrl = "https://api.adzuna.com/v1/api/jobs/gb/search/{page}"
    resultsPerPage = 50

    # Argument Parameters
    apiRequestParams = {
        "app_id": adzunaID,
        "app_key": adzunaKey,
        "results_per_page": resultsPerPage,
        "what": searchKeyword  # The search term
    }

    allJobListings = []  #stores all results 
    currentPageNumber = 1

    # Keep fetching pages until we have result count requested

    while len(allJobListings) < targetCount:
        
        #Build URL for current page
        currentPageURL = apiBaseUrl.format(page=currentPageNumber)
        print(f"{searchKeyword} - Getting page {currentPageNumber}")
        
        #Make API request
        apiResponse = requests.get(currentPageURL,params=apiRequestParams,timeout=30)

       #List error code responses for user 
        errorMessages = {
                400: "Bad Request - Check your search parameters",
                401: "Unauthorized - Your API credentials are invalid",
                403: "Forbidden - You don't have permission",
                404: "Not Found - The endpoint doesn't exist",
                429: "Too Many Requests - You've hit the rate limit",
                500: "Internal Server Error - Adzuna's server is having issues",
                503: "Service Unavailable - Adzuna API is temporarily down"
            }
        
         # If response fails 
        if apiResponse.status_code != 200:
            print(f"ERROR: Request failed with status {apiResponse.status_code}")
            print(f"URL: {apiResponse.url}")
            print("See below for list of error codes:")
            for code, message in errorMessages.items():
                    print(f"  {code}: {message}")
            raise SystemExit("API request failed")
        
        #Parse JSON response
        responseData = apiResponse.json()
        #look for "results" in response json and return , otherwise return an empty list
        jobsOnCurrentPage = responseData.get("results",[])

        #If no more results then stop
        if jobsOnCurrentPage == []:
             print(f"No more results available for {searchKeyword}")
             break
        
        #Filter jobs so dont get unrelated jobs due to adzunas fuzzy search
        filtered_jobs = []
        for job in jobsOnCurrentPage:
            # Check if the keyword actually exists in the title
            if searchKeyword.lower() in job.get('title', '').lower():
                filtered_jobs.append(job)

        # Add found jobs to list
        allJobListings.extend(filtered_jobs)

        currentPageNumber +=1

    # Convert list of jobs to dataframe
    jobsDataFrame = pd.json_normalize(allJobListings)

    #Add tracking columns to know where data came from for future reference
    jobsDataFrame["search_keyword"] = searchKeyword
    jobsDataFrame["date_pulled"] = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    return jobsDataFrame


def cleanDataFrame(rawDataFrame):
    
     # Remove unnecessary columns

     columnsToRemove = [
        "adref",
        "__CLASS__",
        "location.__CLASS__",
        "category.__CLASS__",
        "company.__CLASS__"
    ]

     cleanedData = rawDataFrame.drop(columns=columnsToRemove, errors="ignore")
     return cleanedData

#Check collected data for missing values, salary anomolies and data types
def DataQualityChecks(dataFrame):
    
    #empty array to add quality check warnings to later
    qualityWarnings = []

    totalJobs = len(dataFrame)

    #Missing value checks
    missingValueColumns = ["title", "salary_min", "salary_max", "latitude", "longitude", "contract_type"]
    for column in missingValueColumns:
        if column in dataFrame.columns:
            missingCount = dataFrame[column].isna().sum()
            if missingCount > 0:
                qualityWarnings.append(f"Missing Values : '{column}' is missing in {missingCount} out of {totalJobs} job postings")

    #Salary anomaly checks
    if "salary_min" in dataFrame.columns and "salary_max" in dataFrame.columns:
        #convert to numeric and used coerce to set any errors to NaN as pandas skips NaN when comparing numbers
        salaryMin = pd.to_numeric(dataFrame["salary_min"],errors="coerce")
        salaryMax = pd.to_numeric(dataFrame["salary_max"],errors="coerce")

        #check how many string values before and after converting to numeric, to determine how many salary values were strings that couldnt be converted to numbers
        nonNumericMin = dataFrame["salary_min"].notna().sum() - salaryMin.notna().sum()
        nonNumericMax = dataFrame["salary_max"].notna().sum() - salaryMax.notna().sum()
        if nonNumericMin > 0:
            qualityWarnings.append(f"Data type issue: {nonNumericMin} non-numeric values found in 'salary_min'")
        if nonNumericMax > 0:
            qualityWarnings.append(f"Data type issue: {nonNumericMax} non-numeric values found in 'salary_max'")

        #check if any min salaries are greater than max salaries
        invalidSalaryRange = (salaryMin > salaryMax).sum()
        if invalidSalaryRange > 0:
             qualityWarnings.append(f"Salary anomaly: {invalidSalaryRange} postings have salary_min greater than salary_max")

    #Summary of quality issues
    if len(qualityWarnings) == 0:
        print(" Data quality checks passed with no issues")
    else:
        print(f"Data quality checks found {len(qualityWarnings)} issues:")
        for warning in qualityWarnings:
            print(f"- {warning}")

    return qualityWarnings



def main(streamlitKeywords=None, streamlitCount=None):
     
     #Get API credentials
     adzunaApplicationID , adzunaApplicationKey = loadApiCredentials()
   
    #Determine if keywords provided via streamlit app or running manually
     if streamlitKeywords:
          userKeyWords = streamlitKeywords
     else:
          userKeyWords = input("Enter keywords for job titles (separated by commas): ").strip()

    # split keywords by commas and add to a list
     rawKeywords = userKeyWords.split(",")
     searchKeywordList = []

     for keyword in rawKeywords:
          cleanedKeyword = keyword.strip()
          if cleanedKeyword != "":
               searchKeywordList.append(cleanedKeyword)
     
     if len(searchKeywordList) == 0:
          raise ValueError("You must enter at least one keyword")
     
     if streamlitCount:
          targetCountList = [int(streamlitCount) for keyword in searchKeywordList]
     else:
        # ask for how many results per keyword
        userCountInput = input("Results per keyword (Min: 50). Enter one number OR comma to seperate multiple numbers: ").strip()
            
        #If multiple target records then split each one 
        if "," in userCountInput:
            rawCounts = userCountInput.split(",")
            targetCountList = []
            for count in rawCounts:
                cleanedCount = count.strip()
                if cleanedCount != "" :
                    targetCountList.append(cleanedCount)
        
            if len(targetCountList) != len(searchKeywordList):
                    raise ValueError("Number of counts must match the number of entered keywords")
            
            #convert list of strings in strCountList into ints
            intCountList = []
            for str in targetCountList:
                convertInt = int(str)
                intCountList.append(convertInt)

            #update original list with the ints
            targetCountList = intCountList

        #If no commas , and only 1 number entered for counts then create a list of just that number
        else:
            singleNumber = int(userCountInput)
            targetCountList = []
            for keyword in searchKeywordList:
                targetCountList.append(singleNumber)


     #Get jobs for each keyword
    
     allDataList = []
     numberOfKeywords = len(searchKeywordList)

     # Get keyword and count that are at the same position
     for position in range(numberOfKeywords):
        currentKeyword = searchKeywordList[position]
        currentCount = targetCountList[position]
        #Get api results as table for current keyword and count
        keywordResultsTable = callApiForKeywords(currentKeyword,currentCount,adzunaApplicationID,adzunaApplicationKey)

        #Add to master table on line 166
        allDataList.append(keywordResultsTable)

     #Combine all dataframes into one
     combinedDataFrame = pd.concat(allDataList,ignore_index=True)

     #Clean the data frame using the function defined earlier
     combinedDataFrame = cleanDataFrame(combinedDataFrame)

     #Remove duplicate jobs based on job ID column
     if "id" in combinedDataFrame.columns:
          originalJobCount = len(combinedDataFrame)
          combinedDataFrame = combinedDataFrame.drop_duplicates(subset=["id"],keep="first")
          finalJobCount = len(combinedDataFrame)
          print(f"Removed {originalJobCount-finalJobCount} duplicates")

    
     #run data quality checks
     qualityWarnings = DataQualityChecks(combinedDataFrame)


     #Save to Excel
     
     outputFilePath = Path(__file__).parents[2]/"data/raw/adzuna_raw.xlsx"
     # create parent folders if they don't exist
     outputFilePath.parent.mkdir(parents=True, exist_ok=True)

     with pd.ExcelWriter(outputFilePath, engine="openpyxl") as excelWriter:
        combinedDataFrame.to_excel(excelWriter, sheet_name="Jobs_Raw", index=False)

     return qualityWarnings

# Only run if called , not when this script imported into another file
if __name__ == "__main__":
    main()
 