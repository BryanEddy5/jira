from datetime import datetime, timedelta
from typing import List
import pytz
import typer
from src.adapters.secondary.jira import jira_factory

jira_app = typer.Typer()
_jira = jira_factory.create()


@jira_app.command()
def create(summary: str, description: str, date: str = None, project: str = "BB"):
    """Create a new JIRA issue."""
    if date is None:
        date = datetime.now(pytz.utc) + timedelta(weeks=1)
    issue_dict = {
        "project": project,
        "summary": summary,
        "description": description,
        "issuetype": {"name": "Task"},
        "duedate": date.strftime("%Y-%m-%d"),
    }
    new_issue = _jira.create_issue(fields=issue_dict)
    print(new_issue.key)


@jira_app.command()
def get_issue(id: str):
    """Get details of a specific JIRA issue."""
    issue = _jira.issue(id, expand="changelog")
    print(issue.key, issue.fields.summary)



@jira_app.command()
def rm(ids: List[str]):
    """Delete one or more JIRA issues."""
    for id in ids:
        try:
            issue = _jira.issue(id)
            if issue:
                issue.delete()
            print(f"Deleted issue {id}")
        except Exception as e:
            print(f"Error: {e}")


@jira_app.command()
def query(jql: str):
    """Query JIRA issues using JQL."""
    issues = _jira.search_issues(jql)
    for issue in issues:
        print(issue.key, issue.fields.summary)


@jira_app.command()
def my_items():
    """Get items from your JIRA filter."""
    jira_filter = _jira.filter("15232")
    print(jira_filter.raw)


@jira_app.command()
def health_check():
    """Check if JIRA API is accessible."""
    try:
        _jira.myself()
        print("Jira API is up and running.")
    except Exception as e:
        print(f"Health check failed: {e}")
