from fastapi import FastAPI,HTTPException,File, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .agents import LLMCompilerAgent
from .Messagetool import Message
import logging
import traceback
from typing import Optional, List,Dict


app= FastAPI()

logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)
agent=  LLMCompilerAgent()

class MessageRequest(BaseModel):
    content: str  # The message content
class MessageResponse(BaseModel):
    response:str

# @app.post("/api/chat",response_model=MessageResponse)
# async def chat(request: MessageRequest):    
#     try:
#         # Check if the agent has been initialized
#         if not hasattr(LLMCompilerAgent, "_agent"):
#             await agent.aon_start()

#         # Pass the user message to the agent
#         response = await agent.aon_message(Message(content=request.message, author="user"))
        
#         # Return the response from the agent to the frontend
#         return {"response": response}

#     except Exception as e:
#         # Log the full traceback for better debugging information
#         logging.error(f"Error in /api/chat: {str(e)}")
#         logging.error(traceback.format_exc())  # This will log the full traceback

#         raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):    
    try:
        # For testing, just return the message content with a simple response
        user_message = request.content
        bot_response = f"Bot received: {user_message}"
        
        # Return the response
        return {"response": bot_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_file(file:UploadFile= File(...)):
    #check if upload file is csv
    file_type = file.content_type

    try:
        await agent.receive_file(file,file_type)
    except Exception as e:
        logging.error(f"Error in /api/upload: {str(e)}")
        logging.error(traceback.format_exc()) #log full traceback

        raise HTTPException(status_code= 200,detail="File receive error") 



# For testing, root path
@app.get("/")
def read_root():
    return {"Hello": "Welcome to the FastAPI Chatbot"}