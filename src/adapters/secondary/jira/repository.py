from datetime import datetime
from typing import List
from jira import JIRA

from ....domain.interfaces import IssueRepository
from ....domain.models import JiraIssue


class JiraRepository(IssueRepository):
    """
    Jira adapter implementing the IssueRepository interface.
    Handles all Jira-specific concerns and maps to domain models.
    """

    def __init__(self, jira: JIRA):
        self.jira = jira
        self.engineering_work_taxonomy = "customfield_11173"

    def get_all_projects(self) -> List[str]:
        """Get list of all projects."""
        projects = self.jira.projects()
        res = []
        for project in projects:
            if (
                hasattr(project, "projectCategory")
                and project.projectCategory.name == "Core Connectivity"
            ):
                res.append(project.name)
        return res

    def get_issues(
        self, start_date: datetime, end_date: datetime, projects: List[str] = None
    ) -> List[JiraIssue]:
        """
        Get issues for the specified date range and projects.

        Args:
            start_date: Start date for fetching issues
            end_date: End date for fetching issues
            projects: Optional list of specific projects to fetch

        Returns:
            List of JiraIssue domain objects
        """
        # Build JQL query
        jql_parts = [
            f'resolved >= "{start_date.strftime("%Y-%m-%d")}"',
            f'resolved <= "{end_date.strftime("%Y-%m-%d")}"',
        ]

        if not projects:
            project_clause = "category = 'Core Connectivity'"
        jql_parts.append(f"({project_clause})")

        jql = " AND ".join(jql_parts)

        # Fetch issues
        issues = self.jira.search_issues(
            jql,
            maxResults=1000,
            fields=f"key,project,issuetype,resolutiondate,status, {self.engineering_work_taxonomy}",
        )

        # Map to domain objects
        return [
            JiraIssue(
                key=issue.key,
                project_name=issue.fields.project.key,
                category=self._get_issue_category(issue),
                issue_type=issue.fields.issuetype.name,
                resolved_date=datetime.strptime(
                    issue.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z"
                )
                if issue.fields.resolutiondate
                else None,
                url=f"{self.jira.server_url}/browse/{issue.key}",
            )
            for issue in issues
        ]

    def _get_issue_category(self, issue) -> str:
        """Helper method to determine issue category."""
        if not hasattr(issue.fields, self.engineering_work_taxonomy):
            return "Unknown"

        category = getattr(issue.fields, self.engineering_work_taxonomy, "Unknown")
        return category
