from adapters.secondary.jira import jira_factory

from jira import JIRA, Issue


def test_create_jira_ticket():
    # Define test parameters
    jira = jira_factory.create()

    # Call the method
    new_issue = jira.create_issue(
        project="BB",
        summary="BB Test Task",
        description="test description",
        issuetype={"name": "Task"},
    )

    issue = jira.issue(new_issue.key)

    # Assertions
    assert isinstance(jira, JIRA)
    assert isinstance(new_issue, Issue)
    assert new_issue.key == issue.key
    assert isinstance(issue, Issue)
    assert issue.fields.issuetype.name == "Task"
    issue.delete()
