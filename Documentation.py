import streamlit as st
import json
import os

def app():
    
    st.markdown("### How to Use the Streamlit Application")

    # Section 1: Use Personal API Keys
    with st.expander("API Keys"):
        st.subheader("Steps to Obtain API Keys:")
        st.write("""
        To use this application, you need to provide your own personal API keys. **Public or shared API keys should never be used** to ensure security.
        """)
        st.markdown("""
        - **Notion API Key**: 
            1. Log in to your Notion account.
            2. Visit the [Notion API Integration Page](https://www.notion.so/my-integrations).
            3. Create a new integration and copy the generated API key.
        - **Azure DevOps Personal Access Token (PAT)**:
             1. Navigate to your Azure DevOps organization.
            2. Go to your **Profile Settings** by clicking on your profile picture.
            3. Select **Personal Access Tokens** under **Security**.
            4. Click **+ New Token**:
                - Provide a name for the token.
                - Select the expiration date.
                - Choose the required scopes such as **Work Items (Read/Write)** or **Project/Area Path Access**.
            5. Generate and copy the PAT securely.
        """)
        st.write("""
        If you don't have the required permissions to create these keys, please ask your administrator to generate them for you.
        """)
        #st.image("", caption="Example Screenshot Placeholder")

    # Section 2: Connecting Notion Page with Database
    with st.expander("Connect Notion Page with API Key"):
        st.subheader("Steps to Link a Database:")
        st.markdown("""
        1. Open the database in Notion that you want to use with this application.
        2. Share the database with the integration created in **Step 1**:
            - Click **Share** at the top right of the database.
            - Enter the name of your integration and click **Invite**.
        """)
       # st.image("", caption="Database Sharing Screenshot")

    # Section 4: Fetch Notion Database
    with st.expander("Notion"):
        st.subheader("Steps to Fetch Database and pages from Notion")
        st.markdown("""
        After entering your Notion API Key and database ID, the application will fetch the database.
        """)
        
        st.subheader("4.1 Add Missing Columns")
        st.markdown("""
        If the database does not have the required columns for proper synchronization with Azure DevOps, the application will guide you to:
        **REQUIRED_PROPERTIES**:
        These properties must be present in the Notion database for proper syncing:
        - **Date**: Date of creation/update.
        - **Last Edited Date on ADO**: Date when the work item was last updated in Azure DevOps.
        - **ADO ID**: A unique ID from Azure DevOps to link the Notion database entry with the corresponding work item in ADO.
        - **Type**: Type of work item (e.g.,Feature, Epic, Story, Bug, Task, etc.).
        - **ADO Status**: The current status of the work item in Azure DevOps.
        - **Estimates**: The estimated effort or time for the work item.
        - **Last edited time**: The time when the last update was made (for validation purposes).
        
        **Note**: If any of these properties are missing, you can easily add them directly from the application interface. However, the **Last Edited Date on ADO** column must be updated manually in the Notion database for proper tracking and syncing.
    
        """)

    # Section 5: Fetch Azure DevOps Work Items
    with st.expander("Azure DevOps"):
        st.subheader("Steps to Fetch Work items")
        st.markdown("""
        Using your Azure DevOps Personal Access Token, you can fetch work items based on project and area paths.
        """)
        st.subheader("Steps:")
        st.markdown("""
        1. Enter the **Project Name** and **Area Path** in the application.
        ```
            Only Features and Epics are fetched as of now. 
        ```
        2. Click the **Fetch ADO Work Items** button.
        3. The fetched work items will be displayed in the application for comparison and synchronization.
        """)

    # Section 6: Synchronize Notion and Azure DevOps
    with st.expander("Notion and ADO"):
        st.subheader("Synchronize Notion and Azure DevOps")
        st.markdown("""
        The application supports multiple synchronization options:
        """)
        st.subheader("6.1 Sync Status")
        st.markdown("""
        - See a comparison of items in both Notion and Azure DevOps:
            - Items present in one system but missing in the other.
            - Items that are out of sync.
        """)
        st.subheader("6.2 Create Missing Items")
        st.markdown("""
        - **Create in ADO**: Automatically create work items in Azure DevOps for tasks present in Notion but missing in ADO.
        - **Create in Notion**: Automatically add entries in Notion for work items present in ADO but missing in Notion.
        """)
        st.subheader("6.3 Sync Updates")
        st.markdown("""
        - Synchronize updates for:
            - Items where fields (like status) are outdated in either system.
            - Descriptions where content has been updated.
        """)
        st.subheader("6.4 Sync Descriptions Only")
        st.markdown("""
        - If only descriptions are out of sync, choose this option to update descriptions in both systems.
        """)

    st.title("Example on how to use")
    st.header("Connecting Notion with DBT Digital Payments")
    st.markdown("""
            Follow these steps:
            
            1. **Notion Database Setup**: 
                - Ensure that the Notion database you want to sync with ADO is connected to the app. 
                    - For this example, **Test Page Database** is already connect to dbtDigitalPayments
                    - You can then all pages from the selected Databases 
                - Connect **Notion** with the database
                ```
                    dbtDigitalPayments 
                ```
            2. **Azure DevOps Setup**: 
                - You can test with below detials
                - Select the **Digital Finance** project in Azure DevOps.
                - Use the following Area Path: 
                ```
                    Digital Finance\\Direct Business Transactions\\Digital Payments - Green
                ```
                - You can then fetch work items from this area 
                - Sync them with the Notion database.

            3. **App Sync Process**:
                - You can and update work items from the **Digital Finance** project in Azure DevOps, 
                using the **Area Path: Digital Finance\\Direct Business Transactions\\Digital Payments - Green**.
                - It will ensure that missing items are created, existing items are synced, and descriptions are updated.

           
        """)

    
        
    st.success("Documentation loaded successfully!")
        
        
