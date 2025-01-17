from jira import JIRA
from datetime import datetime, timedelta
import pytz


class TaskService:
    def __init__(self, jira: JIRA):
        self.jira = jira

    def create_task(self, project_key: str, summary: str, description: str, date: datetime = None):
        if date is None:
            date = datetime.now(pytz.utc) + timedelta(weeks=1)
        issue_dict = {
            "project": project_key,
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Task"},
            "duedate": date.strftime("%Y-%m-%d"),
        }

        return self.jira.create_issue(fields=issue_dict)