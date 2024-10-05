from enum import Enum
import pprint
from typing import Dict
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
from App.agents import (
    research_assistant_agent_factory,
    data_processing_agent_factory,
    analysis_agent_factory,
    visualization_agent_factory,
    report_generation_agent_factory
)
from llama_index.core.memory import ChatMemoryBuffer
from App.models import load_model

class InvalidSpeakerException(Exception):
    """Custom exception for invalid speakers."""
    pass


class Speaker(str, Enum):
    RESEARCH_ASSISTANT = "research_assistant"
    DATA_PROCESSING = "data_processing"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    REPORT_GENERATION = "report_generation"


class OrchestrationManager:
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
    current_speaker = None
    llm = load_model()
    #maybe

    # Continuation agent
    def continuation_agent_factory(state: dict) -> OpenAIAgent:
        
        def dummy_tool() -> bool:
            """A tool that does nothing."""
            print("Doing nothing.")

        tools = [
            FunctionTool.from_defaults(fn=dummy_tool)
        ]

        system_prompt = (f"""
            The current state of the user is:
            {pprint.pformat(state, indent=4)}
        """)

        return OpenAIAgent.from_tools(
            tools,
            llm=load_model(),
            system_prompt=system_prompt,
        )



    @classmethod
    def orchestration_agent_factory(cls):
        """Creates the orchestration agent that will manage which agent to call next."""
                
        def decide_next_agent(speaker_value: Speaker) -> str:
            return speaker_value
            
        tools = [
            FunctionTool.from_defaults(fn=decide_next_agent),
        ]

        system_prompt = (f"""
        You are an orchestration agent.
        Your job is to decide which agent to run next based on the current state of the user and what they have asked to do. Agents are identified by short strings.
        Your job is to return the name of the agent to run next. You do not do anything else.

        The current state of the user is:
        {pprint.pformat(cls.state, indent=4)}

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

        return OpenAIAgent.from_tools(
            tools,
            llm=cls.llm,
            system_prompt=system_prompt,
        )


    @classmethod
    def get_next_agent(cls, speaker: str):
        """Returns the agent factory based on the speaker."""
        if speaker == Speaker.RESEARCH_ASSISTANT:
            cls.state['current_speaker']= speaker
            return research_assistant_agent_factory(cls.state)
        elif speaker == Speaker.DATA_PROCESSING:
            cls.state['current_speaker']= speaker
            return data_processing_agent_factory(cls.state)
        elif speaker == Speaker.ANALYSIS:
            cls.state['current_speaker']= speaker
            return analysis_agent_factory(cls.state,llm=cls.llm)
        elif speaker == Speaker.VISUALIZATION:
            cls.state['current_speaker']= speaker
            return visualization_agent_factory(cls.state)
        elif speaker == Speaker.REPORT_GENERATION:
            cls.state['current_speaker']= speaker
            return report_generation_agent_factory(cls.state)
        else:
            # Raise an exception if an invalid speaker is provided
            raise InvalidSpeakerException(f"Invalid speaker: {speaker}")

    @classmethod
    def run_conversation(cls,user_message):
        """Main loop to run the multi-agent orchestration conversation."""
        current_history=cls.root_memory.get()
        
        if cls.state["current_speaker"]:
            next_speaker = cls.state["current_speaker"]
        else:
            orchestration_response = cls.orchestration_agent_factory().chat(user_message, chat_history=current_history)
            next_speaker = str(orchestration_response).strip()
        cls.current_speaker= cls.get_next_agent(next_speaker)
        response = cls.current_speaker.chat(user_message, chat_history=current_history)


        new_history = cls.current_speaker.memory.get_all()
        cls.root_memory.set(new_history)
        return response