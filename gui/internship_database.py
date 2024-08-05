import yaml
import os
import streamlit as st
import streamlit_authenticator as stauth
import plotly.graph_objects as go
from yaml.loader import SafeLoader
from os.path import expanduser
from datetime import date

from dbtools.applications import Applications

st.set_page_config(layout='wide')

### GLOBAL VARIABLES ###
CYCLES = ["Summer 2024", "Summer 2025"]
TAGS = ["❤️ Favorite", "💜 Hopeful", "🙏 Long shot", "🌐 Remote", "🦸 Hybrid", "Abroad"]
STATUSES = ["🕒 Pending", "🗣️ Interview", "⛔ Rejected", "🎉 Accepted"]
DEFAULT_CYCLE = "Summer 2024"

### SESSION STATES ###
if "cycle" not in st.session_state:
    st.session_state.cycle = DEFAULT_CYCLE
if "display_cycle" not in st.session_state:
    st.session_state.display_cycle = DEFAULT_CYCLE

### FUNCTIONS ###
def get_shown_table():

    with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
        all_applications = applications.get_applications()
    
    return all_applications[st.session_state.display_cycle]

def set_shown_table():

    st.session_state.table_to_show = get_shown_table()

def get_donut(labels, values, colors, title):

    fig = go.Figure(data=[go.Pie(labels=labels, 
                                 values=values, 
                                 hole=.3, 
                                 marker=dict(colors=colors))]) 
    fig.update_layout(title=title)

    return fig

def get_line_plot(apps_over_time):

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=apps_over_time["Date"],
        y=apps_over_time["Applications"],
        name="Applications by date",
        hovertemplate="%{y} applications"
    ))
    fig.add_trace(go.Scatter(
        x=apps_over_time["Date"],
        y=apps_over_time["Cumulative Applications"],
        name="Cumulative applications",
        hovertemplate="%{y} applications"
    ))
    fig.update_layout(title="Applications over time",
                      xaxis_title="Date",
                      yaxis_title="Applications",
                      hovermode='x unified')
    
    fig.update_xaxes(tickformat="%m-%d")
                     # dtick="D5")
    return fig

### AUTHENTICATION ###
with open("/home/jasmine/PROJECTS/internship_database/gui/credentials.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized'])

st.title("Internship Database")

authenticator.login()

### UI ###
if st.session_state["authentication_status"]:
    PATH = os.path.join(expanduser("~"), f"internship_database_{st.session_state.username}")

    if "table_to_show" not in st.session_state: 
        st.session_state.table_to_show = get_shown_table()
    # st.toast(f'Welcome {st.session_state["name"]}!', icon="👋")
    with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
        cycles = applications.get_table_names(full_names=True)
        default = applications.get_setting("default_cycle")
        DEFAULT_CYCLE = default if default else DEFAULT_CYCLE

    with st.sidebar: 
        add_tab, settings_tab = st.tabs(["Add Application", "Settings"])
        with add_tab:
            app_form = st.form("application_info", clear_on_submit=True)
            with app_form:
                st.markdown("### Add an Application")
                st.selectbox("Application cycle", 
                             options=cycles,
                             index=cycles.index(DEFAULT_CYCLE),
                             key="cycle")
                st.date_input("Date applied", 
                              value="today", 
                              min_value=date(date.today().year - 1, 1, 1),
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
            with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
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
                    st.session_state.display_cycle = st.session_state.cycle
                    set_shown_table()
                else: 
                    app_form.error("One or more required fields not filled.")
        
        with settings_tab:
            st.markdown("### Application Database Settings")
            st.selectbox(f"Default application cycle (currently {DEFAULT_CYCLE})", 
                         options=cycles,
                         index=None,
                         placeholder="Select an application cycle",
                         key="default_cycle")
            submit_default_cycle = st.button("Submit")
            if submit_default_cycle: 
                with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
                    applications.update_settings("default_cycle", new_value=st.session_state.default_cycle) 
                    st.rerun()

    database_tab, stats_tab, resources_tab = st.tabs(["Your Internships", "Statistics and Trends", "Resources"])
    with database_tab: 
        col1, col2, col3 = st.columns(3)
        cycle_to_show = col1.selectbox("Application cycle", 
                       options=cycles,
                       key="to_show_cycle", 
                       index=cycles.index(DEFAULT_CYCLE))
                       # on_change=set_shown_table)
        if cycle_to_show: 
            st.session_state.display_cycle = st.session_state.to_show_cycle
            set_shown_table()
        st.markdown(f"### Your {st.session_state.display_cycle} Applications")

        dynamic_table = st.data_editor(st.session_state.table_to_show, 
                                       column_config={"Tags": st.column_config.ListColumn(),
                                                      "Status": st.column_config.SelectboxColumn(options=STATUSES,required=True),
                                                      "Link": st.column_config.LinkColumn(display_text="Link"),
                                                      "Date": st.column_config.DateColumn(min_value=date(date.today().year - 1, 1, 1),
                                                                                          max_value=date.today(),
                                                                                          format="YYYY-MM-DD")}, 
                                                      key="edited_table", 
                                                      use_container_width=True, 
                                                      disabled=["ID"])

        if st.session_state.edited_table["edited_rows"]:
            with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
                applications.update_table(st.session_state.display_cycle, dynamic_table, st.session_state.edited_table)

    with stats_tab: 
        col1, col2, col3 = st.columns(3)
        col1.selectbox("Application cycle", 
                       options=cycles + ["All Cycles"],
                       key="stats_cycle", 
                       index=cycles.index(st.session_state.cycle) if st.session_state.cycle else len(cycles) - 1)
        st.markdown(f"### Your {st.session_state.stats_cycle} Statistics")

        with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
            (response_numerator, 
             response_denominator, 
             response_rate) = applications.get_response_rate(st.session_state.stats_cycle)
            (acceptance_numerator, 
             acceptance_denominator, 
             acceptance_rate) = applications.get_acceptance_rate(st.session_state.stats_cycle)
            apps_over_time = applications.get_application_counts(st.session_state.stats_cycle)

        response_col, acceptance_col = st.columns(2)

        response_col.metric(label="Response Rate", value=f"{response_rate}%", 
                            help=f"You've heard back from {response_numerator} of {response_denominator} applications",
                            delta=f"{response_numerator} of {response_denominator} applications", 
                            delta_color="off")
        response_labels = ["Response", "No response"]
        response_values = [response_rate, 100 - response_rate]
        response_colors = ["Plum", "LightSalmon"]
        response_col.plotly_chart(get_donut(response_labels,
                                            response_values,
                                            response_colors,
                                            "Response Rate"))

        acceptance_col.metric(label="Acceptance Rate", value=f"{acceptance_rate}%", 
                              help=f"Of all the applications you've heard back completely from, you've been accepted to {acceptance_numerator} of {acceptance_denominator} applications", 
                              delta=f"{acceptance_numerator} of {acceptance_denominator} applications",
                              delta_color="normal")
        acceptance_labels = ["Accepted", "Rejected"]
        acceptance_values = [acceptance_rate, 100 - acceptance_rate]
        acceptance_colors = olors=["#637C63", "IndianRed"]
        acceptance_col.plotly_chart(get_donut(acceptance_labels, 
                                              acceptance_values, 
                                              acceptance_colors, 
                                              "Acceptance Rate"))
        
        st.plotly_chart(get_line_plot(apps_over_time))
    
        with resources_tab:
            st.markdown(f"### Hello, {st.session_state.name}!")
            authenticator.logout(location="main", key="logout_button")
            st.write(f"{st.session_state.username}")
            st.write(f"You've applied to x internships today; your avg. number of applications per day is y.")
