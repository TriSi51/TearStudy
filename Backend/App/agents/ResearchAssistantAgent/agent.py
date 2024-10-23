from enum import Enum
from typing import List
import pprint
from bs4 import BeautifulSoup
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.base.response.schema import Response
from bs4 import BeautifulSoup
import requests
from ...models import load_model
from ...custom_logging import logger


import pprint
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
from .prompt import RESEARCH_INSTRUCTION,RESEARCH_PROMPT

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    return True

def fetch_page_content(url):
    response= requests.get(url)
    
    soup = BeautifulSoup.get(response.content,'html.parser')
    content= []
    paragraphs= soup.find_all("p")
    for p in paragraphs:
        content.append(p.text)
    return " ".join(content)
    

def merge_content_from_urls(urls):
    """
    Fetch content from multiple URLs and merge all content into a single string.
    
    Parameters:
    urls (list): A list of URLs to fetch content from.
    
    Returns:
    str: Merged content from all URLs.
    """
    merged_content_list = []  # Using a list to accumulate content efficiently
    
    for url in urls:
        try:
            content = fetch_page_content(url)  # Fetch content from the URL
            if content:
                merged_content_list.append(content)  # Add the content to the list
            else:
                print(f"No content fetched from {url}")  # Log if no content was returned
        except RuntimeError as e:
            print(f"Error fetching content from {url}: {e}")  # Handle errors gracefully
    
    # Join all content with two new lines separating each URL's content
    return "\n\n".join(merged_content_list)

class ResearchAssistantAgent:
    def __init__(self, state: dict, llm: any):
        self.state = state
        self.llm = llm
        self.url= 'http://localhost:8080/search'  #my searxng search, we will custom later

    @classmethod
    def get_identifier(cls)->str:
        return "Research Agent"
    
    def web_search(self,query_for_search:str, query: str):
        params = {
        'q': query_for_search,   # The search query
        'format': 'json',   # Response format
        }
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.info("Error searching....")
            raise RuntimeError(f"Error occurred during the search request: {e}")
        
        json_response= response.json()
        json_response_top_5= json_response['results'][:5]
        urls = [result['url'] for result in json_response_top_5]

        content= merge_content_from_urls(urls)

        response_from_llm= self.llm.predict(
            RESEARCH_PROMPT,
            query=query,
            instructions=RESEARCH_INSTRUCTION,
            content=content
        )

        return Response(response=response_from_llm)

        


    def get_tools(self) -> list:
        """
        Returns the tools for the research assistant agent.
        """
        return [
            FunctionTool.from_defaults(fn=self.web_search),
        ]

    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for the research assistant agent.
        """
        return f"""
        You are a research assistant tasked with finding relevant information and materials for a given topic.
        You also summarize the findings and organize them.
        """

    def create_agent(self) -> OpenAIAgent:
        """
        Create and return an OpenAIAgent using the LLM and tools.
        """
        return OpenAIAgent.from_tools(self.get_tools(), llm=self.llm, system_prompt=self.get_system_prompt())

