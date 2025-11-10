"""MSAL-based authentication for Databricks."""

import logging
from typing import Any

import msal

logger = logging.getLogger(__name__)


class OBOAuth:
    """On-Behalf-Of (OBO) authentication flow for Databricks."""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, databricks_resource_id: str):
        """Initialize OBO authentication.

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application/client ID
            client_secret: Azure AD client secret
            databricks_resource_id: Databricks Azure resource ID (default is global Databricks resource)
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.databricks_resource_id = databricks_resource_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"

        self.app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=self.authority,
        )

    def acquire_token_on_behalf_of(self, user_token: str) -> dict[str, Any] | None:
        """Acquire Databricks token on behalf of user.

        Args:
            user_token: User's access token from the calling application

        Returns:
            Token response containing access_token or None if failed
        """
        scopes = [f"{self.databricks_resource_id}/user_impersonation"]

        try:
            result = self.app.acquire_token_on_behalf_of(
                user_assertion=user_token,
                scopes=scopes,
            )

            if "access_token" in result:
                logger.info("Successfully acquired OBO token", result)
                return result
            else:
                logger.error(f"Failed to acquire OBO token: {result.get('error_description')}")
                return None

        except Exception as e:
            logger.error(f"Exception during OBO token acquisition: {e}")
            return None


class AppToAppAuth:
    """App-to-App (client credentials) authentication flow for Databricks."""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, databricks_resource_id: str):
        """Initialize App-to-App authentication.

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application/client ID
            client_secret: Azure AD client secret
            databricks_resource_id: Databricks Azure resource ID (default is global Databricks resource)
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.databricks_resource_id = databricks_resource_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"

        self.app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=self.authority,
        )

    def acquire_token(self) -> dict[str, Any] | None:
        """Acquire Databricks token using client credentials.

        Returns:
            Token response containing access_token or None if failed
        """
        scopes = [f"{self.databricks_resource_id}/.default"]

        try:
            # Check cache first
            result = self.app.acquire_token_silent(scopes=scopes, account=None)

            if not result:
                logger.info("No cached token, acquiring new token")
                result = self.app.acquire_token_for_client(scopes=scopes)

            if "access_token" in result:
                logger.info("Successfully acquired app-to-app token")
                return result
            else:
                logger.error(f"Failed to acquire token: {result.get('error_description')}")
                return None

        except Exception as e:
            logger.error(f"Exception during token acquisition: {e}")
            return None
