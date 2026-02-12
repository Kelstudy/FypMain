import streamlit as st
import pandas as pd
import pydeck as pdk
from pathlib import Path
import sys

#Setup Streamlit page config
st.set_page_config(page_title="Job Skill Matcher", layout="wide") 

#Set project root folder
root = Path(__file__).resolve().parents[1]  # FypMain/

#add root folder to pythons search list and set to search there first for imports below
sys.path.insert(0, str(root))

#Import data pipeline functions
from src.data_pipeline.data_pull import main as adzunaPull
from src.data_pipeline.ESCO_combine import buildTechSkillLibrary
from src.data_pipeline.job_skill_assignment import main as assignSkills


