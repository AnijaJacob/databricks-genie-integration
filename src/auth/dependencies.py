"""Authentication dependencies for FastAPI routes."""

import logging

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


def get_access_token(request: Request) -> str:
    """
    Dependency to extract access token from Authorization header.

    Args:
        request: FastAPI Request object

    Returns:
        Access token string

    Raises:
        HTTPException: If no valid token found
    """
    authorization = request.headers.get("authorization", "")

    if authorization.startswith("Bearer "):
        token = authorization.split("Bearer ")[-1]
        if token:
            return token

    raise HTTPException(status_code=401, detail="Not authenticated")


def get_optional_access_token(request: Request) -> str | None:
    """
    Dependency to extract access token from Authorization header (optional).

    Args:
        request: FastAPI Request object

    Returns:
        Access token string or None if not present
    """
    authorization = request.headers.get("authorization", "")

    if authorization.startswith("Bearer "):
        return authorization.split("Bearer ")[-1]

    return None
