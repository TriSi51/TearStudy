from llama_index.core.prompts import PromptTemplate
from enum import Enum

class PromptType(Enum):
    REPORTS= "report"


DEFAULT_COMPREHENSIVE_REPORT_WRITING_INSTRUCTION_STR = (
    "1. Summarize key data types identified by the agent, noting any that require special attention.\n"
    "2. Review the statistical summary from the agent's output. Highlight notable trends, outliers, or patterns.\n"
    "3. Evaluate the handling of missing data. Suggest any improvements if necessary.\n"
    "4. Assess whether the agent’s data type conversions were appropriate and necessary.\n"
    "5. Review and critique the agent’s visualizations. Suggest alternative visualizations if needed to improve clarity and readability.\n"
    "6. Analyze how the agent handled outliers and provide additional recommendations if needed.\n"
    "7. Evaluate the handling of categorical data and suggest methods for managing high-cardinality categories.\n"
    "8. Recommend additional statistical methods to further the analysis and provide deeper insights.\n"
    "9. Generate new insights based on the agent’s output, adding value to the analysis.\n"
    "10. Suggest next steps for continuing the analysis, including further exploration or refining the current findings.\n"
)

DEFAULT_COMPREHENSIVE_REPORT_WRITING_TMPL = (
    "You are a reporting agent that works with outputs from other agents. "
    "You have received the content result:\n"
    "{content}\n\n"
    "The input you receive may be a dict or str\n"
    "Your task is to write a comprehensive report based on this output. Follow these instructions:\n"
    "{instruction_str}\n"
    "Your goal is to add value to the analysis by generating clear, insightful commentary and further recommendations. "
    "Ensure your report is well-documented, reproducible, and professionally written in an approachable manner.\n"
)

DEFAULT_COMPREHENSIVE_REPORT_WRITING_PROMPT = PromptTemplate(
    template=DEFAULT_COMPREHENSIVE_REPORT_WRITING_TMPL, 
    prompt_type= PromptType.REPORTS
)