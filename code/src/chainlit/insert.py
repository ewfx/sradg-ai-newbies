import sqlite3
import pandas as pd

# Define database file
db_file = "mydatabase.db"
table_name = "General_IHub"
excel_file = r"C:\Users\tejas\Anomaly_detect_on_recon\data\IHub_Reconciliatuion_hist.xlsx"  # Change this to your actual Excel file

# Read Excel file into DataFrame
df = pd.read_excel(excel_file, engine="openpyxl")

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Drop the table if it exists (optional, only if you want to recreate the table every time)
cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

# Create table dynamically based on DataFrame columns and include additional columns
columns = ", ".join([f'"{col}" TEXT' for col in df.columns])  # Wrap column names in double quotes
additional_columns = '"anomaly_detected" TEXT, "category" TEXT, "possible_cause" TEXT, "recommended_actions" TEXT'
cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns}, {additional_columns})')

# Insert data into SQLite
df.to_sql(table_name, conn, if_exists="append", index=False)

# Commit and close connection
conn.commit()
conn.close()

print(f"Data from {excel_file} inserted into {table_name} successfully.")