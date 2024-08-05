import sqlite3
import os
import pandas as pd
from datetime import datetime, date

class Applications: 

    def __init__(self, dirpath, predefined_cycles):
        
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)

        self.db_path = os.path.join(dirpath, "Applications.db")
        self.predefined_cycles = ["_".join(cycle.split(" ")) for cycle in predefined_cycles]

    def __enter__(self): 
        
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.create_settings()
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.connection.close()
    
    def _get_db_cycle(self, cycle):
        
        return "_".join(cycle.split(" ")).lower()
    
    def get_table_names(self, full_names=False):
        
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        
        # returning each name as "Summer 2024", e.g., rather than "summer_2024"
        table_names = [table[0] for table in tables]
        table_names.remove("user_settings")
        if "sqlite_sequence" in table_names:
            table_names.remove("sqlite_sequence")
        if full_names:
            table_names = [" ".join(table.split("_")).title() for table in table_names]
        return table_names

    def create_tables(self): 
        
        for cycle in self.predefined_cycles: 
            self.add_cycle(cycle)
    
    def add_cycle(self, cycle_name):
        cycle_name = self._get_db_cycle(cycle_name)
        create_query = f"""CREATE TABLE IF NOT EXISTS {cycle_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        position TEXT NOT NULL,
        company TEXT NOT NULL,
        description TEXT,
        link TEXT,
        tags TEXT,
        status TEXT NOT NULL)"""
        self.cursor.execute(create_query)
        self.connection.commit()

    def delete_cycle(self, cycle_name): 
        cycle_name = self._get_db_cycle(cycle_name)
        delete_query = f"DROP TABLE {cycle_name}"
        self.cursor.execute(delete_query)
        self.connection.commit()

    def create_settings(self):
        create_query = f"""CREATE TABLE IF NOT EXISTS user_settings (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           default_cycle TEXT)"""
        self.cursor.execute(create_query)
        self.connection.commit()

    def update_settings(self, setting, new_value):
        # TODO: depending on if there are other settings to add, this will probs. need fixing
        update_query = f"REPLACE INTO user_settings (id, {setting}) VALUES (1, '{new_value}')"
        self.cursor.execute(update_query)
        self.connection.commit()

    def get_setting(self, setting): 
        get_query = f"SELECT {setting} from user_settings LIMIT 1"
        self.cursor.execute(get_query)

        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def add_entry(self, table_name, app_info):

        table_name = self._get_db_cycle(table_name)
        add_query = f"""INSERT INTO {table_name} (date, position, company, description, link, tags, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(add_query, app_info)
        self.connection.commit()
    
    def update_table(self, table_name, df, updates):
        
        table_name = self._get_db_cycle(table_name)
        edited_rows = updates["edited_rows"]

        for idx, edits in edited_rows.items(): 
            row_id = df.index[idx]
            for col, new_val in edits.items(): 
                update_query = f'UPDATE {table_name} SET {col} = "{new_val}" WHERE id = {row_id}'
                self.cursor.execute(update_query)
        
        self.connection.commit()

    def get_applications(self):

        all_applications = {}
        columns = ["ID", "Date", "Position", "Company", "Description", "Link", "Tags", "Status"]

        for table_name in self.get_table_names(): 
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            full_name = " ".join(table_name.split("_")).title()

            df = pd.DataFrame(rows, columns=columns).set_index("ID")
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            df = df.sort_values(by=["Date"], ascending=[True])
            all_applications[full_name] = df

        return all_applications
    
    def get_cycle_df(self, cycle):

        all_applications = self.get_applications()

        if cycle == "All Cycles": 
            return pd.concat([df for df in all_applications.values()], axis=0)
        
        return all_applications[cycle]
    
    def get_response_rate(self, cycle):

        cycle_df = self.get_cycle_df(cycle)
        not_pending_df = cycle_df[cycle_df["Status"] != "🕒 Pending"]

        pct = (not_pending_df.shape[0] / cycle_df.shape[0]) * 100 if cycle_df.shape[0] else 0.0

        return not_pending_df.shape[0], cycle_df.shape[0], round(pct, 2)
    
    def get_acceptance_rate(self, cycle):
        
        cycle_df = self.get_cycle_df(cycle)
        not_pending_df = cycle_df[~cycle_df["Status"].isin(["🗣️ Interview", "🕒 Pending"])]
        accepted_df = not_pending_df[not_pending_df["Status"].isin(["💸 Offer", "🎉 Accepted Offer"])]

        pct = (accepted_df.shape[0] / not_pending_df.shape[0]) * 100 if not_pending_df.shape[0] else 0.0

        return accepted_df.shape[0], not_pending_df.shape[0], round(pct, 2)
    
    def get_application_counts(self, cycle):

        cycle_df = self.get_cycle_df(cycle)
        cycle_df["Date"] = pd.to_datetime(cycle_df["Date"]).dt.date

        apps_over_time = cycle_df["Date"].value_counts().sort_index()
        apps_over_time = apps_over_time.rename_axis("Date").reset_index(name="Applications")
        apps_over_time["Cumulative Applications"] = apps_over_time["Applications"].cumsum()

        return apps_over_time
    
    def get_average_apps(self, cycle):
        
        application_counts = self.get_application_counts(cycle)
        if application_counts.shape[0]:
            started_date = application_counts["Date"][0]
            today_date = date.today()
            day_delta = (today_date - started_date).days

            try:
                apps_today = application_counts[application_counts["Date"] == today_date]["Applications"].values[0]
                # minus 2 as to not include the current date - average is up and not including
                cumulative_apps = application_counts["Cumulative Applications"][application_counts.shape[0] - 2]
            except IndexError:
                apps_today = 0
                cumulative_apps = application_counts["Cumulative Applications"][application_counts.shape[0] - 1]
            avg_apps_per_day = round(cumulative_apps / day_delta, 2)
            
        else: 
            avg_apps_per_day = 0.0
            apps_today = 0

        return apps_today, avg_apps_per_day