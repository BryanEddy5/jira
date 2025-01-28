from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional


class IssueType(StrEnum):
    EPIC = "Epic"
    INITIATIVE = "Initiative"
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"


class IssueStatus(StrEnum):
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    WONT_DO = "Won't Do"


@dataclass
class Project:
    key: str
    name: str
    category_id: Optional[str] = None


@dataclass
class StatusTransition:
    status: str
    timestamp: datetime


@dataclass
class Issue:
    description: str
    summary: str
    key: str
    project: Project
    issue_type: str
    resolution_date: Optional[datetime]
    status: str
    engineering_category: str
    url: str
    status_history: list[StatusTransition]
    lead_time_hours: Optional[float] = None

    @property
    def is_completed(self) -> bool:
        return self.status == IssueStatus.DONE

    @property
    def is_cancelled(self) -> bool:
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
    lead_time_hours: Optional[float]

    @classmethod
    def from_issue(cls, issue: Issue) -> "IssueAnalytics":
        """Create an IssueAnalytics instance from an Issue."""
        return cls(
            project=issue.project.name,
            issue_key=issue.key,
            category=issue.engineering_category,
            resolved=issue.resolution_date.isoformat()
            if issue.resolution_date
            else None,
            type=issue.issue_type,
            url=issue.url,
            lead_time_hours=issue.lead_time_hours,
        )
