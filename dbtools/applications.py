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
    
    def update_table(self, table_name, df):
        
        table_name = "_".join(table_name.split(" ")).lower()
        self.cursor.execute(f"DELETE FROM {table_name}")
        df.to_sql(table_name, self.connection, if_exists='append', index=False)
        print(f"HERE ARE THE UPDATED ROWS: {self.cursor.fetchall()}")
        self.connection.commit()

    def get_applications(self):

        all_applications = {}
        columns = ["ID", "Date", "Position", "Company", "Description", "Link", "Tags", "Status"]

        for table_name in self.get_table_names(): 
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            full_name = " ".join(table_name.split("_")).title()

            df = pd.DataFrame(rows, columns=columns).set_index("ID")
            # df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.floor("D")
            df = df.sort_values(by=["Date"], ascending=[True])
            all_applications[full_name] = df

        return all_applications