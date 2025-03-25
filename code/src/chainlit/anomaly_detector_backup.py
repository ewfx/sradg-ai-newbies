import numpy as np
import pandas as pd
import google.generativeai as genai  # Google's Gemini SDK
import sqlite3
import re
import time

# Set up Gemini API key
genai.configure(api_key="AIzaSyA6TxOJVzQHRPXynceK5ciaeVvpJBvrfYM")
# SQLite DB2 connection setup
DB_PATH = "mydatabase.db"
conn = sqlite3.connect(DB_PATH)
import os
print(f"Database path: {os.path.abspath(DB_PATH)}")
cursor = conn.cursor()
table_name = "General_IHub"
# Set journal mode to WAL for persistence
cursor.execute("PRAGMA journal_mode=WAL;")

# Connect to database and get the reconciled details
# conn = sqlite3.connect(DB_PATH)
data = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

if data.empty:
    print("No data available for analysis")
    exit()

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
    category_match = re.search(r"Category:\s*(.+)", response_text)
    cause_match = re.search(r"Possible Cause:\s*(.+)", response_text)
    actions_match = re.search(r"Recommended Actions:\s*(.+)", response_text)

    # Extract values or set defaults if no match is found
    anomaly_detected = anomaly_detected_match.group(1).strip() if anomaly_detected_match else "No"
    category = category_match.group(1).strip() if category_match else "N/A"
    possible_cause = cause_match.group(1).strip() if cause_match else "Not provided"
    recommended_actions = actions_match.group(1).strip() if actions_match else "Not provided"

    print("Extracted Fields:")
    print(f"Anomaly Detected: {anomaly_detected}")
    print(f"Category: {category}")
    print(f"Possible Cause: {possible_cause}")
    print(f"Recommended Actions: {recommended_actions}")

    return anomaly_detected,category, possible_cause, recommended_actions


for _, row in account_au_combinations.iterrows(): 
    account, au = row['Account'], row['AU'] 
    print(f"\n🔍 **Processing Account: {account}, AU: {au}**")

    df_subset = data[(data['Account'] == account) & (data['AU'] == au)].copy()
    db_date = df_subset['As of Date'].max()

    # Convert 'As of Date' column to datetime if not already
    df_subset['As of Date'] = pd.to_datetime(df_subset['As of Date'])

    # Get the latest date in the dataset
    latest_date = pd.to_datetime(df_subset['As of Date'].max())

    # Filter only the latest month's data
    df_latest = df_subset[df_subset['As of Date'] == latest_date]

    prompt = f"""

    You are an AI reconciliation report analyzer. The dataset contains historical reconciliation records for multiple Account-AU combinations.
    Your task is to detect anomalies in the 'Balance Difference' column when 'Match Status' is 'Break' and return only the **latest month's anomalies**.

    **Dataset Columns:**
    - 'As of Date': Month-end date
    - 'Company', 'Account', 'AU', 'Currency'
    - 'Primary Account', 'Secondary Account'
    - 'GL Balance', 'IHub Balance', 'Balance Difference'
    - 'Match Status': Indicates "Match" or "Break"
    - 'Comments': Contains observations (or) can be empty 

    ### **Instructions:**
    1. Consider all 'Break' records for each **Account-AU** combination.
    2. Analyze the 'Balance Difference' column for deviations from historical patterns
    3. If there is any  inconsistency, or deviation, set `Anomaly_Detected` to `"Yes"`. Otherwise, set it to `"No"`.
    4. Ensure that the `Anomaly_Detected` field is consistent with the description provided in the `Possible Cause` field.
    5. Provide a clear explanation for your decision in the `Possible Cause` field.
    6. Suggest actionable recommendations in the `Recommended Actions` field (limit: 255 characters).

    ### **Response Format:**
    # Provide the response in the following structured format:
    # anomalies: <Yes/No>  ('Yes' when there is no trend/pattern followed in Balance Difference, or if there is any Unusual spike/Inconsistencies or any deviations, Otherwise return No)
    # Category: <One of the predefined categories mentioned below> 
    # Possible Cause: <Brief explanation of the cause> 
    # Recommended Actions: <Specific and actionable recommendations>

    ### **Predefined Categories:**
    1. **Unposted journal entries**
    2. **Late adjustments**
    3. **Data sync delays between GL and iHub**
    4. **Incorrect mapping of transactions**
    5. **Missing or duplicate entries**
    6. **Foreign exchange rate differences**
    7. **System timing differences**

    ### **Example Responses:**

    #### Example 1 (Anomaly Detected):
    # For **Account: XYZ123, AU: 45678** (Latest Month: {latest_date.strftime('%Y-%m-%d')})
    Anomaly_Detected: Yes 
    Category: Incorrect mapping of transactions
    Possible Cause: Sudden unaccounted transaction or data entry error 
    Recommended Actions: Verify entries for April, check system logs

    #### Example 2 (No Anomaly Detected):
    # For **Account: ABC456, AU: 78910** (Latest Month: {latest_date.strftime('%Y-%m-%d')})
    Anomaly_Detected: No 
    Category: N/A 
    Possible Cause: Not provided 
    Recommended Actions: Not provided
    

    # ### **Data for Analysis (Historical Break Records)**
    
    # Append historical data for each Account-AU to the prompt

    """


    
    # prompt = f"""
    # You are an AI reconciliation report analyzer. The dataset contains historical reconciliation records for multiple Account-AU combinations.
    # Your task is to detect anomalies in the 'Balance Difference' column when 'Match Status' is 'Break' and return only the **latest month's anomalies**.

    # **Dataset Columns:**
    # - 'As of Date': Month-end date
    # - 'Company', 'Account', 'AU', 'Currency'
    # - 'Primary Account', 'Secondary Account'
    # - 'GL Balance', 'IHub Balance', 'Balance Difference'
    # - 'Match Status': Indicates "Match" or "Break"
    # - 'Comments': Contains observations (or) can be empty 

    # ### **Analysis Approach:**
    # 1. Consider all 'Break' records for each **Account-AU** combination.
    # 2. Analyze historical patterns in the 'Balance Difference' column.
    # 3. Detect **anomalies** based on deviations from trends.
    # 4. Return anomaly categorization **only for the latest month's data**.

    # ### **Example Output Format:**
    # For **Account: XYZ123, AU: 45678** (Latest Month: {latest_date.strftime('%Y-%m-%d')})

    # Anomaly_Detected: Yes
    # Category: Unusual Spike
    # Possible Cause: Sudden unaccounted transaction or data entry error
    # Recommended Actions: Verify entries for April, check system logs

    # ### **Data for Analysis (Historical Break Records)**

    # ### **Context**
    # As an AI reconciliation report analyzer, you have done the analysis and found anomalies. If the difference follows historical patterns, no anomaly is flagged. However, a deviation from the trend indicates a potential reconciliation issue.

    # ### **Request**
    # Given this data, categorize the anomaly into one of the following predefined categories:
    # 1. **Unposted journal entries**
    # 2. **Late adjustments**
    # 3. **Data sync delays between GL and iHub**
    # 4. **Incorrect mapping of transactions**
    # 5. **Missing or duplicate entries**
    # 6. **Foreign exchange rate differences**
    # 7. **System timing differences**

    # Then, respond with:
    # 1. **Anomaly Detected:** (Yes/No)
    # 1. **Category:** (Select one from the list)
    # 2. **Possible Cause**
    # 3. **Recommended Actions** (Make sure recommended actions are actionable and specific and the character limit is 255)
    # """

    # Append historical data for each Account-AU to the prompt
    for _, row in df_subset.iterrows():
        prompt += f"\n#### **Account: {row['Account']}, AU: {row['AU']}**\n"
        prompt += f"**As of Date:** {row['As of Date']}\n"
        prompt += f"**Balance Difference:** ${row['Balance Difference']}M\n"

    # Send the prompt to Gemini
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    gemini_reasoning = response.text
    print("Gemini Reasoning:", gemini_reasoning)
    # Parse Gemini Response
    anomaly_detected,category, possible_cause, recommended_actions = parse_gemini_response(gemini_reasoning)
    # Debugging: Print the SQL query and parameters
    print(f"Executing SQL: UPDATE \"{table_name}\" SET anomaly_detected = ?, category = ?, possible_cause = ?, recommended_actions = ? WHERE \"As of Date\" = ? AND Account = ? AND AU = ?")
    print(f"Parameters: {anomaly_detected},{category}, {possible_cause}, {recommended_actions}, {db_date}, {account}, {au}")



    # Debugging: Check if the row exists before the update
    cursor.execute(f'SELECT * FROM "{table_name}" WHERE "As of Date" = ? AND Account = ? AND AU = ?', (db_date, account, au))
    print("Row before update:", cursor.fetchone())

    # Execute the update query
    cursor.execute(
        f'UPDATE "{table_name}" SET anomaly_detected = ?, category = ?, possible_cause = ?, recommended_actions = ? WHERE "As of Date" = ? AND Account = ? AND AU = ?',
        (anomaly_detected, category, possible_cause, recommended_actions, db_date, account, au)
    )

    # Check the number of affected rows
    rows_affected = cursor.rowcount
    print(f"Rows affected: {rows_affected}")


    if rows_affected == 0:
        print(f"Warning: No rows were updated for Account: {account}, AU: {au}, Date: {latest_date_str}")
    
        print("anomaly_detected", anomaly_detected, "category", category, "possible_cause", possible_cause, "recommended_actions", recommended_actions, "latest_date_str", latest_date_str, "account", account, "au", au)
   


    report = f"🔍 **Gemini Analysis:**\n{gemini_reasoning}\n"

        

    #print(report)

# Commit and close connection after processing all accounts
# conn.commit()
# conn.close()
cursor.execute(f'SELECT * FROM "{table_name}" WHERE "As of Date" = ? AND Account = ? AND AU = ?', (db_date, account, au))
print("After Row after update:", cursor.fetchone())
# Commit the changes
try:
    conn.commit()
    print("Changes committed successfully.")
except Exception as e:
    print(f"Error during commit: {e}")
time.sleep(2)
conn.close()
