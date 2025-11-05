"""Databricks Genie Conversation API client."""

import logging
from typing import Any

import httpx

from src.models.genie import CreateMessageRequest, GenieConversation, GenieMessage

logger = logging.getLogger(__name__)


class GenieClient:
    """Client for Databricks Genie Conversation API."""

    def __init__(self, workspace_url: str, access_token: str):
        """Initialize Genie client.

        Args:
            workspace_url: Databricks workspace URL (e.g., https://adb-xxxxx.azuredatabricks.net)
            access_token: Databricks access token
        """
        self.workspace_url = workspace_url.rstrip("/")
        self.base_url = f"{self.workspace_url}/api/2.0/genie"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        self.client = httpx.Client(headers=self.headers, timeout=30.0)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: ANN001
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def create_conversation(self, space_id: str) -> GenieConversation | None:
        """Create a new Genie conversation.

        Args:
            space_id: Genie space ID

        Returns:
            GenieConversation object or None if failed
        """
        url = f"{self.base_url}/spaces/{space_id}/conversations"

        try:
            response = self.client.post(url, json={})
            response.raise_for_status()
            data = response.json()
            logger.info(f"Created conversation: {data.get('conversation_id')}")
            return GenieConversation(**data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating conversation: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None

    def create_message(
        self, space_id: str, conversation_id: str, content: str
    ) -> GenieMessage | None:
        """Create a message in a Genie conversation.

        Args:
            space_id: Genie space ID
            conversation_id: Conversation ID
            content: Message content/query

        Returns:
            GenieMessage object or None if failed
        """
        url = f"{self.base_url}/spaces/{space_id}/conversations/{conversation_id}/messages"
        payload = CreateMessageRequest(content=content)

        try:
            response = self.client.post(url, json=payload.model_dump())
            response.raise_for_status()
            data = response.json()
            logger.info(f"Created message: {data.get('id')}")
            return GenieMessage(**data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating message: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            return None

    def get_message(self, space_id: str, conversation_id: str, message_id: str) -> GenieMessage | None:
        """Get a message from a Genie conversation.

        Args:
            space_id: Genie space ID
            conversation_id: Conversation ID
            message_id: Message ID

        Returns:
            GenieMessage object or None if failed
        """
        url = f"{self.base_url}/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"

        try:
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return GenieMessage(**data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting message: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting message: {e}")
            return None

    def list_messages(self, space_id: str, conversation_id: str) -> list[GenieMessage]:
        """List all messages in a Genie conversation.

        Args:
            space_id: Genie space ID
            conversation_id: Conversation ID

        Returns:
            List of GenieMessage objects
        """
        url = f"{self.base_url}/spaces/{space_id}/conversations/{conversation_id}/messages"

        try:
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()
            messages = [GenieMessage(**msg) for msg in data.get("messages", [])]
            logger.info(f"Retrieved {len(messages)} messages")
            return messages

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error listing messages: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error listing messages: {e}")
            return []

    def get_conversation(self, space_id: str, conversation_id: str) -> GenieConversation | None:
        """Get a Genie conversation.

        Args:
            space_id: Genie space ID
            conversation_id: Conversation ID

        Returns:
            GenieConversation object or None if failed
        """
        url = f"{self.base_url}/spaces/{space_id}/conversations/{conversation_id}"

        try:
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return GenieConversation(**data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting conversation: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None

    def query_genie(self, space_id: str, query: str, conversation_id: str | None = None) -> dict[str, Any]:
        """Query Genie with automatic conversation management.

        Args:
            space_id: Genie space ID
            query: Query content
            conversation_id: Optional existing conversation ID

        Returns:
            Dictionary with conversation_id, message_id, and message details
        """
        # Create conversation if not provided
        if not conversation_id:
            conversation = self.create_conversation(space_id)
            if not conversation:
                return {"error": "Failed to create conversation"}
            conversation_id = conversation.id

        # Create message
        message = self.create_message(space_id, conversation_id, query)
        if not message:
            return {"error": "Failed to create message"}

        return {
            "conversation_id": conversation_id,
            "message_id": message.id,
            "status": message.status,
            "content": message.content,
            "query_result": message.query_result,
            "attachments": message.attachments,
        }
