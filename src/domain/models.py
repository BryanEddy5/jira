from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


import pytz
from pydantic import BaseModel, ConfigDict, Field


class IssueType(StrEnum):
    """Enumeration of possible JIRA issue types."""

    EPIC = "Epic"
    INITIATIVE = "Initiative"
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"


class IssueStatus(StrEnum):
    """Enumeration of possible JIRA issue statuses."""

    IN_PROGRESS = "In Progress"
    DONE = "Done"
    WONT_DO = "Won't Do"


@dataclass
class Project:
    """Represents a JIRA project with its key, name and optional category."""

    key: str
    name: str
    category_id: str | None = None


@dataclass
class StatusTransition:
    """Represents a status change event with the new status and timestamp."""

    status: str
    timestamp: datetime


class CreateIssueRequest(BaseModel):
    """Request model for creating a new issue."""

    model_config = ConfigDict(frozen=True)

    project_key: str = "BB"
    summary: str
    description: str
    issue_type: IssueType = Field(IssueType.TASK)
    date: datetime = Field(default=datetime.now(pytz.utc) + timedelta(weeks=1))


@dataclass
class Issue:
    """Represents a JIRA issue with all its attributes and history."""

    description: str
    summary: str
    key: str
    project: Project
    issue_type: str
    resolution_date: datetime | None
    status: str
    engineering_category: str
    url: str
    status_history: list[StatusTransition]
    lead_time_hours: float | None = None

    @property
    def is_completed(self) -> bool:
        """Check if the issue is marked as done."""
        return self.status == IssueStatus.DONE

    @property
    def is_cancelled(self) -> bool:
        """Check if the issue is marked as won't do."""
        return self.status == IssueStatus.WONT_DO


@dataclass
class JiraPlan:
    """Represents a collection of related Jira issues."""

    root_issues: list[Issue]  # The original issues provided
    parent_issues: list[Issue]  # Parent issues discovered
    child_issues: list[Issue]  # Child issues discovered
    jql: str  # The JQL query that can fetch all related issues


@dataclass
class IssueAnalytics:
    """Analytics view of an Issue, containing only the fields needed for analysis."""

    project: str
    issue_key: str
    category: str
    resolved: str
    type: str
    url: str
    lead_time_hours: float | None

    @classmethod
    def from_issue(cls, issue: Issue) -> "IssueAnalytics":
        """Create an IssueAnalytics instance from an Issue."""
        return cls(
            project=issue.project.name,
            issue_key=issue.key,
            category=issue.engineering_category,
            resolved=issue.resolution_date.isoformat() if issue.resolution_date else None,
            type=issue.issue_type,
            url=issue.url,
            lead_time_hours=issue.lead_time_hours,
        )
