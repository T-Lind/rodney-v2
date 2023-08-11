import os
from os.path import join, dirname

import pyodbc
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "./../.env")
load_dotenv(dotenv_path)


class AzureDatabase:
    def create_table_ONE_TIME(self):
        """
        THIS SHOULD ONLY BE RUN ONCE, EVER
        """
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS PersonInfo (
               UUID NVARCHAR(50) PRIMARY KEY,
               Name NVARCHAR(255),
               Notes NVARCHAR(MAX)
            );"""
        )

    def __init__(self):
        # Database connection setup
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.environ.get('AZURE_SQL_SERVER')};"
            f"DATABASE={os.environ.get('AZURE_SQL_DB')};"
            f"UID={os.environ.get('AZURE_SQL_USER')};"
            f"PWD={os.environ.get('AZURE_SQL_PASSWORD')}"
        )
        self.conn = pyodbc.connect(self.conn_str)
        self.cursor = self.conn.cursor()

    def insert_person_info(self, uuid, name, notes=""):
        try:
            self.cursor.execute(
                "INSERT INTO PersonInfo (UUID, Name, Notes) VALUES (?, ?, ?)",
                uuid, name, notes
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")

    def retrieve_person_info(self, uuid):
        self.cursor.execute("SELECT Name, Notes FROM PersonInfo WHERE UUID=?", uuid)
        row = self.cursor.fetchone()
        if row:
            return {"Name": row.Name, "Notes": row.Notes}
        return None

    def update_person_notes(self, uuid, notes):
        try:
            self.cursor.execute(
                "UPDATE PersonInfo SET Notes=? WHERE UUID=?",
                notes, uuid
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error updating notes: {e}")

    def __del__(self):
        # Destructor to close the database connection when the object is deleted
        self.cursor.close()
        self.conn.close()
