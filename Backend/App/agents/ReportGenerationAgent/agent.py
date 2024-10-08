from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from ...models import load_model


class ReportGenerationAgent:
    def __init__(self, state: dict, llm: any):
        self.state = state
        self.llm = llm
        self.identifier="Report Generation Agent"
    def get_identifier(self)->str:
        return self.identifier
    def compile_report(self, analysis_results: str, charts: list, summary: str) -> str:
        """
        Compile report from various elements like analysis results, charts, and summary.
        """
        print("Compiling report...")
        report = f"Report: {summary}\nAnalysis Results: {analysis_results}\nCharts: {charts}"
        self.state["report"] = report
        return report

    def format_document(self, report: str, format_type: str) -> str:
        """
        Simulate formatting the report in a given format type (e.g., PDF, DOCX).
        """
        print(f"Formatting document as {format_type}")
        formatted_report = f"{report} in {format_type} format"
        self.state["formatted_report"] = formatted_report
        return formatted_report

    def generate_summary(self) -> str:
        """
        Generate a summary for the report.
        """
        print("Generating summary...")
        summary = f"Summary: {self.state.get('summary', 'No summary available')}"
        self.state["report_summary"] = summary
        return summary

    def get_tools(self) -> list:
        """
        Returns the tools that will be available to the agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.compile_report),
            FunctionTool.from_defaults(fn=self.format_document),
            FunctionTool.from_defaults(fn=self.generate_summary),
        ]
    
    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for the report generation agent.
        """
        return f"""
        You are a report generation agent compiling all analysis, visualizations, and summaries into a comprehensive report.
        Current user state: {pprint.pformat(self.state, indent=4)}
        """

    def create_agent(self) -> OpenAIAgent:
        """
        Create and return an OpenAIAgent using the LLM and tools.
        """
        return OpenAIAgent.from_tools(self.get_tools(), llm=self.llm, system_prompt=self.get_system_prompt())