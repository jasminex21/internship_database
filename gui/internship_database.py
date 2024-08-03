import yaml
import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from datetime import datetime

from dbtools.applications import Applications

st.set_page_config(layout='wide')

### GLOBAL VARIABLES ###
CYCLES = ["Summer 2024", "Summer 2025"]
TAGS = ["Favorite", "Hopeful", "Long shot", "Remote", "Hybrid"]
STATUSES = ["Pending", "Interview", "Rejected", "Accepted"]

### SESSION STATES ###
if "cycle" not in st.session_state:
    st.session_state.cycle = CYCLES[0]

### FUNCTIONS ###
def get_shown_table():

    print("GET SHOWN TABLE RAN")
    with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
        all_applications = applications.get_applications()
    
    return all_applications[st.session_state.cycle]

def set_shown_table():

    st.session_state.table_to_show = get_shown_table()

if "table_to_show" not in st.session_state: 
    st.session_state.table_to_show = get_shown_table()

### AUTHENTICATION ###
with open("/home/jasmine/PROJECTS/internship_database/gui/credentials.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized'])

authenticator.login()

### UI ###

st.title("Internship Database")

if st.session_state["authentication_status"]:
    # st.toast(f'Welcome {st.session_state["name"]}!', icon="👋")
    # authenticator.logout(location="sidebar", key="logout_button")
    with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
        cycles = applications.get_table_names(full_names=True)

    with st.sidebar: 
        with st.form("application_info"):
            cycle = st.selectbox("Application cycle", 
                                 options=CYCLES,
                                 key="submitted_cycle")
            date = st.date_input("Date applied", 
                             value="today", 
                             format="MM/DD/YYYY")
            position = st.text_input("Position", 
                                          placeholder="e.g. Data Science Intern")
            company = st.text_input("Company", 
                                         placeholder="e.g. Google")
            description = st.text_area("Role description (optional)", 
                                       placeholder="A brief description of your role")
            link = st.text_input("Link", 
                                 placeholder="Link to position")
            tags = st.multiselect("Tags", 
                                  options=TAGS)
            status = st.selectbox("Status", 
                                  options=STATUSES)
            submit_btn = st.form_submit_button("Submit")
        
        if submit_btn:
            with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
                applications.add_entry(cycle, (date, position, company, description, link, ", ".join(tags), status))
                all_applications = applications.get_applications()

    database_tab, stats_tab = st.tabs(["Your Internships", "Statistics and Trends"])
    with database_tab: 

        cycle = st.selectbox("Application cycle", 
                             options=cycles,
                             key="cycle", 
                             on_change=set_shown_table)

        dynamic_table = st.data_editor(st.session_state.table_to_show, 
                                       column_config={"Tags": st.column_config.ListColumn(),
                                                      "Status": st.column_config.SelectboxColumn(options=STATUSES,required=True),
                                                      "Link": st.column_config.LinkColumn(display_text="Link")}, 
                                                      key="edited_table", 
                                                      use_container_width=True, 
                                                      disabled=["ID", "Date"])
        st.write(st.session_state.edited_table)

        # with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
        #     applications.update_table(cycle, st.session_state.edited_table)
        #     all_applications = applications.get_applications()

    
    with stats_tab: 
        st.write("Stats will be shown here")