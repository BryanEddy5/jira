from datetime import datetime
from typing import List, Protocol
from .models import JiraIssue, ProjectComposition, WeeklyTrend


class IssueRepository(Protocol):
    """Interface for retrieving issue data."""

    def get_all_projects(self) -> List[str]:
        """Get list of all projects."""
        ...

    def get_issues(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> List[JiraIssue]:
        """Get issues for the specified date range and projects."""
        ...


class DataTransformer(Protocol):
    """Interface for transforming raw issue data into analysis-ready formats."""

    def calculate_project_composition(
        self, issues: List[JiraIssue]
    ) -> List[ProjectComposition]:
        """Transform issues into project composition data."""
        ...

    def calculate_weekly_trends(
        self, issues: List[JiraIssue]
    ) -> List[WeeklyTrend]:
        """Transform issues into weekly trend data."""
        ...


class ChartGenerator(Protocol):
    """Interface for generating visualizations."""

    def create_project_composition_chart(
        self, composition_data: List[ProjectComposition], output_path: str
    ) -> None:
        """Generate project composition visualization."""
        ...

    def create_weekly_trends_chart(
        self, trend_data: List[WeeklyTrend], output_path: str
    ) -> None:
        """Generate weekly trends visualization."""
        ...


class AnalyticsService(Protocol):
    """Interface for the high-level analytics service."""

    def get_all_projects(self) -> List[str]:
        """Get list of all projects."""
        ...

    def get_project_composition(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> List[ProjectComposition]:
        """Get project composition analysis."""
        ...

    def get_weekly_trends(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> List[WeeklyTrend]:
        """Get weekly trends analysis."""
        ...

    def visualize_project_composition(
        self, composition_data: List[ProjectComposition], output_path: str
    ) -> None:
        """Create project composition visualization."""
        ...

    def visualize_weekly_trends(
        self, trend_data: List[WeeklyTrend], output_path: str
    ) -> None:
        """Create weekly trends visualization."""
        ...
