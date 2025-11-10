"""Configuration models for Databricks Genie integration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", populate_by_name=True)

    # Azure AD Configuration
    tenant_id: str = Field(..., description="Azure AD tenant ID")
    client_id: str = Field(..., description="Azure AD client/application ID")
    client_secret: str = Field(..., description="Azure AD client secret")

    # Databricks Configuration
    databricks_resource_id: str = Field(description="Databricks Azure resource ID")

    # Genie Configuration
    genie_workspace_url: str = Field(
        ..., validation_alias="GENIE__WORKSPACE_URL", description="Databricks workspace URL"
    )
    genie_space_id: str = Field(..., validation_alias="GENIE__SPACE_ID", description="Genie space ID")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")  # nosec B104
    api_port: int = Field(default=8000, description="API port")
