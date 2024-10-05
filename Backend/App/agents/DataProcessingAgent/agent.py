from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model


def data_processing_agent_factory(state: dict) -> OpenAIAgent:
    def clean_data(data: str) -> str:
        # Simulate cleaning data
        print(f"Cleaning data: {data}")
        cleaned_data = data.replace("NA", "0")  # Example of cleaning missing values
        state["cleaned_data"] = cleaned_data
        return f"Cleaned data: {cleaned_data}"

    def normalize_data(data: str) -> str:
        # Simulate normalizing data
        print(f"Normalizing data: {data}")
        normalized_data = data.lower()  # Example normalization
        state["normalized_data"] = normalized_data
        return f"Normalized data: {normalized_data}"

    def handle_missing_values(data: str) -> str:
        # Simulate handling missing values
        print(f"Handling missing values in: {data}")
        filled_data = data.replace("missing", "filled")
        state["filled_data"] = filled_data
        return f"Data with missing values handled: {filled_data}"

    tools = [
        FunctionTool.from_defaults(fn=clean_data),
        FunctionTool.from_defaults(fn=normalize_data),
        FunctionTool.from_defaults(fn=handle_missing_values),
    ]
    
    system_prompt = f"""
        You are a data processing agent responsible for cleaning and preprocessing raw data.
        You clean, normalize, and handle missing data before analysis.
        Current user state: {pprint.pformat(state, indent=4)}
    """
    
    return OpenAIAgent.from_tools(tools, llm=load_model(), system_prompt=system_prompt)
