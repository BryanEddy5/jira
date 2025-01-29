from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


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


@dataclass
class CreateIssueRequest:
    """Request model for creating a new issue."""

    project_key: str
    summary: str
    description: str
    issue_type: IssueType = IssueType.TASK


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
