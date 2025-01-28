"""Mapping functions to convert JIRA entities to domain models.

This module provides functions to map JIRA's data structures to our domain models,
ensuring a clean separation between the JIRA API and our domain logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from src.domain.models import Issue, Project, StatusTransition

if TYPE_CHECKING:
    from jira import Issue as JiraIssue
    from jira import Project as JiraProject


def map_project(jira_project: JiraProject) -> Project:
    """Convert a JIRA project to a domain Project."""
    return Project(
        key=jira_project.key,
        name=jira_project.name,
        category_id=getattr(jira_project.projectCategory, "id", None)
        if hasattr(jira_project, "projectCategory")
        else None,
    )


def map_status_history(jira_issue: JiraIssue) -> list[StatusTransition]:
    """Extract status transition history from a JIRA issue."""
    if not (hasattr(jira_issue, "changelog") and jira_issue.changelog):
        return []

    return [
        StatusTransition(
            status=item.toString,
            timestamp=datetime.strptime(
                history.created,
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        for history in jira_issue.changelog.histories
        for item in history.items
        if item.field == "status"
    ]


def calculate_lead_time(status_history: list[StatusTransition]) -> float | None:
    """Calculate lead time from status transitions."""
    in_progress_dates = [t.timestamp for t in status_history if t.status == "In Progress"]
    done_dates = [t.timestamp for t in status_history if t.status == "Done"]

    if in_progress_dates and done_dates:
        start_date = min(in_progress_dates) # get the earliest date
        end_date = max(done_dates)  # get the latest date
        return (end_date - start_date).total_seconds() / 3600  # Convert to hours

    return None


def map_issue(jira_issue: JiraIssue, engineering_taxonomy_field: str) -> Issue:
    """Convert a JIRA issue to a domain Issue."""
    status_history = map_status_history(jira_issue)

    return Issue(
        key=jira_issue.key,
        project=map_project(jira_issue.fields.project),
        issue_type=jira_issue.fields.issuetype.name,
        resolution_date=datetime.strptime(
            jira_issue.fields.resolutiondate,
            "%Y-%m-%dT%H:%M:%S.%f%z",
        )
        if hasattr(jira_issue.fields, "resolutiondate") and jira_issue.fields.resolutiondate
        else None,
        status=jira_issue.fields.status.name,
        engineering_category=str(
            getattr(jira_issue.fields, engineering_taxonomy_field, "Uncategorized"),
        ),
        url=jira_issue.self,
        status_history=status_history,
        lead_time_hours=calculate_lead_time(status_history),
        summary=jira_issue.fields.summary,
        description=jira_issue.fields.description,
    )
