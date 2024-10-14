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
from ...custom_logging import logger


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
        self.identifier="Data Processing Agent"
        

    def get_identifier(self)->str:
        return self.identifier


    def generate_and_run_data_preprocessing_code(self, query_str: str):

        logger.info("im using generate and run data preprocessing code tool")
        logger.info(f"Query: {query_str}")
        try: 
            response = self._llm.predict(
                DEFAULT_DATA_PREPROCESSING_PROMPT,
                query_str=query_str,
                instruction_str=DEFAULT_DATA_PREPROCESSING_INSTRUCTION
            )
        except Exception as e:
            raise Exception(str(e))
        logger.info(f"Data pre processing generated:{response}")
        raw_output = self._instruction_parser.parse(response)
        logger.info(f"The raw output of data processing agent: {raw_output}")
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
                    pandas_output=raw_output
                )
            )
        else:
            response_str = str(raw_output)

        return Response(response=response_str, metadata=response_metadata)

    def get_tools(self):
        """
        Return the tools required for data processing.
        """
        tools = [
            FunctionTool.from_defaults(fn=self.generate_and_run_data_preprocessing_code),
    
        ]
        return tools

    def create_agent(self):
        """
        Create and return the OpenAIAgent with the tools and system prompt.
        """
        system_prompt = f"""
            You are a data processing agent responsible for cleaning and preprocessing raw data.
            You clean, normalize, and handle missing data before analysis.
        """

        return OpenAIAgent.from_tools(
            tools=self.get_tools(),
            llm=self._llm,
            system_prompt=system_prompt,
        )
