from jira import JIRA
from datetime import datetime
from typing import List
import polars as pl
from src.adapters.secondary.jira.models import ProjectCategory


class TaskService:
    def __init__(self, jira: JIRA):
        self.jira = jira
        self.project = "project"
        self.engineering_work_taxonomy = "customfield_11173"


    def get_issue(self, issue_id: str):
        """Get details of a specific JIRA issue."""

        issue = self.jira.issue(issue_id, expand="changelog")
        return issue

    def get_all_projects(self) -> List[str]:
        """Get list of all projects from Jira."""
        results = set()

        # Search for issues and extract unique project names
        projects = self.jira.projects()
        for project in projects:
            if (
                project.name not in projects
                and hasattr(project, "projectCategory")
                and project.projectCategory.id == ProjectCategory.CORE_CONNECTIVITY
            ):
                results.add(project.name)

        return sorted(list(results))

    def _fetch_issues(self, jql: str) -> list[JIRA.issue]:
        """Fetch issues from Jira using the provided JQL query."""
        pos = 0
        batch = 100  # 100 is the max batch size Jira will return results for
        issues_all = []
        while True:
            issues_batch = self.jira.search_issues(
                jql,
                startAt=pos,
                maxResults=batch,
                fields=[
                    "key",
                    "project",
                    "issuetype",
                    "resolutiondate",
                    "status",
                    self.engineering_work_taxonomy,
                    "changelog",
                ],expand="changelog"
            )
            if issues_batch == []:
                break
            else:
                issues_all += issues_batch
            pos += len(issues_batch)
        return issues_all

    def get_engineering_taxonomy(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> pl.DataFrame:
        """
        Get engineering work taxonomy for all projects or specified projects.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            projects: Optional list of specific projects to analyze. If None, analyzes all projects.

        Returns:
            DataFrame with project work composition
        """
        if projects is None:
            projects = self.get_all_projects()

        all_data = []

        jql = (
            f'category = "Core Connectivity" '
            f'AND resolved >= "{start_date.strftime("%Y-%m-%d")}" '
            f'AND resolved <= "{end_date.strftime("%Y-%m-%d")}" '
            'AND type not in (Epic, Initiative) and status != "Won\'t Do"'
            'AND project != "Core Connectivity Intake"'
        )

        issues = self._fetch_issues(jql)

        for issue in issues:
            # Calculate lead time
            lead_time_hours = None
            if hasattr(issue, 'changelog') and issue.changelog:
                in_progress_histories = []
                done_histories = []

                for history in issue.changelog.histories:
                    for item in history.items:
                        if item.field == 'status':
                            if item.toString == 'In Progress':
                                in_progress_histories.append(datetime.strptime(history.created, "%Y-%m-%dT%H:%M:%S.%f%z"))
                            elif item.toString == 'Done':
                                done_histories.append(datetime.strptime(history.created, "%Y-%m-%dT%H:%M:%S.%f%z"))



                if in_progress_histories and done_histories:
                    in_progress_date = min(in_progress_histories)
                    done_date = max(done_histories)
                    lead_time_hours = (done_date - in_progress_date).total_seconds() / 3600  # Convert to hours

            category = getattr(
                issue.fields, self.engineering_work_taxonomy, "Uncategorized"
            )
            all_data.append(
                {
                    "project": issue.fields.project.name,
                    "issue_key": issue.key,
                    "category": str(category),
                    "resolved": issue.fields.resolutiondate,
                    "type": issue.fields.issuetype.name,
                    "url": issue.self,
                    "lead_time_hours": lead_time_hours,  # Add lead time in days
                }
            )

        print(f"Retrieved {len(all_data)} issues")

        # Convert to DataFrame for easier analysis
        df = pl.DataFrame(all_data)
        if not df.is_empty():
            df = df.with_columns(
                [
                    pl.col("resolved")
                    .str.strptime(pl.Datetime)
                    .dt.week()
                    .alias("week"),
                ]
            )

        return df.unique()
