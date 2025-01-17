from jira import JIRA
from pydantic import HttpUrl

from configuration import Settings

_settings = Settings()


def create(server: HttpUrl  = "https://shippo.atlassian.net", ) -> JIRA:
    jira = JIRA(server=server, basic_auth=(_settings.jira_user_email, _settings.jira_api_key))
    return jira
