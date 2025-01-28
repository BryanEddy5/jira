import typer
from src.cli.jira.jira_commands import jira_app
from src.cli.projects.analytics_commands import team_app

app = typer.Typer()
app.add_typer(jira_app, name="jira", help="JIRA-related commands")
app.add_typer(team_app, name="projects", help="Team and Project analysis commands")

if __name__ == "__main__":
    app()
