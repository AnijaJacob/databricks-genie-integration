# Databricks Genie Integration

## Overview
This project provides a FastAPI-based integration with Azure Databricks Genie Conversation API, supporting both On-Behalf-Of (OBO) and App-to-App authentication flows.

## Architecture

### Authentication Flows
1. **OBO (On-Behalf-Of)**: Allows the API to act on behalf of an authenticated user, maintaining user context in Databricks
2. **App-to-App**: Uses client credentials flow for service-to-service authentication without user context

### Key Components
- **src/auth/msal_auth.py**: MSAL-based authentication handlers for both OBO and App-to-App flows
- **src/api/genie_client.py**: HTTP client for Databricks Genie Conversation API
- **src/models/**: Pydantic models for configuration and API data structures
- **app.py**: FastAPI application with endpoints for querying Genie

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
- Requires app registration with appropriate Databricks permissions
- Default Databricks resource ID: `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d`

## Design Decisions

### Why MSAL over direct OAuth2?
MSAL provides built-in token caching, automatic refresh, and better error handling for Azure AD flows.

### Why httpx over requests?
httpx provides async support and better performance for concurrent API calls, aligning with FastAPI's async capabilities.

### Context Managers for GenieClient
The client uses context managers to ensure proper cleanup of HTTP connections, preventing resource leaks.

## Configuration
All configuration is managed through environment variables via Pydantic Settings:
- Azure AD credentials (tenant, client ID, secret)
- Databricks workspace URL and Genie space ID
- API server settings

## Security Considerations
- Credentials stored in `.env` (never committed to git)
- Token acquisition failures are logged but tokens never exposed in logs
- Pre-commit hooks enforce security checks via bandit and gitleaks
