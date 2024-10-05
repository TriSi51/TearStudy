from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model
def analysis_agent_factory(state: dict) -> OpenAIAgent:
    def perform_analysis(data: str) -> str:
        # Simulate statistical analysis
        print(f"Performing analysis on: {data}")
        analysis_result = f"Analysis result of {data}"
        state["analysis_result"] = analysis_result
        return analysis_result

    def run_ml_model(data: str, model: str) -> str:
        # Simulate running an ML model
        print(f"Running {model} model on data: {data}")
        ml_result = f"Result of {model} on {data}"
        state["ml_result"] = ml_result
        return ml_result

    def explain_results(analysis: str) -> str:
        # Explain the results of analysis
        print(f"Explaining analysis results: {analysis}")
        explanation = f"Explanation of {analysis}"
        state["explanation"] = explanation
        return explanation

    tools = [
        FunctionTool.from_defaults(fn=perform_analysis),
        FunctionTool.from_defaults(fn=run_ml_model),
        FunctionTool.from_defaults(fn=explain_results),
    ]
    
    system_prompt = f"""
        You are an analysis agent performing statistical or machine learning analysis on processed data.
        You also explain the results of your analysis to the user in understandable terms.
        Current user state: {pprint.pformat(state, indent=4)}
    """
    
    return OpenAIAgent.from_tools(tools, llm=load_model(), system_prompt=system_prompt)
