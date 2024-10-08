from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model


class VisualizationAgent:
    def __init__(self, state: dict, llm: any):
        self.state = state
        self.llm = llm
        self.identifier="Visualization Agent"
    def get_identifier(self)->str:
        return self.identifier
    def create_chart(self, analysis_result: str) -> str:
        """
        Simulate creating a chart based on the analysis result.
        """
        print(f"Creating chart for: {analysis_result}")
        chart = f"Chart of {analysis_result}"
        self.state["chart"] = chart
        return chart

    def generate_interactive_visual(self, analysis_result: str) -> str:
        """
        Simulate generating an interactive visual based on the analysis result.
        """
        print(f"Generating interactive visualization for: {analysis_result}")
        interactive_visual = f"Interactive visual of {analysis_result}"
        self.state["interactive_visual"] = interactive_visual
        return interactive_visual

    def get_tools(self) -> list:
        """
        Returns the tools for the visualization agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.create_chart),
            FunctionTool.from_defaults(fn=self.generate_interactive_visual),
        ]

    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for the visualization agent.
        """
        return f"""
        You are a visualization agent responsible for generating charts and visual representations of analysis results.
        Current user state: {pprint.pformat(self.state, indent=4)}
        """

    def create_agent(self) -> OpenAIAgent:
        """
        Create and return an OpenAIAgent using the LLM and tools.
        """
        return OpenAIAgent.from_tools(self.get_tools(), llm=self.llm, system_prompt=self.get_system_prompt())