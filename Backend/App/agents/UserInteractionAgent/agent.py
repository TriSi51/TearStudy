
from enum import Enum
from typing import List,Dict
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.base.response.schema import Response
import json
from ...models import load_model
from .prompt import *


class UserInteractionAgent:
    def __init__(self, state: dict, llm: any,agent_responses: Dict):
        self.state = state
        self.llm = llm
        self.identifier="User Interaction Agent"
        if agent_responses:
            self.agent_responses=json.dumps(agent_responses, indent=4)
            
        else:
            self.agent_responses="None"

    def get_identifier(self):
        return self.identifier
    
    def interact_with_user(self, query_str: str):

        response = self._llm.predict(
            USER_INTERACTION_PROMPT,
            query_str=query_str,
            agents_output= self.agent_responses,
            instruction_str=USER_INTERACTION_INSTRUCTION,
            
        )


        return Response(response=response)

    def get_tools(self) -> list:
        """
        Returns the tools for the user interaction agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.interact_with_user),
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
