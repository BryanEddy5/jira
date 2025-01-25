from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import pytz
import typer

from ....domain.interfaces import AnalyticsService
from ....domain.services.analytics import AnalyticsServiceImpl
from ...secondary.jira.repository import JiraRepository
from ...secondary.jira.transformer import JiraDataTransformer
from ...secondary.visualization.chart_generator import PlotlyChartGenerator

app = typer.Typer()


def create_analytics_service(jira_client) -> AnalyticsService:
    """
    Create and configure the analytics service with its required adapters.
    This is our composition root where we wire up the hexagonal architecture.
    """
    repository = JiraRepository(jira_client)
    transformer = JiraDataTransformer()
    chart_generator = PlotlyChartGenerator()

    return AnalyticsServiceImpl(
        repository=repository,
        transformer=transformer,
        chart_generator=chart_generator,
    )


@app.command("analyze-teams")
def analyze_teams(
    weeks: int = typer.Option(4, help="Number of weeks to analyze"),
    output_dir: str = typer.Option(
        "analysis_output", help="Directory to save visualization files"
    ),
    start_date: Optional[datetime] = typer.Option(
        datetime.now(pytz.UTC),
        help="Start date for analysis (format: YYYY-MM-DD). Defaults to X weeks ago based on weeks parameter",
    ),
):
    """
    Analyze engineering work taxonomy across teams and generate visualizations.
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set date range
    def prev_weekday(date: datetime, weekday: int = 0):
        days_ahead = weekday - date.weekday()
        return date + timedelta(days_ahead)

    start_date = prev_weekday(start_date, 0)
    end_date = start_date + timedelta(weeks=weeks)

    # Create analytics service
    from src.service import jira_factory
    analytics_service = create_analytics_service(jira_factory.create())

    # Get and process data
    print(f"Analyzing team data from {start_date.date()} to {end_date.date()}...")

    # Get project composition
    composition_data = analytics_service.get_project_composition(start_date, end_date)
    if not composition_data:
        print("No composition data found for the specified parameters.")
        return

    # Get weekly trends
    trend_data = analytics_service.get_weekly_trends(start_date, end_date)
    if not trend_data:
        print("No trend data found for the specified parameters.")
        return

    # Generate visualizations
    print("Generating visualizations...")
    analytics_service.visualize_project_composition(
        composition_data, str(output_path / "team_composition.html")
    )
    analytics_service.visualize_weekly_trends(
        trend_data, str(output_path / "weekly_trends.html")
    )

    print(f"\nAnalysis complete! Visualization files have been saved to: {output_path}")
    print("\nGenerated files:")
    print(f"- {output_path}/team_composition.html (Overall team composition)")
    print(f"- {output_path}/weekly_trends.html (Weekly trends by team)")


@app.command("list-teams")
def list_teams():
    """List all available teams."""
    from src.service import jira_factory
    analytics_service = create_analytics_service(jira_factory.create())

    teams = analytics_service.get_all_projects()
    if teams:
        print("\nAvailable teams:")
        for team in teams:
            print(f"- {team}")
    else:
        print("No teams found.")


if __name__ == "__main__":
    app()
