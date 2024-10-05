from enum import Enum
from typing import List
import pprint
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from App.agents import (
    research_assistant_agent_factory,
    data_processing_agent_factory,
    analysis_agent_factory,
    visualization_agent_factory,
    report_generation_agent_factory


)
from App.models import load_model
# Enum for different speakers/agents
class Speaker(str, Enum):
    RESEARCH_ASSISTANT = "research_assistant"
    DATA_PROCESSING = "data_processing"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    REPORT_GENERATION = "report_generation"
    ORCHESTRATOR = "orchestrator"
    USER_INTERACTION = "user_interaction"

def orchestration_agent_factory(state: dict) -> OpenAIAgent:
    # Orchestrator decides which agent should be called next based on the state
    def decide_next_agent() -> str:
        if "data" in state and not state.get("cleaned"):
            return Speaker.DATA_PROCESSING.value
        elif state.get("cleaned") and not state.get("analyzed"):
            return Speaker.ANALYSIS.value
        elif state.get("analyzed") and not state.get("visualized"):
            return Speaker.VISUALIZATION.value
        else:
            return Speaker.REPORT_GENERATION.value
    
    tools = [
        FunctionTool.from_defaults(fn=decide_next_agent),
    ]
    
    system_prompt = (f"""
    You are an orchestration agent.
    Your job is to decide which agent to run next based on the current state of the user and what they have asked to do. Agents are identified by short strings.
    Your job is to return the name of the agent to run next. You do not do anything else.

    The current state of the user is:
    {pprint.pformat(state, indent=4)}

    If a current_speaker is already selected in the state, simply output that value.

    If there is no current_speaker value, look at the chat history and the current state and you MUST return one of these strings identifying an agent to run:
    * "{Speaker.RESEARCH_ASSISTANT.value}" - if the user wants to gather research materials or needs assistance organizing study materials.
    * "{Speaker.DATA_PROCESSING.value}" - if the user has provided data that needs to be cleaned, preprocessed, or normalized.
    * "{Speaker.ANALYSIS.value}" - if the data has been processed and the user wants to perform statistical analysis, machine learning, or other computations.
    * "{Speaker.VISUALIZATION.value}" - if the analysis has been completed and the user wants to generate visualizations like charts or graphs.
    * "{Speaker.REPORT_GENERATION.value}" - if the user wants to compile a comprehensive report based on the analysis and visualizations.

    Output one of these strings and ONLY these strings, without quotes.
    NEVER respond with anything other than one of the above five strings. DO NOT be helpful or conversational.
""")

    
    return OpenAIAgent.from_tools(tools, llm=load_model(), system_prompt=system_prompt)

# Main runner to handle the multi-agent orchestration
def run() -> None:
    state = {
        "username": None,
        "data": None,
        "cleaned": False,
        "analyzed": False,
        "visualized": False,
        "current_speaker": None,
        "just_finished": False,
    }

    root_memory = ChatMemoryBuffer.from_defaults(token_limit=8000)
    first_run = True

    while True:
        if first_run:
            user_msg_str = "Hello"
            first_run = False
        else:
            user_msg_str = input("> ").strip()

        current_history = root_memory.get()

        if state["current_speaker"]:
            next_speaker = state["current_speaker"]
        else:
            orchestration_response = orchestration_agent_factory(state).chat(user_msg_str, chat_history=current_history)
            next_speaker = str(orchestration_response).strip()
        print(f"Next speaker: {next_speaker}")

        if next_speaker == Speaker.RESEARCH_ASSISTANT:
            current_speaker = research_assistant_agent_factory(state)
            state["current_speaker"] = next_speaker
        elif next_speaker == Speaker.DATA_PROCESSING:
            current_speaker = data_processing_agent_factory(state)
            state["current_speaker"] = next_speaker
        # Handle other agents...
        else:
            print("Orchestration agent failed to return a valid speaker; ask it to try again")
            is_retry = True
            continue
        
        response = current_speaker.chat(user_msg_str, chat_history=current_history)
        print(response)

        # Update state and chat history
        new_history = current_speaker.memory.get_all()
        root_memory.set(new_history)
        state["just_finished"] = True
run()