# Databricks Genie Integration

## Overview
This project provides a FastAPI-based integration with Azure Databricks Genie Conversation API with interactive Swagger UI authentication using Azure AD OAuth2.

## Architecture

### Authentication Flows

#### Primary Flow: OBO (On-Behalf-Of) - RECOMMENDED
- **Use Case**: User-initiated queries with full user context preservation
- **Flow**:
  1. User authenticates via Swagger UI using Azure AD OAuth2 (Authorization Code Flow + PKCE)
  2. User receives token scoped to this API (`{client_id}/.default`)
  3. API receives user's token in Authorization header
  4. API performs OBO flow to exchange user token for Databricks token
  5. API calls Databricks Genie with Databricks token
- **Benefits**: Maintains user identity, audit trail, and Databricks permissions
- **Endpoints**: `/genie/query-obo`, `/genie/conversation/{id}`, `/genie/conversation/{id}/messages`

#### Secondary Flow: App-to-App (Client Credentials) - LIMITED USE
- **Status**: ⚠️ **Blocked in current environment**
- **Reason**: Enterprise policy requires Service Principal (SPN) mapping via Azure API Management (APIM)
- **Limitation**: Direct app-to-app authentication to Databricks workspace is not permitted without APIM gateway
- **Future Consideration**: Can be enabled if APIM gateway is configured with SPN mapping policies
- **Current State**: Endpoint implemented (`/genie/query-app`) but non-functional without APIM setup

### Key Components
- **src/auth/msal_auth.py**: MSAL-based authentication handlers for both OBO and App-to-App flows
- **src/api/genie_client.py**: HTTP client for Databricks Genie Conversation API
- **src/models/**: Pydantic models for configuration and API data structures
- **src/swagger/**: Custom Swagger UI implementation with Azure AD OAuth2 support
  - **routing/swagger_ui.py**: Custom Swagger UI HTML generation with OAuth2 redirect handling
  - **routing/openapi.py**: OpenAPI schema configuration with Authorization Code Flow + PKCE
- **app.py**: FastAPI application with interactive Swagger authentication and Genie endpoints

## Technology Stack
- **FastAPI**: Modern async web framework
- **MSAL**: Microsoft Authentication Library for Azure AD token acquisition
- **httpx**: Async HTTP client for Databricks API calls
- **Pydantic**: Data validation and settings management
- **uv**: Fast Python package manager

## Integration Points

### Databricks Genie API
The project integrates with the following Genie Conversation API endpoints:
- `POST /api/2.0/genie/spaces/{space_id}/conversations` - Create conversation
- `POST /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages` - Create message
- `GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}` - Get message
- `GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages` - List messages
- `GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}` - Get conversation

### Azure AD Integration
- Uses Microsoft Entra ID (Azure AD) for authentication
- Single app registration (`a36bace0-849e-46d9-82c5-ac4eda6a60ed`) for both API and Swagger UI
- Interactive browser-based authentication via Swagger UI with Authorization Code Flow + PKCE
- Workspace-specific Databricks resource ID: `aa5bd296-7205-4063-93e5-e4ed0d9ca3e2`
- Required API permissions:
  - **Azure Databricks** - `user_impersonation` (Delegated) - Requires admin consent
  - **Microsoft Graph** - Pre-configured permissions
- Redirect URI configuration:
  - Platform: Single-page application (SPA)
  - URI: `http://localhost:8000/docs/oauth2-redirect` (local dev)
  - Production: `https://{your-domain}/docs/oauth2-redirect`

## Design Decisions

### Why Single App Registration for Both API and Swagger?
- **Simplified configuration**: One app registration to manage instead of two
- **Consistent permissions**: Same delegated permissions apply to both flows
- **User experience**: Users consent once to access the API
- **Token flow**: Swagger requests token for API (`{client_id}/.default`), API performs OBO to Databricks

### Why Authorization Code Flow + PKCE for Swagger?
- **Security**: PKCE prevents authorization code interception attacks
- **No client secret**: Public client pattern suitable for browser-based authentication
- **User consent**: Prompts proper consent flow for delegated permissions
- **Standards compliant**: Recommended OAuth2 flow for SPAs and browser-based clients

### Why OBO Flow Over Direct Databricks Authentication?
- **User context preservation**: Maintains user identity throughout the flow
- **Audit trail**: Databricks logs show actual user actions, not service principal
- **Permission inheritance**: Respects user's Databricks workspace permissions
- **Compliance**: Better for regulated environments requiring user attribution

### Why MSAL over direct OAuth2?
MSAL provides built-in token caching, automatic refresh, and better error handling for Azure AD flows.

### Why httpx over requests?
httpx provides async support and better performance for concurrent API calls, aligning with FastAPI's async capabilities.

### Context Managers for GenieClient
The client uses context managers to ensure proper cleanup of HTTP connections, preventing resource leaks.

## Configuration
All configuration is managed through environment variables via Pydantic Settings:
- **Azure AD credentials**: tenant ID, client ID, client secret
- **Databricks workspace**: workspace URL, Genie space ID, resource ID
- **API server settings**: host, port

See `.env.example` for all required variables.

## Security Considerations
- Credentials stored in `.env` (never committed to git)
- Token acquisition failures are logged but tokens never exposed in logs
- Pre-commit hooks enforce security checks via bandit and gitleaks
- PKCE flow prevents authorization code interception
- No client secrets in browser (Swagger uses public client pattern)
- Tokens stored only in browser memory, never persisted

## Known Limitations & Enterprise Constraints

### APIM Requirement for App-to-App Flow
- **Finding**: Direct Service Principal (SPN) authentication to Databricks workspace is blocked
- **Error**: `AADSTS501051: Application is not assigned to a role for the application`
- **Root Cause**: Enterprise policy requires SPN mapping via Azure API Management (APIM)
- **Impact**: `/genie/query-app` endpoint is non-functional without APIM gateway
- **Workaround**: Use OBO flow (`/genie/query-obo`) which authenticates via user identity
- **Future Solution**: Configure APIM gateway with SPN mapping policies if app-to-app authentication is required

### Admin Consent Requirement
- **Finding**: Delegated Databricks permission requires admin consent despite being marked "Admin consent not required"
- **Reason**: Tenant-level policies may restrict user consent for certain API permissions
- **Solution**: Admin must grant consent via Azure Portal → App registrations → API permissions → "Grant admin consent"
- **Alternative**: Users see "Request approval" screen and must wait for admin approval

## Getting Started

1. **Configure Azure AD App Registration**: See `docs/swagger-oauth-setup.md`
2. **Set environment variables**: Copy `.env.example` to `.env` and fill in values
3. **Request admin consent**: For Azure Databricks delegated permission
4. **Run the application**: `uv run uvicorn app:app --reload`
5. **Access Swagger UI**: Navigate to `http://localhost:8000/docs`
6. **Authenticate**: Click "Authorize" and sign in with Azure AD credentials
7. **Test OBO endpoint**: Use `/genie/query-obo` to query Databricks Genie
