import os

from pydantic import (
    Field,
)

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding='utf-8')
    jira_api_key: str = Field(alias='JIRA_API_KEY', default="missing")
    jira_user_email: str = Field(default="bryan.eddy@shippo.com", alias='JIRA_USER_EMAIL')