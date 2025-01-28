from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import pytz
import typer
import webbrowser

from src.adapters.secondary.jira import jira_factory
from src.service.task_service import TaskService
from src.service.team_analysis import TeamAnalysis

team_app = typer.Typer()
_jira = jira_factory.create()
_task_service = TaskService(_jira)
_team_analysis = TeamAnalysis()


@team_app.command("analyze")
def analyze_teams(
    weeks: int = typer.Option(4, help="Number of weeks to analyze"),
    output_dir: str = typer.Option(
        "analysis_output", help="Directory to save visualization files"
    ),
    start_date: Optional[datetime] = typer.Option(
        datetime.now(pytz.UTC),
        help="Start date for analysis (format: YYYY-MM-DD). Defaults to X weeks ago based on weeks parameter",
    ),
    open_files: bool = typer.Option(
        True, help="Open visualization files in browser after generation"
    ),
):
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
    print(f"Analyzing team data from {start_date.date()} to {end_date.date()}...")
    df = _task_service.get_engineering_taxonomy(start_date, end_date)

    if df.is_empty():
        print("No data found for the specified parameters.")
        return

    # Generate visualizations
    print("Generating visualizations...")
    team_composition = str(output_path / "team_composition.html")
    weekly_trends = str(output_path / "weekly_trends.html")
    lead_time = str(output_path / "lead_time.html")

    _team_analysis.analyze_weekly_trends(df, weekly_trends)
    _team_analysis.visualize_project_composition(df, team_composition)
    _team_analysis.visualize_project_lead_time(df, lead_time)
    _team_analysis.write_to_csv(df)

    print(f"\nAnalysis complete! Visualization files have been saved to: {output_path}")
    print("\nGenerated files:")
    print(f"- {output_path}/team_composition.html (Overall team composition)")
    print(f"- {output_path}/weekly_trends.html (Weekly trends by team)")
    print(f"- {output_path}/lead_time.html (Lead time by project and category)")
    print(f"- {output_path}/engineering_taxonomy.csv (Raw data)")

    if open_files:
        webbrowser.open(team_composition)
        webbrowser.open(weekly_trends)
        webbrowser.open(lead_time)


@team_app.command("list")
def list_teams():
    """List all available teams."""
    teams = _task_service.get_all_projects()
    if teams:
        print("\nAvailable projects:")
        for team in teams:
            print(f"- {team}")
    else:
        print("No teams found.")
