
from jira import JIRA, Issue

from configuration import Settings
from src.service import jira_factory


def test_create_jira_instance():

    # Define test parameters
    jira = jira_factory.create()

    # Call the method
    new_issue = jira.create_issue(project='BB', summary="testing summary",
                                  description="test description", issuetype={'name': 'Task'})
    # Assertions
    assert isinstance(jira, JIRA)
    assert isinstance(new_issue, Issue)