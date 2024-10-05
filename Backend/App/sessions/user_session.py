import uuid
import asyncio
from typing import Dict, Union, Optional,List,Any
from contextvars import ContextVar
from fastapi import WebSocket, Depends
from lazify import LazyProxy
from contextvars import ContextVar

# In-memory storage for user sessions
user_sessions: Dict[str, Dict] = {}

class SessionContextException(Exception):
    """Exception raised when session context is not found."""
    def __init__(self, msg="Session context not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class SessionContext:
    """A class to manage individual user session data."""
    def __init__(self, session_id: str, user_data: Optional[Dict] = None):
        self.session_id = session_id
        self.user_data = user_data or {}

    def get(self, key: str, default=None):
        """Retrieve a value from the session context."""
        return self.user_data.get(key, default)

    def set(self, key: str, value: Any):
        """Store a value in the session context."""
        self.user_data[key] = value

    def clear(self):
        """Clear all session data."""
        self.user_data.clear()


class UserSession:
    """
    Manages user-specific session data between API calls.
    """

    def get_context(self) -> Optional[SessionContext]:
        """Retrieve the current session context."""
        context = context_var.get()
        if context is None:
            context = self.init_context()  # Automatically initialize the contex
        return context

    def init_context(self) -> SessionContext:
        """Initialize a new session context."""
        session_id = str(uuid.uuid4())
        user_data = user_sessions.get(session_id, {})
        context = SessionContext(session_id, user_data)
        context_var.set(context)
        return context
    
    def get_history(self, agent_identifier: str, default: Optional[List] = None) -> List:
        """Retrieve the chat history for a specific agent."""
        context = self.get_context()
        history_key = f"{agent_identifier}_chat_history"
        return context.get(history_key, default=default or [])
    
    def set_history(self, agent_identifier: str, history: List):
        """Store the chat history for a specific agent."""
        context = self.get_context()
        history_key = f"{agent_identifier}_chat_history"
        context.set(history_key, history)
    
    def get_agent(self, agent_identifier: str, default: Optional[Any] = None) -> Any:
        """Retrieve the agent instance for a specific agent identifier."""
        context = self.get_context()
        return context.get(agent_identifier, default=default)

    def set_agent(self, agent_identifier: str, agent: Any):
        """Store the agent instance for a specific agent identifier."""
        context = self.get_context()
        context.set(agent_identifier, agent)


user_session__ = UserSession()


context_var :ContextVar[Optional[SessionContext]]= ContextVar("session_context",default=None)
