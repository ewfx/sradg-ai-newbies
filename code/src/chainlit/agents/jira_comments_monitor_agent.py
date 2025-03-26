import requests
import google.generativeai as genai  # Google's Gemini SDK
import json
import os

class JiraCommentsMonitorAgent:
    def __init__(self, jira_url, jira_username, jira_api_token):
        self.jira_url = jira_url
        self.jira_username = jira_username
        self.jira_api_token = jira_api_token
        detector_api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=detector_api_key)
        self.llm = genai.GenerativeModel("gemini-1.5-pro")

    def get_recent_comments(self):
        """
        Fetch the most recent comments for all issues in JIRA.
        """
        url = f"{self.jira_url}/rest/api/2/search"
        headers = {
            "Content-Type": "application/json",
        }
        auth = (self.jira_username, self.jira_api_token)
        query = {
            "jql": "ORDER BY updated DESC",
            "fields": ["comment", "key"],
            "maxResults": 50
        }

        response = requests.get(url, headers=headers, auth=auth, params=query)
        if response.status_code == 200:
            issues = response.json().get("issues", [])
            recent_comments = []
            for issue in issues:
                key = issue.get("key")
                comments = issue.get("fields", {}).get("comment", {}).get("comments", [])
                if comments:
                    recent_comments.append({
                        "issue_key": key,
                        "comment": comments[-1]["body"]  # Get the most recent comment
                    })
            return recent_comments
        else:
            raise Exception(f"Failed to fetch JIRA comments: {response.status_code} {response.text}")

    def process_comment_with_llm(self, comment):
        """
        Use Gemini LLM to extract details and generate a plan of action from the comment.
        """
        prompt = (
            f"You are an intelligent assistant. Analyze the following JIRA comment and perform the following tasks:\n"
            f"1. Extract the following details:\n"
            f"   - 'As of Date'\n"
            f"   - 'Account'\n"
            f"   - 'AU'\n"
            f"   - 'Balance'\n"
            f"2. If any details are missing, ask for clarification.\n"
            f"3. Based on the extracted details, generate a step-by-step plan of action to update the balance on a website.\n"
            f"   Example plan:\n"
            f"   - Go to http://127.0.0.1:5000 website.\n"
            f"   - Match the row with the extracted details.\n"
            f"   - Update the balance field.\n"
            f"   - Submit the changes.\n\n"
            f"Comment: {comment}\n\n"
            f"Respond with the extracted details and the plan of action. Only include the formatted step-by-step plan of action in response"
        )
        
        response = self.llm.generate_content(prompt)
        # Extract the "Plan of Action" section from the response
        try:
            # Parse the response to find the "Plan of Action" section
            candidates = response.candidates 
            if not candidates:
                return "No candidates found in the LLM response."

            # Extract the first candidate's content
            response_text = candidates[0].content.parts[0].text

            # Ensure response_text is a string
            if not isinstance(response_text, str):
                raise ValueError("Response text is not a valid string.")

            # Find and extract the "Plan of Action" section
            plan_start = response_text.find("Plan of Action:")
            if plan_start != -1:
                plan_of_action = response_text[plan_start + len("Plan of Action:"):].strip()
                return plan_of_action
            else:
                return "Plan of action could not be extracted from the response."
        except Exception as e:
            return f"Error while parsing LLM response: {str(e)}"
            

    def monitor_recent_jira_comment(self, content):
        """
        Main function to monitor JIRA comments and generate a plan of action.
        """
        try:
            recent_comments = self.get_recent_comments()
            for comment_data in recent_comments:
                issue_key = comment_data["issue_key"]
                comment = comment_data["comment"]

                # Process the comment using Gemini LLM
                llm_response = self.process_comment_with_llm(comment)

                # Return the LLM's response (details and plan of action)
                return f"Issue: {issue_key}\n{llm_response}"
        except Exception as e:
            return f"Error: {str(e)}"