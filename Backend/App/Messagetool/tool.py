import uuid
import json
from typing import Optional, List, Dict, Union
from datetime import datetime, timezone
import httpx

class Message:
    def __init__(
        self,
        content: Union[str, Dict],
        author: Optional[str] = "assistant",
        language: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[str] = None,
        actions: Optional[List[Dict]] = None,
        elements: Optional[List[Dict]] = None,
    ):
        self.content = self._format_content(content)
        self.author = author
        self.language = language or "text"
        self.metadata = metadata or {}
        self.tags = tags or []
        self.parent_id = parent_id
        self.id = id or str(uuid.uuid4())
        self.created_at = created_at or self._get_current_time()
        self.actions = actions or []
        self.elements = elements or []
    def _get_content(self):
        return self.content

    def _format_content(self, content: Union[str, Dict]) -> str:
        """Convert content to a JSON string if it's a dictionary, otherwise leave it as a string."""
        if isinstance(content, dict):
            return json.dumps(content, indent=4, ensure_ascii=False)
        return str(content)

    def _get_current_time(self) -> str:
        """Get the current UTC time as a string."""
        return datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        """Convert the message into a dictionary for sending as a response."""
        return {
            "id": self.id,
            "parentId": self.parent_id,
            "author": self.author,
            "content": self.content,
            "createdAt": self.created_at,
            "language": self.language,
            "metadata": self.metadata,
            "tags": self.tags,
            "actions": self.actions,
            "elements": self.elements,
        }

    async def send(self, api_url: str):
        """Send the message to the frontend via an API using httpx."""
        message_data = {"content": self.content}  # Only send the content
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=message_data)

            try:
                response = await client.post(api_url, json=message_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"Failed to send message: {e}")

    async def update(self, api_url: str):
        """Update an existing message by sending updated data to the frontend."""
        message_data = self.to_dict()
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(f"{api_url}/{self.id}", json=message_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"Failed to update message: {e}")

        return response.json()

    async def remove(self, api_url: str):
        """Remove the message from the frontend by sending a delete request."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(f"{api_url}/{self.id}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise RuntimeError("Failed to remove  message: {e}")