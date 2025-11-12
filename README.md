# Databricks Genie Integration

FastAPI-based integration with Azure Databricks Genie Conversation API, supporting  On-Behalf-Of (OBO) , OAuth App-to-App , PAT authentication flows.

## Prerequisites:

- ADB workspace with Genie enabled and a Genie space created linked wth delta table schema.
- An Azure AD application with:
  - `user_impersonation` delegated permission for ADB workspace for OBO flow
  - Azure AD application added to ADB workspace for App-to-App flow


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

**Requires**: User must have Genie space access

```bash
POST /genie/query-obo
Authorization: Bearer <user-token>

{
  "query": "Show me sales by region",
  "conversation_id": "optional-conversation-id"
}
```

### Query Genie (App-to-App Flow)

**Requires**: Service principal must be added to workspace AND granted Genie space access

```bash
POST /genie/query-app

{
  "query": "Show me sales by region",
  "conversation_id": "optional-conversation-id"
}
```

## Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

For architecture and design decisions, see [CLAUDE.md](CLAUDE.md)

## Development

### Pre-commit Hooks

The project uses pre-commit hooks for code quality and security:

```bash
# Install hooks (done automatically during uv sync)
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks include:
- **Ruff**: Linting and formatting
- **Bandit**: Security scanning
- **Gitleaks**: Secret detection
