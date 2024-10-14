from llama_index.core.prompts import PromptTemplate
from enum import Enum

class PromptType(Enum):
    DATAPREPROCESSING="data_preprocessing"
    SYNTHESIS="synthesis"

DEFAULT_DATA_PREPROCESSING_INSTRUCTION = (
    "1. You need to generate python code based on the query"
    "3. Clean data appropriately and describe the methods used.\n"
    "4. Determine the data types of each column and convert them to appropriate types if necessary.\n"
    "8. Ensure the analysis is reproducible and clearly documented.\n"
    "9. Please try your best not to generate error"

)

DEFAULT_DATA_PREPROCESSING_TEMPLATE = (
    "You are an advanced data processing agent that help data analysis agent cleaned the data. The data is stored in the variable `input_data`.\n"

    "`input_data` is a list of dictionaries, where each dictionary contains the following keys:\n"
    "   - 'filename': The name of the file.\n"
    "   - 'filetype': The type of the file (e.g., csv, xlsx).\n"
    "   - 'data': A pandas DataFrame that has been loaded from the file and needs to be processed.\n"
    "you need to load the key 'data' in the input_data. that is the data you need to process."
    "Follow these instructions:\n"
    "{instruction_str}\n"
    "Query: {query_str}\n\n"
    "Your goal is to help users clean their data.\n"
    "You need to replace the data in input data with the cleaned data"
    
)

DEFAULT_DATA_PREPROCESSING_PROMPT = PromptTemplate(
    DEFAULT_DATA_PREPROCESSING_TEMPLATE, prompt_type=PromptType.DATAPREPROCESSING
)

# DEFAULT_DATA_PREPROCESSING_PROMPT = PromptTemplate(
#     DEFAULT_DATA_PREPROCESSING_TEMPLATE,prompt_type=PromptType.DATAPREPROCESSING
# )


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