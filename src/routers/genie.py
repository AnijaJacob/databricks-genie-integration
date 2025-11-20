import logging

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.dependencies import get_access_token
from src.auth.msal_auth import AppToAppAuth, OBOAuth
from src.models.config import Config
from src.routers.schema import FollowupRequest, QueryRequest
from src.services.genie_client import GenieClient

logger = logging.getLogger(__name__)

router = APIRouter()
config = Config()
security = HTTPBearer(auto_error=False)


@router.post("/new-conversation/obo")
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
            )

            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OBO query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new-conversation/app")
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


@router.post("/new-conversation/pat")
async def query_genie_pat(
    query_request: QueryRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
):
    """Query Genie using PAT flow.

    Args:
        request: Query request containing query text and optional conversation_id
        credentials: Databricks PAT token

    Returns:
        Query result from Genie
    """
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Missing Authorization header with PAT token")

        databricks_token = credentials.credentials
        # Query Genie
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            result = genie.query_genie(
                space_id=config.genie_space_id,
                query=query_request.query,
            )

            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OBO query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message")
async def create_followup(
    query_request: FollowupRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
):
    """Query Genie using PAT flow.

    Args:
        request: Query request containing query text and optional conversation_id
        credentials: Databricks PAT token

    Returns:
        Query result from Genie
    """
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Missing Authorization header with PAT token")

        databricks_token = credentials.credentials
        # Query Genie
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            result = genie.create_message(
                space_id=config.genie_space_id,
                content=query_request.query,
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


@router.get("/conversation/{conversation_id}/messages/{message_id}")
async def get_message(
    conversation_id: str,
    message_id: str,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
):
    """List messages in a conversation using OBO flow.

    Args:
        conversation_id: Conversation ID
        message_id: Message ID
        authorization: User's bearer token

    Returns:
        List of messages
    """
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Missing Authorization header with PAT token")

        databricks_token = credentials.credentials

        # List messages
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            message = genie.get_message(config.genie_space_id, conversation_id, message_id)
            return message

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}/messages/{message_id}/query-result/{attachment_id}")
async def get_query_result_attachment(
    conversation_id: str,
    message_id: str,
    attachment_id: str,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
):
    """Get a query result attachment from a Genie message.

    Args:
        conversation_id: Conversation ID
        message_id: Message ID
        attachment_id: Attachment ID
        credentials: Databricks PAT token

    Returns:
        Query result attachment data
    """
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Missing Authorization header with PAT token")

        databricks_token = credentials.credentials

        # Get query result attachment
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            attachment = genie.get_query_result_attachment(
                config.genie_space_id, conversation_id, message_id, attachment_id
            )
            
            if not attachment:
                raise HTTPException(status_code=404, detail="Query result attachment not found")
            
            return attachment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting query result attachment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/new-conversation-sdk/pat")
async def query_genie_pat(
    query_request: QueryRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
):
    """Query Genie using PAT flow.

    Args:
        request: Query request containing query text and optional conversation_id
        credentials: Databricks PAT token

    Returns:
        Query result from Genie
    """
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Missing Authorization header with PAT token")

        databricks_token = credentials.credentials
        # Query Genie
        with GenieClient(config.genie_workspace_url, databricks_token) as genie:
            conv_id, message_id, attachment_id, answer = genie.start_conversation_and_wait(
                space_id=config.genie_space_id,
                question=query_request.query,
            )

            query_results = genie.fetch_attachment_results(
                space_id=config.genie_space_id,
                conversation_id=conv_id,
                message_id=message_id,
                attachment_id=attachment_id,
            )
            response = {
                    "conversation_id": conv_id,
                    "message_id": message_id,
                    "attachment_id": attachment_id,
                    "answer": answer,
                    "query_results": query_results.as_dict() if query_results else None,
                }
                
            return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OBO query: {e}")
        raise HTTPException(status_code=500, detail=str(e))