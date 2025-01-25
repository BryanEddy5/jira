from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class JiraIssue:
    """Represents a Jira issue with its core attributes."""
    key: str
    project_name: str
    category: str
    issue_type: str
    resolved_date: Optional[datetime]
    url: str


@dataclass
class ProjectComposition:
    """Represents the composition of work in a project."""
    project: str
    category: str
    count: int
    total_count: int
    percentage: float
    issues: list[JiraIssue]


@dataclass
class WeeklyTrend:
    """Represents weekly trend data for a project."""
    week: int
    project: str
    category: str
    count: int
