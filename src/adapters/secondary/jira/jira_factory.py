from jira import JIRA
from src.adapters.secondary.jira.jira_adapter import JiraAdapter
from src.lib.configuration import Settings

_settings = Settings()
_jira = JIRA(
    server=_settings.jira_server,
    basic_auth=(_settings.jira_user_email, _settings.jira_api_key),
)
_adapter = JiraAdapter(_jira)


def create() -> JiraAdapter:
    """Create and return a configured JiraAdapter instance."""
    return _adapter
