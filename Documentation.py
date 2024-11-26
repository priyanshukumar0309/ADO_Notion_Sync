import streamlit as st
import json
import os

def app():
    
    st.markdown("### How to Use the Streamlit Application")
    st.markdown("""
    ### Hi there! 👋
    If you're new to syncing Notion and Azure DevOps (ADO), don't worry — this guide will walk you through everything step by step.
    """)
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
            ```
                If you don't have the required permissions to create these keys, please ask your administrator to generate them for you.
            ```
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
        st.write('### How to Access?')
        st.write('1. Go to Azure Devops, click on profile and click  on Personal access tokens')
        st.image('images/ADOProfile.png', width=400)
        st.write('2. Provide Full Access to Read and Write, Set a expiry date (preferally a year) and Create')
        st.image('images/CreatePATToken.png',width=500)
        st.write('3. Make sure to copy and save it at a safe place')
        st.image('images/savePATToken.png',width=500)
        st.info('if you want to remove access, you can go to same location and revoke')
        st.image('images/RevokePATToken.png',width=1200)
       
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
        st.image("images/connectWithNotion.png", caption="Database Sharing Screenshot", width=700)

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
        st.image('images/NotionPageUpdate.png', width=600)

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
        st.image('images/ADOPageUpdated.png', width =1200)

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

    # Adding a more visually appealing title with an icon
    st.header("✨ Notion & Azure DevOps Integration: Testing Guide")

    # Add a separator to make sections distinct
    st.markdown("---")

    # Step 1: Setting Up Notion
    st.markdown("### Step 1: Setting Up Notion")
    st.markdown("""
        <div style="font-size:18px;">
            <ul>
                <li><b> Start with a Test Database:</b>
                You can either create your own test database or use the pre-filled <b>'Notion ADO Sync Test Database'</b>, which is already connected to <code>dbtDigitalPayments</code>. If you're new, the test database is a quick way to get started.</li>
                <li><b> Connect Your Database:</b>
                <ul>
                    <li><b>If you're using your own database:</b>
                    Go to your Notion page and create a new page (e.g., "YourName Test Database").
                    Open the page settings, and in the API section, add a connection to the <code>dbtDigitalPayments</code> integration or enter your personal API key.</li>
                    <li><b>Using the test database?</b>
                    You’re all set! This database is pre-connected, so just move ahead with the next steps.</li>
                </ul></li>
                <li><b>API Key Integration:</b>
                If you have a personal API key, make sure it’s updated in both your Notion page and the app settings so everything syncs smoothly.</li>              
                <li><b>Fetch Your Data:</b>
                Once connected, you can easily fetch all pages from your Notion database to start syncing with Azure DevOps.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Step 2: Azure DevOps Setup
    st.markdown("### Step 2: Azure DevOps Setup")
    st.markdown("""
        <div style="font-size:18px;">
            <ul>
                <li><b> Use an Existing Area Path for Testing:</b>
                Instead of creating a new testing area, use the following existing one to get started:
                <ul>
                    <li><b>Project:</b> <code>Digital Finance</code></li>
                    <li><b>Area Path:</b> <code>Digital Finance\\Direct Business Transactions\\Digital Payments - Green</code></li>
                </ul>
                This area is currently unused and available for your testing purposes.</li>               
                <li><b>Fetch Work Items from Azure DevOps:</b>
                Once you’ve set up your area path, you can fetch work items from it and sync them with your Notion database.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Step 3: Syncing Process
    st.markdown("### Step 3: Syncing Process")
    st.markdown("""
        <div style="font-size:18px;">
            <ul>
                <li><b>Syncing:</b>
                The app will ensure that any missing items in Notion are created, existing items are updated, and all data is synced between your Notion database and Azure DevOps.
                This will keep your information accurate and up-to-date across both platforms.</li>               
                <li><i><b>Remember:</b> You don’t have to worry about syncing manually. The app takes care of everything for you!</i></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Step 4: Tidying Up
    st.markdown("### Step 4: Tidying Up")
    st.markdown("""
        <div style="font-size:18px;">
            <ul>
                <li><b>Clean Up After Testing:</b>
                After you're done testing, please clear your test data so others can use the same resources:
                <ul>
                    <li><b>In Notion:</b> Clear the database or disconnect the <code>dbtDigitalPayments</code> integration.</li>
                    <li><b>In Azure DevOps:</b> Delete any work items you created during testing.</li>
                </ul>
                This helps maintain a clean testing environment for everyone to use.</li>             
                <li>Thank you for keeping the resources available for others!</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Need Help Section
    st.markdown("### Need Help? 🚑")
    st.markdown("""
        <div style="font-size:18px;">
            <ul>
                <li>If you face any issues or need assistance, please feel free to reach out to me directly on <a href="https://teams.microsoft.com/l/chat/0/0?users=kumar.priyanshu@volvocars.com">Teams</a>.</li>
                <li>Alternatively, you can click the <b>alert icon</b> in the bottom-right corner of this app to submit an issue. I’ll be happy to assist you!</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Adding a visual separator at the bottom to close the guide section
    st.markdown("---")

    
        
    st.success("Documentation loaded successfully!")
        
        
