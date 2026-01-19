import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parents[2]
FILE_IN = BASE_DIR / "data" / "manual" / "300TechJobsFinal.xlsx"
FILE_OUT = BASE_DIR / "data" / "processed" /"job_skills_extracted.xlsx"

# Skill extraction dictionaries 

#core skills
coreSkillsExtract = {
    "sql": ["sql", "mysql", "postgresql", "sqlite", "tsql"],
    "query optimisation": ["indexes", "joins", "subqueries", "query performance"],
    "excel": ["excel", "advanced excel", "pivot tables", "vlookup", "xlookup", "power query", "formulas"],
    "python": ["python", "pandas", "numpy"],
    "scripting": ["python scripting", "automation scripts", "powershell", "bash"],
    "r": ["r", "r studio", "tidyverse"],
    "data cleaning": ["data cleaning", "data cleansing", "data wrangling", "data preprocessing","data manipulation", "data transformation", "data structuring","etl", "extract", "transform", "load"],
    "data analysis": ["data analysis", "exploratory data analysis", "eda"],
    "data visualisation": ["data visualization", "data visualisation", "power bi", "tableau", "dashboards"],
    "statistics": ["statistics", "descriptive statistics", "probability", "hypothesis testing"],
    "reporting": ["reporting", "kpi reporting", "operational reporting"],
    "databases": ["relational databases", "database querying", "data storage"],
    "basic nosql": ["nosql", "mongodb"],
    "data formatting": ["csv", "excel files", "json", "xml", "markdown"],
    "apis": ["api", "rest api", "json", "api integration"],
    "version control": ["git", "github", "version control"],
    "linux basics": ["linux", "bash basics", "command line", "bash"],
    "operating systems": ["windows", "windows server", "linux", "macos"],
    "networking basics": ["networking", "tcp ip", "dns", "dhcp", "patching"],
    "hardware support": ["hardware support", "pc repair", "device setup", "peripherals", "technical support", "desktop support"],
    "it support": ["it support", "technical support", "desktop support", "365"],
    "helpdesk": ["helpdesk", "service desk", "ticketing systems"],
    "virtualisation": ["virtualisation", "virtual machines", "vmware", "hyper-v"],
    "cloud basics": ["cloud computing", "aws basics", "azure basics"],
    "data security basics": ["data security", "access control", "permissions"],
    "backup & recovery": ["backups", "data recovery", "system recovery"],
    "automation": ["automation", "scripting", "task automation"],
    "testing": ["testing", "data validation testing"],
    "monitoring basics": ["system monitoring", "log files"],
    "etl basics": ["etl", "data extraction", "data loading"],
    "certifications (core)": [
        "itil foundation", "comptia a+", "comptia network+",
        "microsoft azure fundamentals", "aws cloud practitioner",
        "google it support professional"
    ]
}

#senior skills
seniorSkillsExtract =  {
    "senior sql": ["advanced sql", "execution plans", "window functions", "stored procedures", "performance tuning"],
    "senior sql optimisation": ["index tuning", "query refactoring", "database performance analysis", "cost-based optimisation"],
    "senior excel": ["power pivot", "data modelling in excel", "complex formulas", "vba", "excel automation"],
    "senior python": ["object oriented programming", "modular code design", "performance optimisation", "exception handling", "python testing"],
    "senior python scripting": ["workflow automation", "scheduled scripts", "data pipeline scripting", "production scripts"],
    "senior r": ["advanced statistical modelling", "custom r functions", "package development", "performance tuning in r"],
    "senior data cleaning": ["data quality frameworks", "data validation rules", "anomaly detection", "data consistency checks"],
    "senior data analysis": ["advanced exploratory analysis", "trend analysis", "root cause analysis", "predictive analysis"],
    "senior data visualisation": ["semantic data models", "dashboard optimisation", "performance tuning dashboards", "enterprise reporting"],
    "senior statistics": ["regression modelling", "multivariate analysis", "time series analysis", "statistical inference"],
    "senior reporting": ["automated reporting", "enterprise reporting frameworks", "self-service reporting platforms"],
    "senior databases": ["database design", "normalisation", "schema optimisation", "database administration"],
    "senior nosql": ["nosql data modelling", "distributed databases", "replication", "partitioning"],
    "senior data formats": ["schema design", "data serialization", "parquet", "avro"],
    "senior apis": ["api design", "api authentication", "rate limiting", "api versioning"],
    "senior version control": ["branching strategies", "pull request workflows", "code reviews", "release management"],
    "senior linux": ["shell scripting", "process management", "cron jobs", "system performance tuning"],
    "senior operating systems": ["windows server administration", "linux server administration", "os hardening"],
    "senior networking": ["network troubleshooting", "vpn configuration", "firewall rules", "network monitoring"],
    "senior hardware support": ["hardware diagnostics", "device lifecycle management", "asset management"],
    "senior it support": ["endpoint management", "mdm", "group policy", "enterprise support"],
    "senior helpdesk": ["incident escalation", "problem management", "service desk optimisation"],
    "senior virtualisation": ["virtual infrastructure design", "resource allocation", "high availability", "vm performance tuning"],
    "senior cloud": ["cloud architecture", "cost optimisation", "iam", "cloud security"],
    "senior data security": ["data governance", "access auditing", "encryption at rest", "encryption in transit"],
    "senior backup & recovery": ["disaster recovery planning", "business continuity", "backup strategy design"],
    "senior automation": ["workflow orchestration", "process automation frameworks", "automation pipelines"],
    "senior testing": ["automated testing", "data integrity testing", "test frameworks"],
    "senior monitoring": ["centralised logging", "alerting systems", "performance monitoring"],
    "senior etl": ["etl pipeline design", "data orchestration", "incremental loading", "error handling pipelines"],
    "senior certifications": [
        "itil managing professional", "comptia security+", "comptia linux+",
        "aws solutions architect", "azure data engineer associate",
        "google professional data engineer"
    ]
}

#Default skills for predifined job titles

defaultSkills = {
    ("data_analyst", "junior"): ["excel", "sql"],
    ("data_engineer", "junior"): ["sql", "python", "etl basics"],
    ("data_scientist", "junior"): ["python", "statistics"],
    ("it_support", "junior"): ["it support", "operating systems"],
    ("sys_admin", "junior"): ["operating systems", "it support"],
    ("business_analyst", "junior"): ["excel", "reporting", "documentation"],


    ("it_support", "standard"): ["it support", "operating systems", "certifications (core)"],
    ("sys_admin", "standard"): ["operating systems", "networking basics", "linux basics"],
    ("data_analyst", "standard"): ["excel", "sql", "data visualisation"],
    ("data_engineer", "standard"): ["sql", "python", "etl basics", "cloud basics"],
    ("data_scientist", "standard"): ["python", "statistics", "data analysis"],
    ("business_analyst", "standard"): ["excel", "reporting", "requirements gathering", "documentation", "stakeholder communication"],

    ("data_analyst", "senior"): ["sql", "data visualisation", "databases"],
    ("data_engineer", "senior"): ["senior etl", "cloud basics", "version control"],
    ("data_scientist", "senior"): ["senior statistics", "senior data analysis"],
    ("it_support", "senior"): ["data security basics", "networking basics", "scripting"],
    ("sys_admin", "senior"): ["senior cloud", "senior networking", "senior data security"],
    ("business_analyst", "senior"): ["sql", "data analysis", "reporting", "data visualisation", "stakeholder management", "requirements gathering", "process modelling", "kpi definition", "documentation", "business process improvement"],

}

# Scan job title + job description to find any matching skills from skill extraction dictionaries
def scanForSkills(text, skillDict):
    foundSkills = {}
    text = text.lower()

    for item in skillDict.items():
        skillName = item[0]
        keywordList = item[1]

        for keyword in keywordList:
            pattern = rf"\b{re.escape(keyword.lower())}\b"  # match whole word only and escape regex special chars
            if re.search(pattern, text):    # check if this keyword appears in the text
                foundSkills[skillName] = keyword # store the skill name and keyword that matched
                break

    return foundSkills



def main():
    if not Path(FILE_IN).exists():
        print(f"Error - {FILE_IN} not found")
        return

    dataFrame = pd.read_excel(FILE_IN)
    results = []

   
    seniorTerms = ["senior", "lead", "principal", "manager", "head"]
    juniorTerms = ["junior", "trainee", "graduate", "placement", "intern", "entry level"]

    # join the term lists and split with "|"" so can use re.search later
    # r keeps backslashes safe, f inserts variables instead of string
    seniorPattern = rf"\b({'|'.join(seniorTerms)})\b"
    juniorPattern = rf"\b({'|'.join(juniorTerms)})\b"

    #Extract text from each cell
    for index, row in dataFrame.iterrows():
        title = str(row["title"]).lower()
        description = str(row["description"]).lower()
        fullText = title + " " + description
        role = str(row["role_group"]).lower().strip()
        jobId = row["id"]

        foundSkills = {}

        # if senior terms in seniority colum or job title
        if re.search(seniorPattern, title):
            tier = "senior"
            sourceLabel = "senior_default"
        elif re.search(juniorPattern, title):
            tier = "junior"
            sourceLabel = "junior_default"
        else:
            tier = "standard"
            sourceLabel = "standard_default"

        #Apply Defaults
        if (role, tier) in defaultSkills:
            for skill in defaultSkills[(role, tier)]:
                foundSkills[skill] = (sourceLabel, "N/A (Default)")
        
        #Scan for Core Skills
        coreHits = scanForSkills(fullText, coreSkillsExtract)
        for skill, keyWord in coreHits.items():
            foundSkills[skill] = ("Extracted from posting", keyWord)

        #Scan for Senior Skills if applicable
        if tier == "senior":
            seniorHits = scanForSkills(fullText, seniorSkillsExtract)
            for skill, keyWord in seniorHits.items():
                foundSkills[skill] = ("Extracted from posting", keyWord)

        #Append to results 
        for skill, (source, keyWord) in foundSkills.items():
            results.append({
                "id": jobId,
                "title": row["title"],
                "role": role,
                "level": tier,
                "skill": skill,
                "source": source,
                "matched_keyword": keyWord
            })

   

    output_df = pd.DataFrame(results)
    Path(FILE_OUT).parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(FILE_OUT, engine="openpyxl") as writer:
        output_df.to_excel(writer, sheet_name="Processed Skills", index=False)
        dataFrame.to_excel(writer, sheet_name="Original Data", index=False)

    print(f"Success! Saved {len(output_df)} skill rows to {FILE_OUT}")

if __name__ == "__main__":
    main()