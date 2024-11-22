import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import json
import time

def app():
    st.markdown("""
            <style>
                .stButton > button {
                    float: right;
                }
            </style>
        """, unsafe_allow_html=True)

    st.title("Azure DevOps Databases")
    st.write("Display details about your Azure DevOps databases here.")
    st.info("Connect your Azure DevOps database API and display details.", icon="ℹ️")
    st.warning('Please provide both organization and personal access token.')
    # Default values for Organization and Personal Access Token
    default_organization =  st.session_state["global_variable"]["default_organization"] 
    default_pat = st.session_state["global_variable"]["default_pat"]  # Replace with your PAT or make it dynamic
    
    # Input fields for Organization and Personal Access Token
   




    organization = st.text_input("Enter your Azure DevOps Organization", value=default_organization)
    personal_access_token = st.text_input("Enter your Personal Access Token", value=default_pat, type="password")
    if st.button("Save Variable"):
        st.session_state["global_variable"]["default_pat"] = personal_access_token
        st.session_state["global_variable"]["default_organization"] = organization
        with open(st.session_state['file_path'], 'w') as file:
            json.dump(st.session_state["global_variable"], file)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    table_data = []  # Initialize table_data
    if organization and personal_access_token:
        if st.button("Fetch Azure Projects"):
            message =st.info('Fetching Azure Projects')
            status, projects = fetch_azure_projects(organization, personal_access_token)
            time.sleep(0.5)
            if status:
                message.empty()
                message=st.success('Projects Fetched')
                st.session_state.projects = projects
            else:
                message.empty()
                st.error (f'{projects[0]['error']}')

        # Check if projects are available in session state
        if 'projects' in st.session_state:
            st.info("Please select a project and then  Area Path(s) from below drop downs.")
            # Initialize session state if it's not present
            if "selected_project" not in st.session_state or "selected_project_index" not in st.session_state :
                # Create a dropdown without any pre-selected value
                selected_project = st.selectbox("Select a Project", options=[""] + st.session_state.projects)
                
                # Only update session state if the user selects a project (non-empty value)
                if selected_project:
                    st.session_state["selected_project"] = selected_project
            else:
                selected_project = st.selectbox("Select a Project", options=[""] + st.session_state.projects, index=st.session_state.selected_project_index+1)


            # Proceed with fetching area paths if a project is selected
            if selected_project  :
                st.session_state.selected_project = selected_project
                st.session_state.selected_project_index = st.session_state.projects.index(selected_project)
                area_paths = fetch_area_paths(organization, selected_project, personal_access_token)
                if area_paths:
                        st.session_state.area_paths = area_paths
                if 'area_paths' in st.session_state:
                    area_paths = st.session_state.area_paths
                    selected_area_paths = st.multiselect("Select Area Paths", area_paths)
                    if selected_area_paths:
                        st.session_state["selected_area_paths"] = selected_area_paths
        
                        if st.button("Fetch work items"):
                            work_items = fetch_work_items_by_area_paths(organization, selected_project, selected_area_paths, personal_access_token)
                            if 'error' in work_items:
                                st.error(work_items['error'])
                            else:
                                # Prepare data for table
                                table_data = DataFrame_from_workitems(work_items)
                                if table_data:
                                    st.write("### Work Items Table:")
                                    for area_path in st.session_state["selected_area_paths"]:
                                        st.write(f"Area Path: {area_path}")
                                    st.dataframe(table_data)                   
                else:
                    st.warning(f"Fetch Area Paths ")
        

        # Display data collected in session state (ADO_data)
        if "ADO_data" in st.session_state and not table_data:
            ADO_data = st.session_state["ADO_data"]
            st.write("### Previously Collected Data:")
            st.write(f"Selected Project: {st.session_state.get('selected_project', 'Not selected')}")
            st.write(f"Selected Area Paths: {', '.join(st.session_state.get('selected_area_paths', []))}")
            st.dataframe(ADO_data)
       

def DataFrame_from_workitems(work_items):
    table_data = []
    for work_item in work_items:
        title = work_item['fields'].get('System.Title', 'No title')
        state = work_item['fields'].get('System.State', 'No state')
        assigned_to = work_item['fields'].get('System.AssignedTo', {}).get('displayName', 'Unassigned')
        work_item_type = work_item['fields'].get('System.WorkItemType', 'No type')
        created_date = work_item['fields'].get('System.CreatedDate', 'No date')
        target_date = work_item['fields'].get('Microsoft.VSTS.Scheduling.TargetDate', None)
        start_date =work_item['fields'].get('Microsoft.VSTS.Scheduling.StartDate', None)
        Last_edit_date_on_Ado =work_item['fields'].get('System.ChangedDate', None)
        table_data.append({
            'ID': work_item['id'],
            'Title': title,
            'State': state,
            'Assigned To': assigned_to,
            'Work Item Type': work_item_type,
            'Created Date': created_date,
            'Change Date':Last_edit_date_on_Ado,
            'Start Date':start_date,
            'Target Date':target_date

        })
    
    # Display the data in a table format
    if table_data:
        st.session_state["ADO_data"] = table_data
        return table_data
    else:
        return table_data


def fetch_area_paths(organization, project_name, personal_access_token):
    base_url = f"https://dev.azure.com/{organization}/{project_name}/_apis/wit/classificationnodes/areas?$depth=10&api-version=7.1"
    area_paths_list = []
    continuation_token = None

    while True:
        url = base_url
        if continuation_token:
            url += f"&continuationToken={continuation_token}"

        response = requests.get(url, auth=HTTPBasicAuth('', personal_access_token))

        if response.status_code == 200:
            area_paths = response.json()

            def extract_area_paths(node, parent_path=""):
                current_path = f"{parent_path}\\{node['name']}" if parent_path else node['name']
                area_paths_list.append(current_path)
                if 'children' in node:
                    for child in node['children']:
                        extract_area_paths(child, current_path)

            extract_area_paths(area_paths)

            continuation_token = area_paths.get('continuationToken')
            if not continuation_token:
                break  # No more area paths to fetch
        else:
            return {"error": f"Failed to fetch area paths: {response.status_code}"}

    return list(set(area_paths_list))  # Remove duplicates and return unique area paths

def fetch_azure_projects(organization, personal_access_token):
    api_url = f"https://dev.azure.com/{organization}/_apis/projects?api-version=7.1"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(api_url, auth=HTTPBasicAuth('', personal_access_token), headers=headers)
        print(response)
        if response.status_code == 200:
            projects = response.json().get('value', [])
            return (1,[project['name'] for project in projects])
        else:
            return (0,[{"error": f"Failed to fetch projects. Status code: {response.status_code}", "details": response.text}])
    except requests.exceptions.RequestException as e:
        return (0,[{"error": "Request failed", "details": str(e)}])

def fetch_work_items_by_area_paths(organization, project, area_paths, personal_access_token, batch_size=50):
    if not area_paths:
        return {"error": "No area paths found."}

    area_paths_conditions = [f"[System.AreaPath] = '{path.replace("'", "''")}'" for path in area_paths]
    area_paths_conditions_str = " OR ".join(area_paths_conditions)
    
    wiql_query = {
        "query": f"""
        SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.WorkItemType], [System.CreatedDate], [System.ChangedDate]
        FROM WorkItems
        WHERE ({' OR '.join(area_paths_conditions)})
        AND [System.WorkItemType] IN ('Epic', 'Feature')
        ORDER BY [System.CreatedDate] DESC
        """
    }

    api_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=7.1"
    headers = {"Content-Type": "application/json"}

    response = requests.post(api_url, 
                             auth=HTTPBasicAuth('', personal_access_token),
                             headers=headers, 
                             json=wiql_query)

    if response.status_code == 200:
        work_items_data = response.json()
        work_item_ids = [item["id"] for item in work_items_data.get("workItems", [])]

        if work_item_ids:
            # Fields to fetch
            fields = [
               "System.Id",
               "System.Title",
               "System.State",
               "System.AssignedTo",
               "System.WorkItemType",
               "Microsoft.VSTS.Scheduling.TargetDate",
               "Microsoft.VSTS.Scheduling.StartDate",
               "System.CreatedDate",
               "System.ChangedDate"
          ]

           # API payload
            payload = {
               "ids": work_item_ids,
               "fields": fields
                }
            url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitemsbatch?api-version=7.1"
          
   
            batch_detailed_work_items = []
            max_batch_size = 199  # Maximum batch size
            batches = [work_item_ids[i:i + max_batch_size] for i in range(0, len(work_item_ids), max_batch_size)]
   
            start_time = time.time()
            for idx, batch in enumerate(batches, start=1):
                payload = {
                    "ids": batch,
                    "fields": fields
                }
            
                info_message = st.info(f"Fetching batch {idx}/{len(batches)}...")
                response = requests.post(url, auth=HTTPBasicAuth('', personal_access_token), json=payload)
                if response.status_code == 200:
                    batch_items = response.json().get('value', [])
                    batch_detailed_work_items.extend(batch_items)
                else:
                    st.error(f"Error fetching batch {idx}: {response.status_code} {response.text}")
                
            info_message.empty()
            elapsed_time = time.time()-start_time
            st.success(f"Fetching Completed for {len(work_item_ids)} items in {elapsed_time:.2f} seconds!")
                
            return batch_detailed_work_items
        else:
            return {"error": "No work items found for the selected area paths."}
    else:
        return {"error": f"Error: {response.status_code} {response.text}"}

