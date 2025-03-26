import sqlite3
import pandas as pd
import chainlit as cl

async def handle_feedback():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()

        # Query the records where 'anomaly_detected' is not NULL and 'feedback_taken' is 'No'
        query = """
            SELECT rowid, "As of Date", Account, AU, anomaly_detected
            FROM General_IHub
            WHERE anomaly_detected IS NOT NULL AND feedback_taken = 'No'
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Check if there are records to display
        if not rows:
            await cl.Message(content="No records found for feedback.").send()
            return

        # Format the results into a table
        columns = ["Row ID", "As of Date", "Account", "AU", "Anomaly Detected"]
        table = pd.DataFrame(rows, columns=columns)

        # Display the table to the user
        await cl.Message(
            content=f"Here are the records requiring feedback:\n\n{table.to_markdown(index=False)}"
        ).send()

        # Iterate through each row and display buttons for feedback
        for row in rows:
            row_id, as_of_date, account, au, anomaly_detected = row
            feedback_message = await cl.AskActionMessage(
                content=(
                    f"Record:\n"
                    f"- As of Date: {as_of_date}\n"
                    f"- Account: {account}\n"
                    f"- AU: {au}\n"
                    f"- Anomaly Detected: {anomaly_detected}\n\n"
                    f"Please provide your feedback for this record."
                ),
                actions=[
                    cl.Action(name="Detected Right", payload={"action": "detected_right", "row_id": row_id}, label="✅ Detected Right"),
                    cl.Action(
                        name="False Positive" if anomaly_detected == "Yes" else "False Negative",
                        payload={"action": "false_positive" if anomaly_detected == "Yes" else "false_negative", "row_id": row_id},
                        label="❌ False Positive" if anomaly_detected == "Yes" else "❌ False Negative"
                    ),
                ],
            ).send()

            # Process the user's feedback
            if feedback_message and feedback_message.get("payload"):
                action = feedback_message["payload"]["action"]
                row_id = feedback_message["payload"]["row_id"]

                if action == "false_positive":
                    # Update 'anomaly_detected' to 'No' and 'feedback_taken' to 'Yes'
                    cursor.execute("""
                        UPDATE General_IHub
                        SET anomaly_detected = 'No', feedback_taken = 'Yes'
                        WHERE rowid = ?
                    """, (row_id,))
                elif action == "false_negative":
                    # Update 'anomaly_detected' to 'Yes' and 'feedback_taken' to 'Yes'
                    cursor.execute("""
                        UPDATE General_IHub
                        SET anomaly_detected = 'Yes', feedback_taken = 'Yes'
                        WHERE rowid = ?
                    """, (row_id,))
                elif action == "detected_right":
                    # Only update 'feedback_taken' to 'Yes'
                    cursor.execute("""
                        UPDATE General_IHub
                        SET feedback_taken = 'Yes'
                        WHERE rowid = ?
                    """, (row_id,))

                # Commit the changes to the database
                conn.commit()

                # Notify the user about the update
                await cl.Message(content=f"Feedback recorded for Row ID: {row_id}.").send()

        # Close the database connection
        conn.close()

    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()

