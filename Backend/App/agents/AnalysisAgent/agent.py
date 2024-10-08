from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model

class AnalysisAgent:
    def __init__(self, state: dict, llm: any):
        self.state = state
        self.llm = llm
        self.identifier="Analysis Agent"
    def get_identifier(self)->str:
        return self.identifier

    def perform_analysis(self, data: str) -> str:
        """
        Simulate performing statistical analysis on the provided data.
        """
        print(f"Performing analysis on: {data}")
        analysis_result = f"Analysis result of {data}"
        self.state["analysis_result"] = analysis_result
        return analysis_result


    def get_tools(self) -> list:
        """
        Returns the tools for the analysis agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.perform_analysis),
        ]

    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for the analysis agent.
        """
        return f"""
        You are an analysis agent performing statistical or machine learning analysis on processed data.
        You also explain the results of your analysis to the user in understandable terms.
        """

    def create_agent(self) -> OpenAIAgent:
        """
        Create and return an OpenAIAgent using the LLM and tools.
        """
        return OpenAIAgent.from_tools(self.get_tools(), llm=self.llm, system_prompt=self.get_system_prompt())
