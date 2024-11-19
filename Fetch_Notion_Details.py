import streamlit as st
import requests
import pandas as pd
import json
from Fetch_ADO_Details import fetch_work_items_by_area_paths, DataFrame_from_workitems


# Notion API URL
NOTION_API_URL = "https://api.notion.com/v1/databases"

# Initialize session state for database details and radio button selection
if "selected_db_id" not in st.session_state:
    st.session_state.selected_db_id = None
if "database_details" not in st.session_state:
    st.session_state.database_details = None

def app():
    st.title("Notion Databases")
    st.write("Display details about your Notion databases here.")
    # Add code to fetch and display Notion data
    st.info("Connect your Notion database API and display details.",  icon="ℹ️")
    
    # Default API key (you can set this to your actual API key)
    NOTION_API_KEY = st.session_state["global_variable"]["NOTION_API_KEY"]
    
    # Input for API Key
    notion_api_key = st.text_input("Notion API Key", value=NOTION_API_KEY, type="password")
    if st.button("Save Variable"):
        st.session_state["global_variable"]["NOTION_API_KEY"] = notion_api_key
        with open(st.session_state['file_path'], 'w') as file:
            json.dump(st.session_state["global_variable"], file)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Button to fetch Notion Databases
    if st.button("Fetch Notion Databases"):
        if notion_api_key:
            notion_databases = fetch_all_notion_databases(notion_api_key)
            if notion_databases:
                if isinstance(notion_databases, list):
                    st.session_state.databases = notion_databases  # Store the databases in session state
                    st.success("Notion Databases fetched successfully.")
                else:
                    st.error("No databases found or error fetching them.")
            else:
                st.warning("please Refresh the page and retry")
        else:
            st.error("Please provide a Notion API Key.")
    
    # Only show database selection once the databases have been fetched
    if 'databases' in st.session_state:
        database_names = [f"{db['name']} ({db['id']})" for db in st.session_state.databases]
        selected_db = st.selectbox("**Select a Database**", options=[""] + database_names)

        if st.button('Load Database'):
            st.session_state.selected_db =selected_db
            selected_db_id = selected_db.split("(")[-1].strip(")")
            # Fetch data from Notion API using the selected database ID
            info_message=st.info("Fetching data from Notion...")
            st.session_state["selected_db_id"]=selected_db_id
            st.session_state["Notion DB Name"] = selected_db
            
            database_details = fetch_notion_database_details(notion_api_key, selected_db_id)
            if database_details:
                elements_df=DataFrame_from_notionDatabase(database_details)
                if not elements_df.empty:
                    st.write("**Database Content**:",selected_db)
                    st.dataframe(elements_df)
                    info_message.empty()
                    validate_schema(st.session_state["properties"],selected_db_id,NOTION_API_KEY)
                else:
                    st.error('Database Failed')
            else:
                st.error('Database Failed')
                
        elif "Notion_data" in st.session_state:
            properties = st.session_state["properties"] 
            selected_db_id = st.session_state["selected_db_id"] 
            Notion_data = st.session_state["Notion_data"]
            
            st.write("**Previously Fetched Data**:",st.session_state["Notion DB Name"])
            st.dataframe(Notion_data)
            

        else:
            st.write("Please select a database.")
    st.markdown("""
            <style>
                .stButton > button {
                    float: right;
                }
            </style>
        """, unsafe_allow_html=True)


def DataFrame_from_notionDatabase(database_details):
    elements, properties = store_data(database_details)
    elements_df = pd.DataFrame()
    if elements and properties:
        st.session_state["properties"]=properties
        headers = extract_headers_from_properties(properties)
        elements_df=convert_elements_to_dataframe(elements, headers) 
        st.success('Databases Fetched')
    if not elements_df.empty:
        # Convert elements to a DataFrame and display
        st.session_state["Notion_data"]=elements_df 
        return elements_df
    else:
        return elements_df



# Function to fetch the details of a selected database

def fetch_notion_database_details(apikey,database_id):
    try:
        headers = {
            "Authorization": f"Bearer {apikey}",
            "Notion-Version": "2022-06-28"  # Use the correct version of the Notion API
        }

        # Retrieve database info
        database_url = f"https://api.notion.com/v1/databases/{database_id}"
        database_response = requests.get(database_url, headers=headers)
        database_response.raise_for_status()  # Raise an exception for HTTP errors
        database_info = database_response.json()

        # Query database for elements
        query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        results = []
        has_more = True
        next_cursor = None

        while has_more:
            payload = {"start_cursor": next_cursor} if next_cursor else {}
            query_response = requests.post(query_url, headers=headers, json=payload)
            query_response.raise_for_status()
            query_data = query_response.json()

            results.extend(query_data.get("results", []))
            has_more = query_data.get("has_more", False)
            next_cursor = query_data.get("next_cursor", None)

        return {"database_info": database_info, "elements": results}

    except requests.exceptions.RequestException as e:
        st.error(f"An API error occurred: {e}")
        return None

# Function to extract headers from properties
def extract_headers_from_properties(properties):
    # Define the list of prioritized headers
    prioritized_headers = ['ADO ID', 'Name', 'Type', 'Status', 'Summary']
    
    # Start with an empty list for headers
    headers = []
    
    # First, append the prioritized headers that are actually present in the properties
    for header in prioritized_headers:
        if header in properties:
            headers.append(header)
    
    # Now, add any other properties that aren't part of the prioritized headers
    for property_name in properties.keys():
        if property_name not in prioritized_headers and property_name not in headers:
            headers.append(property_name)
    
    return headers


def store_data(database_details):
    """
    Stores Notion database information and elements into separate Excel sheets.
    
    Args:
        database_details (dict): The database information and elements.
        output_file (str): The path of the output Excel file.
    """
    # Extract headers from database properties
    properties = database_details.get("database_info", {}).get("properties", {})
    headers = extract_headers_from_properties(properties)
    
    # Convert elements to a DataFrame
    elements = database_details.get("elements", [])
    return elements ,properties



# Function to fetch all notion databases
def fetch_all_notion_databases(api_key, query=""):
    url = 'https://api.notion.com/v1/search'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    data = {
        "query": query,
        "filter": {"value": "database", "property": "object"},
        "sort": {"direction": "ascending", "timestamp": "last_edited_time"}
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()

        databases_info = []
        if results.get('results'):
            for result in results['results']:
                title = result['title'][0]['text']['content'] if result.get('title') else "Untitled"
                db_id = result['id']
                databases_info.append({"name": title, "id": db_id})
        return databases_info
    except Exception as e:
        st.error(f"Error fetching Notion databases: {str(e)}")
        return []
def convert_elements_to_dataframe(elements, headers):
    """
    Converts elements data to a DataFrame using specified headers.
    
    Args:
        elements (list): The list of elements from the Notion database.
        headers (list): The list of headers extracted from the database properties.
    
    Returns:
        DataFrame: A pandas DataFrame containing the element data with properties as columns.
    """
    elements_data = []
    
    for element in elements:
        element_data = {}
        properties = element.get("properties", {})
        
        for header in headers:
            # Extract the field value based on the type of the property
            property_info = properties.get(header, {})
            
            # Handle different types of property values
            if property_info.get("type") == "title":
                value = " ".join([t.get("plain_text", "") for t in property_info.get("title", [])])
            elif property_info.get("type") == "rich_text":
                value = " ".join([t.get("plain_text", "") for t in property_info.get("rich_text", [])])
            elif property_info.get("type") == "select":
                select_info = property_info.get("select")
                value = select_info.get("name", "") if select_info else ""
            elif property_info.get("type") == "multi_select":
                multi_select_info = property_info.get("multi_select", [])
                value = ", ".join([m.get("name", "") for m in multi_select_info if m])
            elif property_info.get("type") == "date":
                date_info = property_info.get("date")
                value = date_info.get("start", "") if date_info else ""
            elif property_info.get("type") == "checkbox":
                value = property_info.get("checkbox", "")
            elif property_info.get("type") == "number":
                value = property_info.get("number", "")
            elif property_info.get("type") == "url":
                value = property_info.get("url", "")
            elif property_info.get("type") == "email":
                value = property_info.get("email", "")
            elif property_info.get("type") == "phone_number":
                value = property_info.get("phone_number", "")
            elif property_info.get("type") == "people":
                people_info = property_info.get("people", [])
                value = ", ".join([p.get("name", "") for p in people_info if p])
            elif property_info.get("type") == "files":
                files_info = property_info.get("files", [])
                value = ", ".join([f.get("name", "") for f in files_info if f])
            elif property_info.get("type") == "relation":
                relation_info = property_info.get("relation", [])
                value = ", ".join([r.get("id", "") for r in relation_info if r])
            elif property_info.get("type") == "status":
                status_info = property_info.get("status")
                value = status_info.get("name", "") if status_info else ""
            elif property_info.get("type") == "last_edited_time":
                value = property_info.get("last_edited_time", "")
            elif property_info.get("type") == "unique_id":
                unique_id_info = property_info.get("unique_id", {})
                value = f"{unique_id_info.get('prefix', '')}{unique_id_info.get('number', '')}"

            # Add to the element data
            element_data[header] = value
        
        element_data['id'] = element.get("id")  # Add element ID
        elements_data.append(element_data)
    
    # Create DataFrame from elements data
    return pd.DataFrame(elements_data)

def validate_schema(properties,DATABASE_ID,NOTION_API_KEY):
    REQUIRED_PROPERTIES = {
    "Date": "date",
    "Last Edited Date on ADO": "date",
    "ADO ID": "text",  # Assuming ADO ID is a text field
    "Type": "multi_select",  # Assuming Type is a dropdown
    "ADO Status": "text",
    "Estimates":"select",  # Assuming ADO Status is a dropdown
    "Last edited time": "last_edited_time"  # Validation only
    }
    # Identify missing properties
    missing_properties = [
        prop for prop in REQUIRED_PROPERTIES if prop != "Last edited time" and prop not in properties
    ]

    # Display status of required properties
    if missing_properties:
        st.warning("The following properties are missing from the database:")
        for prop in missing_properties:
            st.write(f"- {prop}")
        
        # Button to add missing properties
        if st.button("Add Missing Properties"):
            success = True
            for prop in missing_properties:
                property_type = REQUIRED_PROPERTIES[prop]
                if not add_property_to_database(prop, property_type,DATABASE_ID,NOTION_API_KEY):
                    success = False

            if success:
                st.success("All missing properties have been added successfully, please Reload Database!")
            else:
                st.error("Some properties could not be added. Please check the logs.")
    else:
        st.success("All required properties are already present in the database.")
    # Validate presence of "last_edited_time"
    if "Last edited time" not in properties:
        st.warning(
            "'Last Edited Time' is a read-only property automatically provided by Notion. Ensure it is available in the database entries."
        )



# Add a missing property to the Notion database
def add_property_to_database(property_name, property_type,DATABASE_ID,NOTION_API_KEY):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    property_config = {
        "text": {"rich_text": {}},
        "date": {"date": {}},
        "select": {"select": {}},
        "multi_select": {"multi_select": {}},  # Added multi_select handling
        "Last edited time": {
            "last_edited_time": {}
    }
    }
    if property_type not in property_config:
        st.error(f"Unsupported property type: {property_type}")
        return False

    data = {
        "properties": {
            property_name: property_config[property_type]
        }
    }
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        return True
    else:
        st.error(f"Failed to add property '{property_name}': {response.status_code}, {response.json().get('message')}")
        return False








