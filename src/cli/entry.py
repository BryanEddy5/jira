from datetime import datetime, timedelta

import pytz
import typer

from src.service import jira_factory

app = typer.Typer()
_jira = jira_factory.create()


@app.command()
def create(summary: str, description: str, date: str = None):
    # Call the method
    if date is None:
        date = datetime.now(pytz.utc) + timedelta(weeks=1)
    issue_dict = {
        "project": "BB",
        "summary": summary,
        "description": description,
        "issuetype": {"name": "Task"},
        "duedate": date.strftime("%Y-%m-%d"),
    }
    return _jira.create_issue(fields=issue_dict)


@app.command()
def issue(id: str):
    issue = _jira.issue(id)
    print(issue)


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
