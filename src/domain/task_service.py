from datetime import datetime

from src.adapters.secondary.jira.jira_adapter import JiraAdapter
from src.domain.models import CreateIssueRequest, Issue, IssueAnalytics, Project


class TaskService:
    """Service class responsible for handling JIRA task-related operations and analytics."""

    def __init__(self, jira_adapter: JiraAdapter) -> None:
        """Initialize TaskService with a JIRA adapter."""
        self.jira_adapter = jira_adapter

    def create_issue(self, create_issue_request: CreateIssueRequest) -> Issue:
        """Create a new JIRA issue."""
        return self.jira_adapter.create_issue(create_issue_request)

    def get_issue(self, issue_id: str) -> Issue:
        """Get details of a specific issue."""
        return self.jira_adapter.get_issue(issue_id)

    def delete_issue(self, issue_id: str) -> None:
        """Delete a JIRA issue."""
        self.jira_adapter.delete_issue(issue_id)

    def get_core_connectivity_projects_keys(self) -> list[Project]:
        """Get list of all Core Connectivity projects."""
        return self.jira_adapter.get_core_connectivity_projects_keys()

    def get_engineering_taxonomy(
        self,
        start_date: datetime,
        end_date: datetime,
        projects: list[str] | None = None,
    ) -> list[IssueAnalytics]:
        """Get engineering work taxonomy for all projects or specified projects.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            projects: Optional list of specific projects to analyze.
                If None, analyzes all projects.

        Returns:
            DataFrame with project work composition

        """
        issues = self.jira_adapter.search_issues(start_date, end_date, projects)

        # Convert issues to IssueAnalytics domain models
        return [IssueAnalytics.from_issue(issue) for issue in issues]
