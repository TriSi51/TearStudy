from enum import Enum
from typing import List,Dict
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model
from llama_index.core.base.response.schema import Response


import pprint
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
import logging
from ...tools.output_parser import InstructionParser

from .prompt import *
class DataProcessingAgent:
    """
    A class-based data processing agent that handles cleaning, normalization, and missing values in the data.
    The agent uses LLM-generated tools for these tasks.
    """

    def __init__(self, state: dict, llm: any,input_data:List[Dict]):
        self.state = state
        self._llm = llm
        self._instruction_parser= InstructionParser(input_data)
        self._synthesize_response= True


    def clean_data(self, data: str) -> str:
        """
        Simulate cleaning data by replacing 'NA' values.
        """
        print(f"Cleaning data: {data}")
        cleaned_data = data.replace("NA", "0")  # Example of cleaning missing values
        self.state["cleaned_data"] = cleaned_data
        return f"Cleaned data: {cleaned_data}"
    def generate_and_run_data_preprocessing_code(self, query_str: str) -> dict:
        """Generate code for a given query and execute the code to preprocessing the dataframe."""

        response = self._llm.predict(
            DEFAULT_DATA_PREPROCESSING_PROMPT,
            query_str=query_str,
            instruction_str=DEFAULT_DATA_PREPROCESSING_INSTRUCTION,
        )

        raw_output = self._instruction_parser.parse(response)

        response_metadata = {
            "instruction_str": response,
            "raw_output": raw_output,
        }
        
        if self._synthesize_response:
            response_str = str(
                self._llm.predict(
                    DEFAULT_RESPONSE_SYNTHESIS_PROMPT,
                    query_str=query_str,
                    pandas_instructions=response,
                    pandas_output=raw_output,
                )
            )
        else:
            response_str = str(raw_output)

        return Response(response=response_str, metadata=response_metadata)
    def normalize_data(self, data: str) -> str:
        """
        Simulate normalizing data.
        """
        print(f"Normalizing data: {data}")
        normalized_data = data.lower()  # Example normalization
        self.state["normalized_data"] = normalized_data
        return f"Normalized data: {normalized_data}"

    def handle_missing_values(self, data: str) -> str:
        """
        Simulate handling missing values by replacing them.
        """
        print(f"Handling missing values in: {data}")
        filled_data = data.replace("missing", "filled")
        self.state["filled_data"] = filled_data
        return f"Data with missing values handled: {filled_data}"

    def get_tools(self):
        """
        Return the tools required for data processing.
        """
        tools = [
            FunctionTool.from_defaults(fn=self.clean_data),
            FunctionTool.from_defaults(fn=self.normalize_data),
            FunctionTool.from_defaults(fn=self.handle_missing_values),
        ]
        return tools

    def get_agent(self):
        """
        Create and return the OpenAIAgent with the tools and system prompt.
        """
        system_prompt = f"""
            You are a data processing agent responsible for cleaning and preprocessing raw data.
            You clean, normalize, and handle missing data before analysis.
            Current user state: {pprint.pformat(self.state, indent=4)}
        """

        return OpenAIAgent.from_tools(
            tools=self.get_tools(),
            llm=self.llm,
            system_prompt=system_prompt,
        )
