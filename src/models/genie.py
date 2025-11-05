"""Data models for Genie Conversation API."""

from typing import Any

from pydantic import BaseModel, Field


class GenieMessage(BaseModel):
    """Message in a Genie conversation."""

    id: str = Field(..., description="Message ID")
    content: str = Field(..., description="Message content")
    status: str = Field(..., description="Message status (EXECUTING_QUERY/COMPLETED/FAILED)")
    query_result: dict[str, Any] | None = Field(default=None, description="Query result if available")
    attachments: list[dict[str, Any]] = Field(default_factory=list, description="Message attachments")


class CreateMessageRequest(BaseModel):
    """Request to create a message in Genie conversation."""

    content: str = Field(..., description="Message content/query")


class GenieConversation(BaseModel):
    """Genie conversation details."""

    id: str = Field(..., description="Conversation ID")
    space_id: str = Field(..., description="Genie space ID")
    title: str | None = Field(default=None, description="Conversation title")
    created_timestamp: int = Field(..., description="Creation timestamp")
    last_updated_timestamp: int = Field(..., description="Last update timestamp")
