from llama_index.core.prompts import PromptTemplate
from enum import Enum

class PromptType(Enum):
    SYNTHESIS="synthesis"


DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n\n"
    "Instructions (optional):\n{pandas_instructions}\n\n"
    "Execution Output: {pandas_output}\n\n"
    "Response: "
)
DEFAULT_RESPONSE_SYNTHESIS_PROMPT = PromptTemplate(
    DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL,prompt_type=PromptType.SYNTHESIS
)