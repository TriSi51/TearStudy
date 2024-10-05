from fastapi import FastAPI,HTTPException,File, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
from App.agents.agent import OrchestrationManager
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
agent=  OrchestrationManager()

class UserInput(BaseModel):
    message: str



# Endpoint to receive user input
@app.post("/message")
async def process_message(user_input: UserInput):
    try:
        user_message = user_input.message
        # Assuming the run_conversation method processes user input and returns a response
        response = agent.run_conversation(user_message=user_message)
        return {"message": response}

    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        logging.error(traceback.format_exc())
        return {"error": "An error occurred while processing the message."}