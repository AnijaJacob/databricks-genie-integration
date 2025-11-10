"""Custom Swagger UI HTML generation with OAuth2 support."""

import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse

swagger_ui_default_parameters = {
    "layout": "StandaloneLayout",
    "deepLinking": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "displayRequestDuration": True,
    "persistAuthorization": True,
}


def get_swagger_ui_html(
    openapi_url: str,
    title: str,
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
    swagger_ui_parameters: dict[str, Any] | None = None,
    oauth2_redirect_url: str | None = None,
    init_oauth: dict[str, Any] | None = None,
) -> HTMLResponse:
    """
    Generate and return the HTML that loads Swagger UI for the interactive
    API docs (normally served at `/docs`).

    Args:
        openapi_url: URL to the OpenAPI schema
        title: Title of the API documentation
        swagger_favicon_url: URL to favicon
        swagger_ui_parameters: Additional Swagger UI parameters
        oauth2_redirect_url: OAuth2 redirect URL for authentication
        init_oauth: OAuth initialization parameters

    Returns:
        HTMLResponse with Swagger UI HTML
    """
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
    window.onload = function() {{
        const ui = SwaggerUIBundle({{
        url: "{openapi_url}",
    """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(jsonable_encoder(value))},\n"

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += """
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
        ],
        plugins: [
            SwaggerUIBundle.plugins.DownloadUrl
        ],
      })
      window.ui = ui
    """

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """

    html += """
    }
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)
