import sqlite3
from langchain.tools import BaseTool
from pydantic import Field

class SQLiteTool(BaseTool):
    """Tool for interacting with a local SQLite database."""
    name: str = Field(default="SQLiteTool")
    description: str = Field(default="Tool for interacting with SQLite databases")
    system: str
    db_path: str = Field(default=None)  # Define db_path as a field
    table_name: str = Field(default=None)  # Define table_name as a field

    def __init__(self, system: str):
        super().__init__(name="SQLiteTool", description="Tool for interacting with SQLite databases", system=system)
        # Set the database and table based on the selected system
        if system == "General_IHub":
            self.db_path = "mydatabase.db"
            self.table_name = "General_IHub"
        elif system == "Catalyst":
            self.db_path = "catalystdat.db"
            self.table_name = "Catalyst"
        else:
            raise ValueError("Invalid system. Please select 'General_IHub' or 'Catalyst'.")

    def _run(self, query: str) -> str:
        """Execute a query on the SQLite database."""
        try:
            # Connect to the appropriate database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # If the query does not specify a table, prepend the table name
            if not any(table in query for table in [self.table_name]):
                query = query.replace("<table>", self.table_name)

            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                # Fetch and return results for SELECT queries
                result = cursor.fetchall()
                conn.close()
                return str(result)
            else:
                # Commit changes for non-SELECT queries
                conn.commit()
                conn.close()
                return "Query executed successfully."
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Execute a query on the SQLite database."""
        try:
            # Connect to the appropriate database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # If the query does not specify a table, prepend the table name
            if not any(table in query for table in [self.table_name]):
                query = query.replace("<table>", self.table_name)

            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                # Fetch and return results for SELECT queries
                result = cursor.fetchall()
                conn.close()
                return str(result)
            else:
                # Commit changes for non-SELECT queries
                conn.commit()
                conn.close()
                return "Query executed successfully."
        except Exception as e:
            return f"Error: {str(e)}"

        # """Asynchronous version of the tool (not implemented)."""
        # raise NotImplementedError("SQLiteTool does not support async operations.")