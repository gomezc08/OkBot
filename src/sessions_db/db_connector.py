"""
Provides a streamlined interface for connecting to the MySQL Workbench/database.
"""

import os
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

class DBConnector:
    def __init__(self):
        self.cnx = None
        self.cursor = None


    def open_connection(self):
        print("<<Opening>> connection to MySQL")
        load_dotenv()
        config = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "database": os.getenv("DB_NAME"),
            "raise_on_warnings": True,
        }

        try:
            self.cnx = mysql.connector.connect(**config)
            self.cursor = self.cnx.cursor()
            print("Connected to MySQL")
            
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print("Could not connect to MySQL:", err)

    def close_connection(self):
        print("<<Closing>> connection to MySQL")
        self.cnx.close()
        self.cursor.close()

if __name__ == "__main__":
    db_connector = DBConnector()
    db_connector.open_connection()