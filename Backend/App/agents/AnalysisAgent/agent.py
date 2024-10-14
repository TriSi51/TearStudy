from enum import Enum
from typing import List,Dict
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.base.response.schema import Response
from ...models import load_model
from .prompts import ANALYSIS_INSTRUCTION,ANALYSIS_PROMPT
from ...tools.prompts import DEFAULT_RESPONSE_SYNTHESIS_PROMPT
from ...tools.output_parser import InstructionParser

from ...custom_logging import logger
class AnalysisAgent:
    def __init__(self, state: dict, llm: any,input_data:List[Dict]):
        self.state = state
        self.llm = llm
        self.identifier="Analysis Agent"
        self._synthesize_response= True
        self._instruction_parser=InstructionParser(input_data)

    def get_identifier(self)->str:
        return self.identifier

    def generate_and_run_data_analysis_code(self,query_str:str):
        logger.info("Running data analysis tool!!!!")
        logger.info(f"analysis query: {query_str}")

        response= self.llm.predict(
            ANALYSIS_PROMPT,
            query_str = query_str,
            instruction_str= ANALYSIS_INSTRUCTION
        )   
        logger.info(f"Data analysis response: {response}")

        raw_output = self._instruction_parser.parse(response)

        logger.info(f"Raw_output from data analysis agent: {raw_output}")
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
        
        return Response(response=response_str,metadata= response_metadata )


    def get_tools(self) -> list:
        """
        Returns the tools for the analysis agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.generate_and_run_data_analysis_code),
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
