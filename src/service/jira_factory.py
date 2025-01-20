from jira import JIRA

from src.lib.configuration import Settings

_settings = Settings()
_jira = JIRA(
    server=_settings.jira_server,
    basic_auth=(_settings.jira_user_email, _settings.jira_api_key),
)


def create() -> JIRA:
    return _jira
