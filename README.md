# Databricks Genie Integration

FastAPI-based integration with Azure Databricks Genie Conversation API, supporting both On-Behalf-Of (OBO) and App-to-App authentication flows.

## Features

- **Dual Authentication**: Supports both OBO and App-to-App flows
- **Genie Conversation API**: Full integration with Databricks Genie
- **Modern Stack**: FastAPI, MSAL, httpx, Pydantic
- **Type-Safe**: Full type hints and Pydantic validation
- **Production-Ready**: Logging, error handling, security hooks

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required configuration:
- `TENANT_ID`: Azure AD tenant ID
- `CLIENT_ID`: Azure AD application/client ID
- `CLIENT_SECRET`: Azure AD client secret
- `GENIE__WORKSPACE_URL`: Databricks workspace URL
- `GENIE__SPACE_ID`: Genie space ID

### 3. Run the API

```bash
# Activate the virtual environment first
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows

# Run the app
python app.py
```

Or run directly with uv:
```bash
uv run python app.py
```

API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /health
```

### Query Genie (OBO Flow)
```bash
POST /genie/query-obo
Authorization: Bearer <user-token>

{
  "query": "Show me sales by region",
  "conversation_id": "optional-conversation-id"
}
```

### Query Genie (App-to-App Flow)
```bash
POST /genie/query-app

{
  "query": "Show me sales by region",
  "conversation_id": "optional-conversation-id"
}
```

### Get Conversation
```bash
GET /genie/conversation/{conversation_id}
Authorization: Bearer <user-token>
```

### List Messages
```bash
GET /genie/conversation/{conversation_id}/messages
Authorization: Bearer <user-token>
```

## Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

For architecture and design decisions, see [CLAUDE.md](CLAUDE.md)

## License

MIT
