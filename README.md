# 🚀 Project Name 
Smarter Reconciliation and Anomaly Detection using GenAI

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
### Problem Statement:
Implement an anomaly detection system within the reconciliation process by leveraging historical data to identify patterns, trends, and expected ranges. The system should be able to:
   1. Automatically detect data anomalies by comparing real-time data against historical baselines.
   2. Provide insights into potential root causes of detected anomalies.
   3. Integrate with existing reconciliation tools to streamline the anomaly identification process.
   4. Reduce manual effort and minimize human error in anomaly detection.
### Proposed Solution: 
We have divided the solution to 4 workflows
   1. Anomaly Detection and Handling
   2. Agentic Action through JIRA monitoring and integrating with core reconciliation systems
   3. Feedback loop to identify if the anomalies detected are right (or) False Positive (or) False Negative
   4. User queries through chain-of-thought ReAct processing


## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](#) (if applicable)  
   Please see video attached in artifacts
🖼️ Screenshots:
   Please see ppt attached in artifacts

## 💡 Inspiration
What inspired you to create this project? Describe the problem you're solving.
   Smarter Reconciliation and Anomaly Detection using GenAI

## ⚙️ What It Does
Explain the key features and functionalities of your project.
## Features

- **Reconciliation Data Processing**: Upload and process financial reconciliation data from Excel files.
- **Anomaly Detection**: Detect anomalies in reconciliation data and provide possible causes and recommended actions.
- **Feedback Workflow**: Collect user feedback on detected anomalies and update the database accordingly.
- **JIRA Integration**: Automatically create JIRA tickets for anomalies and send email notifications.
- **Generative AI Integration**: Use GenAI models like Gemini for extracting insights and generating action plans.
- **SQLite Database**: Store and manage reconciliation data efficiently.
   

## 🛠️ How We Built It
Briefly outline the technologies, frameworks, and tools used in development.
1. Database refresh with historical data : insert.py
2. Chainlit key component: app.py
3. Anomaly detection: anomaly_detector.py
4. JIRA and Email creation: anomaly_action_agent.py (with tools email_handler.py and jira_handler.py)
5. JIRA monitor and update core system IHub: 
    jira_comments_monitor_agent.py
    browser_agent.py
    IHub_system.html
6. Feedback: feedback.py
7. System and User conversations: react_agent.py
8. Remaining Tools:
    sqlite_tool.py
    web_search_tool.py
    wiki_search.py
9. LLM's :
   gemini-1.5-pro
   gemini-2.0-flas
   

## 🚧 Challenges We Faced
Describe the major technical or non-technical challenges your team encountered.

## 🏃 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/sradg-ai-newbies.git
   cd sradg-ai-newbies

2. Create and activate a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
    pip install -r requirements.txt

4. Set up environment variables:

    Create a .env file in the root directory.
    Add the following variables
    yourJIRA_API_TOKEN=<-jira-api-token>
    JIRA_BASE_URL=<your-jira-base-url>
    GEMINI_API_KEY = <your Gemini token>
    GMAIL_TOKEN = <your-Gmail-token>

## Usage
1. Start Flask API
    python -m flask_app.py

2. Start the Chainlit application
    chainlit run app.py

3. Upload new reconciliation data via the chatbot interface to detect the anomalies.

4. Review detected anomalies and check the JIRA tickes and email sent on the anomalies

5. Log comments with considerable actions to be taken against JIRA ticket

6. /monitor command on chainlit parses the comment and connects to IHub core system to update the balances and then reflects on database

7. /feedback to provide feedback.

8. Ask any general question or any balance inquiries of the IHub reconciliation system

## 🏗️ Tech Stack
- 🔹 Frontend: Chainlit/html
- 🔹 Backend: Python/flaskApi
- 🔹 Database: SQLite

## 👥 Team
- **Sai Tejaswi Avvaru** - [https://github.com/tejuavvaru](#) | [LinkedIn](#)
- **Shobha Rani Ganta** - [GitHub](#) | [LinkedIn](#)
- **Vijay Potturi** - [GitHub](#) | [LinkedIn](#)
- **Rohan Bodhi Kadam** - [GitHub](#) | [LinkedIn](#)
- **Nagesh Potharaju** - [GitHub](#) | [LinkedIn](#)