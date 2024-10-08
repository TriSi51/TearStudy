
from enum import Enum
from typing import List,Dict
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model
from .prompt import *


class UserInteractionAgent:
    def __init__(self, state: dict, llm: any,response_from_agents: List[Dict]):
        self.state = state
        self.llm = llm
        self.identifier="User Interaction Agent"
        self.response_from_agents=response_from_agents


    def get_identifier(self)->str:
        return self.identifier


    def answer_user(self) -> str:
        pass

    def get_tools(self) -> list:
        """
        Returns the tools for the user interaction agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.handle_user_input),
        ]

    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for the user interaction agent.
        """
        return f"""
        You are the User Interaction Agent. Your task is to interact with the user.
        
        
        """

    def create_agent(self) -> OpenAIAgent:
        """
        Create and return an OpenAIAgent using the LLM and tools.
        """
        return OpenAIAgent.from_tools(self.get_tools(), llm=self.llm, system_prompt=self.get_system_prompt())
