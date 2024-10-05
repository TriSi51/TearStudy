from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model


def visualization_agent_factory(state: dict) -> OpenAIAgent:
    def create_chart(analysis_result: str) -> str:
        # Simulate creating a chart
        print(f"Creating chart for: {analysis_result}")
        chart = f"Chart of {analysis_result}"
        state["chart"] = chart
        return chart

    def generate_interactive_visual(analysis_result: str) -> str:
        # Simulate generating an interactive visual
        print(f"Generating interactive visualization for: {analysis_result}")
        interactive_visual = f"Interactive visual of {analysis_result}"
        state["interactive_visual"] = interactive_visual
        return interactive_visual

    tools = [
        FunctionTool.from_defaults(fn=create_chart),
        FunctionTool.from_defaults(fn=generate_interactive_visual),
    ]
    
    system_prompt = f"""
        You are a visualization agent responsible for generating charts and visual representations of analysis results.
        Current user state: {pprint.pformat(state, indent=4)}
    """
    
    return OpenAIAgent.from_tools(tools, llm=load_model(), system_prompt=system_prompt)
