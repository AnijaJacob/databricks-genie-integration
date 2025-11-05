"""FastAPI application for Databricks Genie integration."""

import logging

from fastapi import Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel

from src.api.genie_client import GenieClient
from src.auth.msal_auth import AppToAppAuth, OBOAuth
from src.models.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Databricks Genie Integration",
    description="API for interacting with Databricks Genie using OBO and App-to-App authentication",
    version="0.1.0",
)

# Load configuration
config = Config()


class QueryRequest(BaseModel):
    """Request model for Genie query."""

    query: str
    conversation_id: str | None = None


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/genie/query-obo")
async def query_genie_obo(
    request: QueryRequest,
    authorization: str = Header(..., description="Bearer token from user"),
):
    """Query Genie using On-Behalf-Of (OBO) flow.

    Args:
        request: Query request containing query text and optional conversation_id
        authorization: User's bearer token

    Returns:
        Query result from Genie
    """
    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        user_token = authorization.replace("Bearer ", "")

        # Acquire Databricks token using OBO
        obo_auth = OBOAuth(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            databricks_resource_id=config.databricks_resource_id,
        )

        token_result = obo_auth.acquire_token_on_behalf_of(user_token)
        if not token_result or "access_token" not in token_result:
            raise HTTPException(status_code=401, detail="Failed to acquire Databricks token")

        databricks_token = token_result["access_token"]

        # Query Genie
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            result = genie.query_genie(
                space_id=config.genie_space_id,
                query=request.query,
                conversation_id=request.conversation_id,
            )

            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OBO query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/genie/query-app")
async def query_genie_app(request: QueryRequest):
    """Query Genie using App-to-App (client credentials) flow.

    Args:
        request: Query request containing query text and optional conversation_id

    Returns:
        Query result from Genie
    """
    try:
        # Acquire Databricks token using client credentials
        app_auth = AppToAppAuth(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            databricks_resource_id=config.databricks_resource_id,
        )

        token_result = app_auth.acquire_token()
        if not token_result or "access_token" not in token_result:
            raise HTTPException(status_code=401, detail="Failed to acquire Databricks token")

        databricks_token = token_result["access_token"]

        # Query Genie
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            result = genie.query_genie(
                space_id=config.genie_space_id,
                query=request.query,
                conversation_id=request.conversation_id,
            )

            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in app-to-app query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/genie/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    authorization: str = Header(..., description="Bearer token from user"),
):
    """Get conversation details using OBO flow.

    Args:
        conversation_id: Conversation ID
        authorization: User's bearer token

    Returns:
        Conversation details
    """
    try:
        # Extract token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        user_token = authorization.replace("Bearer ", "")

        # Acquire Databricks token using OBO
        obo_auth = OBOAuth(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            databricks_resource_id=config.databricks_resource_id,
        )

        token_result = obo_auth.acquire_token_on_behalf_of(user_token)
        if not token_result or "access_token" not in token_result:
            raise HTTPException(status_code=401, detail="Failed to acquire Databricks token")

        databricks_token = token_result["access_token"]

        # Get conversation
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            conversation = genie.get_conversation(config.genie_space_id, conversation_id)

            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            return conversation.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/genie/conversation/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    authorization: str = Header(..., description="Bearer token from user"),
):
    """List messages in a conversation using OBO flow.

    Args:
        conversation_id: Conversation ID
        authorization: User's bearer token

    Returns:
        List of messages
    """
    try:
        # Extract token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        user_token = authorization.replace("Bearer ", "")

        # Acquire Databricks token using OBO
        obo_auth = OBOAuth(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            databricks_resource_id=config.databricks_resource_id,
        )

        token_result = obo_auth.acquire_token_on_behalf_of(user_token)
        if not token_result or "access_token" not in token_result:
            raise HTTPException(status_code=401, detail="Failed to acquire Databricks token")

        databricks_token = token_result["access_token"]

        # List messages
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            messages = genie.list_messages(config.genie_space_id, conversation_id)
            return {"messages": [msg.model_dump() for msg in messages]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.api_host, port=config.api_port)
