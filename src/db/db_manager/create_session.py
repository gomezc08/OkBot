from db_connector import DBConnector
import mysql.connector

class DBManager:
    def __init__(self):
        self.connector = DBConnector()
    
    def create_session(self, data: dict):
        self.connector.open_connection()
        try:
            query = "INSERT INTO sessions(name, description, version) VALUES (%s, %s, %s)"
            self.connector.cursor.execute(query, (data["name"], data["description"], data["version"]))
            self.connector.cnx.commit()
            print(f"Session created: {data['name']} - {data['description']} - {data['version']}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def create_session_step(self, data: dict):
        self.connector.open_connection()
        try:
            query = "INSERT INTO session_steps(session_name, session_version, step_number, action) VALUES (%s, %s, %s, %s)"
            self.connector.cursor.execute(query, (data["session_name"], data["session_version"], data["step_number"], data["action"]))
            self.connector.cnx.commit()
            print(f"Session step created: {data['session_name']} - {data['session_version']} - {data['step_number']} - {data['action']}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def create_session_variable(self, data: dict):
        self.connector.open_connection()
        try:
            query = "INSERT INTO session_variables(session_name, session_version, variable_name, label, required, requires_approval) VALUES (%s, %s, %s, %s, %s, %s)"
            self.connector.cursor.execute(query, (data["session_name"], data["session_version"], data["variable_name"], data["label"], data["required"], data["requires_approval"]))
            self.connector.cnx.commit()
            print(f"Session variable created: {data['session_name']} - {data['session_version']} - {data['variable_name']} - {data['label']} - {data['required']} - {data['requires_approval']}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def create_session_run(self, data: dict):
        self.connector.open_connection()
        try:
            query = "INSERT INTO session_runs(session_name, session_version, started_at, ended_at, status, log_path) VALUES (%s, %s, %s, %s, %s, %s)"
            self.connector.cursor.execute(query, (data["session_name"], data["session_version"], data["started_at"], data["ended_at"], data["status"], data["log_path"]))
            self.connector.cnx.commit()
            print(f"Session run created: {data['session_name']} - {data['session_version']} - {data['started_at']} - {data['ended_at']} - {data['status']} - {data['log_path']}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()