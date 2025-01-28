import contextlib
from datetime import datetime, timedelta
from typing import Optional

import pytz
import typer

from src.adapters.secondary.jira import jira_factory
from src.domain.task_service import TaskService

jira_app = typer.Typer()
_jira = jira_factory.create()
_task_service = TaskService(_jira)


@jira_app.command()
def create(
    summary: str,
    description: str,
    date: Optional[str] = None,
    project: str = "BB",
) -> None:
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
    _jira.create_issue(fields=issue_dict)


@jira_app.command("list-projects")
def get_all_projects() -> None:
    """Get list of all projects from Jira."""
    projects = _task_service.get_all_projects()
    for _project in projects:
        print(_project.key)


@jira_app.command()
def get_issue(id: str) -> None:
    """Get details of a specific JIRA issue."""
    issue = _task_service.get_issue(id)
    print(issue.key, issue.summary)


@jira_app.command()
def rm(ids: list[str]) -> None:
    """Delete one or more JIRA issues."""
    for id in ids:
        issue = _jira.issue(id)
        if issue:
            print(f"Deleted issue {id}")
            issue.delete()


@jira_app.command()
def query(jql: str) -> None:
    """Query JIRA issues using JQL."""
    issues = _jira.search_issues(jql)
    for _issue in issues:
        print(_issue.key, _issue.fields.summary)


@jira_app.command()
def my_items() -> None:
    """Get items from your JIRA filter."""
    _jira.filter("15232")


@jira_app.command()
def health_check() -> None:
    """Check if JIRA API is accessible."""
    print(f"JIRA API is accessible. {_jira.jira.server_url}")
