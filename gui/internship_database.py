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
TAGS = ["❤️ Favorite", "💜 Hopeful", "🙏 Long shot", "🌐 Remote", "🦸 Hybrid", "🌏 Abroad"]
STATUSES = ["🕒 Pending", "🗣️ Interview", "❌ Rejected after Interview", "⛔ Straight Rejection", "💸 Offer", "🎉 Accepted Offer"]
DEFAULT_CYCLE = "Summer 2024"
# THEME = {"background_color": "#082D1B",
#          "button_color": "#0E290E",
#          "inputs": "#547054",
#          "text_color": "white"}
THEME = {"background_color": "#212145",
         "button_color": "#1D1D34",
         "inputs": "#4e4466",
         "text_color": "white"}

### SESSION STATES ###
if "cycle" not in st.session_state:
    st.session_state.cycle = DEFAULT_CYCLE
if "display_cycle" not in st.session_state:
    st.session_state.display_cycle = DEFAULT_CYCLE
if "added_cycle" not in st.session_state:
    st.session_state.added_cycle = ""

### FUNCTIONS ###
def apply_theme(selected_theme):
    css = f"""
    <style>
    .stApp > header {{
        background-color: transparent;
    }}
    .stApp {{
        color: {selected_theme["text_color"]};
        font-family: "Helvetica", "Arial", sans-serif;
    }}
    button[data-baseweb="tab"] {{
        background-color: transparent !important;
    }}
    div[data-baseweb="select"] > div, div[data-baseweb="base-input"] > input, div[data-baseweb="base-input"] > textarea {{
        color: {selected_theme["text_color"]};
        -webkit-text-fill-color: {selected_theme["text_color"]} !important;
        font-weight: 600 !important;
    }}
    p, ul, li {{
        color: {selected_theme["text_color"]};
        font-weight: 600 !important;
        font-size: large !important;
    }}
    h3, h2, h1, strong, h4 {{
        color: {selected_theme["text_color"]};
        font-weight: 900 !important;
    }}
    [data-baseweb="tag"] {{
        color: {selected_theme["text_color"]};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def get_shown_table():

    with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
        all_applications = applications.get_applications()
    
    return all_applications[st.session_state.display_cycle]

def set_shown_table():

    st.session_state.table_to_show = get_shown_table()

def get_donut(labels, values, counts, colors, title):

    fig = go.Figure(data=[go.Pie(labels=labels, 
                                 values=values, 
                                 hole=.3, 
                                 hovertext=[f"{cnt} applications" for cnt in counts],
                                 hoverinfo='label+text',
                                 # hovertemplate='%<b>{labels}</b><br>%{customdata}',
                                 marker=dict(colors=colors))]) 
    fig.update_layout(title=title,
                      paper_bgcolor='rgba(0,0,0,0)',  
                      plot_bgcolor='rgba(0,0,0,0)')
    fig.update_traces(marker=dict(line=dict(color="black", width=1)))

    return fig

def get_line_plot(apps_over_time):

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=apps_over_time["Date"],
        y=apps_over_time["Applications"],
        name="Applications by date",
        hovertemplate="%{y} applications",
        line=dict(width=4)
    ))
    fig.add_trace(go.Scatter(
        x=apps_over_time["Date"],
        y=apps_over_time["Cumulative Applications"],
        name="Cumulative applications",
        hovertemplate="%{y} applications",
        line=dict(width=4)
    ))
    fig.update_layout(title="Applications over time",
                      xaxis_title="Date",
                      yaxis_title="Applications",
                      hovermode='x unified',
                      paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)')
    
    fig.update_xaxes(tickformat="%m-%d")
                     # dtick="D5")
    return fig

def clear_cycle(): 
    st.session_state.added_cycle = st.session_state.cycle_to_add
    st.session_state.cycle_to_add = ""

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

apply_theme(THEME)

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
        ACTIVE_CYCLES = applications.get_active_cycles()

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
            st.markdown("# Application Database Settings")
            st.selectbox(f"Default application cycle (currently {DEFAULT_CYCLE})", 
                         options=cycles,
                         index=None,
                         placeholder="Select an application cycle",
                         key="default_cycle")
            submit_default_cycle = st.button("Set default cycle")
            if submit_default_cycle: 
                with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
                    applications.update_settings("default_cycle", new_value=st.session_state.default_cycle) 
                    st.success(f"Cycle {st.session_state.default_cycle} set as default cycle. Refresh to view changes.")

            st.divider()
            
            st.text_input(f"Add application cycle (enter to submit)",
                          placeholder="e.g. Fall 2024",
                          key="cycle_to_add", 
                          on_change=clear_cycle)
            
            if st.session_state.added_cycle: 
                if st.session_state.added_cycle.lower() not in [cycle.lower() for cycle in cycles]:
                    with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
                        applications.add_cycle(st.session_state.added_cycle)
                    st.success(f"Cycle {st.session_state.added_cycle} successfully added. Refresh to view changes.")
                    st.session_state.added_cycle = ""
                else: 
                    st.error(f"Cycle {st.session_state.added_cycle} already exists.")

            st.selectbox(f"[PERMANENT ACTION]: Delete application cycle", 
                options=cycles,
                index=None,
                placeholder="Select an application cycle",
                key="cycle_to_delete")
            submit_delete_cycle = st.button("Delete cycle")

            if submit_delete_cycle:
                with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
                        applications.delete_cycle(st.session_state.cycle_to_delete)
                st.warning(f"Cycle {st.session_state.cycle_to_delete} deleted. Refresh to view changes.")

            st.divider()

            st.multiselect("Currently active cycles", 
                           options=cycles, 
                           default=ACTIVE_CYCLES,
                           key="active_cycles")
            submit_active_cycles = st.button("Set active cycle(s)")
            if submit_active_cycles:
                with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications:
                    applications.update_statuses(st.session_state.active_cycles)

    database_tab, stats_tab, resources_tab = st.tabs(["Your Internships", "Statistics and Trends", "Resources"])
    with database_tab: 
        col1, col2, col3 = st.columns(3)
        col1.selectbox("Application cycle", 
                       options=cycles,
                       key="to_show_cycle", 
                       index=cycles.index(DEFAULT_CYCLE))
        
        if st.session_state.to_show_cycle != st.session_state.display_cycle:
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
                       index=cycles.index(DEFAULT_CYCLE))
        st.markdown(f"### Your {st.session_state.stats_cycle} Statistics")

        with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
            (response_numerator, 
             response_denominator, 
             response_rate) = applications.get_response_rate(st.session_state.stats_cycle)
            (acceptance_numerator, 
             acceptance_denominator, 
             acceptance_rate) = applications.get_acceptance_rate(st.session_state.stats_cycle)
            apps_over_time = applications.get_application_counts(st.session_state.stats_cycle)
            resources_df = applications.get_resources()

        response_col, acceptance_col = st.columns(2)

        response_col.metric(label="Response Rate", value=f"{response_rate}%", 
                            help=f"You've heard back from {response_numerator} of {response_denominator} applications",
                            delta=f"{response_numerator} of {response_denominator} applications", 
                            delta_color="off")
        response_labels = ["Response", "No response"]
        response_values = [response_rate, 100 - response_rate]
        response_counts = [response_numerator, response_denominator - response_numerator]
        response_colors = ["Plum", "LightSalmon"]
        response_col.plotly_chart(get_donut(response_labels,
                                            response_values,
                                            response_counts,
                                            response_colors,
                                            "Response Rate"))

        acceptance_col.metric(label="Acceptance Rate", value=f"{acceptance_rate}%", 
                              help=f"Of all the applications you've heard back completely from, you've been accepted to {acceptance_numerator} of {acceptance_denominator} applications", 
                              delta=f"{acceptance_numerator} of {acceptance_denominator} applications",
                              delta_color="normal")
        acceptance_labels = ["Accepted", "Rejected"]
        acceptance_values = [acceptance_rate, 100 - acceptance_rate]
        acceptance_counts = [acceptance_numerator, acceptance_denominator - acceptance_numerator]
        acceptance_colors = olors=["#637C63", "IndianRed"]
        acceptance_col.plotly_chart(get_donut(acceptance_labels, 
                                              acceptance_values, 
                                              acceptance_counts,
                                              acceptance_colors, 
                                              "Acceptance Rate"))
        
        st.plotly_chart(get_line_plot(apps_over_time))
    
        with resources_tab:
            status = "Active" if DEFAULT_CYCLE in ACTIVE_CYCLES else "Inactive"
            st.markdown(f"### Hello, {st.session_state.name} ({st.session_state.username})!")
            # TODO: add start and end date of cycle here
            authenticator.logout(location="main", key="logout_button")
            st.markdown(f"### Your current cycle is {DEFAULT_CYCLE} [{status}]")
            st.caption("You can change your default cycle in the Settings tab.")

            with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
                apps_today, avg_apps = applications.get_average_apps(DEFAULT_CYCLE)
            
            if status == "Active":
                avg_col, today_col = st.columns(2)
                diff = apps_today - avg_apps
                if diff < 0: 
                    delt = f"-You are {-round(diff, 2)} applications below your daily average"
                    delt_col = "normal"
                elif diff > 0: 
                    delt = f"You are {round(diff, 2)} applications above your daily average!"
                    delt_col = "normal"
                elif diff == 0: 
                    delt = "You have matched your daily average!"
                    delt_col = "off"
                avg_col.metric(label="Average applications per day", 
                        value=avg_apps,
                        delta=delt, 
                        delta_color=delt_col,
                        help="The daily average does *not* include the current day.")
                if apps_today > 0: 
                    today_delt = "Well done for applying today!"
                else: 
                    today_delt = "-Take some time to apply to something today!"
                today_col.metric(label="Applications today",
                                value=apps_today, 
                                delta=today_delt)
            else: 
                avg_col, total_col = st.columns(2)
                avg_col.metric(label="Average applications per day",
                          value=avg_apps)
                total_apps = apps_over_time["Cumulative Applications"][apps_over_time.shape[0] - 1]
                total_col.metric(label="Total applications", 
                          value=total_apps)
        
            st.markdown("### Your Resources")
            resources = st.data_editor(resources_df, 
                                       num_rows="dynamic",
                                       use_container_width=True, 
                                       key="resources_edits", 
                                       disabled=["ID"])
            st.write(st.session_state.resources_edits)
            st.write(st.session_state.resources_edits["added_rows"])

            if st.session_state.resources_edits["added_rows"]:
                with Applications(dirpath=PATH, predefined_cycles=CYCLES) as applications: 
                    for added in st.session_state.resources_edits["added_rows"]:
                        if len(list(added.values())) == 2:
                            applications.add_resources(tuple(added.values()))
