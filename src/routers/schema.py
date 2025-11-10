from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for Genie query."""

    query: str
