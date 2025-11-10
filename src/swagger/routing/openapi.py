"""OpenAPI schema configuration with Azure AD OAuth."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def create_swagger_ui_oauth_params(client_id: str) -> dict:
    """Create OAuth parameters for Swagger UI.

    Args:
        client_id: Azure AD client ID
        databricks_resource_id: Databricks Azure resource ID

    Returns:
        Dictionary with OAuth parameters for Swagger UI
    """
    return {
        # "clientId": client_id,
        # "usePkceWithAuthorizationCodeGrant": True,
        # "scopes": [f"api://{client_id}/access_as_user"],
        "clientId": client_id,
        "usePkceWithAuthorizationCodeGrant": True,
        "useBasicAuthenticationWithAccessCodeGrant": True,
        "scopes": [f"{client_id}/.default"],
    }


def set_azure_ad_openapi(app: FastAPI, client_id: str | None, tenant_id: str | None, databricks_resource_id: str):
    """
    Configures OpenAPI schema with Azure AD authentication using authorization code flow with PKCE.

    Args:
        app: The FastAPI application instance
        client_id: Azure AD client ID
        tenant_id: Azure AD tenant ID
    """

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Clean up authorization parameters from routes
        paths = openapi_schema.get("paths", {})
        http_methods = ["get", "post", "patch", "delete", "put"]

        for path in paths:
            for http_method in http_methods:
                if http_method not in paths[path] or "parameters" not in paths[path][http_method]:
                    continue

                parameters: list[dict] = paths[path][http_method]["parameters"]
                openapi_schema["paths"][path][http_method]["parameters"] = list(
                    filter(
                        lambda param: param["name"].lower() != "authorization" or param["in"].lower() != "header",
                        parameters,
                    )
                )

        if client_id and tenant_id:
            # Configure Azure AD OAuth security scheme with authorization code flow + PKCE
            openapi_schema["components"]["securitySchemes"] = {
                "AzureOAuth": {
                    "type": "oauth2",
                    "flows": {
                        "authorizationCode": {
                            "authorizationUrl": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
                            "tokenUrl": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                            "scopes": {
                                # f"api://{client_id}/access_as_user": "Access API as user",
                                f"{client_id}/.default": "Default scopes",
                            },
                        }
                    },
                },
            }

            # Apply security requirement globally
            openapi_schema["security"] = [
                {"AzureOAuth": []},
            ]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
