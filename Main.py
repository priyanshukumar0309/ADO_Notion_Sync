import sys
import streamlit as st
import json
import os
from Fetch_Notion_Details import app as notion_app
from Fetch_ADO_Details import app as azure_app
from Sync_and_Actions import app as sync_app
from Homepage import app as home_app
# Sidebar navigation
st.set_page_config(layout="wide")

file_path = 'variable.json'
st.session_state['file_path'] = file_path
# Check if the file exists
if os.path.exists(file_path):
    # Open the file safely using `with` statement
    with open(file_path, 'r') as file:
        global_variable = json.load(file)
else:
    # Default values if the file does not exist
    global_variable = {
        "default_organization": "temp",
        "default_pat": "o5nggeu2u4tkvalw563kzrczjwy5g5ruuibbnva6xgk3jbq3vgra",
        "NOTION_API_KEY": "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"
    }
st.session_state["global_variable"]=global_variable
PAGES = {
    "Home": home_app,
    "Notion Details": notion_app,
    "Azure DevOps": azure_app,
    "Sync & Actions": sync_app
}


st.sidebar.title("Pages")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Render the selected page
page = PAGES[selection]
page()