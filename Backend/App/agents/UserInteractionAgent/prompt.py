from llama_index.core.prompts import PromptTemplate
from enum import Enum

class PromptType(Enum):
    USER_INTERACTION="user_interaction"


USER_INTERACTION_INSTRUCTION = (
    "1. You are the user interaction agent. Your role is to communicate with the user by answering their questions."
    "2. When a user asks a question that involves results from multiple agents, you will summarize the outputs from all relevant agents."
    "3. For each question:"
        "If agent outputs are provided, summarize them and respond to the user."
        "If  agent outputs are none, engage with the user directly and answer their question based on the context, without acknowledging the missing data."
    "5. If there is no specific output from other agents, respond directly to the user based on their query."
    "6. Always prioritize clarity and avoid technical jargon unless the user explicitly requests it."
    "7. If the agent outputs is none. It just because we dont use those agents in this query. So please talk to user normally"
)

USER_INTERACTION_TMPL = (
    "Query: {query_str}\n\n"
    "Agent Outputs: {agent_outputs}\n\n"
    "Instruction: {instruction}\n\n"
    
)


USER_INTERACTION_PROMPT= PromptTemplate(USER_INTERACTION_TMPL,prompt_type=PromptType.USER_INTERACTION)
