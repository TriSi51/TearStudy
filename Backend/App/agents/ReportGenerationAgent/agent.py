from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model

def report_generation_agent_factory(state: dict) -> OpenAIAgent:
    def compile_report(analysis_results: str, charts: List[str], summary: str) -> str:
        # Compile report from various elements
        print("Compiling report...")
        report = f"Report: {summary}\nAnalysis Results: {analysis_results}\nCharts: {charts}"
        state["report"] = report
        return report

    def format_document(report: str, format_type: str) -> str:
        # Simulate formatting the report
        print(f"Formatting document as {format_type}")
        formatted_report = f"{report} in {format_type} format"
        state["formatted_report"] = formatted_report
        return formatted_report

    def generate_summary() -> str:
        # Generate a summary of the report
        print("Generating summary...")
        summary = f"Summary: {state.get('summary', 'No summary available')}"
        state["report_summary"] = summary
        return summary

    tools = [
        FunctionTool.from_defaults(fn=compile_report),
        FunctionTool.from_defaults(fn=format_document),
        FunctionTool.from_defaults(fn=generate_summary),
    ]
    
    system_prompt = f"""
        You are a report generation agent compiling all analysis, visualizations, and summaries into a comprehensive report.
        Current user state: {pprint.pformat(state, indent=4)}
    """
    
    return OpenAIAgent.from_tools(tools, llm=load_model(), system_prompt=system_prompt)
