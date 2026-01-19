import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path


def loadApiCredentials():   #Setup API key and ID
    envPath = Path(__file__).parents[2]/"api.env"
    #load api.env file 
    load_dotenv(envPath)


    apiId = os.getenv("ADZUNA_APP_ID")
    apiKey = os.getenv("ADZUNA_APP_KEY")

    # API ID and key Error check
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
        
        # Add found jobs to list
        allJobListings.extend(jobsOnCurrentPage)

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

def main():
     
     #Get API credentials
     adzunaApplicationID , adzunaApplicationKey = loadApiCredentials()

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

    
     #Save to Excel
     outputFilePath = Path("data/raw/adzuna_raw.xlsx")
     with pd.ExcelWriter(outputFilePath, engine="openpyxl") as excelWriter:
        combinedDataFrame.to_excel(excelWriter, sheet_name="Jobs_Raw", index=False)


main()
