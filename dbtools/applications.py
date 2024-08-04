import sqlite3
import pandas as pd

class Applications: 

    def __init__(self, db_path, predefined_cycles):
        
        self.db_path = db_path
        self.predefined_cycles = ["_".join(cycle.split(" ")) for cycle in predefined_cycles]

    def __enter__(self): 
        
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.connection.close()
    
    def get_table_names(self, full_names=False):
        
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        
        # returning each name as "Summer 2024", e.g., rather than "summer_2024"
        table_names = [table[0] for table in tables]
        if "sqlite_sequence" in table_names:
            table_names.remove("sqlite_sequence")
        if full_names:
            table_names = [" ".join(table.split("_")).title() for table in table_names]
        return table_names

    def create_tables(self): 
        
        for cycle in self.predefined_cycles: 
            create_query = f"""CREATE TABLE IF NOT EXISTS {cycle} (
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
    
    def add_entry(self, table_name, app_info):

        table_name = "_".join(table_name.split(" ")).lower()
        add_query = f"""INSERT INTO {table_name} (date, position, company, description, link, tags, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(add_query, app_info)
        self.connection.commit()
    
    def update_table(self, table_name, updates):
        
        table_name = "_".join(table_name.split(" ")).lower()
        edited_rows = updates["edited_rows"]

        for idx, edits in edited_rows.items(): 
            row_id = idx + 1
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
        accepted_df = not_pending_df[not_pending_df["Status"] == "🎉 Accepted"]

        pct = (accepted_df.shape[0] / not_pending_df.shape[0]) * 100 if not_pending_df.shape[0] else 0.0

        return accepted_df.shape[0], not_pending_df.shape[0], round(pct, 2)
    
    def get_application_counts(self, cycle):

        cycle_df = self.get_cycle_df(cycle)
        cycle_df["Date"] = pd.to_datetime(cycle_df["Date"]).dt.date

        apps_over_time = cycle_df["Date"].value_counts().sort_index()
        apps_over_time = apps_over_time.rename_axis("Date").reset_index(name="Applications")
        apps_over_time["Cumulative Applications"] = apps_over_time["Applications"].cumsum()

        return apps_over_time