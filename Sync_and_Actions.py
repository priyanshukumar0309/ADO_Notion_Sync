import streamlit as st
import requests
import time
from requests.auth import HTTPBasicAuth
import streamlit as st
import pandas as pd
import json
import pandas as pd
import logging
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pandas as pd
from datetime import datetime  # Import datetime module
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
import re
import functools
from Fetch_ADO_Details import fetch_work_items_by_area_paths, DataFrame_from_workitems
from Fetch_Notion_Details import  fetch_notion_database_details, DataFrame_from_notionDatabase

import time


def app():

    st.title("Azure and Notion Databases")
    with st.expander("## Sync Flow"):
        st.image('images/ADO_Notion_Sync.png',width=1800)
    with st.expander('### Steps'):
        st.write("""
            -  This page shows comparison of Data from ADO and Notion.
            -  Depending upon, if item is missing or out of sync from other board you can take actions.
            -  You can push items from ADO to Notion.
            -  You can push items from Notion to ADO.
            -  You can sync between existing items.
            -  You can update descriptions at both places without ***overwriting.*** """)
    # Add code to fetch and display Notion data
    st.markdown(""" <h4>Color Coding</h4>
        <ul>
            <li><span style="background-color: red; color: white;">Red</span> means missing items in other board</li>
            <li><span style="background-color: yellow; color: black;">Yellow</span> means items present on both boards but out of sync</li>
            <li><span style="background-color: green; color: white;">Green</span> means items present on both boards and in sync</li>
            <li><Strong>'Sync'</Strong> column provides the same status</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    

    # Check if data exists in session state
    if "Notion_data" not in st.session_state:
         st.warning("No Data from Notion, please go to Fetch Notion Page")
    if "ADO_data" not in st.session_state:
        st.warning("No Data from ADO, please go to Azure DevOps Page")
    if st.button('Reload Data'):
       refresh_data()
    def highlight_rows_notion(row):
        # Convert both 'ADO ID' and 'ID' to string to avoid type mismatch
        notion_id = str(row['ADO ID'])
        ado_ids = ADO_data['ID'].astype(str)  # Convert all ADO IDs to string for comparison
        
        # Default color is red (not present in Notion_data)
        color = 'background-color: #f9d3d3'  # Red
        
        if notion_id in ado_ids.values:
            # Get the matching Notion row
            ado_row = ADO_data[ADO_data['ID'] == notion_id]

            # Compare dates if present in both datasets
            if not ado_row.empty:
                ado_date = ado_row.iloc[0]['Change Date']
                notion_date = row['Last Edited Date on ADO']
                
                # Ensure both dates are comparable (convert to datetime)
                # Parse both dates, trimming to seconds
                notion_date = pd.to_datetime(notion_date).floor('min')  # Trim to seconds
                ado_date = pd.to_datetime(ado_date).floor('min')  # Trim to seconds
                
                if notion_date == ado_date:
                    color = 'background-color: #d3f9d8'  # Green (match)
                else:
                    color = 'background-color: #f9f3d3'  # Yellow (date mismatch)
        return [color] * len(row)
    

    def highlight_rows_ado(row):
        # Convert both 'ID' and 'ADO ID' to string to avoid type mismatch
        ado_id = str(row['ID'])
        notion_ids = Notion_data['ADO ID'].astype(str)  # Convert all Notion IDs to string for comparison

        # Default color is red (not present in Notion_data)
        color = 'background-color: #f9d3d3'  # Red

        if ado_id in notion_ids.values:
            # Get the matching Notion row
            notion_row = Notion_data[Notion_data['ADO ID'] == ado_id]

            # Compare dates if present in both datasets
            if not notion_row.empty:
                notion_date = notion_row.iloc[0]['Last Edited Date on ADO']
                ado_date = row['Change Date']
                
                # Ensure both dates are comparable (convert to datetime)
                # Parse both dates, trimming to seconds
                notion_date = pd.to_datetime(notion_date).floor('min')  # Trim to seconds
                ado_date = pd.to_datetime(ado_date).floor('min')  # Trim to seconds
                
                if notion_date == ado_date:
                    color = 'background-color: #d3f9d8'  # Green (match)
                else:
                    color = 'background-color: #f9f3d3'  # Yellow (date mismatch)
        return [color] * len(row)

    if "Notion_data" in st.session_state and "ADO_data" in st.session_state:
        # Retrieve the data
        Notion_data = st.session_state["Notion_data"]
        ADO_data = st.session_state["ADO_data"]
        Notion_data = pd.DataFrame(Notion_data)
        ADO_data = pd.DataFrame(ADO_data)
        Notion_data.insert(2, 'Sync', 'Missing')
        ADO_data.insert(2, 'Sync', 'Missing')
        Notion_data['Last Edited Date on ADO'] = pd.to_datetime(Notion_data['Last Edited Date on ADO'],format='ISO8601').dt.floor('min')
        ADO_data['Change Date'] = pd.to_datetime(ADO_data['Change Date'],format='ISO8601').dt.floor('min')
        Notion_data['ADO ID'] = Notion_data['ADO ID'].astype(str)
        ADO_data['ID'] = ADO_data['ID'].astype(str)
        

        # Iterate through Notion_data rows
        for index, row in Notion_data.iterrows():
            ado_id = row['ADO ID']
            if ado_id in ADO_data['ID'].values:  # Check if ADO ID matches
                ado_row = ADO_data[ADO_data['ID'] == ado_id].iloc[0]
                if row['Last Edited Date on ADO'] == ado_row['Change Date']:  # Check if dates match
                    Notion_data.at[index, 'Sync'] = 'Up to Date'
                else:
                    Notion_data.at[index, 'Sync'] = 'Needs update'



        for index, row in ADO_data.iterrows():
            ado_id = row['ID']
            if ado_id in Notion_data['ADO ID'].values:  # Check if ID matches ADO ID
                notion_row = Notion_data[Notion_data['ADO ID'] == ado_id].iloc[0]
                if row['Change Date'] == notion_row['Last Edited Date on ADO']:
                    # Check if dates match
                    ADO_data.at[index, 'Sync'] = 'Up to Date'
                else:
                    ADO_data.at[index, 'Sync'] = 'Needs update'
        # Ensure the data is in DataFrame format (convert if necessary)
        
        
       
        # Apply the styling to the DataFrames
        styled_notion = Notion_data.style.apply(highlight_rows_notion, axis=1)
        styled_ado = ADO_data.style.apply(highlight_rows_ado, axis=1)


            
        # Display the dataframes in Streamlit
        st.write("##### Notion Data")
        st.dataframe(styled_notion, use_container_width=True)
       
        
        st.write("##### ADO Data")
        st.dataframe(styled_ado, use_container_width=True)       
        st.markdown("<hr>", unsafe_allow_html=True)
#ADO Data====================================================================================================================================
        st.write("### Azure Devops -> Notion")
        st.write("#### Create Pages on Notion")
        if ADO_data.loc[ADO_data['Sync'] == 'Missing', 'ID'].tolist():
            
            
            ADO_filtered_df_to_add_unique_types = ADO_data['Work Item Type'].unique().tolist()
    
            # Step 4: Create a checkbox section for filtering by 'type'
            ADO_filtered_df_to_add_unique_types_elected_work_item_types = st.multiselect(
                "Select Work Item Types to Include:",
                options=ADO_filtered_df_to_add_unique_types,
                key="ADO_filtered_df_to_add_unique_types_elected_work_item_types"
            )
            ADO_filtered_df_to_add = ADO_data[ADO_data['Work Item Type'].isin(ADO_filtered_df_to_add_unique_types_elected_work_item_types)]

            # Create a multiselect widget to select ADO Items that are not present in Notion (Sync == 0)
            selected_not_sync_values = st.multiselect(
                "ADO Items ****Missing**** in Notion",
                options=ADO_filtered_df_to_add.loc[ADO_filtered_df_to_add['Sync'] == 'Missing', 'ID'].tolist(),
                default=ADO_filtered_df_to_add.loc[ADO_filtered_df_to_add['Sync'] == 'Missing', 'ID'].tolist()   # Default to the same list
            )

            # Filter the DataFrame based on the selected sync values for non-synced items (Sync == 0)
            ADO_filtered_df_to_add = ADO_filtered_df_to_add[ADO_filtered_df_to_add['ID'].isin(selected_not_sync_values)]

            if not ADO_filtered_df_to_add.empty:
                st.dataframe(ADO_filtered_df_to_add)
                if st.button("Create Notion Pages"):
                    total_items = len(ADO_filtered_df_to_add)
                    progress_message = st.empty()  # Placeholder for progress updates
                    index = 1
                    with st.spinner(f'Creating {len(ADO_filtered_df_to_add)} Notion pages') :   
                        for _, row in ADO_filtered_df_to_add.iterrows():
                            # Fetch work item details from Azure DevOps
                            progress_message.info(f"Creating {index}/{total_items}...")
                            index +=1
                            work_item_details = fetch_ado_work_item(
                                row['ID'], 
                                st.session_state["global_variable"]["default_organization"],
                                st.session_state["selected_project"],
                                st.session_state["global_variable"]["default_pat"]
                            )
                            
                            if work_item_details:
                                # Create a page in Notion
                                status, message = create_notion_page(
                                    database_id=st.session_state.get('selected_db').split("(")[-1].strip(")"),
                                    work_item_details=work_item_details,
                                    notion_api_key=st.session_state["global_variable"]["NOTION_API_KEY"]
                                )
                                if status:
                                    st.success(message)
                                    
                                else:
                                    st.error(message)
                        #refresh_data()
                        st.info('Please reload Azure Devops to see updates...')
                        time.sleep(3)
                        st.rerun() 
        else:
            st.success('All items of ADO are already in Notion')

            # Create a multiselect widget to select ADO Items that are in Notion but not updated (Sync == 1)
        st.write("#### Update Pages on Notion")
    
        if ADO_data.loc[ADO_data['Sync'] == 'Needs update', 'ID'].tolist():
            
            ADO_filtered_df_to_sync_unique_types = ADO_data['Work Item Type'].unique().tolist()
    
            # Step 4: Create a checkbox section for filtering by 'type'
            ADO_filtered_df_to_sync_unique_types_elected_work_item_types = st.multiselect(
                "Select Work Item Types to Include:",
                options=ADO_filtered_df_to_sync_unique_types,
                key="ADO_filtered_df_to_sync_unique_types_elected_work_item_types"
            )
            ADO_filtered_df_to_sync = ADO_data[ADO_data['Work Item Type'].isin(ADO_filtered_df_to_sync_unique_types_elected_work_item_types)]

            selected_to_sync_values = st.multiselect(
                "ADO Items ****Not Updated**** in Notion",
                options=ADO_filtered_df_to_sync.loc[ADO_filtered_df_to_sync['Sync'] == 'Needs update', 'ID'].tolist(),
                default=ADO_filtered_df_to_sync.loc[ADO_filtered_df_to_sync['Sync'] == 'Needs update', 'ID'].tolist()  # Default to the same list
            )

            # Filter the DataFrame based on the selected sync values for items that are in Notion but not updated (Sync == 1)
            ADO_filtered_df_to_sync = ADO_filtered_df_to_sync[ADO_filtered_df_to_sync['ID'].isin(selected_to_sync_values)]


            if not ADO_filtered_df_to_sync.empty:
                st.dataframe(ADO_filtered_df_to_sync)
                if st.button("Update Notion Pages"):
                    total_items = len(ADO_filtered_df_to_sync)
                    progress_message = st.empty()  # Placeholder for progress updates
                    index = 1
                    for _, row in ADO_filtered_df_to_sync.iterrows():
                        progress_message.info(f"Updating {index}/{total_items}...")
                        index +=1
                        status, message = Sync_ADO_Notion(next(iter([row['ID']])))
                        if status:
                            st.success(message)
                            
                        else:
                            st.error(message)
                    #refresh_data()
                    st.info('Please reload Azure Devops to see updates...')
                    time.sleep(3)
                    st.rerun()


        else:
            st.warning('''
            - No more items available to sync.
            - Please check if items are present in both Notion and ADO 
            - If not please use above options to push it to respective systems''')
        st.markdown("<hr>", unsafe_allow_html=True)
#=Notion Data===================================================================================================================================

        st.write("### Notion -> Azure Devops")
        filtered_notion_data = Notion_data[
            (Notion_data['Sync'] == 'Missing') & 
            Notion_data['Name'].notnull() & 
            Notion_data['Name'].str.strip().ne('') & 
            Notion_data['Type'].notnull() & 
            Notion_data['Type'].str.strip().ne('')
            ]
        # Create a multiselect widget to select ADO Items that are not present in Notion (Sync == 0)
        if filtered_notion_data.loc[filtered_notion_data['Sync'] == 'Missing', 'Name'].tolist():
            
            Notion_data_filtered_df_unique_types = filtered_notion_data['Type'].unique().tolist()
    
            # Step 4: Create a checkbox section for filtering by 'type'
            Notion_data_filtered_df_selected_work_item_types = st.multiselect(
                "Select Work Item Types to Include:",
                options=Notion_data_filtered_df_unique_types,
                key="Notion_data_filtered_df_selected_work_item_types"
            )

            # Step 5: Further filter the DataFrame based on selected work item types
            Notion_data_filtered_df = filtered_notion_data[filtered_notion_data['Type'].isin(Notion_data_filtered_df_selected_work_item_types)]

            selected_not_in_ADO_values = st.multiselect(
                "Notion Pages ****Missing**** in Azure Devops",
                options=Notion_data_filtered_df.loc[Notion_data_filtered_df['Sync'] == 'Missing', 'Name'].tolist(),
                default=Notion_data_filtered_df.loc[Notion_data_filtered_df['Sync'] == 'Missing', 'Name'].tolist(),
                key="not_in_ado_multiselect"    # Default to the same list
            )
            # Filter the DataFrame based on the selected sync values for non-synced items (Sync == 0)
            Notion_data_filtered_df = Notion_data_filtered_df[Notion_data_filtered_df['Name'].isin(selected_not_in_ADO_values)]

            if not Notion_data_filtered_df.empty:
                st.dataframe(Notion_data_filtered_df)
                if st.session_state["selected_area_paths"]:
                    selected_area_path = st.selectbox("Select a Area Path to Creat ADO work Items",options=[""] +  st.session_state["selected_area_paths"])
                    if selected_area_path:
                        selected_area_path = selected_area_path.replace("\\", "\\\\")
                        if st.button("Create ADO Work Item"):
                            total_items = len(Notion_data_filtered_df)
                            progress_message = st.empty()  # Placeholder for progress updates
                            index = 1
                            for _, row in Notion_data_filtered_df.iterrows():
                                # Fetch work item details from Azure DevOps
                                progress_message.info(f"Creating {index}/{total_items}...")
                                index +=1
                                Notion_page_details = fetch_notion_page(
                                    row['id'], 
                                    st.session_state["global_variable"]["NOTION_API_KEY"]
                                )
                                
                                if Notion_page_details:
                                    # Create a page in Notion
                                    status, message = Create_ADO_items(
                                        Notion_page_details,selected_area_path,
                                        st.session_state["global_variable"]["default_organization"],
                                        st.session_state["selected_project"],
                                        st.session_state["global_variable"]["default_pat"]
                                        
                                    )
                                    if status:
                                        st.success(message)
                                        
                                        
                                        
                                    else:
                                        st.error(message)
                            #refresh_data()
                            st.info('Please reload Azure Devops to see updates...')
                            time.sleep(3)
                            st.rerun()
        else:
            st.warning('Name and Type must be present to create ADO item. No more items to create ')
        st.markdown("<hr>", unsafe_allow_html=True)
## Just descriptions:=======================================================================      
        st.write("### Sync Descriptions 🔄")
        if ADO_data.loc[ADO_data['Sync'] != 'Missing', 'ID'].tolist():
            
            # Create a multiselect widget to select ADO Items that are not present in Notion (Sync == 0)
            
            ADO_Notion_sync_data_unique_types = ADO_data['Work Item Type'].unique().tolist()
    
            # Step 4: Create a checkbox section for filtering by 'type'
            ADO_Notion_sync_data_selected_work_item_types = st.multiselect(
                "Select Work Item Types to Include:",
                options=ADO_Notion_sync_data_unique_types,
                key="ADO_Notion_sync_data_selected_work_item_types"
            )
            ADO_Notion_sync_data_filtered_df = ADO_data[ADO_data['Work Item Type'].isin(ADO_Notion_sync_data_selected_work_item_types)]
            
            ADO_Notion_sync_data_sync_values = st.multiselect(
                "These are all items which are present and can be synced for descriptions",
                options=ADO_Notion_sync_data_filtered_df.loc[ADO_Notion_sync_data_filtered_df['Sync'] != 'Missing', 'ID'].tolist(),
                default=ADO_Notion_sync_data_filtered_df.loc[ADO_Notion_sync_data_filtered_df['Sync'] != 'Missing', 'ID'].tolist(),
                key="notion_ado_sync_multiselect"  
                   # Default to the same list
            )

            # Filter the DataFrame based on the selected sync values for non-synced items (Sync == 0)
            ADO_Notion_sync_data_filtered_df = ADO_Notion_sync_data_filtered_df[ADO_Notion_sync_data_filtered_df['ID'].isin(ADO_Notion_sync_data_sync_values)]

            if not ADO_Notion_sync_data_filtered_df.empty:
                st.dataframe(ADO_Notion_sync_data_filtered_df)
                if st.button("Sync Notion ADO Descriptions"):
                    total_items = len(ADO_Notion_sync_data_filtered_df)
                    progress_message = st.empty()  # Placeholder for progress updates
                    index = 1

                    for _, row in ADO_Notion_sync_data_filtered_df.iterrows():
                        progress_message.info(f"Updating {index}/{total_items}...")
                        index  +=1
                        status, message = update_work_item_description(next(iter([row['ID']])))
                        if status:
                            st.success(f'{message}')
                        else:
                            st.error(message)
        else:
            st.success('All items of ADO are already in Notion')

    

def refresh_data():
    database_details = fetch_notion_database_details(st.session_state["global_variable"]["NOTION_API_KEY"], st.session_state["selected_db_id"])
    if database_details:
        elements_df=DataFrame_from_notionDatabase(database_details)
        st.info('Please reload Notion Details to see updates')
    work_items = fetch_work_items_by_area_paths(st.session_state["global_variable"]["default_organization"], st.session_state["selected_project"],st.session_state["selected_work_item_types"],st.session_state["selected_area_paths"], st.session_state["global_variable"]["default_pat"])
    if 'error' in work_items:
        st.error(work_items['error'])
    else:
        # Prepare data for table
        table_data = DataFrame_from_workitems(work_items)
        st.session_state["ADO_data"] = table_data
        st.session_state["Notion_data"]=elements_df 


# Functions for Notion
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

def fetch_notion_database_elements(api_key, database_id):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        results = response.json().get("results", [])
        elements = []
        for result in results:
            properties = result.get("properties", {})
            ado_id = properties.get("ADO ID", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            elements.append({"id": result["id"], "ADO ID": ado_id})
        return elements
    except Exception as e:
        st.error(f"Error fetching database elements: {str(e)}")
        return []


# Fetch Azure DevOps work item details
def fetch_ado_work_item(work_item_id, ado_organization, ado_project, ado_pat):
    """
    Fetches details of a work item from Azure DevOps.
    """
    url = f"https://dev.azure.com/{ado_organization}/{ado_project}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    response = requests.get(url, auth=HTTPBasicAuth('', ado_pat))
    if response.status_code == 200:
        return response.json()
        
    else:
        print(f"Failed to fetch work item: {response.status_code} - {response.text}")
        return None

# Create Notion pages
def create_notion_page(database_id, work_item_details, notion_api_key):
    """
    Creates a new Notion page in the specified database using work item details.
    """

    url = f"https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Notion-Version": "2021-05-13",
        "Content-Type": "application/json"
    }

    # Validate fields with default values
    title = work_item_details['fields'].get('System.Title', 'Untitled Work Item')
    ado_id = str(work_item_details['id'])
    state = work_item_details['fields'].get('System.State', 'Unknown State')
    work_item_type = work_item_details['fields'].get('System.WorkItemType', 'Unknown Type')
    target_date = work_item_details['fields'].get('Microsoft.VSTS.Scheduling.TargetDate', None)
    start_date =work_item_details['fields'].get('Microsoft.VSTS.Scheduling.StartDate', None)
    Last_edit_date_on_Ado =work_item_details['fields'].get('System.ChangedDate', None)
    

    # Prepare data for the Notion page
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "ADO ID": {"rich_text": [{"text": {"content": ado_id}}]},
            "ADO Status": {"rich_text": [{"text": {"content": state}}]},
            "Type": {"multi_select": [{"name": work_item_type}]}, 
            "Last Edited Date on ADO" :{
                "date": {
                    "start": Last_edit_date_on_Ado,
                    "time_zone": None  # Adjust if you have a specific time zone
                }
             }
        } 
    }
    if start_date is not None:
            data["properties"]["Date"] = {
                "date": {
                    "start": start_date,
                    "end": target_date,
                    "time_zone": None  # Adjust if you have a specific time zone
                }
            }
    # Remove None values from the data dictionary
    data['properties'] = {k: v for k, v in data['properties'].items() if v is not None}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return (1,f"Created Notion page for work item {ado_id}.")
    else:
        return (0,f"Failed to create Notion page for: {work_item_id} Reasons: {response.status_code} - {response.text}")


# Sync ADO and Notion Items


def fetch_notion_page(page_id, NOTION_API_KEY):
    """
    Fetches a Notion page's properties.

    :param page_id: ID of the Notion page.
    :param NOTION_API_KEY: Notion API integration key.
    :return: Notion page properties or None if not found.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2021-05-13"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch Notion page: {response.status_code} - {response.text}")
        return None


def update_ado_work_item(work_item_id, title, target_date, start_date, estimate, notion_page_id, ado_last_edited_date, PERSONAL_ACCESS_TOKEN):
    """
    Updates an Azure DevOps work item with new content.

    :param work_item_id: ID of the Azure DevOps work item.
    :param title: Title to set in Azure DevOps.
    :param status: Status to set in Azure DevOps.
    :param work_item_type: Work item type to set in Azure DevOps.
    :param target_date: Target date to set in Azure DevOps.
    :param start_date: Start date to set in Azure DevOps.
    :param estimate: Estimate to set in Azure DevOps.
    :param ado_last_edited_date: Last edited date to set in Azure DevOps.
    :param personal_access_token: ADO personal access token.
    """
    patch_url = f"https://dev.azure.com/{ st.session_state["global_variable"]["default_organization"]}/{st.session_state["selected_project"]}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    headers = {
        "Authorization": f"Basic {PERSONAL_ACCESS_TOKEN}",
        "Content-Type": "application/json-patch+json"
    }
    
    # Construct the data to be updated
    data = [
        {"op": "replace", "path": "/fields/System.Title", "value": title},
        {"op": "replace", "path": "/fields/Custom.EffortForSAFe", "value": estimate}

       
    ]
    if target_date:
        data.append( {"op": "replace", "path": "/fields/Microsoft.VSTS.Scheduling.TargetDate", "value": target_date})
    if start_date:
        data.append(  {"op": "replace", "path": "/fields/Microsoft.VSTS.Scheduling.StartDate", "value": start_date})
    response = requests.patch(
        patch_url,
        headers=headers,
        auth=HTTPBasicAuth('', PERSONAL_ACCESS_TOKEN),
        json=data
    )
    if response.status_code == 200:
        print(f"Updated ADO work item {work_item_id} successfully.")
    else:
        print(f"Failed to update ADO work item:{work_item_id} Reasons:{response.status_code} - {response.text}")
    try:
        ado_last_edited_date = response.json()['fields']['System.ChangedDate']
    except KeyError:
        ado_last_edited_date = ''
    url = f"https://api.notion.com/v1/pages/{notion_page_id}"
    headers2 = {
        "Authorization": f"Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}",
        "Notion-Version": "2021-05-13",
        "Content-Type": "application/json"
    }

    # Update properties based on work item details
    data = {
        "properties": {
            "Last Edited Date on ADO": {
                "date": {
                    "start": ado_last_edited_date,
                    "end": None,  # If there is no end date, set it to None
                    "time_zone": None  # Adjust if you have a specific time zone
                }
            }
        }    
    }

   
   
    
   
    response = requests.patch(url, headers=headers2, data=json.dumps(data))
    if response.status_code == 200:
        print(f"Updated Notion page {notion_page_id} successfully.")
    else:
        print(f"Failed to update Notion page for: {title} Reasons: {response.status_code} - {response.text}")

def update_notion_page(page_id, title, status, work_item_type, target_date, start_date,Estimate,ado_last_edited_date, NOTION_API_KEY):
    """
    Updates a Notion page with new content.

    :param page_id: ID of the Notion page.
    :param title: Title to set in Notion.
    :param status: Status to set in Notion.
    :param work_item_type: Work item type to set in Notion.
    :param target_date: Target date to set in Notion.
    :param start_date: Start date to set in Notion.
    :param NOTION_API_KEY: Notion API integration key.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2021-05-13",
        "Content-Type": "application/json"
    }

    # Update properties based on work item details
    data = {
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "ADO Status": {
                "rich_text": [{"text": {"content": status}}]
            },
            "Estimates": {
                "select": {"name": str(Estimate) if Estimate is not None else "0"}
            }
        }
    }

    # Add Date property if start_date is provided
    if start_date is not None:
        data["properties"]["Date"] = {
            "date": {
                "start": start_date,
                "end": target_date,
                "time_zone": None  # Adjust if you have a specific time zone
            }
        }

    # Add 'Last Edited Date on ADO' if provided
    if ado_last_edited_date is not None:  # Assuming last_edited_date is a variable holding the date
        data["properties"]["Last Edited Date on ADO"] = {
            "date": {
                "start": ado_last_edited_date,
                "end": None,  # If there is no end date, set it to None
                "time_zone": None  # Adjust if you have a specific time zone
            }
        }
    
   
    response = requests.patch(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print(f"Updated Notion page {page_id} successfully.")
    else:
        print(f"Failed to update Notion page for: {title} Reasons: {response.status_code} - {response.text}")

def Sync_ADO_Notion(work_item_id):
    # Fetch Azure DevOps work item
    notion_page_id = fetch_page_id_by_ado_id(work_item_id)
    if not notion_page_id:
        return (0,"Notion sync Failed")
    ado_work_item = fetch_ado_work_item(
        work_item_id, 
        st.session_state["global_variable"]["default_organization"],
        st.session_state["selected_project"],
        st.session_state["global_variable"]["default_pat"]) 
    if ado_work_item is None:
        return(0,"No Ado work item ")

    # Extract relevant data from ADO work item with error handling
    try:
        title = ado_work_item['fields']['System.Title']
    except KeyError:
        title = 'Empty Title'  # or some default value
    
    try:
        status = ado_work_item['fields']['System.State']
    except KeyError:
        status = 'Unknown State'
    
    try:
        work_item_type = ado_work_item['fields']['System.WorkItemType']
    except KeyError:
        work_item_type = 'Feature'
    
    try:
        ado_last_edited_date = ado_work_item['fields']['System.ChangedDate']
    except KeyError:
        ado_last_edited_date = '9999-01-01'
    
    try:
        Estimate = ado_work_item['fields']['Custom.EffortForSAFe']
    except KeyError:
        Estimate =1
    
    # Using get method with a default value for optional fields
    
    target_date = ado_work_item['fields'].get('Microsoft.VSTS.Scheduling.TargetDate', None)
    start_date = ado_work_item['fields'].get('Microsoft.VSTS.Scheduling.StartDate', None)
   
    
    # Fetch Notion page
    notion_page = fetch_notion_page(notion_page_id,  st.session_state["global_variable"]["NOTION_API_KEY"])
    if notion_page is None:
        return(0,"No Notion page")
    
    # Extract Notion properties with error handling
    try:
        notion_title = notion_page['properties']['Name']['title'][0]['text']['content']
    except (KeyError, IndexError):
        notion_title = ' '  # or some default value
    
    try:
        notion_status = notion_page['properties']['ADO Status']['rich_text'][0]['text']['content']
    except (KeyError, IndexError):
        notion_status = ' '
    
    try:
        notion_work_item_type = notion_page['properties']['Type']['multi_select'][0]['name']
    except (KeyError, IndexError):
        notion_work_item_type = ' '
    
    try:
        notion_estimate = notion_page['properties']['Estimates']['select']['name']
    except KeyError:
        notion_estimate = ' '
    
    try:
        notion_start_date = notion_page['properties']['Date']['date']['start']
    except KeyError:
        notion_start_date = None
    
    try:
        notion_target_date = notion_page['properties']['Date']['date']['end']
    except KeyError:
        notion_target_date = notion_start_date
        
        
    notion_last_edited_date = notion_page['properties']['Last edited time']['last_edited_time']
    # Convert string dates to datetime objects for comparison
    ado_last_edited_dt = datetime.fromisoformat(ado_last_edited_date[:-1])  # Remove 'Z' for conversion
    notion_last_edited_dt = datetime.fromisoformat(notion_last_edited_date[:-1])  # Remove 'Z' for conversion
    
    # Compare last edited dates and update Notion page if ADO is later
    if ado_last_edited_date > notion_last_edited_date:
        print("ADO is up-to-date. Updating Notion page")
        update_notion_page(notion_page_id, title, status, work_item_type, target_date, start_date,Estimate,ado_last_edited_date, st.session_state["global_variable"]["NOTION_API_KEY"])
    else:
        print("Notion is up-to-date. Updating ADO page")
        update_ado_work_item(work_item_id, notion_title, notion_target_date, notion_start_date, notion_estimate,notion_page_id, ado_last_edited_date, st.session_state["global_variable"]["default_pat"])
    
    #update descriptions in either case
    
    return (1,f"Work item update function Done for {work_item_id} - {title} ")

def Create_ADO_items(notion_page,selected_area_path,organization,project,pat):
    # Extract Notion properties with error handling
    """
    Create a work item in Azure DevOps.

    :param organization: The name of your Azure DevOps organization.
    :param project: The name of the Azure DevOps project.
    :param work_item_type: The type of work item to create (e.g., Bug, Task, Feature).
    :param pat: Personal Access Token for Azure DevOps authentication.
    :param title: Title of the work item.
    :param description: Description of the work item (optional).
    :param area_path: The area path to assign to the work item (optional).
    :param start_date: The start date for the work item (optional).
    :param target_date: The target date for the work item (optional).
    :param estimates: Estimates for the work item (optional).
    :param state: State of the work item (optional).
    :param fields: Additional fields to set on the work item as a dictionary (optional).
    :return: Response from Azure DevOps API.
    """
    

    try:
        notion_title = notion_page['properties']['Name']['title'][0]['text']['content']
    except (KeyError, IndexError):
        notion_title = ' '  # or some default value
        return (0,'Title is necessary to create ADO item')
    
    try:
        notion_status = notion_page['properties']['ADO Status']['rich_text'][0]['text']['content']
    except (KeyError, IndexError):
        notion_status = None
    
    # Define allowed Azure DevOps work item types
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitemtypes?api-version=7.1"

    response = requests.get(
        url,
        auth=HTTPBasicAuth('', st.session_state["global_variable"]["default_pat"])
    )

    if response.status_code == 200:
        work_item_types = response.json().get('value', [])
        allowed_work_item_types = [item['name'] for item in work_item_types]
    else:
        raise Exception(f"Failed to fetch work item types. Status Code: {response.status_code}, Response: {response.text}")

    try:
        notion_work_item_type = notion_page['properties']['Type']['multi_select'][0]['name']
    except (KeyError, IndexError):
        notion_work_item_type = None

    if notion_work_item_type not in allowed_work_item_types:
        return (0, f"Invalid work item type '{notion_work_item_type}'. Must be one of {', '.join(allowed_work_item_types)}.")    
    
    try:
        notion_estimate = notion_page['properties']['Estimates']['select']['name']
    except KeyError:
        notion_estimate = None
    
    try:
        notion_start_date = notion_page['properties']['Date']['date']['start']
    except KeyError:
        notion_start_date = None
    
    try:
        notion_target_date = notion_page['properties']['Date']['date']['end']
    except KeyError:
        notion_target_date = None

    

    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": str(notion_title)
        }
    ]
    
    if selected_area_path:
        payload.append({
            "op": "add",
            "path": "/fields/System.AreaPath",
            "value": selected_area_path
        })
    if notion_start_date:
        payload.append({
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Scheduling.StartDate",
            "value": notion_start_date
        })
    if notion_target_date:
        payload.append({
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Scheduling.TargetDate",
            "value": notion_target_date
        })
    if notion_estimate:
        payload.append({
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Scheduling.Effort",
            "value": notion_estimate
        })
   
    
    
    
    
    
    headers = {"Content-Type": "application/json-patch+json"}
    url = f"https://dev.azure.com/{organization}/Digital%20Finance/_apis/wit/workitems/${notion_work_item_type}?api-version=7.1"
    response = requests.post(
        url,
        auth=HTTPBasicAuth('', st.session_state["global_variable"]["default_pat"]),
        json=payload,
        headers=headers
    )
    #response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in (200, 201):
        work_item_id = response.json().get('id')
        if update_notion_page_ado_id(notion_page['id'],work_item_id):
            return (1, f"Work item created :{work_item_id} - {notion_title} ")
        else:
            (0,f'Failed to update ADO ID on Notion for {work_item_id} - {notion_title} ')
    else:
        return (0, f"Failed at create ADO item for {notion_title}")
    #==============================================================================================================================

    


def update_notion_page_ado_id(page_id, ado_id):
    """
    Update the 'ADO ID' property of a Notion page.

    :param page_id: The ID of the Notion page.
    :param ado_id: The Azure DevOps Work Item ID.
    :param notion_api_key: The API key for Notion.
    :return: Tuple (status, message).
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "properties": {
            "ADO ID": {
                "rich_text": [{"text": {"content": str(ado_id)}}]
            }
        }
    }

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code == 200:
        return (1, "Notion page updated successfully with ADO ID.")
    else:
        return (0, f"Failed to update Notion page for: {ado_id} Reasons: {response.text}") 

def update_work_item_description(work_item_id):
    message = st.info(f'Updating notion page for {work_item_id}...')
    #first we update notion page from ADO content
    update=update_notion_description_from_ado(work_item_id)
    message.empty()
    if not update:
        print( f'update_notion_description_from_ado Failed: {work_item_id}')
        return (0,'Notion Page Update Failed')
    #second we update ADO from Notion content
    message = st.success(f'Updated Notion Page for {work_item_id}')
    
    page_id = fetch_page_id_by_ado_id(work_item_id)
    if not page_id:
        return (0,f'Notion Page Fetch Failed for: {work_item_id} ')
    # Step 1: Fetch the content from the Notion page
    blocks = fetch_notion_page_content(page_id)
    time.sleep(0.5)  # Simulate work

    message.empty()
    message = st.info(f'Updating ADO Page for {work_item_id}...')
        # Step 2: Convert blocks to HTML

    html_content = convert_notion_blocks_to_html(blocks)
    # Step 3: Remove the 'ADO Description' from Notion Page section if it exists
    new_notion_description = remove_ado_description_section(html_content)
    existing_description = fetch_work_item_description(work_item_id)
    # Regex to match the <h2> Notion Description section and all content until the next <h2> or end of description
    notion_section_regex = r"(?is)(<h2>\s*Notion Description\s*<\/h2>.*?)(?=<h2>|$)"
    # Remove the old Notion Description section if it exists
    updated_description = re.sub(notion_section_regex, "", existing_description, flags=re.DOTALL).strip()


        # Append the new Notion Description section
    updated_description += f"<h2>Notion Description</h2><p>{new_notion_description}</p>"

    # Prepare the JSON patch data to update the description
    patch_data = [
        {
            "op": "add" if not existing_description else "replace",
            "path": "/fields/System.Description",
            "value": updated_description
        }
    ]
    headers = {
    'Content-Type': 'application/json-patch+json'
    }


    # Send the PATCH request to update the work item
    patch_url = f"https://dev.azure.com/{st.session_state["global_variable"]["default_organization"]}/{st.session_state["selected_project"]}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    response = requests.patch(
        patch_url,
        headers=headers,
        auth=HTTPBasicAuth('', st.session_state["global_variable"]["default_pat"]),
        json=patch_data
    )
    if response.status_code == 200:
        message.empty()
        message = st.success(f'Updated ADO Page for {work_item_id}')
        time.sleep(2)
        message.empty()
        return (1,f'ADO and Notion Synced for {work_item_id}')
    else:
        return (0,f' Notion Update Failed for: {work_item_id} ')
        
    
    
    

def update_notion_description_from_ado(ado_id):
    # Fetch the Notion page details
    # Set API Key and Notion API base URL
    notion_page_id=fetch_page_id_by_ado_id(ado_id)
    notion_api_key = st.session_state["global_variable"]["NOTION_API_KEY"]
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Notion-Version": "2022-06-28",  # Use the correct version of the Notion API
        "Content-Type": "application/json"
    }

    # Fetch the Notion page details
    notion_page_url = f"https://api.notion.com/v1/pages/{notion_page_id}"
    notion_page_response = requests.get(notion_page_url, headers=headers)
    if notion_page_response:
        notion_page = notion_page_response.json()
    else:
        print (f'notion_page_response failed for: {ado_id} Reasons:')
        return 0

    
    
    # Extract ADO ID from the Notion page
    #ado_id = extract_ado_id_from_notion(notion_page)
    #if not ado_id:
    #    print(f"No valid ADO ID found for page {notion_page_id}. Skipping update.")
    #    return
    
    # Fetch details from Azure DevOps
    work_item_details = fetch_detailed_work_items(
        st.session_state["global_variable"]["default_organization"],
        st.session_state["selected_project"],
        [ado_id])
    if work_item_details :
        if "System.Description" in work_item_details[0]:
            # Update Notion page with fetched description
            existing_description = work_item_details[0]["System.Description"]
            notion_section_regex = r"(?is)(<h2>\s*Notion Description\s*<\/h2>.*?)(?=<h2>|$)"
            # Remove the old Notion Description section if it exists
            updated_description = re.sub(notion_section_regex, "", existing_description, flags=re.DOTALL).strip()
            if update_notion_page_description(notion_page_id, updated_description):
                child_items = fetch_child_items(st.session_state["global_variable"]["default_organization"], st.session_state["selected_project"],ado_id, st.session_state["global_variable"]["default_pat"])
                if child_items :
                    if push_dataframe_to_notion(notion_page_id,pd.DataFrame(child_items)):
                        print (f'All Pushed for: {ado_id} ')
                        return 1
                    else: 
                        print (f'Child Items table push failed for: {ado_id} ')
                        return 0
                else:
                    print (f'Child Items fetch failed for: {ado_id} ')
                    return 1
            else:
                print (f'update_notion_page_description failed for: {ado_id} ')
                return 0

        else:
            print (f'no System.Description for: {ado_id}  ')
            return 1
    else:
        print (f'failed work_item_details for: {ado_id} ' )
        return 0
           

def fetch_page_id_by_ado_id( ado_id):
    """
    Fetch the page ID from a Notion database where the ADO ID matches the given ado_id.
    :param database_id: The Notion database ID.
    :param ado_id: The ADO ID to match.
    :return: The page ID if found, otherwise None.
    """
    db_id=next(iter({st.session_state["selected_db_id"]}))
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    headers = {
    'Authorization': f'Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'  # Update to the latest Notion API version
    }
    
    query_payload = {
        "filter": {
            "property": "ADO ID",  # Replace with the exact name of the ADO ID column in Notion
            "rich_text": {
                "equals": str(ado_id)
            }
        }
    }

    response = requests.post(url, headers=headers, json=query_payload)
    results = response.json().get('results')
    
    if results:
        # Return the first matching page's ID
        return results[0]['id']
    else:
        print(f"No page found with the given ADO ID. for: {ado_id} Reasons:")
        return None

def fetch_detailed_work_items(organization, project, work_item_ids):
# To fetch detailed information for all work items
    ids_string = ','.join(map(str, work_item_ids))
    api_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems?ids={ids_string}&api-version=7.1"
    response = requests.get(api_url, auth=HTTPBasicAuth('', st.session_state["global_variable"]["default_pat"]))
    if response.status_code == 200:
        detailed_data = response.json()
        work_items = []
        for work_item in detailed_data.get("value", []):
            # Create a dictionary to hold all field information
            item_info = {
                "ID": work_item['id'],
                "WorkItemType": work_item['fields'].get('System.WorkItemType', 'N/A'),
                "Title": work_item['fields'].get('System.Title', 'N/A'),
                "State": work_item['fields'].get('System.State', 'N/A'),
                "AssignedTo": work_item['fields'].get('System.AssignedTo', {}).get('displayName', 'Unassigned'),
                "CreatedDate": work_item['fields'].get('System.CreatedDate', 'N/A'),
                "ChangedDate": work_item['fields'].get('System.ChangedDate', 'N/A'),
            }
            # Adding all other fields dynamically
            for key, value in work_item['fields'].items():
                if key not in item_info:  # Avoid overwriting existing fields
                    item_info[key] = value
            
            work_items.append(item_info)
        return work_items
    else:
        print(f"Error fetching detailed info: {response.status_code} - {response.text}")
        return []

def update_notion_page_description(page_id, ado_description):
    """Update or create an ADO Description section in the Notion page."""
    blocks = get_page_blocks(page_id)
    header_exists = False
    updated_blocks = []
    content_block= html_to_notion_blocks(ado_description)
    
    for block in blocks['results']:
        block_type = block['type']
        block_content = ""
        # Extract text from the block
        if block_type == 'heading_2' and block['heading_2']['rich_text']:
            block_content = block['heading_2']['rich_text'][0]['text']['content']
            if block_content == "ADO Description":
                header_exists = True
                if update_block_childern(block['id'],content_block):
                #delete_block(block['id'])
                    return 1  # Skip appending the original block
                else :
                    print ('update_block_childern failed')
                    return 0

        # Keep other existing blocks as they are
        #updated_blocks.append(block)
    if header_exists == False:
        header_block =[{
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "ADO Description",
                        },
                    },
                ],'is_toggleable': True,
            },
        }]
        if append_blocks(page_id, header_block, content_block):
            return 1
        else:
            print ('append_blocks failed')
            return 0  
    
   
   

    print(f"Successfully updated Notion page {page_id} with new description.")


#=============================================================================================================================================
#update notion blocks


def delete_block(block_id):
    """Delete a block from Notion using its block ID."""
    url = f'https://api.notion.com/v1/blocks/{block_id}'
    headers = {
        'Authorization': f'Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    response = requests.delete(url, headers=headers)
    # Raise an error for bad responses
    if response.status_code == 204 or response.status_code == 200:
        return 1
    else:
        return 0  # Raise an error for other responses

def update_block_childern(block_id,content_block):
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'
    headers = {
        'Authorization': f'Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    response = requests.get(url, headers=headers)
    res=response.json()  # Raise an error for bad responses
    if res:
        for block in res['results']:
            delete_block(block['id'])
    else:
        print ('update_block_childern get call failed')
        return o
    payload = {"children": content_block}
    response = requests.patch(url, headers=headers, json=payload)
    if response:
        return 1
    else:
        print (f'update_block_childern post call failed{payload} ')
        return 0

def get_page_blocks(page_id):
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    headers = {
        'Authorization': f'Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    response = requests.get(url, headers=headers)
    if response:
        return response.json()
    else:
        None

def append_blocks(page_id, header_block, content_block):
    headers = {
        'Authorization': f'Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    """Append new blocks to the Notion page."""
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    payload = {"children": header_block}  # Wrap blocks in the correct JSON structure
    response = requests.patch(url, headers=headers, json=payload)
    res=response.json()
    if response.json() : 
        for block in res['results']:
            if not update_block_childern(block['id'], content_block):
                return 0
        return 1
            
    else:
        return 0    
            

from bs4 import BeautifulSoup

from bs4 import BeautifulSoup

from bs4 import BeautifulSoup

def html_to_notion_blocks(html):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    blocks = []

    # Helper function to clean up text by removing extra line breaks and whitespace
    def clean_text(text):
        return ' '.join(text.split())

    # Function to convert a text element to a rich text block
    def text_to_rich_text(element):
        cleaned_content = clean_text(element.get_text(strip=True))
        # Only return if there is content
        return {
            "type": "text",
            "text": {
                "content": cleaned_content
            }
        } if cleaned_content else None

    # Function to process each element and convert it to a Notion block
    def process_element(element):
        block = None  # Default to None if no valid block is created
        
        if element.name == 'h1':
            rich_text = text_to_rich_text(element)
            if rich_text:
                block = {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [rich_text],
                        "is_toggleable": False,
                    }
                }

        elif element.name == 'h2':
            rich_text = text_to_rich_text(element)
            if rich_text:
                block = {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [rich_text],
                        "is_toggleable": False,
                    }
                }

        elif element.name == 'h3':
            rich_text = text_to_rich_text(element)
            if rich_text:
                block = {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [rich_text],
                        "is_toggleable": False,
                    }
                }

        elif element.name in ['p', 'div']:
            # Check if paragraph/div contains strong or bold text and adjust accordingly
            rich_texts = []
            for child in element.contents:
                content = clean_text(child.get_text(strip=True))
                if content:  # Only add if content is non-empty
                    if child.name in ['strong', 'b']:
                        rich_texts.append({
                            "type": "text",
                            "text": {
                                "content": content
                            },
                            "annotations": {
                                "bold": True
                            }
                        })
                    elif child.name == 'a':
                        rich_texts.append({
                            "type": "text",
                            "text": {
                                "content": content,
                                "link": {"url": child['href']}
                            }
                        })
                    else:
                        rich_texts.append({
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        })
            
            if rich_texts:  # Only create block if there's content
                block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": rich_texts
                    }
                }

        elif element.name == 'ul':
            list_blocks = []
            for li in element.find_all('li'):
                rich_text = text_to_rich_text(li)
                if rich_text:
                    list_blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [rich_text]
                        }
                    })
            return list_blocks if list_blocks else None

        return block

    # Iterate over all elements and keep the order intact
    for element in soup.find_all(recursive=False):
        processed_block = process_element(element)
        if processed_block:
            if isinstance(processed_block, list):  # Handle list blocks
                blocks.extend(processed_block)
            else:
                blocks.append(processed_block)

    print(f"html_to_notion_blocks function Doned {blocks}")
    return blocks

    #=============================================================================================================================================
#Update ADO Page with Notion Content

def fetch_notion_page_content(page_id):
    notion_headers = {
    'Authorization': f'Bearer {st.session_state["global_variable"]["NOTION_API_KEY"]}',
    'Notion-Version': '2022-06-28'
    }
    """Fetch content from a Notion page."""
    url = f'https://api.notion.com/v1/blocks/{page_id}/children?page_size=100'
    response = requests.get(url, headers=notion_headers)
    response.raise_for_status()
    return response.json()['results']


def convert_notion_blocks_to_html(blocks):
    """Convert Notion blocks to a simple HTML format."""
    html_content = ""
    for block in blocks:
        block_type = block['type']
        if block_type == 'paragraph':
            text = ''.join([item['text']['content'] for item in block['paragraph']['rich_text']])
            html_content += f"<p>{text}</p>\n"
        
        elif block_type == 'heading_2':
            text = ''.join([item['text']['content'] for item in block['heading_2']['rich_text']])
            html_content += f"<h2>{text}</h2>\n"
        
        elif block_type == 'heading_3':
            text = ''.join([item['text']['content'] for item in block['heading_3']['rich_text']])
            html_content += f"<h3>{text}</h3>\n"
        
        elif block_type == 'bulleted_list_item':
            text = ''.join([item['text']['content'] for item in block['bulleted_list_item']['rich_text']])
            html_content += f"<li>{text}</li>\n"
            
            # Check if the block has children and process them
            if block.get('has_children', False):
                children_blocks = fetch_notion_page_content(block['id'])
                html_content += "<ul>\n"
                html_content += convert_notion_blocks_to_html(children_blocks)  # Recursive call
                html_content += "</ul>\n"
        
        elif block_type == 'numbered_list_item':
            text = ''.join([item['text']['content'] for item in block['numbered_list_item']['rich_text']])
            html_content += f"<li>{text}</li>\n"
            
            # Check if the block has children and process them
            if block.get('has_children', False):
                children_blocks = fetch_notion_page_content(block['id'])
                html_content += "<ol>\n"
                html_content += convert_notion_blocks_to_html(children_blocks)  # Recursive call
                html_content += "</ol>\n"
        
        elif block_type == 'quote':
            text = ''.join([item['text']['content'] for item in block['quote']['rich_text']])
            html_content += f"<blockquote>{text}</blockquote>\n"
        
        elif block_type == 'code':
            text = block['code']['text'][0]['text']['content']
            language = block['code']['language']
            html_content += f"<pre><code class='{language}'>{text}</code></pre>\n"
        
        # Handle unsupported block types gracefully
        else:
            html_content += f"<!-- Unsupported block type: {block_type} -->\n"
        # Add more block types as needed
    return html_content


def remove_ado_description_section(html_content):
    """Remove the section titled 'ADO Description' along with its content until the next <h2> tag or end."""
    ado_section_regex = r"(?is)(<h2>\s*ADO Description\s*<\/h2>.*?)(?=<h2>|$)"
    updated_content = re.sub(ado_section_regex, "", html_content, flags=re.DOTALL).strip()
    return updated_content

def fetch_work_item_description(work_item_id):
    """Fetches the description of a work item."""
    headers = {
    'Content-Type': 'application/json-patch+json'
    }
    ado_organization =st.session_state["global_variable"]["default_organization"]
    ado_project=st.session_state["selected_project"]
    ado_pat =st.session_state["global_variable"]["default_pat"]
    url = f"https://dev.azure.com/{ado_organization}/{ado_project}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    response = requests.get(url, auth=HTTPBasicAuth('',ado_pat ))
    
    # Retrieve description field if it exists
    fields = response.json().get('fields', {})
    return fields.get('System.Description', '')

#=============Clean Json Payload===================================================================================================
def clean_json_payload(payload):
    """
    Cleans a JSON payload by escaping or removing problematic characters.
    
    Args:
        payload (dict or str): The JSON payload as a dictionary or a JSON string.

    Returns:
        str: A cleaned JSON string.
    """
    def clean_value(value):
        """
        Recursively cleans individual values in the JSON payload.
        - Escapes special characters in strings.
        - Processes nested lists or dictionaries.
        """
        if isinstance(value, str):
            # Escape necessary characters
            return (
                value
                .replace('\\', '\\\\')  # Escape backslashes
                .replace('"', '\\"')    # Escape double quotes
                .replace('\n', '\\n')   # Escape newlines
                .replace('\t', '\\t')   # Escape tabs
                .replace('\r', '\\r')   # Escape carriage returns
                .replace('\b', '\\b')   # Escape backspaces
                .replace('\f', '\\f')   # Escape form feeds
            )
        elif isinstance(value, list):
            # Recursively clean each item in a list
            return [clean_value(item) for item in value]
        elif isinstance(value, dict):
            # Recursively clean keys and values in a dictionary
            return {clean_value(k): clean_value(v) for k, v in value.items()}
        else:
            # Return the value as-is for non-string types
            return value

    try:
        # If the payload is a JSON string, parse it into a Python object
        if isinstance(payload, str):
            payload = json.loads(payload)

        # Clean the payload
        cleaned_payload = clean_value(payload)

        # Convert back to JSON string
        return json.dumps(cleaned_payload, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ValueError(f"Error cleaning JSON payload: {e}")

def fetch_child_items(organization, project, parent_work_item_id, pat):
    """
    Fetches child items, their types, and status from Azure DevOps.
    
    Parameters:
        ado_url (str): Azure DevOps URL (e.g., "https://dev.azure.com").
        organization (str): Azure DevOps organization name.
        project (str): Azure DevOps project name.
        parent_work_item_id (int): The parent work item ID to fetch children.
        pat (str): Personal Access Token for Azure DevOps.
    
    Returns:
        list: A list of dictionaries containing child items, their types, and status.
    """
    
    # API endpoint for work items
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{parent_work_item_id}?$expand=relations&api-version=7.0"
    # Authentication header
    response = requests.get(url, auth=HTTPBasicAuth('', pat))
    # Fetch parent work item details
    if response:
        parent_work_item = response.json()
  
    # Extract child items (if any)
    child_items = []
    if "relations" in parent_work_item:
        for relation in parent_work_item["relations"]:
            if relation["rel"] == "System.LinkTypes.Hierarchy-Forward":  # Child relation
                # Extract child work item ID
                child_id = relation["url"].split("/")[-1]
                
                # Fetch child work item details
                child_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{child_id}?api-version=7.0"
                child_response = requests.get(
                                child_url,
                                auth=HTTPBasicAuth('', pat)
                            )
                child_work_item = child_response.json()
                
                # Extract relevant details
                child_items.append({
                    "id": child_work_item["id"],
                    "type": child_work_item["fields"]["System.WorkItemType"],
                    "Title": child_work_item["fields"]["System.Title"],
                    "status": child_work_item["fields"]["System.State"],
                    "Estimates":child_work_item["fields"].get('Microsoft.VSTS.Scheduling.Effort', 0)
                })
    
    return child_items

def push_dataframe_to_notion(page_id, df):
    """Push the DataFrame as a table to Notion, creating or updating it under the ADO description."""
    
  

    # Step 2: Check if a table exists under the ADO description
    blocks = get_page_blocks(page_id)
    table_block_id = None
    header_exists = False
    for block in blocks['results']:
        if block['type'] == 'heading_2' and block['heading_2']['rich_text']:
            content = block['heading_2']['rich_text'][0]['text']['content']
            if content == "ADO Description" :
                ADO_block_id=block['id']
                if block['has_children']== True:
                    url = f'https://api.notion.com/v1/blocks/{block['id']}/children'
                    headers = {
                        'Authorization': f'Bearer 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',
                        'Content-Type': 'application/json',
                        'Notion-Version': '2022-06-28'
                    }
                    response = requests.get(url, headers=headers)
                    # After finding the "ADO Description" heading, check for the table under it
                    if response:
                        for block in response.json()['results']:                   
                            if block['type'] == 'table':
                                table_block_id = block['id']
                                break

                        # Step 3: If table exists, update rows, otherwise create table
                        if table_block_id:
                            print("Table found, updating rows...")
                            # Get the existing table rows and update them, or append new rows if needed
                            if delete_block(table_block_id) == 1:
                                table_block_id = create_table(ADO_block_id, df)
                                if table_block_id :
                                    print("Update the table .")
                                    return 1
                                else:
                                    print("Failed to update the table rows.")
                                    return 0
                            else:
                                print("Failed to update the table rows.")
                                return 0
            if table_block_id is None:
                print("Table not found, creating a new table...")
                # Create a new table
                table_block_id = create_table(ADO_block_id, df)
                if table_block_id :
                    print(" Created the table .")
                    return 1
                else:
                    print(" Failed in Created the table .")
                    return 0

                    
        
                
                


def update_table_rows(page_id, table_block_id, df):
    """Update the rows of an existing table in Notion."""
    table_data = df.to_dict(orient="records")  # Convert dataframe to a list of dictionaries
    row_blocks = []
    header_row_block = {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "ID"
                        },
                        "plain_text": "ID",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Type"
                        },
                        "plain_text": "Type",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Title"
                        },
                        "plain_text": "Title",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Status"
                        },
                        "plain_text": "Status",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Estimates"
                        },
                        "plain_text": "Estimates",
                        "href": None
                    }
                ]
            ]
        }
    }
    for row in table_data:
        row_block = {
            "object": "block",
            "type": "table_row",
            "table_row": {
                "cells": [
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['id'])
                            },
                            "plain_text": str(row['id']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['type'])
                            },
                            "plain_text": str(row['type']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['Title'])
                            },
                            "plain_text": str(row['Title']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['status'])
                            },
                            "plain_text": str(row['status']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['Estimates'])
                            },
                            "plain_text": str(row['Estimates']),
                            "href": None
                        }
                    ]
                ]
            }
        }
        row_blocks.append(header_row_block)
        row_blocks.append(row_block)

    # Assuming we have an API function to append or update rows in an existing table
    if update_block_childern(table_block_id, row_blocks):
        return 1
    else:
        return 0


def create_table(page_id, df):
    """Create a new table in Notion under the specified page."""
    print (len(df.columns))
    table_blocks = [{
        "object": "block",
        "type": "table",
        "table": {
            "has_column_header": True,
            "table_width": len(df.columns) # Set table width to number of columns in the DataFrame
        }
    }]
    header_row_block = {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "ID"
                        },
                        "plain_text": "ID",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Type"
                        },
                        "plain_text": "Type",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Title"
                        },
                        "plain_text": "Title",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Status"
                        },
                        "plain_text": "Status",
                        "href": None
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                            "content": "Estimates"
                        },
                        "plain_text": "Estimates",
                        "href": None
                    }
                ]
            ]
        }
    }
    
    table_data = df.to_dict(orient="records")  # Convert dataframe to a list of dictionaries
    row_blocks = []
    row_blocks.append(header_row_block)

    for row in table_data:
        row_block = {
            "object": "block",
            "type": "table_row",
            "table_row": {
                "cells": [
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['id'])
                            },
                            "plain_text": str(row['id']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['type'])
                            },
                            "plain_text": str(row['type']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['Title'])
                            },
                            "plain_text": str(row['Title']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['status'])
                            },
                            "plain_text": str(row['status']),
                            "href": None
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "text": {
                                "content": str(row['Estimates'])
                            },
                            "plain_text": str(row['Estimates']),
                            "href": None
                        }
                    ]
                ]
            }
        }
        row_blocks.append(row_block)
        
    table_blocks[0]['table']['children'] = row_blocks

    # Append table to the page with the new rows
    headers = {
        'Authorization': f'Bearer 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',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    """Append new blocks to the Notion page."""
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    payload = {"children": table_blocks}  # Wrap blocks in the correct JSON structure
    response = requests.patch(url, headers=headers, json=payload)
    res=response.json()
    if response.json() : 
        return 1
    else:
        return 0


