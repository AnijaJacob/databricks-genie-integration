from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for Genie query."""

    query: str


class FollowupRequest(QueryRequest):
    """Request model for Genie follow-up query."""

    conversation_id: str
