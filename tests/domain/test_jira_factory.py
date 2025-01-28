from src.adapters.secondary.jira import jira_factory
from src.adapters.secondary.jira.jira_adapter import Issue, JiraAdapter


def test_create_jira_ticket() -> None:
    """Test create JIRA ticket."""
    # Define test parameters
    jira = jira_factory.create()

    # Call the method
    fields = {
        "project": "BB",
        "summary": "Test Summary",
        "description": "Test Description",
        "issuetype": {"name": "Task"},
    }
    new_issue = jira.create_issue(fields=fields)

    issue = jira.get_issue(new_issue.key)

    # Assertions
    assert isinstance(jira, JiraAdapter)
    assert isinstance(new_issue, Issue)
    assert new_issue.key == issue.key
    assert isinstance(issue, Issue)
    assert issue.issue_type == "Task"
    jira.delete_issue(new_issue.key)
