from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
import chainlit as cl
from typing import Dict, Any, List
import uuid

from agents.base_agent import BaseAgent
# from tools.mongodb_tool import MongoDBTool
from tools.web_search_tool import FinanceWebSearchTool
from tools.wiki_search import WikipediaSearchTool
from tools.sqlite_tool import SQLiteTool

class ChainlitStepsCallbackHandler(BaseCallbackHandler):
    """Callback handler to create Chainlit Steps for agent actions"""
    
    def __init__(self):
        self.steps = {}
        self.current_step_id = None
    
    def on_agent_action(self, action, **kwargs):
        """Called when agent takes an action - creates a new step"""
        tool = action.tool
        tool_input = action.tool_input
        
        # Create a unique ID for this step
        step_id = str(uuid.uuid4())
        self.current_step_id = step_id
        
        # Create a new step for this tool use
        step = cl.Step(
            name=tool,
            type="tool", 
            # content=f"**Input**: {tool_input}",
            show_input=True
        )
        
        # Store step reference
        self.steps[step_id] = step
        
        # Send the step to UI
        cl.run_sync(step.send())
    
    def on_tool_end(self, output, **kwargs):
        """Called when a tool finishes running - updates the step with output"""
        if self.current_step_id and self.current_step_id in self.steps:
            step = self.steps[self.current_step_id]
            step.output = str(output)
            cl.run_sync(step.update())
    
    def on_text(self, text, **kwargs):
        """Called when the agent produces intermediate reasoning text"""
        # This can be used to capture thought steps if needed
        pass
    
    def on_agent_finish(self, output, **kwargs):
        """Called when agent finishes its execution"""
        # We could create a final step here if desired
        pass


class ReactAgent(BaseAgent):
    """React agent with specialized tools and visible chain of thought using Chainlit Steps"""
    
    def __init__(
        self, 
        persona: str,
        system: str,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.2
    ):
        super().__init__(persona, model_name, temperature)
        self.tools = [
            # MongoDBTool(),
            FinanceWebSearchTool(),
            WikipediaSearchTool(),
            SQLiteTool(system)
        ]
        self.setup_agent()
    
    def setup_agent(self):
        # For ReAct agent, we need to use a specific template
        # This is the standard ReAct template with our persona added
        template = f"""
        {self.persona}

        Answer the following questions as best you can. You have access to the following tools:

        {{tools}}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of {{tool_names}}
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        The SQLiteTool can be used to query and update the local SQLite database. Use it for tasks like retrieving data or updating records.
        
        Begin!

        Question: {{input}}
        {{agent_scratchpad}}
        """

        prompt = PromptTemplate.from_template(template)
        
        agent = create_react_agent(
            self.llm,
            self.tools,
            prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.memory
        )
    
    async def get_response(self, message: str) -> str:
        """Process a message and return a response using the React agent with Steps visualization"""
        task_list = cl.TaskList()
        task_list.status = "Running..."
        # Create a new task element to represent the overall operation
        task = cl.Task(
            title="🔍 Analyzing with ReAct Agent",
            status=cl.TaskStatus.RUNNING
        )
        await task_list.add_task(task)
        await task_list.send()
        
        # Set up our callback handler to create Steps
        callback_handler = cl.LangchainCallbackHandler(to_keep=["retriever", "agent", "chain", "tool"], to_ignore=["RunnableSequence",
        "RunnableParallel",
        "RunnableAssign",
        "RunnableLambda",
        "<lambda>", "llm"])
        
        try:
            # Run agent with callbacks for Steps
            response = await self.agent_executor.ainvoke(
                {"input": message},
                {"callbacks": [callback_handler]}
            )
            
            # Update task status when complete
            task.status = cl.TaskStatus.DONE
            task_list.status = "Done"
            await task_list.send()
            
            return response["output"]
            
        except Exception as e:
            # Mark task as failed if there's an error
            task.status = cl.TaskStatus.FAILED
            task.output = str(e)
            await task.update()
            raise e
    
    def update_persona(self, persona: str):
        """Update the agent's persona"""
        super().update_persona(persona)
        self.setup_agent()  # Recreate the agent with the new persona