import requests

class JiraHandler:
    def __init__(self, jira_url, jira_username, jira_api_token):
        self.jira_url = jira_url
        self.auth = (jira_username, jira_api_token)

    def create_ticket(self, summary, description, priority):
        """Create a JIRA ticket."""
        url = f"{self.jira_url}/rest/api/2/issue"
        headers = {"Content-Type": "application/json"}
        data = {
            "fields": {
                "project": {"key": "SMAR"},  # Replace with your JIRA project key
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Task"},
                "priority": {"name": priority},
            }
        }

        response = requests.post(url, json=data, auth=self.auth, headers=headers)
        if response.status_code == 201:
            ticket_key = response.json()["key"]
            return ticket_key
        else:
            raise Exception(f"Failed to create JIRA ticket: {response.text}")