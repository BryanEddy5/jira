import os

from pydantic import (
    Field,
)

from dotenv import load_dotenv, dotenv_values

from pydantic_settings import BaseSettings, SettingsConfigDict

test = os.environ.get("JIRA_API_KEY")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars
        case_sensitive=False,  # Make env var names case-insensitive
    )
    jira_api_key: str = Field(validation_alias="JIRA_API_KEY")
    jira_user_email: str = Field(
        default="bryan.eddy@shippo.com", alias="JIRA_USER_EMAIL"
    )
    jira_server: str = Field(
        default="https://shippo.atlassian.net", alias="JIRA_SERVER"
    )
