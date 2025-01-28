#!/usr/bin/env python3
"""CLI entry point for the metrics application providing JIRA and project
analysis commands.
"""

import typer

from src.adapters.primary.cli.jira.jira_commands import jira_app
from src.adapters.primary.cli.projects.analytics_commands import team_app

app = typer.Typer()
app.add_typer(jira_app, name="jira", help="JIRA-related commands")
app.add_typer(team_app, name="projects", help="Team and Project analysis commands")

if __name__ == "__main__":
    app()
