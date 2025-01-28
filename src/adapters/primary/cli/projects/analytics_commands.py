"""CLI commands for analyzing team and project metrics."""

from datetime import datetime, timedelta
from pathlib import Path

import pytz
import typer

from src.adapters.secondary.jira import jira_factory
from src.domain.task_service import TaskService
from src.domain.team_analysis import TeamAnalysis

# Default values for command options
DEFAULT_WEEKS = 4
DEFAULT_OUTPUT_DIR = "analysis_output"
DEFAULT_START_DATE = datetime.now(pytz.UTC)

# Command options
WEEKS_OPTION = typer.Option(
    DEFAULT_WEEKS,
    help="Number of weeks to analyze",
)
OUTPUT_DIR_OPTION = typer.Option(
    DEFAULT_OUTPUT_DIR,
    help="Directory to save visualization files",
)
START_DATE_OPTION = typer.Option(
    None,  # Will be set to DEFAULT_START_DATE if None
    help="Start date for analysis (format: YYYY-MM-DD). "
    "Defaults to current date minus specified weeks.",
)
PROJECT_KEYS_OPTION = typer.Option(
    None,
    help="Projects to analyze. Defaults to just API BU Projects",
)

team_app = typer.Typer()
_jira = jira_factory.create()
_task_service = TaskService(_jira)
_team_analysis = TeamAnalysis()


@team_app.command("analyze")
def analyze_teams(
    weeks: int = WEEKS_OPTION,
    output_dir: str = OUTPUT_DIR_OPTION,
    start_date: datetime | None = START_DATE_OPTION,
    project_keys: list[str] = PROJECT_KEYS_OPTION,
) -> None:
    """Analyze engineering work taxonomy across teams and generate visualizations."""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set date range
    def prev_weekday(date: datetime, weekday: int = 0) -> datetime:
        """Get previous weekday from given date."""
        days_ahead = weekday - date.weekday()
        return date + timedelta(days=days_ahead)

    start = prev_weekday(start_date or DEFAULT_START_DATE, 0)
    end_date = start + timedelta(weeks=weeks)

    # Get and process data
    analytics = _task_service.get_engineering_taxonomy(
        start,
        end_date,
        project_keys,
    )

    if not analytics:
        return

    # Generate visualizations
    team_composition = str(output_path / "team_composition.html")
    weekly_trends = str(output_path / "weekly_trends.html")
    lead_time = str(output_path / "lead_time.html")

    _team_analysis.analyze_weekly_trends(analytics, weekly_trends)
    _team_analysis.visualize_project_composition(analytics, team_composition)
    _team_analysis.visualize_project_lead_time(analytics, lead_time)
    _team_analysis.write_to_csv(analytics)

    print(f"\nAnalysis complete! Visualization files have been saved to: {output_path}")
    print("\nGenerated files:")
    print(f"- {output_path}/team_composition.html (Overall team composition)")
    print(f"- {output_path}/weekly_trends.html (Weekly trends by team)")
    print(f"- {output_path}/lead_time.html (Lead time by project and category)")
    print(f"- {output_path}/engineering_taxonomy.csv (Raw data)")


@team_app.command("list")
def list_projects() -> None:
    """List all available projects."""
    projects = _task_service.get_core_connectivity_projects_keys()
    if projects:
        for _project in projects:
            print(f"Project: {_project.key}")
