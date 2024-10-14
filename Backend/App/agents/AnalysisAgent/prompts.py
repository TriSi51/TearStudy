from llama_index.core.prompts import PromptTemplate
from enum import Enum

class PromptType(Enum):
    ANALYSIS="analysis"

ANALYSIS_INSTRUCTION = (
    "1. You need to generate python code based on the query.\n"
    "2. Provide a brief summary of the data types used for variables, including the most common data types and any that require special attention.\n"
    "3. Provide a brief summary of the data, including count, mean, std, min, 25%, 50%, 75%, max for each column.\n"
    "4. Determine the data types of each column and convert them to appropriate types if necessary.\n"
    "6. Provide insights and interpretations for each analysis step to help understand the significance of the findings.\n"
    "7. Suggest appropriate statistical methods for deeper analysis when relevant.\n"
    "8. Ensure the analysis is reproducible and clearly documented.\n"
)


ANALYSIS_TEMPLATE= (
    "You are an advanced data analysis agent that analyze the data. The data is stored in the variable `input_data`.\n"

    "`input_data` is a list of dictionaries, where each dictionary contains the following keys:\n"
    "   - 'filename': The name of the file.\n"
    "   - 'filetype': The type of the file (e.g., csv, xlsx).\n"
    "   - 'data': A pandas DataFrame that has been loaded from the file and needs to be processed.\n"
    "Follow these instructions:\n"
    "{instruction_str}\n"
    "Query: {query_str}\n\n"
    "Your goal is to help users understand their data by providing clear and detailed insights.\n"
    "Ensure the analysis is well-documented, reproducible, and presented in a professional yet approachable manner.\n"
    "Do not generate code to display the datatype of each column. Instead, summarize the data types and highlight any that require special attention.\n"
)


ANALYSIS_PROMPT= PromptTemplate(ANALYSIS_TEMPLATE,
                                prompt_type=PromptType.ANALYSIS)