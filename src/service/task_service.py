from datetime import datetime
from typing import List
from jira import JIRA
from .jira_service import JiraService
from .data_transformer import IssueDataTransformer
from .visualization_service import VisualizationService
from ..domain.interfaces import AnalyticsService
from ..domain.models import ProjectComposition, WeeklyTrend


class TaskService(AnalyticsService):
    """
    Orchestrates the workflow between data retrieval, transformation, and visualization.
    Acts as a facade for the underlying services.
    """

    def __init__(self, jira: JIRA):
        self.repository = JiraService(jira)
        self.transformer = IssueDataTransformer()
        self.visualizer = VisualizationService()

    def get_all_projects(self) -> List[str]:
        """Get list of all projects."""
        return self.repository.get_all_projects()

    def get_project_composition(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> List[ProjectComposition]:
        """
        Get project composition analysis.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            projects: Optional list of specific projects to analyze

        Returns:
            List of ProjectComposition objects
        """
        issues = self.repository.get_issues(start_date, end_date, projects)
        return self.transformer.calculate_project_composition(issues)

    def get_weekly_trends(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> List[WeeklyTrend]:
        """
        Get weekly trends analysis.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            projects: Optional list of specific projects to analyze

        Returns:
            List of WeeklyTrend objects
        """
        issues = self.repository.get_issues(start_date, end_date, projects)
        return self.transformer.calculate_weekly_trends(issues)

    def visualize_project_composition(
        self, composition_data: List[ProjectComposition], output_path: str = "project_composition.html"
    ) -> None:
        """
        Create project composition visualization.

        Args:
            composition_data: List of ProjectComposition objects
            output_path: Path to save the visualization
        """
        self.visualizer.create_project_composition_chart(composition_data, output_path)

    def visualize_weekly_trends(
        self, trend_data: List[WeeklyTrend], output_path: str = "weekly_trends.html"
    ) -> None:
        """
        Create weekly trends visualization.

        Args:
            trend_data: List of WeeklyTrend objects
            output_path: Path to save the visualization
        """
        self.visualizer.create_weekly_trends_chart(trend_data, output_path)
