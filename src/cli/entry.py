from datetime import datetime, timedelta
from typing import Optional, List
import pytz
import typer
from pathlib import Path

from src.service import jira_factory
from src.service.task_service import TaskService
from src.service.sheets_service import SheetsService

app = typer.Typer()
_jira = jira_factory.create()
_task_service = TaskService(_jira)
_sheets_service = SheetsService(
    ".credentials.json", "1DIcPml7tUNY0uoMr_12uXRg4W4aLSUpWKRFS56jbnPE"
)


@app.command()
def create(summary: str, description: str, date: str = None, project: str = "BB"):
    # Call the method
    if date is None:
        date = datetime.now(pytz.utc) + timedelta(weeks=1)
    issue_dict = {
        "project": project,
        "summary": summary,
        "description": description,
        "issuetype": {"name": "Task"},
        "duedate": date.strftime("%Y-%m-%d"),
    }
    new_issue = _jira.create_issue(fields=issue_dict)
    print(new_issue.key)


@app.command()
def get_issue(id: str):
    try:
        issue = _jira.issue(id)
        print(issue.key, issue.fields.summary)
    except Exception as e:
        print(f"Error: {e}")


@app.command()
def rm(ids: List[str]):
    for id in ids:
        try:
            issue = get_issue(id)
            if issue:
                issue.delete()
            print(f"Deleted issue {id}")
        except Exception as e:
            print(f"Error: {e}")


@app.command()
def foo():
    print("bar")


@app.command()
def query(jql: str):
    issues = _jira.search_issues(jql)
    for issue in issues:
        print(issue.key, issue.fields.summary)


@app.command()
def my_items():
    jira_filter = _jira.filter("15232")
    print(jira_filter.raw)


@app.command()
def health_check():
    try:
        _jira.myself()
        print("Jira API is up and running.")
    except Exception as e:
        print(f"Health check failed: {e}")


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
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead -= 7
        return date + timedelta(days_ahead)

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
    _task_service.visualize_project_composition(
        df, str(output_path / "team_composition.html")
    )
    _task_service.analyze_weekly_trends(df, str(output_path / "weekly_trends.html"))

    print(f"\nAnalysis complete! Visualization files have been saved to: {output_path}")
    print("\nGenerated files:")
    print(f"- {output_path}/team_composition.html (Overall team composition)")
    print(f"- {output_path}/weekly_trends.html (Weekly trends by team)")


@app.command("list-teams")
def list_teams():
    """List all available teams."""
    teams = _task_service.get_all_teams()
    if teams:
        print("\nAvailable teams:")
        for team in teams:
            print(f"- {team}")
    else:
        print("No teams found.")


@app.command("sync-to-sheets")
def sync_to_sheets(
    weeks: int = typer.Option(4, help="Number of weeks of data to sync"),
    sheet_range: str = typer.Option("Sheet1!A:E", help="Sheet range in A1 notation"),
):
    """
    Sync Jira data to Google Sheets with deduplication.
    """
    # Set date range
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(weeks=weeks)

    # Get data
    print(f"Fetching Jira data from {start_date.date()} to {end_date.date()}...")
    df = _task_service.get_engineering_taxonomy(start_date, end_date)

    if df.empty:
        print("No data found for the specified parameters.")
        return

    # Sync to Google Sheets
    print("Syncing data to Google Sheets...")
    _sheets_service.append_dataframe(df, sheet_range)
    print("Data sync complete!")


if __name__ == "__main__":
    app()
