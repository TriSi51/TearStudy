from llama_index.core.prompts import PromptTemplate
from enum import Enum

class PromptType(Enum):
    ANALYSIS="analysis"

ANALYSIS_INSTRUCTION = (
    "1. You are the Analysis Agent. You have received cleaned/preprocessed data as input.\n"
    "2. Your task is to perform Exploratory Data Analysis (EDA) on the data like a data analyst.\n"
    "3. The input data is a variable called `cleaned_data`, which is a list of dictionaries.\n"
    "   - Each dictionary contains three keys: 'filename', 'filetype', and 'data'.\n"
    "   - The key 'data' contains the pandas DataFrame ready for analysis.\n"
    "4. For each DataFrame, perform the following EDA tasks:\n"
    "   - Display the basic statistics of the data: mean, median, mode, variance, standard deviation, and range.\n"
    "   - Plot histograms for each numerical feature.\n"
    "   - Generate pair plots to visualize relationships between numerical features.\n"
    "   - Plot bar charts for categorical data to show the distribution.\n"
    "   - Detect and visualize any outliers using box plots.\n"
    "5. Identify key patterns or trends in the data.\n"
    "6. Check for correlations among features using a correlation heatmap.\n"
    "7. Summarize key insights, such as: are there any correlations, clusters, outliers, or trends worth noting?\n"
    "8. Generate a final report summarizing all the key findings from the EDA.\n"
    "9. Use clean, well-documented code in Python. Write everything in markdown format and do not include extra information outside the EDA task.\n"
)

ANALYSIS_TEMPLATE=


ANALYSIS_PROMPT= PromptTemplate(ANALYSIS_TEMPLATE,
                                prompt_type=PromptType.ANALYSIS)