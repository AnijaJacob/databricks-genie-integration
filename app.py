"""FastAPI application for Databricks Genie integration."""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse

from src.models.config import Config
from src.routers import genie
from src.swagger.routing.openapi import create_swagger_ui_oauth_params, set_azure_ad_openapi
from src.swagger.routing.swagger_ui import get_swagger_ui_html

# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)

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

# Load configuration
config = Config()

# Initialize FastAPI app
app = FastAPI(
    title="Databricks Genie Integration",
    description="API for interacting with Databricks Genie using OBO and App-to-App authentication",
    version="0.1.0",
    docs_url=None,  # Disable default docs to use custom OAuth
    redoc_url=None,
)

# Configure Azure AD OAuth for OpenAPI
set_azure_ad_openapi(
    app=app,
    client_id=config.client_id,
    tenant_id=config.tenant_id,
    databricks_resource_id=config.databricks_resource_id,
)


app.include_router(genie.router, prefix="/genie", tags=["Genie"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    """Custom Swagger UI with Azure AD OAuth2."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=app.title,
        oauth2_redirect_url="/docs/oauth2-redirect",
        init_oauth=create_swagger_ui_oauth_params(config.client_id),
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    """OAuth2 redirect endpoint for Swagger UI."""
    return get_swagger_ui_oauth2_redirect_html()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.api_host, port=config.api_port)
