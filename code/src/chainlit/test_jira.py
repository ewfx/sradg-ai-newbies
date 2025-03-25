from tools.jira_handler import JiraHandler
import os 
from dotenv import load_dotenv
load_dotenv()


jira_handler = JiraHandler(
    jira_url="https://sradghackathon.atlassian.net",
    jira_username="tejaswiavvaru@gmail.com",
    jira_api_token=os.getenv("JIRA_API_TOKEN"),
)

ticket = jira_handler.create_ticket(
    summary="Test Ticket",
    description="This is a test ticket created via the JIRA API.",
    priority="Medium"
)

print(f"JIRA Ticket Created: {ticket}")