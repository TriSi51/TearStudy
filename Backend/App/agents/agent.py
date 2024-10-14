from enum import Enum
import json
import pprint
from typing import Dict
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.base.response.schema import Response
from llama_index.core.base.llms.types import ChatMessage,MessageRole
from App.agents import (
    ReportGenerationAgent,
    DataProcessingAgent,
    AnalysisAgent,
    VisualizationAgent,
    ResearchAssistantAgent,
    UserInteractionAgent,
)

from App.models import load_model
from ..custom_logging import logger


class Speaker(str,Enum):
    RESEARCH_ASSISTANT = "research_assistant"
    DATA_PROCESSING = "data_processing"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    REPORT_GENERATION = "report_generation"
    USER_INTERACTION="user_interaction"


class OrchestrationManager:
    state = {
        "username": None,
        "data": None,
        "cleaned": False,
        "analyzed": False,
        "visualized": False,
        "current_speaker": None,
        "just_finished": False,
        "uploaded":False,
    }


    root_memory = ChatMemoryBuffer.from_defaults(token_limit=8000)
    first_run = True
    current_speaker = None
    administrator_prompt=None
    agent_responses={}
    llm = load_model()

    @classmethod
    def get_agent_factory_map(cls):
        """Returns the agent factory map with references to cls.llm."""
        return {
            Speaker.RESEARCH_ASSISTANT: lambda : ResearchAssistantAgent(cls.state,cls.llm),
            Speaker.DATA_PROCESSING: lambda : DataProcessingAgent(state=cls.state, llm=cls.llm,input_data=cls.state["data"]),
            Speaker.ANALYSIS: lambda : AnalysisAgent(cls.state, llm=cls.llm,input_data=cls.state["data"]),
            Speaker.VISUALIZATION: lambda : VisualizationAgent(cls.state,cls.llm),
            Speaker.REPORT_GENERATION: lambda : ReportGenerationAgent(cls.state,cls.llm),
            Speaker.USER_INTERACTION: lambda : UserInteractionAgent(cls.state,cls.llm,cls.agent_responses)
        }

    # Continuation agent
    def continuation_agent_factory(state: dict) -> OpenAIAgent:
        
        """
        Dummy agent
        """
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
    def load_input(cls,input_data:list) -> None:

        if not isinstance(input_data,list) or not all(isinstance(item,dict) for item in input_data):
            raise ValueError("Input must be a list of dictionary with key 'filename' , 'filetype' and 'data' ")
        cls.state['data'] = input_data
        cls.state['cleaned']= False
        cls.state['analyzed']=False
        cls.state['visualized']=False

        chat_history = cls.root_memory.get()

        # Append the new message using the ChatMessage model
        chat_history.append(ChatMessage.from_str("You uploaded successfully", role=MessageRole.ASSISTANT))

        cls.root_memory.set(chat_history)
        response=cls.run_conversation("Data has been uploaded. Do not do anything. Wait for my next query")
        return response

    
    @classmethod
    def orchestration_agent_factory(cls):
        """Creates the orchestration agent that will manage which agent to call next."""
                
        def decide_next_agent(speaker: Speaker,query_needed:str):
            try:
                logger.info(f"using tool: {speaker}")
                logger.info(f"using query: {query_needed}")
                response_dict = {
                    "speaker_value": str(speaker),
                    "query": query_needed
                }
                response_str=json.dumps(response_dict)
                logger.info(f"response_str: {response_str}")
                return response_str
                # return speaker,query_needed
            except Exception as e:
                logger.info(f"This tool encounter error {str(e)}")
                raise Exception("We have error when using tool for orchestration agent!!!")
            
        tools = [
            FunctionTool.from_defaults(fn=decide_next_agent)
        ]

        system_prompt =  ( f"""
        You are an orchestration agent.
        Your job is to decide which agent to run next based on the user's inputs and the chat history. Agents are identified by short strings in the format '{Speaker.RESEARCH_ASSISTANT.value}', '{Speaker.DATA_PROCESSING.value}', etc. For some complex tasks, you may need to use multiple agents consecutively (e.g., use the data processing agent before using the analysis agent).

        Your task includes:
        1. Evaluate the user’s current query from the chat history to determine which agent should handle the task.
        2. Paraphrase the user input to generate a query string tailored to the task the selected agent should perform. This query must provide clear, actionable instructions to the agent about what needs to be done based on the user’s request.
        3. For complex tasks, delegate work to multiple agents in sequence. For example, if the user asks for data analysis, ensure that the data is first processed using the Data Processing Agent, then analyzed using the Analysis Agent.
        4. Once the required agents have completed their tasks, always pass the final results to the User Interaction Agent, who will communicate the outcome to the user.
        5. Based on the user input and chat history, select one of these agents to run next and generate an appropriate query:
        * "{Speaker.RESEARCH_ASSISTANT.value}" - if the user asks for help gathering research materials. Generate a query such as "Find relevant papers on [topic]."
        * "{Speaker.DATA_PROCESSING.value}" - if the user has provided raw data that needs cleaning, preprocessing, or normalization. Generate a query such as "Clean and preprocess the dataset."
        * "{Speaker.ANALYSIS.value}" - if the data has been processed and the user wants to perform statistical analysis or machine learning. Generate a query such as "Perform analysis on the dataset using [specific technique]."
        * "{Speaker.VISUALIZATION.value}" - if the user requests data visualizations such as charts or graphs. Generate a query such as "Generate a visualization for [analysis result]."
        * "{Speaker.REPORT_GENERATION.value}" - if the user requests to compile a comprehensive report based on the analysis and visualizations. Generate a query such as "Compile a report from the analysis results."
        * "{Speaker.USER_INTERACTION.value}" - to communicate with the user and deliver any results or outputs generated by other agents.

        Remember:
        - Paraphrase the user's input to form a concise query that captures the essence of the user's request.
        - Do not ask user what they want to do. Just do your best to complete user query
        - Do not be conversational or perform any other task except selecting the appropriate agent to run next and generating the query string for it.
        The output must follow this format:
        {{
            "speaker": "agent_value", "query_needed": "generated_query"
        }}


        """)


        # The output must follow this format:
        # {{
        #     "speaker": "agent_value", "query_needed": "generated_query"
        # }}

        return OpenAIAgent.from_tools(
            tools,
            llm=cls.llm,
            system_prompt=system_prompt,
        )


    @classmethod
    def get_next_agent(cls, speaker: str):
        """Returns the agent factory based on the speaker."""
 
        try:
            cls.state['current_speaker'] = speaker
            agent_factory_map = cls.get_agent_factory_map()
            agent_factory = agent_factory_map.get(speaker)
            
            if agent_factory:
                cls.current_speaker = agent_factory()  # Invoke the lambda to create the agent
                logger.info(cls.current_speaker.get_identifier())
                return cls.current_speaker.create_agent()
            else:
                raise Exception(f"Invalid speaker: {speaker}")
        
        except KeyError:
            raise Exception(f"Invalid speaker: {speaker}")
        except Exception as e:
            raise Exception(f"An unexpected error occurs: {str(e)}")
    @classmethod
    def extract_speak_and_query(cls,string:str):
        try:
            response= json.loads(string)
            speaker= response.get("speaker")
            query= response.get("query_needed")
            return speaker,query
        except json.JSONDecodeError:
            raise Exception("error extract speaker value and query")
    @classmethod
    def run_conversation(cls,user_message):
        """Main loop to run the multi-agent orchestration conversation."""

        current_history=cls.root_memory.get()
        logger.info(f"current history: {current_history}")
        next_speaker = None
        while next_speaker != Speaker.USER_INTERACTION.value:
            # If there is a current speaker, continue with that agent
            if cls.state.get("current_speaker"):
                next_speaker = cls.state["current_speaker"]
            else:
                # Otherwise, call the orchestration agent to get the next speaker
                orchestration_response = cls.orchestration_agent_factory().chat(
                    user_message, chat_history=current_history
                )
                logger.info(f'orchestration: {orchestration_response}')

                # Ensure the orchestration response returns both next_speaker and query
                try:
                    orchestration_response=orchestration_response.__str__()
                    # Unpack the response
                    next_speaker,query= cls.extract_speak_and_query(orchestration_response)
                except ValueError:
                    raise Exception(f"Invalid response from Orchestration Agent: {orchestration_response}")
                
            logger.info(f"next speaker is:{next_speaker}")
            # Get the agent for the next task
            cls.current_speaker = cls.get_next_agent(next_speaker)
            if cls.current_speaker==Speaker.USER_INTERACTION.value:  # fix later
                agent_response = cls.current_speaker.chat(user_message, chat_history=current_history)
                cls.agent_responses={}
            else:
            # Run the agent and capture the output (the next agent will use this output)
                agent_response = cls.current_speaker.chat(query, chat_history=current_history)
            logger.info(f"Agent response: {agent_response.__str__()}")
            cls.agent_responses[next_speaker]= agent_response.__str__()
            # Add the response to chat history
            new_history = cls.current_speaker.memory.get_all()
            cls.root_memory.set(new_history)

            # Update the user_message with the output of the previous agent
            user_message = f"{cls.current_speaker} response:" +agent_response.__str__()
            cls.state["current_speaker"] = None
        

        return agent_response