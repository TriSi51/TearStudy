from enum import Enum
import json
import pprint
from typing import Dict
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.base.response.schema import Response
from llama_index.core.base.llms.types import ChatMessage,MessageRole
from llama_index.core.agent import ReActAgent
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
        "work_flow": None,
        
    }


    root_memory = ChatMemoryBuffer.from_defaults(token_limit=8000)
    first_run = True
    current_speaker = None
    administrator_prompt=None
    agent_responses={}
    llm = load_model(LLM_PROVIDER="openai")

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

            logger.info(f"using tool: {speaker}")
            logger.info(f"using query: {query_needed}")
            response_dict = {
                "speaker": str(speaker),
                "query_needed": query_needed
            }
            response_str=json.dumps(response_dict)
            logger.info(f"response_str: {response_str}")
            return response_str

        def retry_decide_next_agent(speaker: Speaker, query_needed:str, prev_bug: str):
            try:
                logger.info(f"using retry tool: {speaker}")
                logger.info(f"using query: {query_needed}")
                logger.info(f"previous bug: {prev_bug}")
                response_dict = {
                    "speaker": str(speaker),
                    "query_needed": query_needed
                }
                response_str=json.dumps(response_dict)
                logger.info(f"response_str: {response_str}")
                return response_str
                # return speaker,query_needed
            except Exception as e:
                logger.info(f"This tool encounter error {str(e)}")
                raise Exception("We have error when using tool for orchestration agent!!!")
        
        def generate_workflow(workflow: str):
            logger.info("workflow")
            return workflow
        tools = [
            FunctionTool.from_defaults(fn=generate_workflow)
        ]

        system_prompt =  ( f"""
        You are an orchestration agent.
        You may receive:

            User Input: An initial message from the user, denoted as "user: ...".
            Agent Response: A response from another agent after completing a task.        
         

        Your task includes:
        1. Create a workflow contain list of agents and query you give to those agents if you receive the input from user to complete user query. We will proceed the work flow from agent1 to agent2. 
        2. 
        5. You can select from the following agents for constructing the workflow:
        * "{Speaker.RESEARCH_ASSISTANT.value}" -  To gather relevant research materials.
        * "{Speaker.DATA_PROCESSING.value}" - To handle tasks like data cleaning, preprocessing, or normalization.
        * "{Speaker.ANALYSIS.value}" - To conduct statistical analysis or machine learning, but only if data has already been processed by {Speaker.DATA_PROCESSING.value}
        * "{Speaker.VISUALIZATION.value}" - To create visual representations of the data, such as charts or graphs.
        * "{Speaker.REPORT_GENERATION.value}" - To compile a comprehensive report based on analysis and visualizations.
        * "{Speaker.USER_INTERACTION.value}" - To communicate with the user, deliver results, or provide updates.

        Remember:
        - Paraphrase the User's Input: Create a concise query for each agent that captures the essence of what needs to be done.
        - Avoid Asking the User for Decisions: Make your best attempt to complete the user’s request without asking them what they want.
        - When creating a workflow, output the tasks in the following format:
        {{
            "agent": "query", 
            "agent": "query", 
            "agent": "query",
             ... 
        }}
        We will run from the first agent in the dict until we meet the final agent. Please replace "agent" with the actual agent name and replace "query" with a query
        if you can answer without using tool anymore, just give the answer

        """) 



        return OpenAIAgent.from_tools(
            tools,
            llm=cls.llm,
            system_prompt=system_prompt,
            verbose=True
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
    def extract_work_flow(cls,response:str):
        try:
            logger.info(f"response: {response}")
            workflow= json.loads(response)
            if not isinstance(workflow, dict):
                raise Exception("Workflow not type dict")
            return workflow
        
        except json.JSONDecodeError:
            raise Exception("error extract workflow")
    @classmethod
    def run_conversation(cls,input_message):
        """Main loop to run the multi-agent orchestration conversation."""

        current_history=cls.root_memory.get()
        input_message= "user: " + input_message
        # logger.info(f"current history: {current_history}")

        # Generate work_flow
        orchestration_response= cls.orchestration_agent_factory().chat(
            input_message, chat_history= current_history
        )
        workflow= cls.extract_work_flow(orchestration_response.__str__())

        next_speaker = None
        for agent,query in workflow.items():

        
            # If there is a current speaker, continue with that agent
            logger.info("new loop")

        
            # Get the agent for the next task
            cls.current_speaker = cls.get_next_agent(agent)
            agent_response = cls.current_speaker.chat(query, chat_history=current_history)
            cls.agent_responses = {}
            
            # Run the agent and capture the output (the next agent will use this output)
            logger.info(f"Agent response: {agent_response.__str__()}")
            cls.agent_responses[next_speaker]= agent_response.__str__()
            # Add the response to chat history
            new_history = cls.current_speaker.memory.get_all()
            cls.root_memory.set(new_history)

                        

            # Update the user_message with the output of the previous agent
            input_message = f"{cls.current_speaker} response:" +agent_response.__str__()
            cls.state["current_speaker"] = None

        return agent_response