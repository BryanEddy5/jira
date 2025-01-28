from src.adapters.secondary.jira import jira_factory
from src.adapters.secondary.jira.jira_adapter import Issue, JiraAdapter
from src.domain.models import CreateIssueRequest, IssueType


def test_create_jira_ticket() -> None:
    """Test create JIRA ticket."""
    # Define test parameters
    jira = jira_factory.create()

    # Call the method using domain model
    request = CreateIssueRequest(
        project_key="BB",
        summary="Test Summary",
        description="Test Description",
        issue_type=IssueType.TASK,
    )
    new_issue = jira.create_issue(request)

    issue = jira.get_issue(new_issue.key)

    # Assertions
    assert isinstance(jira, JiraAdapter)
    assert isinstance(new_issue, Issue)
    assert new_issue.key == issue.key
    assert isinstance(issue, Issue)
    assert issue.issue_type == "Task"
    jira.delete_issue(new_issue.key)
