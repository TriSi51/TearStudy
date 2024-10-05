
from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model


def user_interaction_agent_factory(state: dict) -> OpenAIAgent:
    # Dummy function to simulate user interaction
    def ask_user(question: str) -> str:
        print(f"User Interaction Agent: {question}")
        return input("User: ").strip()

    def handle_user_input(user_input: str) -> str:
        print(f"Processing user input: {user_input}")
        state["user_query"] = user_input
        return f"Received user input: {user_input}"

    tools = [
        FunctionTool.from_defaults(fn=ask_user),
        FunctionTool.from_defaults(fn=handle_user_input),
    ]
    
    system_prompt = f"""
        You are the User Interaction Agent. Your task is to interact with the user by asking questions,
        receiving input, and relaying it to the Orchestrator Agent or other agents. You also guide the user
        through their tasks based on their requests.
        
        Current user state: {pprint.pformat(state, indent=4)}
    """
    
    return OpenAIAgent.from_tools(tools, llm=load_model(), system_prompt=system_prompt)
