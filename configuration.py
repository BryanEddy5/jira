import os

from pydantic import (
    Field,
)

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding="utf-8")
    jira_api_key: str = Field(validation_alias="JIRA_API_KEY")
    jira_user_email: str = Field(
        default="bryan.eddy@shippo.com", alias="JIRA_USER_EMAIL"
    )
    jira_server: str = Field(
        default="https://shippo.atlassian.net", alias="JIRA_SERVER"
    )
