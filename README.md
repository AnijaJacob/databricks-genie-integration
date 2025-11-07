# Databricks Genie Integration

FastAPI-based integration with Azure Databricks Genie Conversation API, supporting both On-Behalf-Of (OBO) and App-to-App authentication flows.

## Features

- **Dual Authentication**: Supports both OBO and App-to-App flows
- **Genie Conversation API**: Full integration with Databricks Genie
- **Modern Stack**: FastAPI, MSAL, httpx, Pydantic
- **Type-Safe**: Full type hints and Pydantic validation
- **Production-Ready**: Logging, error handling, security hooks

## Prerequisites

### Azure AD App Registration

#### 1. Create App Registration

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Enter a name (e.g., "Demo-app")
4. Select supported account types (usually "Single tenant")
5. Click **Register**
1. Go to **Certificates & secrets** → **Client secrets** tab
2. Click **New client secret**
3. Add description (e.g., "Genie Integration Secret")
4. Select expiration period
5. Click **Add**
6. **Copy the secret value immediately** → `CLIENT_SECRET` (you can't see it again!)

#### . Configure API Permissions for OBO Flow
**What this permission does**: Allows your application to access Databricks on behalf of the signed-in user, maintaining their identity and permissions.


To enable On-Behalf-Of authentication, add Databricks delegated permission:

1. Go to **API permissions** → **Add a permission**
2. Click **APIs my organization uses**
3. Search for **"Azure Databricks"** or **"AzureDatabricks"**
   - If not found, search by Application ID: `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d`
4. Click on **Azure Databricks** in the results
5. Select **Delegated permissions**
6. Check **user_impersonation** permission
7. Click **Add permissions**
8. (Optional but recommended) Click **Grant admin consent for [tenant]** - this allows users to use the app without individual consent



#### 5. Authentication Flow Summary

```
OBO Flow (user context):
User → Your App → Azure AD → Databricks (as user)
Requires: user_impersonation delegated permission

App-to-App Flow (service context):
Your App → Azure AD → Databricks (as service principal)
Requires: Service principal added to Databricks workspace
```

### Databricks Workspace Setup

The service principal (Azure AD app) **must be mapped to Databricks** for authentication to work:

#### 1. Add Service Principal to Databricks Workspace

**Option A: Using Databricks UI**
```
1. Go to Databricks Workspace → Settings → Identity and Access
2. Click "Service Principals" → "Add Service Principal"
3. Enter your CLIENT_ID (Azure AD Application ID)
4. Assign workspace role (User, Developer, or Admin)
```

**Option B: Using Databricks CLI**
```bash
databricks service-principals create \
  --application-id <CLIENT_ID> \
  --display-name "Genie Integration App"
```

**Option C: Using REST API**
```bash
curl -X POST https://<workspace-url>/api/2.0/account/scim/v2/ServicePrincipals \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServicePrincipal"],
    "applicationId": "<CLIENT_ID>",
    "displayName": "Genie Integration App"
  }'
```

#### 2. Grant Service Principal Access to Genie Space

After adding the service principal to the workspace:

```
1. Navigate to your Genie Space in Databricks
2. Click "Share" or "Permissions"
3. Add the service principal (search by CLIENT_ID or display name)
4. Grant "Can Use" or "Can Manage" permission
```

**Important**: Without this step, you'll get a `403 Forbidden` error when using the `/genie/query-app` endpoint.

#### 3. Verify Setup

To verify your service principal is correctly configured:

**Check via Databricks UI:**
```
1. Go to Settings → Identity and Access → Service Principals
2. Find your service principal by CLIENT_ID
3. Verify it has workspace access
```

**Check via REST API:**
```bash
curl -X GET "https://<workspace-url>/api/2.0/preview/scim/v2/ServicePrincipals" \
  -H "Authorization: Bearer <databricks-token>" \
  | jq '.Resources[] | select(.applicationId=="<CLIENT_ID>")'
```

**Test with a simple API call:**
```bash
# Get Databricks token using your app credentials
# Then test access to Genie space
curl -X POST "https://<workspace-url>/api/2.0/genie/spaces/<space-id>/conversations" \
  -H "Authorization: Bearer <databricks-token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

If successful, you should get a conversation ID. If you get 403, the service principal doesn't have space access.


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

**Requires**: Service principal must be added to workspace AND granted Genie space access (see Prerequisites)

```bash
POST /genie/query-app

{
  "query": "Show me sales by region",
  "conversation_id": "optional-conversation-id"
}
```

### Get Conversation

**Requires**: User must have Genie space access

```bash
GET /genie/conversation/{conversation_id}
Authorization: Bearer <user-token>
```

### List Messages

**Requires**: User must have Genie space access

```bash
GET /genie/conversation/{conversation_id}/messages
Authorization: Bearer <user-token>
```


## Troubleshooting

### 403 Forbidden Error

If you get `403 User not authorized` errors:

1. **For App-to-App flow** (`/genie/query-app`):
   - Verify service principal is added to Databricks workspace
   - Verify service principal has access to the Genie space
   - Check the space ID in `.env` is correct

2. **For OBO flow** (`/genie/query-obo`):
   - Verify the user (whose token you're using) has access to the Genie space
   - Verify the Azure AD app has `user_impersonation` delegated permission

### Token Acquisition Fails

If MSAL token acquisition fails:
- Verify `TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET` in `.env`
- Check Azure AD app has not expired
- Ensure client secret is valid and not expired

### Import Errors

If you see `ModuleNotFoundError`:
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Or use uv directly
uv run python app.py
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

## License

MIT
