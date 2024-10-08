from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model

import pprint
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent

class ResearchAssistantAgent:
    def __init__(self, state: dict, llm: any):
        self.state = state
        self.llm = llm
        self.identifier="Research Agent"

    def get_identifier(self)->str:
        return self.identifier
    def find_papers(self, topic: str) -> list:
        """
        Simulate finding papers on a given topic.
        """
        print(f"Searching for papers on {topic}")
        papers = [f"Paper {i+1} on {topic}" for i in range(3)]
        self.state["papers"] = papers
        return papers

    def summarize_research(self, papers: list) -> str:
        """
        Simulate summarizing a list of papers.
        """
        print(f"Summarizing {len(papers)} papers")
        summary = f"Summary of {len(papers)} papers: {'; '.join(papers)}"
        self.state["summary"] = summary
        return summary

    def organize_materials(self, materials: list) -> str:
        """
        Organize materials into categories.
        """
        print(f"Organizing materials: {materials}")
        organized = {f"Category {i+1}": materials[i] for i in range(len(materials))}
        self.state["organized_materials"] = organized
        return f"Materials organized into categories: {organized}"

    def get_tools(self) -> list:
        """
        Returns the tools for the research assistant agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.find_papers),
            FunctionTool.from_defaults(fn=self.summarize_research),
            FunctionTool.from_defaults(fn=self.organize_materials),
        ]

    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for the research assistant agent.
        """
        return f"""
        You are a research assistant tasked with finding relevant research papers and materials for a given topic.
        You also summarize the findings and organize them.
        Current user state: {pprint.pformat(self.state, indent=4)}
        """

    def create_agent(self) -> OpenAIAgent:
        """
        Create and return an OpenAIAgent using the LLM and tools.
        """
        return OpenAIAgent.from_tools(self.get_tools(), llm=self.llm, system_prompt=self.get_system_prompt())

