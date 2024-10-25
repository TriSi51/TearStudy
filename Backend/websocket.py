from fastapi import FastAPI,HTTPException,File, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from App.agents.agent import OrchestrationManager
import traceback
import pandas as pd
from io import BytesIO
import logging
from fastapi import FastAPI, Request, Response,WebSocket,WebSocketDisconnect 

from App.custom_logging import logger

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)
agent=  OrchestrationManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager= ConnectionManager()


class UserInput(BaseModel):
    message: str
