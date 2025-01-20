import json
from datetime import datetime, timedelta

import pytz
import typer

from src.service import jira_factory

app = typer.Typer()
_jira = jira_factory.create()


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
    print(new_issue.permalink())
    print(json.dumps(new_issue.raw, indent=4))


@app.command()
def issue(id: str):
    issue = _jira.issue(id)
    print(json.dumps(issue.raw, indent=4))
    return issue


@app.command()
def rm(id: str):
    issue(id).delete()
    print(f"Deleted issue {id}")


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


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
