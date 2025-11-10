import logging

from fastapi import APIRouter, Depends, HTTPException

from src.auth.dependencies import get_access_token
from src.auth.msal_auth import AppToAppAuth, OBOAuth
from src.models.config import Config
from src.routers.schema import QueryRequest
from src.services.genie_client import GenieClient

logger = logging.getLogger(__name__)

router = APIRouter()
config = Config()


@router.post("/query-obo")
async def query_genie_obo(
    query_request: QueryRequest,
    access_token: str = Depends(get_access_token),
):
    """Query Genie using On-Behalf-Of (OBO) flow.

    Args:
        request: Query request containing query text and optional conversation_id
        authorization: User's bearer token

    Returns:
        Query result from Genie
    """
    try:
        logger.debug(f"User token: {access_token[:20]}...")
        # Acquire Databricks token using OBO
        obo_auth = OBOAuth(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            databricks_resource_id=config.databricks_resource_id,
        )

        token_result = obo_auth.acquire_token_on_behalf_of(access_token)
        if not token_result or "access_token" not in token_result:
            raise HTTPException(status_code=401, detail="Failed to acquire Databricks token")

        databricks_token = token_result["access_token"]

        # Query Genie
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            result = genie.query_genie(
                space_id=config.genie_space_id,
                query=query_request.query,
                conversation_id=query_request.conversation_id,
            )

            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OBO query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-app")
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


@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    access_token: str = Depends(get_access_token),
):
    """Get conversation details using OBO flow.

    Args:
        conversation_id: Conversation ID
        authorization: User's bearer token

    Returns:
        Conversation details
    """
    try:
        # Acquire Databricks token using OBO
        obo_auth = OBOAuth(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            databricks_resource_id=config.databricks_resource_id,
        )

        token_result = obo_auth.acquire_token_on_behalf_of(access_token)
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


@router.get("/conversation/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    access_token: str = Depends(get_access_token),
):
    """List messages in a conversation using OBO flow.

    Args:
        conversation_id: Conversation ID
        authorization: User's bearer token

    Returns:
        List of messages
    """
    try:
        # Acquire Databricks token using OBO
        obo_auth = OBOAuth(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            databricks_resource_id=config.databricks_resource_id,
        )

        token_result = obo_auth.acquire_token_on_behalf_of(access_token)
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
