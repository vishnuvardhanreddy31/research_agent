import sqlite3
from langchain.tools import tool

# Global variable to hold the database connection
conn = None

def create_sample_db():
    """Creates an in-memory SQLite database with a sample 'users' table."""
    global conn
    if conn is None:
        conn = sqlite3.connect(':memory:') # Use an in-memory database for simplicity
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        cursor.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')")
        conn.commit()
        print("Sample SQLite database created with 'users' table.")
    else:
        print("Database already initialized.")

@tool
def sqlite_query_tool(query: str) -> str:
    """
    Executes a SQL query against the SQLite database and returns the results.
    Input should be a valid SQL SELECT statement.
    """
    global conn
    if conn is None:
        return "Database not initialized. Please run create_sample_db() first."
    
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        
        if not rows:
            return "No results found for the query."
        
        # Format results for readability
        results_str = f"Columns: {', '.join(column_names)}\n"
        for row in rows:
            results_str += f"{row}\n"
        return results_str
    except sqlite3.Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    create_sample_db()
    print(sqlite_query_tool("SELECT * FROM users"))
    print(sqlite_query_tool("SELECT name FROM users WHERE id = 1"))
    print(sqlite_query_tool("SELECT * FROM non_existent_table"))
