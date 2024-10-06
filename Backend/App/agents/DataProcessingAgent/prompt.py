from llama_index.core.prompts import PromptTemplate
from enum import Enum

class PromptType(Enum):
    DATAPREPROCESSING="data_preprocessing"

DEFAULT_DATA_PREPROCESSING_INSTRUCTION = (
    "1. Convert the query to executable Python code.\n"
    "2. The final line of code should be a Python expression that can be called with the `eval()` function.\n"
    "3. The code should represent a solution to the query.\n"
    "4. Do not quote the expression.\n"
    "5. The import of pandas as pd, numpy as np, and seaborn as sns are already made, DO NOT IMPORT AGAIN.\n"
    "6. Write code in markdown format.\n"
    "7. The input is a variable called `input_data` which is a list of dictionaries.\n"
    "   - Each dictionary in `input_data` contains three keys: 'filename', 'filetype', and 'data'.\n"
    "   - The key 'data' holds the pandas DataFrame that needs to be processed.\n"
    "8. For each DataFrame, perform the following tasks using pandas:\n"
    "   - Clean the data: remove NA values, fill missing data where necessary, drop duplicate rows, and remove unnecessary whitespace.\n"
    "   - Normalize the data if necessary: apply min-max scaling or z-score normalization.\n"
    "   - Handle missing values using forward-fill, backward-fill, or interpolation where appropriate.\n"
    "9. Replace the original DataFrame in the 'data' key with the cleaned/preprocessed DataFrame for each dictionary in `input_data`.\n"
    "10. After preprocessing, check if each dataset is relevant:\n"
    "    - A dataset is relevant if it is clean, has no significant missing values, and shows no major outliers.\n"
    "11. Generate a report that indicates whether each dataset (or the single dataset) is relevant based on the preprocessing results.\n"
    "12. Write all code in Python and make sure it is clean, well-documented, and efficient.\n"
)




DEFAULT_DATA_PREPROCESSING_TEMPLATE = (
    "You are a data processing agent. You need to preprocess one or more datasets, which are stored in the variable `input_data`.\n"
    "`input_data` is a list of dictionaries, where each dictionary contains the following keys:\n"
    "   - 'filename': The name of the file.\n"
    "   - 'filetype': The type of the file (e.g., csv, xlsx).\n"
    "   - 'data': A pandas DataFrame that has been loaded from the file and needs to be processed.\n"
    "Your task is to loop through each dictionary in `input_data` and perform the following tasks on the DataFrame stored in the 'data' key:\n"
    "   1. Clean the data (e.g., remove NA values, fill missing data, drop duplicates, remove unnecessary whitespace).\n"
    "   2. Normalize the data if necessary (e.g., min-max scaling, z-score normalization).\n"
    "   3. Handle any missing values (e.g., forward-fill, backward-fill, or interpolation).\n"
    "After processing, check if the dataset is relevant:\n"
    "   - A dataset is considered relevant if it is clean, consistent, and does not contain significant missing values or major outliers.\n"
    "Store each processed DataFrame back in the 'data' key of the corresponding dictionary.\n"
    "Finally, generate a report indicating whether each dataset is relevant or not, based on the preprocessing results.\n\n"
    "In addition, please respond to the following query based on the preprocessed data:\n"
    "   Query: {query_str}\n"
    "Follow these instructions:\n\n{instructions}"
)

DEFAULT_DATA_PREPROCESSING_PROMPT = PromptTemplate(
    DEFAULT_DATA_PREPROCESSING_TEMPLATE,prompt_type=PromptType.DATAPREPROCESSING
)


DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n\n"
    "Instructions (optional):\n{pandas_instructions}\n\n"
    "Execution Output: {pandas_output}\n\n"
    "Response: "
)
DEFAULT_RESPONSE_SYNTHESIS_PROMPT = PromptTemplate(
    DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL,
)