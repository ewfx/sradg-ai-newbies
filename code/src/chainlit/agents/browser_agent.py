import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from browser_use import Agent

llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))


async def browser_agent_task(query:str):
    agent = Agent(
        task=query,
        llm = llm,
        page_extraction_llm=llm
    )
    result = await agent.run()
    print(result)


