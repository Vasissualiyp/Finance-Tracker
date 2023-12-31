
import sqlite3
import pandas as pd

class DbDriver:
    """
    Class to handle database operations for mmbak files.

    Methods:
    __init__(self, file) - Initialize the database connection.
    query_to_dataframe(self, query) - Execute a SQL query and return results as a pandas DataFrame.
    close(self) - Close the database connection.
    """
    def __init__(self, file="db.mmbak"):
        """
        Initialize the database connection.

        Args:
        file (str): Path to the mmbak file.
        """
        try:
            self.connection = sqlite3.connect(file)
        except Exception as e:
            raise Exception(f"Error connecting to database: {e}")

    def query_to_dataframe(self, query):
        """
        Execute a query and return the results as a pandas DataFrame.

        Args:
        query (str): SQL query to execute.

        Returns:
        DataFrame: Resulting data in a pandas DataFrame.
        """
        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            raise Exception(f"Error executing query: {e}")

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()
