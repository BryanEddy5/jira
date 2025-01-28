from pydantic import (
    Field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    jira_api_key: str = Field(validation_alias="JIRA_API_KEY")
    jira_user_email: str = Field(alias="JIRA_USER_EMAIL")
    jira_server: str = Field(
        default="https://shippo.atlassian.net",
        alias="JIRA_SERVER",
    )
