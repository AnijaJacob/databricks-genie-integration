# Swagger OAuth Setup Guide

## Overview

This guide explains how to set up interactive browser-based authentication for the Swagger UI using Azure AD OAuth2 with Authorization Code Flow + PKCE.

## Architecture

The setup uses a **single Azure AD app registration** (`CLIENT_ID`) for both:
- Backend API authentication (OBO flow)
- Swagger UI interactive login (Authorization Code Flow + PKCE)

## Azure AD App Registration Setup

### 1. Add Redirect URI to Existing App Registration

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Open your existing app registration: `a36bace0-849e-46d9-82c5-ac4eda6a60ed`
3. Click on "Authentication" in the left sidebar
4. Under "Platform configurations", click "Add a platform"
5. Select "Single-page application"
6. Add redirect URI:
   - **Local dev**: `http://localhost:8000/docs/oauth2-redirect`
   - **Production**: `https://your-domain.com/docs/oauth2-redirect`
7. Click "Configure"

### 2. Verify API Permissions

Ensure your app registration has the following API permissions (should already be configured):

1. Go to "API permissions"
2. Verify you have:
   - **Azure Databricks** (`2ff814a6-3304-4ab8-85cb-cd0e6f879c1d`)
   - **Delegated permission**: `user_impersonation`
   - **Admin consent granted**: ✅
3. If not present, add the permission and grant admin consent
<!--
### 3. Configure Authentication Settings

1. Go to "Authentication" in your app registration
2. Under "Implicit grant and hybrid flows":
   - ✅ **Do NOT** check "Access tokens"
   - ✅ **Do NOT** check "ID tokens"
   - (We use Authorization Code Flow with PKCE, not implicit flow)
3. Under "Advanced settings":
   - **Allow public client flows**: No
4. Click "Save" -->

## Environment Configuration

Your `.env` file should have (no changes needed):

```bash
# Azure AD Configuration
TENANT_ID=your-tenant-id
CLIENT_ID=a36bace0-849e-46d9-82c5-ac4eda6a60ed  # Same app registration for both API and Swagger
CLIENT_SECRET=your-client-secret

# Databricks Configuration
DATABRICKS_RESOURCE_ID=2ff814a6-3304-4ab8-85cb-cd0e6f879c1d

# Genie Configuration
GENIE__WORKSPACE_URL=https://adb-xxxxx.azuredatabricks.net
GENIE__SPACE_ID=your-genie-space-id

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## Testing the Setup

### 1. Start the Application

```bash
uv run uvicorn app:app --reload
```

### 2. Access Swagger UI

Navigate to: `http://localhost:8000/docs`

### 3. Authenticate

1. Click the "Authorize" button (lock icon) at the top right
2. In the "AzureOAuth" section, the client ID should be pre-filled
3. Click "Authorize"
4. You'll be redirected to Microsoft login page
5. Sign in with your Azure AD account
6. Grant consent for the Databricks permissions
7. You'll be redirected back to Swagger UI
8. The lock icon should now appear closed/locked

### 4. Test an Endpoint

1. Try the `/genie/query-obo` endpoint
2. Click "Try it out"
3. Enter a query in the request body
4. Click "Execute"
5. The request should succeed with the OAuth token automatically included

## How It Works

### Authorization Code Flow with PKCE

1. **User clicks "Authorize"** in Swagger UI
2. **Browser redirects** to Azure AD login page with PKCE challenge
3. **User authenticates** and grants consent
4. **Azure AD redirects back** to `/docs/oauth2-redirect` with authorization code
5. **Swagger UI exchanges code** for access token using PKCE verifier
6. **Token is stored** in browser memory and included in API requests
7. **Backend API** receives token and uses it for OBO flow to get Databricks token

### Security Features

- **PKCE (Proof Key for Code Exchange)**: Prevents authorization code interception attacks
- **No client secret**: Swagger UI app doesn't need a secret (public client)
- **Token stays in browser**: Never sent to backend, only used for API calls
- **Short-lived tokens**: Access tokens expire and require re-authentication

## Troubleshooting

### "AADSTS65001: The user or administrator has not consented"

**Solution**: Grant admin consent for the Databricks API permissions in your app registration.

### "AADSTS50011: The redirect URI specified in the request does not match"

**Solution**: Ensure the redirect URI in your app registration exactly matches `http://localhost:8000/docs/oauth2-redirect` (or your production URL).

### "AADSTS7000218: The request body must contain the following parameter: 'client_assertion'"

**Solution**: This error occurs if the app is configured incorrectly. Ensure "Allow public client flows" is set to "No" and you're using SPA redirect URI type.

### "Failed to acquire Databricks token" after successful login

**Possible causes**:

1. Backend API app registration doesn't have OBO permissions for Databricks
2. Databricks resource ID is incorrect
3. User doesn't have access to Databricks workspace

### Token appears in Swagger UI but API calls fail with 401

**Solution**:

1. Check that the backend API properly validates the token
2. Verify OBO flow is working correctly
3. Check that user has appropriate Databricks permissions

## Production Deployment

When deploying to production:

1. **Update redirect URI** in Azure AD app registration:

   ```text
   https://your-production-domain.com/docs/oauth2-redirect
   ```

2. **Add production URI** to app registration (keep localhost for local dev):
   - Platform: `Single-page application (SPA)`
   - URI: `https://your-production-domain.com/docs/oauth2-redirect`

3. **HTTPS required**: Azure AD requires HTTPS for redirect URIs (except localhost)

4. **Consider network restrictions**: Configure conditional access policies if needed

## References

- [Microsoft Authentication Library (MSAL) Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview)
- [OAuth 2.0 Authorization Code Flow with PKCE](https://oauth.net/2/pkce/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Databricks Azure AD Integration](https://docs.databricks.com/administration-guide/users-groups/single-sign-on/azure-ad.html)
