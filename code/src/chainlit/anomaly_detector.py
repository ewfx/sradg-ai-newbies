import numpy as np
import pandas as pd
import google.generativeai as genai  # Google's Gemini SDK
import sqlite3
import re
import time
import os 

# Define the path to the prompt file
PROMPT_FILE_PATH = os.path.join("prompts", "anomaly_detection_prompt.txt")

def load_prompt():
    """Load the prompt from the external file."""
    with open(PROMPT_FILE_PATH, "r") as file:
        return file.read()

# Inside your function
prompt_template = load_prompt()

def detect_anomalies(DB_PATH: str, table_name: str) -> str:
    """
    Detect anomalies in the specified SQLite database table.

    Args:
        database_path (str): Path to the SQLite database.
        table_name (str): Name of the table to analyze.

    Returns:
        str: A summary of detected anomalies.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        # SQLite DB2 connection setup
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Set journal mode to WAL for persistence
        cursor.execute("PRAGMA journal_mode=WAL;")

        # Connect to database and get the reconciled details
        data = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

        if data.empty:
            return "No data available for analysis"

        data = data.sort_values(by=['Account','AU','As of Date'], ascending=True)
        data = data[data['Match Status'] == 'Break']

        # Process each account separately
        account_au_combinations  = data[['Account', 'AU']].drop_duplicates()

        def parse_gemini_response(response_text):
            """Extract Anomaly_Detected, Category, Possible Cause, and Recommended Actions from Gemini's response."""
            #print("response_text:", response_text)  # Log the full response text for debugging

            # Use regex to extract the fields in the new format
            response_text = response_text.strip()  # Remove leading/trailing whitespace
            response_text = re.sub(r"\s+", " ", response_text)  # Replace multiple spaces/newlines with a single space
            anomaly_detected_match = re.search(r"Anomaly_Detected:\s*(Yes|No)", response_text,re.IGNORECASE | re.DOTALL)
            # category_match = re.search(r"Category:\s*(.+)", response_text)
            # cause_match = re.search(r"Possible Cause:\s*(.+)", response_text)
            # actions_match = re.search(r"Recommended Actions:\s*(.+)", response_text)

            # Use regex to extract the fields
            category_match = re.search(r"Category:\s*(.+?)(?=Possible Cause:|Recommended Actions:|$)", response_text, re.IGNORECASE)
            cause_match = re.search(r"Possible Cause:\s*(.+?)(?=Recommended Actions:|$)", response_text, re.IGNORECASE)
            actions_match = re.search(r"Recommended Actions:\s*(.+)", response_text, re.IGNORECASE)


            # Extract values or set defaults if no match is found
            anomaly_detected = anomaly_detected_match.group(1).strip() if anomaly_detected_match else "No"
            category = category_match.group(1).strip() if category_match else "N/A"
            possible_cause = cause_match.group(1).strip() if cause_match else "Not provided"
            recommended_actions = actions_match.group(1).strip() if actions_match else "Not provided"

            # print("Extracted Fields:")
            # print(f"Anomaly Detected: {anomaly_detected}")
            # print(f"Category: {category}")
            # print(f"Possible Cause: {possible_cause}")
            # print(f"Recommended Actions: {recommended_actions}")

            return anomaly_detected,category, possible_cause, recommended_actions


        for _, row in account_au_combinations.iterrows(): 
            account, au = row['Account'], row['AU'] 
            # print(f"\n🔍 **Processing Account: {account}, AU: {au}**")

            df_subset = data[(data['Account'] == account) & (data['AU'] == au)].copy()
            db_date = df_subset['As of Date'].max()

            # Convert 'As of Date' column to datetime if not already
            df_subset['As of Date'] = pd.to_datetime(df_subset['As of Date'])

            # Get the latest date in the dataset
            latest_date = pd.to_datetime(df_subset['As of Date'].max())

            # Filter only the latest month's data
            df_latest = df_subset[df_subset['As of Date'] == latest_date]

            # Customize the prompt with dynamic data
            prompt = prompt_template.format(latest_date=latest_date.strftime('%Y-%m-%d'))

            for _, row in df_subset.iterrows():
                prompt += f"\n#### **Account: {row['Account']}, AU: {row['AU']}**\n"
                prompt += f"**As of Date:** {row['As of Date']}\n"
                prompt += f"**Balance Difference:** ${row['Balance Difference']}M\n"

            # Send the prompt to Gemini
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            gemini_reasoning = response.text
            #print("Gemini Reasoning:", gemini_reasoning)
            # Parse Gemini Response
            anomaly_detected,category, possible_cause, recommended_actions = parse_gemini_response(gemini_reasoning)
            print("anomaly_detected:", anomaly_detected)
            print("category:", category)
            print("possible_cause:", possible_cause)
            print("recommended_actions:", recommended_actions)
            # Execute the update query
            cursor.execute(
                f'UPDATE "{table_name}" SET anomaly_detected = ?, category = ?, possible_cause = ?, recommended_actions = ? WHERE "As of Date" = ? AND Account = ? AND AU = ?',
                (anomaly_detected, category, possible_cause, recommended_actions, db_date, account, au)
            )

        try:
            conn.commit()
            time.sleep(2)
            conn.close()
            return "Changes committed successfully."
        except Exception as e:
            return(f"Error during commit: {e}")

    except Exception as e:
        return f"Error during anomaly detection: {str(e)}"