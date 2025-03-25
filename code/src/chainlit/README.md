# AI-Impact-SmartOnBoard --> Chainlit Setup

1. Create a .env file and fill in credential values - 
    GENAI_API_KEY = ""
    CHAINLIT_AUTH_SECRET = "" (run "chainlit create-secret" to generate)
    MONGODB_URI= ""

2. Create a virtual environment (optional but recommended):
    python -m venv venv
    On Windows use `venv\Scripts\activate`

3. Do "pip install -r requirement_chainlit.txt"

4. Running the Application: To run the FastAPI application, use the following command:
    chainlit run app.py -w --port 9000

5. The application will be accessible at `http://127.0.0.1:9000`.

6. For login: Username : can be anything of choice
                passowrd: wf+{username}
