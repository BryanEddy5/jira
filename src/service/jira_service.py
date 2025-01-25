from datetime import datetime
from typing import List
from jira import JIRA
from ..domain.interfaces import IssueRepository
from ..domain.models import JiraIssue


class JiraService(IssueRepository):
    """Implementation of IssueRepository using Jira API."""

    def __init__(self, jira: JIRA):
        self.jira = jira
        self.engineering_work_taxonomy = "customfield_11173"

    def get_all_projects(self) -> List[str]:
        """Get list of all projects from Jira."""
        jql = 'category in ("core connectivity") and created >= -30d order by created DESC'
        projects = set()

        issues = self.jira.search_issues(
            jql,
            maxResults=1000,
            fields=[self.engineering_work_taxonomy, "project"]
        )

        for issue in issues:
            if hasattr(issue.fields, self.engineering_work_taxonomy):
                project = str(issue.fields.project.name)
                if project:
                    projects.add(project)

        return sorted(list(projects))

    def get_issues(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> List[JiraIssue]:
        """
        Get issues for the specified date range and projects.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            projects: Optional list of specific projects to analyze. If None, analyzes all projects.

        Returns:
            List of JiraIssue objects
        """
        if projects is None:
            projects = self.get_all_projects()

        issues = []
        for project in projects:
            jql = (
                f'category = "Core Connectivity" '
                f'AND resolved >= "{start_date.strftime("%Y-%m-%d")}" '
                f'AND resolved <= "{end_date.strftime("%Y-%m-%d")}" '
                "ORDER BY resolved DESC"
            )

            jira_issues = self.jira.search_issues(
                jql,
                maxResults=1000,
                fields=[
                    "summary",
                    "resolved",
                    "issuetype",
                    self.engineering_work_taxonomy,
                    "project",
                    "key",
                    "resolutiondate"
                ]
            )

            for issue in jira_issues:
                category = getattr(
                    issue.fields, self.engineering_work_taxonomy, "Uncategorized"
                )

                # Parse the resolution date
                resolved_date = None
                if issue.fields.resolutiondate:
                    try:
                        resolved_date = datetime.strptime(
                            issue.fields.resolutiondate,
                            "%Y-%m-%dT%H:%M:%S.%f%z"
                        )
                    except ValueError:
                        # Handle potential different date format
                        try:
                            resolved_date = datetime.strptime(
                                issue.fields.resolutiondate,
                                "%Y-%m-%dT%H:%M:%S.%f"
                            )
                        except ValueError:
                            pass

                issues.append(
                    JiraIssue(
                        key=issue.key,
                        project_name=issue.fields.project.name,
                        category=str(category),
                        issue_type=issue.fields.issuetype.name,
                        resolved_date=resolved_date,
                        url=issue.self
                    )
                )

        return issues
