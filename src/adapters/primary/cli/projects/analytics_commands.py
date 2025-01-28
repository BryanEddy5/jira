from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pytz
import typer

from src.adapters.secondary.jira import jira_factory
from src.domain.task_service import TaskService
from src.domain.team_analysis import TeamAnalysis

team_app = typer.Typer()
_jira = jira_factory.create()
_task_service = TaskService(_jira)
_team_analysis = TeamAnalysis()


@team_app.command("analyze")
def analyze_teams(
    weeks: int = typer.Option(4, help="Number of weeks to analyze"),
    output_dir: str = typer.Option(
        "analysis_output",
        help="Directory to save visualization files",
    ),
    start_date: Optional[datetime] = typer.Option(
        datetime.now(pytz.UTC),
        help="Start date for analysis (format: YYYY-MM-DD). Defaults to X weeks ago based on weeks parameter",
    ),
    project_keys: list[str] = typer.Option(
        None,
        help="Projects to analyze. Defaults to just API BU Projects",
    ),
) -> None:
    """Analyze engineering work taxonomy across teams and generate visualizations."""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set date range
    def prev_weekday(date: datetime, weekday: int = 0):
        days_ahead = weekday - date.weekday()
        return date + timedelta(days=days_ahead)

    start_date = prev_weekday(start_date, 0)
    end_date = start_date + timedelta(weeks=weeks)

    # Get and process data
    analytics = _task_service.get_engineering_taxonomy(
        start_date,
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
            print(_project.key)
    else:
        pass
