from datetime import datetime
from typing import List
from ..models import ProjectComposition, WeeklyTrend
from ..interfaces import IssueRepository, DataTransformer, ChartGenerator, AnalyticsService


class AnalyticsServiceImpl(AnalyticsService):
    """
    Core domain service implementing analytics business logic.
    Pure domain logic with no external dependencies.
    """

    def __init__(
        self,
        repository: IssueRepository,
        transformer: DataTransformer,
        chart_generator: ChartGenerator,
    ):
        self.repository = repository
        self.transformer = transformer
        self.chart_generator = chart_generator

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
        self, composition_data: List[ProjectComposition], output_path: str
    ) -> None:
        """
        Create project composition visualization.

        Args:
            composition_data: List of ProjectComposition objects
            output_path: Path to save the visualization
        """
        self.chart_generator.create_project_composition_chart(composition_data, output_path)

    def visualize_weekly_trends(
        self, trend_data: List[WeeklyTrend], output_path: str
    ) -> None:
        """
        Create weekly trends visualization.

        Args:
            trend_data: List of WeeklyTrend objects
            output_path: Path to save the visualization
        """
        self.chart_generator.create_weekly_trends_chart(trend_data, output_path)
