#!/usr/bin/env python3
"""CLI entry point for the metrics application.

Provides JIRA and project analysis commands.
"""

import typer

from src.adapters.primary.cli.jira_commands.jira_commands import jira_app
from src.adapters.primary.cli.projects.analytics_commands import team_app

app = typer.Typer()
app.add_typer(jira_app, name="jira", help="JIRA-related commands")
app.add_typer(team_app, name="projects", help="Team and Project analysis commands")

if __name__ == "__main__":
    app()
