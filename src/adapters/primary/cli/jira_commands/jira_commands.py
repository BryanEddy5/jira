"""CLI commands for interacting with JIRA."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytz
import typer

from src.adapters.secondary.jira import jira_factory
from src.domain.task_service import TaskService
from src.domain.jira_plan_service import JiraPlanService

jira_app = typer.Typer()
_jira = jira_factory.create()
_task_service = TaskService(_jira)
_jira_plan_service = JiraPlanService(_jira)


@jira_app.command()
def create(
    summary: str,
    description: str,
    date: str | None = None,
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
def get_issue(issue_id: str) -> None:
    """Get details of a specific JIRA issue."""
    issue = _task_service.get_issue(issue_id)
    print(issue.key, issue.summary)


@jira_app.command()
def rm(issue_ids: list[str]) -> None:
    """Delete one or more JIRA issues."""
    for issue_id in issue_ids:
        issue = _jira.issue(issue_id)
        if issue:
            print(f"Deleted issue {issue_id}")
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


@jira_app.command()
def create_plan(
    issue_ids: list[str],
    name: str = typer.Option(..., help="Name of the Jira Plan"),
    lead_email: str | None = typer.Option(None, help="Email address of the plan lead"),
) -> None:
    """Create a Jira Plan from a list of issue IDs.

    This command will:
    1. Get the root issues from the provided IDs
    2. Recursively get all parent issues (epics, initiatives)
    3. Recursively get all child issues (stories, tasks, bugs)
    4. Generate a JQL query that includes all related issues
    5. Create a Jira Plan with all discovered issues
    """
    plan, response = _jira_plan_service.create_plan(issue_ids, name, lead_email)

    print(f"\nRoot Issues ({len(plan.root_issues)}):")
    for issue in plan.root_issues:
        print(f"- {issue.key}: {issue.summary} ({issue.issue_type})")

    if plan.parent_issues:
        print(f"\nParent Issues ({len(plan.parent_issues)}):")
        for issue in plan.parent_issues:
            print(f"- {issue.key}: {issue.summary} ({issue.issue_type})")

    if plan.child_issues:
        print(f"\nChild Issues ({len(plan.child_issues)}):")
        for issue in plan.child_issues:
            print(f"- {issue.key}: {issue.summary} ({issue.issue_type})")

    print("\nJQL to fetch all related issues:")
    print(plan.jql)

    print("\nJira Plan created successfully:")
    print(f"Name: {response.name}")
    print(f"ID: {response.id}")
    print(f"URL: {response.url}")
