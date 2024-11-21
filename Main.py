import sys
import streamlit as st
import json
import os
from Fetch_Notion_Details import app as notion_app
from Fetch_ADO_Details import app as azure_app
from Sync_and_Actions import app as sync_app
from Homepage import app as home_app
from Documentation import app as documentation_app
# Sidebar navigation

def add_floating_button():
    # URL for the issue reporting link
    issue_report_url = "https://your-issue-reporting-link.com"  # Replace with your actual link
    
    # HTML and CSS for the floating button with "Report Issue" icon
    floating_button_html = f"""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet">
    <style>
    /* Floating button styles */
    .floating-button {{
        position: fixed;
        bottom: 20px;   /* Fixed distance from the bottom */
        right: 20px;    /* Fixed distance from the right */
        width: 60px;
        height: 60px;
        background-color: #f39c12;
        color: white;
        border: none;
        border-radius: 50%;
        text-align: center;
        font-size: 24px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        z-index: 9999; /* Ensures the button stays on top of other content */
    }}
    
    .floating-button i {{
        font-size: 30px;
    }}
    
    /* Toast message styles */
    .toast {{
        visibility: hidden;
        position: fixed;
        bottom: 100px;
        right: 20px;
        background-color: rgba(0, 0, 0, 0.75);
        color: white;
        text-align: center;
        border-radius: 4px;
        padding: 10px 20px;
        font-size: 16px;
        z-index: 9999;
        opacity: 0;
        transition: opacity 0.5s, visibility 0s linear 0.5s;
    }}
    
    .toast.show {{
        visibility: visible;
        opacity: 1;
        transition: opacity 0.5s;
    }}
    </style>
    
    <div class="floating-button-container">
        <a href="https://forms.office.com/e/MPv6DPVqqX" target="_blank">
            <button class="floating-button" onclick="showToast()"> 
                <i class="fas fa-exclamation-circle"></i>  <!-- Report Issue Icon -->
            </button>
        </a>
        <div id="toast" class="toast">Report an Issue</div>  <!-- Toast message -->
    </div>
    
    <script>
    function showToast() {{
        var toast = document.getElementById('toast');
        toast.className = 'toast show';  // Show the toast
        setTimeout(function() {{
            toast.className = toast.className.replace('show', '');  // Hide the toast after 2 seconds
        }}, 2000);
    }}
    </script>
    """
    
    # Embedding the floating button HTML into Streamlit
    st.components.v1.html(floating_button_html, height=100)

st.set_page_config(
    layout="wide",
    page_title="Notion ADO Sync",  # Tab name
    page_icon="🌟"             # Emoji as an icon or use a file path for a custom image
                  
)

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
    "Documentation": documentation_app,
    "Notion Details": notion_app,
    "Azure DevOps": azure_app,
    "Sync & Actions": sync_app
}


st.sidebar.title("Pages")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Render the selected page
page = PAGES[selection]
page()
add_floating_button()

