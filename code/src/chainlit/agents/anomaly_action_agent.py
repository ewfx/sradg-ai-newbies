import os
from tools.jira_handler import JiraHandler
from tools.email_handler import EmailHandler
import google.generativeai as genai  # Google's Gemini SDK

class AnomalyAction:
    def __init__(self, jira_url, jira_username, jira_api_token, smtp_server, smtp_port, email_username, email_password):
        self.jira_handler = JiraHandler(jira_url, jira_username, jira_api_token)
        self.email_handler = EmailHandler(smtp_server, smtp_port, email_username, email_password)
        detector_api_key = os.getenv("GEMINI_ACTION_API_KEY")
        genai.configure(api_key=detector_api_key)
        self.llm = genai.GenerativeModel("gemini-1.5-pro")


    async def handle_anomalies_and_create_tickets(self, anomalies):
        """Process anomalies using Gemini-1.5pro, create JIRA tickets, and send emails for high-priority tickets."""


        prompt_template = """
        You are an AI assistant helping to process anomalies in reconciliation data. 
        Analyze the following anomaly and provide the priority, ticket summary, and Description:

        **Anomaly Details:**
        - Category: {category}
        - Possible Cause: {possible_cause}
        - Recommended Actions: {recommended_actions}

        **Response Format:**
        Priority: <High/Medium/Low>
        Summary: <Short summary of the issue and append {Account} and {AU} for reference>
        Description: <Detailed description of the issue and append {category}, {possible_cause} and {recommended_actions}>
        """
        # List to store all ticket numbers
        ticket_numbers = []

        for _, row in anomalies.iterrows():
            if row["Anomaly Detected"] == "Yes":
                # Format the prompt with anomaly details
                prompt = prompt_template.format(
                    category=row["Category"],
                    possible_cause=row["Possible Cause"],
                    recommended_actions=row["Recommended Actions"],
                    Account=row["Account"],
                    AU=row["AU"]
                )

                # Use Gemini-1.5pro to analyze the anomaly and decide on ticket details
                response = self.llm.generate_content(prompt)
                llm_output = response.text.strip()

                # Parse the LLM response
                priority = self._extract_field(llm_output, "Priority")
                summary = self._extract_field(llm_output, "Summary")
                description = self._extract_field(llm_output, "Description")

                # Create JIRA ticket
                ticket_number = self.jira_handler.create_ticket(summary, description, priority)
                ticket_numbers.append(ticket_number)  # Add the ticket number to the list

                # Send email for high-priority tickets
                #if priority == "High":
                subject = f"{priority} Priority JIRA Ticket Created: {ticket_number}"
                body = (
                    f"JIRA ticket has been created:\n\n"
                    f"Summary: {summary}\n"
                    f"Description: {description}\n"
                    f"Ticket Number: {ticket_number}"
                )
                self.email_handler.send_email(to_email="tejaswiavvaru@gmail.com", subject=subject, body=body)

                # Return the ticket number for user notification
        return ticket_numbers

    def _extract_field(self, text, field_name):
        """Extract a specific field from the LLM response."""
        import re
        match = re.search(rf"{field_name}:\s*(.+)", text)
        return match.group(1).strip() if match else None