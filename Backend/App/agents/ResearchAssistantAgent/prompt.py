from llama_index.core.prompts import PromptTemplate
from enum import Enum


class PromptType(Enum):
    RESEARCH="research"

RESEARCH_INSTRUCTION = (
    """
    You are tasked with summarizing the merged content from multiple sources on a specific topic.
    The goal is to:
    1. Analyze the merged content and extract key points.
    2. Summarize the main ideas, findings, and conclusions from the content.
    3. Organize the information in a clear and concise manner.
    4. Provide insights into any key trends, disagreements, or notable findings within the content.
    5. For tool web search, the argument 'query_for_search' is your query to search the content, you can use keyword; for 'query' argument is your query to summarize the content
    
    Ensure that your summary is coherent, avoids repetition, and captures the most important aspects of the topic.
    """
)

RESEARCH_TEMPLATE = (
    """
    You are an advanced research assistant agent that specializes in analyzing and summarizing complex information from multiple sources.
    Given the following merged content, perform the following tasks:
    
    1. Summarize the key points and conclusions.
    2. Highlight important findings or trends, and mention any conflicting information or disagreements.
    3. Structure the response in sections for clarity, ensuring that the summarized content is easy to understand.
    
    Merged Content: {merged_content}
    Query: {query}
    Instructions: {instructions}
    """
)

# Create a prompt template for the research assistant agent
RESEARCH_PROMPT = PromptTemplate(
    RESEARCH_TEMPLATE,
    prompt_type=PromptType.RESEARCH
)