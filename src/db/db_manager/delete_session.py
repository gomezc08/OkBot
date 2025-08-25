from db_connector import DBConnector
import mysql.connector

class DeleteSession:
    def __init__(self):
        self.connector = DBConnector()
    
    def delete_session(self, name: str, version: int):
        """Delete a session by name and version (composite primary key)"""
        self.connector.open_connection()
        try:
            query = "DELETE FROM sessions WHERE name = %s AND version = %s"
            self.connector.cursor.execute(query, (name, version))
            if self.connector.cursor.rowcount > 0:
                self.connector.cnx.commit()
                print(f"Session deleted: {name} - version {version}")
            else:
                print(f"No session found with name '{name}' and version {version}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def delete_session_step(self, session_name: str, session_version: int, step_number: int):
        """Delete a session step by session_name, session_version, and step_number (composite primary key)"""
        self.connector.open_connection()
        try:
            query = "DELETE FROM session_steps WHERE session_name = %s AND session_version = %s AND step_number = %s"
            self.connector.cursor.execute(query, (session_name, session_version, step_number))
            if self.connector.cursor.rowcount > 0:
                self.connector.cnx.commit()
                print(f"Session step deleted: {session_name} - version {session_version} - step {step_number}")
            else:
                print(f"No session step found with session '{session_name}', version {session_version}, and step {step_number}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def delete_session_variable(self, session_name: str, session_version: int, variable_name: str):
        """Delete a session variable by session_name, session_version, and variable_name (composite primary key)"""
        self.connector.open_connection()
        try:
            query = "DELETE FROM session_variables WHERE session_name = %s AND session_version = %s AND variable_name = %s"
            self.connector.cursor.execute(query, (session_name, session_version, variable_name))
            if self.connector.cursor.rowcount > 0:
                self.connector.cnx.commit()
                print(f"Session variable deleted: {session_name} - version {session_version} - variable {variable_name}")
            else:
                print(f"No session variable found with session '{session_name}', version {session_version}, and variable '{variable_name}'")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def delete_session_run(self, run_id: int):
        """Delete a session run by id (primary key)"""
        self.connector.open_connection()
        try:
            query = "DELETE FROM session_runs WHERE id = %s"
            self.connector.cursor.execute(query, (run_id,))
            if self.connector.cursor.rowcount > 0:
                self.connector.cnx.commit()
                print(f"Session run deleted: ID {run_id}")
            else:
                print(f"No session run found with ID {run_id}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def delete_all_session_steps(self, session_name: str, session_version: int):
        """Delete all steps for a specific session and version"""
        self.connector.open_connection()
        try:
            query = "DELETE FROM session_steps WHERE session_name = %s AND session_version = %s"
            self.connector.cursor.execute(query, (session_name, session_version))
            deleted_count = self.connector.cursor.rowcount
            if deleted_count > 0:
                self.connector.cnx.commit()
                print(f"Deleted {deleted_count} session steps for session '{session_name}' version {session_version}")
            else:
                print(f"No session steps found for session '{session_name}' version {session_version}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def delete_all_session_variables(self, session_name: str, session_version: int):
        """Delete all variables for a specific session and version"""
        self.connector.open_connection()
        try:
            query = "DELETE FROM session_variables WHERE session_name = %s AND session_version = %s"
            self.connector.cursor.execute(query, (session_name, session_version))
            deleted_count = self.connector.cursor.rowcount
            if deleted_count > 0:
                self.connector.cnx.commit()
                print(f"Deleted {deleted_count} session variables for session '{session_name}' version {session_version}")
            else:
                print(f"No session variables found for session '{session_name}' version {session_version}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def delete_all_session_runs(self, session_name: str, session_version: int):
        """Delete all runs for a specific session and version"""
        self.connector.open_connection()
        try:
            query = "DELETE FROM session_runs WHERE session_name = %s AND session_version = %s"
            self.connector.cursor.execute(query, (session_name, session_version))
            deleted_count = self.connector.cursor.rowcount
            if deleted_count > 0:
                self.connector.cnx.commit()
                print(f"Deleted {deleted_count} session runs for session '{session_name}' version {session_version}")
            else:
                print(f"No session runs found for session '{session_name}' version {session_version}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            self.connector.close_connection()
    
    def delete_session_cascade(self, name: str, version: int):
        """Delete a session and all related data (steps, variables, runs)"""
        print(f"Deleting session '{name}' version {version} and all related data...")
        
        # Delete related data first (due to foreign key constraints)
        self.delete_all_session_runs(name, version)
        self.delete_all_session_variables(name, version)
        self.delete_all_session_steps(name, version)
        
        # Finally delete the session
        self.delete_session(name, version)
        print(f"Session '{name}' version {version} and all related data deleted successfully")
