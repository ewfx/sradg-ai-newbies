import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

import chainlit as cl
from tools import sqlite_tool
from tools.feedback import handle_feedback
from agents.anomaly_action_agent import AnomalyAction
from agents.jira_comments_monitor_agent import JiraCommentsMonitorAgent
from agents import browser_agent
import requests
from agents.react_agent import ReactAgent
from prompts.personas import RECON_PERSONA
import pandas as pd
import sqlite3



commands = [
    {"id": "Recon", "icon": "bot", "description": "Assistant will analyze the reconciled data and detect anomalies"},
    {"id": "monitor", "icon": "bot", "description": "Monitor JIRA tickets and connect to core systems to update details"},
    {"id": "feedback", "icon": "bot", "description": "Take feedback on detected anomalies and update the system"},
]

# Initialize the AnomalyAction
anomaly_action = AnomalyAction(
    jira_url="https://sradghackathon.atlassian.net",
    jira_username="tejaswiavvaru@gmail.com",
    jira_api_token=os.getenv("JIRA_API_TOKEN"),
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    email_username="tejaswiavvaru@gmail.com",
    email_password=os.getenv("GMAIL_TOKEN")
)
# Initialize the JiraCommentsMonitorAgent
jira_monitor = JiraCommentsMonitorAgent(
    jira_url="https://sradghackathon.atlassian.net",
    jira_username="tejaswiavvaru@gmail.com",
    jira_api_token=os.getenv("JIRA_API_TOKEN")
)

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Reconciliation Report Analyzer",
            markdown_description="I am your Reconciliation Report Analyzer. I can help you analyze reconciliation data, detect anomalies, and provide actionable insights.",
            icon="https://picsum.photos/300",  # Replace with a relevant icon URL if needed
        ),
    ]

async def send_message(content:str):
     await cl.Message(content = content).send()

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # For demonstration, accept any credentials that reached here.
    # You could check these against your Flask session or a user database.
    if (password == "wf"+username):
        return cl.User(identifier=username, metadata={"role": "user","provider": "credentials"})
    return None

@cl.on_chat_start
async def on_chat_start():
    await cl.context.emitter.set_commands(commands)


    # Welcome message

    await cl.Message(
    content="👋 Hello! I'm your Reconciliation Report Analyzer. Here's how I can assist you:\n\n"
            "- Select a system to work with: **General_IHub** or **Catalyst**.\n"
            "- View last month's analyzed details for all accounts in the selected system.\n"
            "- Upload latest month-end details for analysis, and I'll detect anomalies, provide possible causes, and recommend actions.\n"
            "- I can also generate a plan of action to resolve errors if I can and seek your approval to take necessary action.\n"
            "- If you don't want to upload data, feel free to ask me for specific details about the selected system or general questions about banking and reconciliation.\n\n"
            "Let's get started! 🚀"
    ).send()


    action_message = await cl.AskActionMessage(
        content="Please select the system you want to work with:",
        actions=[
            cl.Action(name="General_IHub", payload={"value": "General_IHub"}, label="General_IHub"),
            cl.Action(name="Catalyst", payload={"value": "Catalyst"}, label="Catalyst"),
        ],
    ).send()

    # Extract the selected system
    if action_message and action_message.get("payload", {}).get("value"):
        system = action_message["payload"]["value"]
    else:
        await cl.Message(content="❌ No system selected. Please restart the chat to try again.").send()
        return

    # Initialize the SQLiteTool with the selected system
    sqlite_tool_loc = sqlite_tool.SQLiteTool(system)

    # Store the ReactAgent in the user session for later use

    await cl.Message(content=f"You selected the {system} system.").send()

    # Directly query the SQLite database and fetch results
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()

        # Execute the query
        query = f"""
                SELECT * FROM 
                (select * from General_IHub
                order by Account, AU, "As of Date" DESC) A
                group by A.Account, A.AU
            """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Check if rows are returned
        if rows:
            # Define the column names based on the table structure
            columns = [
                "As of Date", "Company", "Account", "AU", "Currency",
                "Primary Account", "Secondary Account", "GL Balance",
                "IHub Balance", "Balance Difference", "Match Status", "Comments",
                "anomaly_detected", "category", "possible_cause", "recommended_actions", "feedback_taken"
            ]
            # Format the results into a table
            table = pd.DataFrame(rows, columns=columns)
            await cl.Message(
                content=f"Here are the anomaly detection details for all Account/AU combinations to the latest:\n\n{table.to_markdown(index=False)}"
            ).send()
        else:
            await cl.Message(content="No data found for the selected system.").send()

        # Close the database connection
        conn.close()

    except Exception as e:
        await cl.Message(content=f"❌ Error while querying the database: {str(e)}").send()

    # Ask the user to upload the latest month-end details
    action_message = await cl.AskActionMessage(
    content="Do you want to proceed with anomaly detection for the new month-end data?",
    actions=[
        cl.Action(name="Proceed", payload={"value": "continue"}, label="✅ Yes, let's proceed!"),
        cl.Action(name="Later", payload={"value": "cancel"}, label="❌ No, maybe later."),
    ],
    ).send()
    
    if action_message and action_message.get("payload", {}).get("value") == "continue":
        files = None

        # Wait for the user to upload an Excel file
        while files == None:
            files = await cl.AskFileMessage(
                content="Alright, let's start by uploading the Excel file. Ensure it contains the required columns:\n\n"
                        "**Dataset Columns:**\n"
                        "- 'As of Date': Month-end date\n"
                        "- 'Company', 'Account', 'AU', 'Currency'\n"
                        "- 'Primary Account', 'Secondary Account'\n"
                        "- 'GL Balance', 'IHub Balance', 'Balance Difference'\n"
                        "- 'Match Status': Indicates 'Match' or 'Break'\n"
                        "- 'Comments': Contains observations (or can be empty)",
                accept=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
            ).send()

        excel_file = files[0]
        file_path = excel_file.path
        print(f"Uploaded file path: {file_path}")

        # Read the Excel file into a DataFrame
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
        except Exception as e:
            await cl.Message(content=f"❌ Error reading the Excel file: {str(e)}").send()
            return

        # Validate required columns
        required_columns = [
            'As of Date', 'Company', 'Account', 'AU', 'Currency',
            'Primary Account', 'Secondary Account', 'GL Balance',
            'IHub Balance', 'Balance Difference', 'Match Status', 'Comments'
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            await cl.Message(content=f"❌ The uploaded file is missing the following required columns: {', '.join(missing_columns)}").send()
            return
        # Extract unique combinations of 'As of Date', 'Account', and 'AU'
        unique_combinations = df[['As of Date', 'Account', 'AU']].drop_duplicates()
        
        # Connect to SQLite database
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()

        # Insert data into the table
        inserted_rows = 0
        duplicate_rows = 0
        for _, row in df.iterrows():
            as_of_date = row['As of Date']
            account = row['Account']
            au = row['AU']
            print("As of Date:", as_of_date, "Account:", account, "AU:", au)

            # Check if the combination already exists
            cursor.execute(
                f'SELECT COUNT(*) FROM {sqlite_tool_loc.table_name} WHERE "As of Date" = ? AND Account = ? AND AU = ?',
                (as_of_date, account, au)
            )
            exists = cursor.fetchone()[0]

            if exists:
                duplicate_rows += 1
                print("Duplicate row found. Skipping...")
            else:
                # Insert the row into the table
                cursor.execute(
                    f'INSERT INTO {sqlite_tool_loc.table_name} ("As of Date", Company, Account, AU, Currency, "Primary Account", "Secondary Account", "GL Balance", "IHub Balance", "Balance Difference", "Match Status", Comments) '
                    f'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        as_of_date, row['Company'], account, au, row['Currency'],
                        row['Primary Account'], row['Secondary Account'], row['GL Balance'],
                        row['IHub Balance'], row['Balance Difference'], row['Match Status'], row['Comments']
                    )
                )
                inserted_rows += 1

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Respond to the user
        if inserted_rows > 0:
            await cl.Message(
                content=f"✅ Data upload completed!\n\n"
                        f"- Rows inserted: {inserted_rows}\n"
                        f"- Duplicate rows skipped: {duplicate_rows}"
            ).send()
            # Notify the user that anomaly detection is starting
            await cl.Message(
                content="🔍 Detecting anomalies in the uploaded data. Please wait..."
            ).send()

            # Call the anomaly detector and process the results
            try:
                from anomaly_detector import detect_anomalies  # Import the anomaly detection function
                result = detect_anomalies("mydatabase.db", sqlite_tool_loc.table_name)  # Pass the database and table name
                if result=="Changes committed successfully.":
                    # Notify the user that anomaly detection is completed
                    await cl.Message(
                        content="✅ Anomaly detection completed! Fetching the updated results..."
                    ).send()

                    # Query the database for the updated combinations
                    conn = sqlite3.connect("mydatabase.db")
                    cursor = conn.cursor()

                    # Use the unique combinations extracted from the Excel file
                    query = f"""
                        SELECT "As of Date", Account, AU, anomaly_detected, category, possible_cause, recommended_actions, feedback_taken
                        FROM {sqlite_tool_loc.table_name}
                        WHERE ("As of Date", Account, AU) IN ({','.join(['(?, ?, ?)'] * len(unique_combinations))})
                    """

                    params = [item for _, row in unique_combinations.iterrows() for item in row]
                    
                    cursor.execute(query, params)
                    rows = cursor.fetchall()

                    # Format the results into a table
                    table = pd.DataFrame(rows, columns=["As of Date", "Account", "AU", "Anomaly Detected", "Category", "Possible Cause", "Recommended Actions","Feedback Taken"])
                    await cl.Message(
                        content=f"Here are the updated results:\n\n{table.to_markdown(index=False)}"
                    ).send()

                    conn.close()
                    action_message = await cl.AskActionMessage(
                        content="Do you me to see if I can take any action on detected Anomalies, If so click on 'Let's start Action sequence'",
                        actions=[
                            cl.Action(name="Proceed", payload={"value": "continue"}, label="✅ Let's start Action Sequnce"),
                            cl.Action(name="Later", payload={"value": "cancel"}, label="❌ No, maybe later."),
                    ],
                    ).send()
                    if action_message and action_message.get("payload", {}).get("value") == "continue":
                        # Filter data for anomalies
                        anomalies = table[table["Anomaly Detected"] == "Yes"]

                        # Process anomalies and create JIRA tickets
                        print("anomalies",anomalies)
                        ticket_numbers = await anomaly_action.handle_anomalies_and_create_tickets(anomalies)

                        # Notify the user about the ticket
                        if ticket_numbers:
                            await cl.Message(content=f"✅ JIRA tickets created successfully! Ticket Numbers: {', '.join(ticket_numbers)}").send()
                            await cl.Message(content="📧 Email notifications sent for JIRA tickets.").send()
                        else:
                            await cl.Message(content=f"❌ {result['message']}").send()
                    elif action_message and action_message.get("payload", {}).get("value") == "cancel":
                        await send_message(content="Okay, Then How may I help you today?")

            except Exception as e:
                await cl.Message(
                    content=f"❌ Error during anomaly detection: {str(e)}"
                ).send()
        else:
            await cl.Message(
                content=f"❌ No new rows were inserted. All rows were duplicates."
            ).send()

        
            
    elif action_message and action_message.get("payload", {}).get("value") == "cancel":
        await send_message(content="Okay, Then How may I help you today?")


@cl.on_message
async def on_message(message: cl.Message):
    if message.command == "monitor":
        plan_of_action = jira_monitor.monitor_recent_jira_comment(content=None)  # Pass content if needed
        if plan_of_action:
            await send_message(content =plan_of_action)

            action_message = await cl.AskActionMessage(
                content= "If you are satisfied by the generated plan then should we go ahead?",
                actions=[
                    cl.Action(name="Execute it", payload={"value": "continue"}, label="✅ Execute It!!"),
                    cl.Action(name="Cancel", payload={"value": "cancel"}, label="❌ Cancel"),
                ],
            ).send()

        else:
            await send_message(content="No plan of action generated.")

        if action_message and action_message.get("payload", {}).get("value") == "continue":
            await send_message(content = f"Executing the Automation task... Please wait")

            asyncio.run(browser_agent.browser_agent_task(plan_of_action))
            
            await send_message(content = f"Completed the task!!")
            
        elif action_message and action_message.get("payload", {}).get("value") == "cancel":
            await send_message(content="Plan execution cancelled.")
    elif message.command == "feedback":
        await handle_feedback()
    elif message.command == "Recon":
        query = message.content
        recon_agent = ReactAgent(persona=RECON_PERSONA, system="General_IHub")
        cl.user_session.set("react_agent", recon_agent)
        recon_agent = cl.user_session.get("react_agent")

        # Process with React agent
        try:
            final_response = await recon_agent.get_response(query)
            # Update the message with the final answer
            await cl.Message(content = final_response).send()
            # await msg.update()
        except Exception as e:
            error = f"Error processing your request: {str(e)}"
            await cl.Message(content=error).send()
    else:               
        query = message.content
        recon_agent = ReactAgent(persona=RECON_PERSONA, system="General_IHub")
        cl.user_session.set("react_agent", recon_agent)
        recon_agent = cl.user_session.get("react_agent")

        # Process with React agent
        try:
            final_response = await recon_agent.get_response(query)
            # Update the message with the final answer
            await cl.Message(content = final_response).send()
            # await msg.update()
        except Exception as e:
            error = f"Error processing your request: {str(e)}"
            await cl.Message(content=error).send()



    

