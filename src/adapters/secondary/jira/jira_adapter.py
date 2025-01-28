from datetime import datetime
from typing import Optional

from jira import JIRA

from src.adapters.secondary.jira.mappers import map_issue, map_project
from src.adapters.secondary.jira.models import ProjectCategory
from src.domain.models import Issue, IssueStatus, IssueType, Project


class JiraAdapter:
    def __init__(self, jira: JIRA) -> None:
        self.jira = jira
        self.engineering_work_taxonomy = "customfield_11173"
        self.jira_fields = [
            "key",
            "project",
            "issuetype",
            "resolutiondate",
            "status",
            self.engineering_work_taxonomy,
            "changelog",
            "summary",
            "description",
            "",
        ]

    def get_issue(self, issue_id: str) -> Issue:
        """Get details of a specific issue."""
        jira_issue = self.jira.issue(issue_id, expand="changelog")
        return map_issue(jira_issue, self.engineering_work_taxonomy)

    def get_core_connectivity_projects_keys(self) -> list[Project]:
        """Get list of all Core Connectivity projects."""
        results = []
        jira_projects = self.jira.projects()

        for jira_project in jira_projects:
            project = map_project(jira_project)
            if (
                project.name not in results
                and project.category_id == ProjectCategory.CORE_CONNECTIVITY
            ):
                results.append(Project(project.key, project.name, project.category_id))

        return results

    def search_issues(
        self,
        start_date: datetime,
        end_date: datetime,
        projects: Optional[list[str]] = None,
    ) -> list[Issue]:
        """Search for issues matching the given criteria.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            projects: Optional list of specific projects to analyze

        """
        if projects is None:
            projects = self.get_core_connectivity_projects_keys()
        projects_keys = ','.join([project.key for project in projects])
        print(f"Searching for issues in projects: {projects_keys}")

        jql = (
            f"project in ({projects_keys}) "
            f'AND resolved >= "{start_date.strftime("%Y-%m-%d")}" '
            f'AND resolved <= "{end_date.strftime("%Y-%m-%d")}" '
            f"AND type not in ({IssueType.EPIC}, {IssueType.INITIATIVE}) "
            f'AND status != "{IssueStatus.WONT_DO}" '
            'AND project != "Core Connectivity Intake"'
        )

        return self._fetch_issues(jql)

    def _fetch_issues(self, jql: str) -> list[Issue]:
        """Fetch issues from Jira using the provided JQL query."""
        pos = 0
        batch = 100  # 100 is the max batch size Jira will return results for
        issues_all = []

        while True:
            issues_batch = self.jira.search_issues(
                jql,
                startAt=pos,
                maxResults=batch,
                fields=self.jira_fields,
                expand="changelog",
            )
            if issues_batch == []:
                break
            issues_all.extend(
                map_issue(issue, self.engineering_work_taxonomy)
                for issue in issues_batch
            )
            pos += len(issues_batch)

        return issues_all
