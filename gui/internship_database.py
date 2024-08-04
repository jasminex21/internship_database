import yaml
import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import plotly.graph_objects as go
from yaml.loader import SafeLoader
from datetime import datetime

from dbtools.applications import Applications

st.set_page_config(layout='wide')

### GLOBAL VARIABLES ###
CYCLES = ["Summer 2024", "Summer 2025"]
TAGS = ["❤️ Favorite", "💜 Hopeful", "🙏 Long shot", "🌐 Remote", "🦸 Hybrid"]
STATUSES = ["🕒 Pending", "🗣️ Interview", "⛔ Rejected", "🎉 Accepted"]

### SESSION STATES ###
if "cycle" not in st.session_state:
    st.session_state.cycle = CYCLES[-1]
if "display_cycle" not in st.session_state:
    st.session_state.display_cycle = CYCLES[-1]

### FUNCTIONS ###
def get_shown_table():

    with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
        all_applications = applications.get_applications()
    
    return all_applications[st.session_state.display_cycle]

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
        add_tab, settings_tab = st.tabs(["Add Application", "Settings"])
        with add_tab:
            app_form = st.form("application_info", clear_on_submit=True)
            with app_form:
                st.markdown("### Add an Application")
                st.selectbox("Application cycle", 
                             options=cycles,
                             index=cycles.index(st.session_state.cycle) if st.session_state.cycle else len(cycles) - 1,
                             key="cycle")
                st.date_input("Date applied", 
                              value="today", 
                              format="MM/DD/YYYY",
                              key="date")
                st.text_input("Position*", 
                              placeholder="e.g. Data Science Intern",
                              key="position")
                st.text_input("Company*",
                              placeholder="e.g. Google",
                              key="company")
                st.text_area("Role description", 
                             placeholder="A brief description of your role",
                             key="description")
                st.text_input("Link", 
                              placeholder="Link to position",
                              key="link")
                st.multiselect("Tags", 
                               options=TAGS,
                               key="tags", 
                               placeholder="Select one or more tags")
                st.selectbox("Status",
                             options=STATUSES,
                             key="status", 
                             index=0)
                submit_btn = st.form_submit_button("Submit")
        
        if submit_btn:
            with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
                if (st.session_state.cycle) and (st.session_state.position) and (st.session_state.company):
                    applications.add_entry(st.session_state.cycle, 
                                           (st.session_state.date, 
                                            st.session_state.position, 
                                            st.session_state.company, 
                                            st.session_state.description, 
                                            st.session_state.link, 
                                            ", ".join(st.session_state.tags), 
                                            st.session_state.status))
                    all_applications = applications.get_applications()
                    set_shown_table()
                else: 
                    app_form.error("One or more required fields not filled.")

    database_tab, stats_tab = st.tabs(["Your Internships", "Statistics and Trends"])
    with database_tab: 
        col1, col2, col3 = st.columns(3)
        col1.selectbox("Application cycle", 
                       options=cycles,
                       key="display_cycle", 
                       index=cycles.index(st.session_state.cycle) if st.session_state.cycle else len(cycles) - 1,
                       on_change=set_shown_table)
        st.markdown(f"### Your {st.session_state.display_cycle} Applications")

        dynamic_table = st.data_editor(st.session_state.table_to_show, 
                                       column_config={"Tags": st.column_config.ListColumn(),
                                                      "Status": st.column_config.SelectboxColumn(options=STATUSES,required=True),
                                                      "Link": st.column_config.LinkColumn(display_text="Link")}, 
                                                      key="edited_table", 
                                                      use_container_width=True, 
                                                      disabled=["ID", "Date"])
        # with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
        #     all_applications = applications.get_applications()

        # st.write(all_applications)
        if st.session_state.edited_table["edited_rows"]:
            with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
                applications.update_table(st.session_state.display_cycle, st.session_state.edited_table)

    with stats_tab: 
        col1, col2, col3 = st.columns(3)
        col1.selectbox("Application cycle", 
                       options=cycles + ["All Cycles"],
                       key="stats_cycle", 
                       index=cycles.index(st.session_state.cycle) if st.session_state.cycle else len(cycles) - 1)
        st.markdown(f"### Your {st.session_state.stats_cycle} Statistics")

        with Applications(db_path="Applications.db", predefined_cycles=CYCLES) as applications: 
            response_numerator, response_denominator, response_rate = applications.get_response_rate(st.session_state.stats_cycle)
            acceptance_numerator, acceptance_denominator, acceptance_rate = applications.get_acceptance_rate(st.session_state.stats_cycle)

        response_col, acceptance_col = st.columns(2)
        response_col.metric(label="Response Rate", value=f"{response_rate}%", 
                            help=f"You've heard back from {response_numerator} of {response_denominator} applications",
                            delta=f"{response_numerator} of {response_denominator} applications", 
                            delta_color="off")
        acceptance_col.metric(label="Acceptance Rate", value=f"{acceptance_rate}%", 
                              help=f"Of all the applications you've heard back completely from, you've been accepted to {acceptance_numerator} of {acceptance_denominator} applications", 
                              delta=f"{acceptance_numerator} of {acceptance_denominator} applications",
                              delta_color="normal")
        acceptance_labels = ["Accepted", "Rejected"]
        acceptance_values = [acceptance_rate, 100 - acceptance_rate]
        acceptance_fig = go.Figure(data=[go.Pie(labels=acceptance_labels, 
                                                values=acceptance_values, 
                                                hole=.3, 
                                                marker=dict(colors=["#637C63", "IndianRed"]))]) 
        acceptance_fig.update_layout(title="Acceptance Rate")
        acceptance_col.plotly_chart(acceptance_fig)

        response_labels = ["Response", "No response"]
        response_values = [response_rate, 100 - response_rate]
        response_fig = go.Figure(data=[go.Pie(labels=response_labels, 
                                        values=response_values, 
                                        hole=.3, 
                                        marker=dict(colors=["Plum", "LightSalmon"]))]) 
        response_fig.update_layout(title="Response Rate")
        response_col.plotly_chart(response_fig)
