from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model

def research_assistant_agent_factory(state: dict) -> OpenAIAgent:
    def find_papers(topic: str) -> List[str]:
        # Simulate finding papers on a topic
        print(f"Searching for papers on {topic}")
        papers = [f"Paper {i+1} on {topic}" for i in range(3)]
        state["papers"] = papers
        return papers

    def summarize_research(papers: List[str]) -> str:
        # Simulate summarizing papers
        print(f"Summarizing {len(papers)} papers")
        summary = f"Summary of {len(papers)} papers: {'; '.join(papers)}"
        state["summary"] = summary
        return summary

    def organize_materials(materials: List[str]) -> str:
        # Organize materials into categories (folders)
        print(f"Organizing materials: {materials}")
        organized = {f"Category {i+1}": materials[i] for i in range(len(materials))}
        state["organized_materials"] = organized
        return f"Materials organized into categories: {organized}"

    tools = [
        FunctionTool.from_defaults(fn=find_papers),
        FunctionTool.from_defaults(fn=summarize_research),
        FunctionTool.from_defaults(fn=organize_materials),
    ]
    
    system_prompt = f"""
        You are a research assistant tasked with finding relevant research papers and materials for a given topic.
        You also summarize the findings and organize them.
        Current user state: {pprint.pformat(state, indent=4)}
    """
    
    return OpenAIAgent.from_tools(tools, llm=load_model(), system_prompt=system_prompt)
