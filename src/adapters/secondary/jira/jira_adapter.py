"""JIRA adapter for interacting with the JIRA API.

This module provides a clean interface for interacting with JIRA,
handling the mapping between JIRA's data structures and our domain models.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.adapters.secondary.jira.mappers import map_issue, map_project
from src.adapters.secondary.jira.models import (
    JiraPlanRequest,
    JiraPlanResponse,
    ProjectCategory,
    JiraFilter,
)
import json
from src.domain.models import CreateIssueRequest, Issue, IssueStatus, IssueType, Project

if TYPE_CHECKING:
    from datetime import datetime

    from jira import JIRA


class JiraAdapter:
    """Adapter for interacting with JIRA API.

    Handles all JIRA operations including issue creation, deletion, searching,
    and project management. Maps JIRA data structures to domain models.
    """

    def __init__(self, jira: JIRA) -> None:
        """Initialize the JIRA adapter.

        Args:
            jira: Initialized JIRA client instance

        """
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

    def create_issue(self, request: CreateIssueRequest) -> Issue:
        """Create a new JIRA issue from a domain model request."""
        fields = {
            "project": request.project_key,
            "summary": request.summary,
            "description": request.description,
            "issuetype": {"name": request.issue_type.value},
        }
        jira_issue = self.jira.create_issue(fields=fields)
        return map_issue(jira_issue, self.engineering_work_taxonomy)

    def delete_issue(self, issue_id: str) -> None:
        """Delete a JIRA issue."""
        self.jira.issue(issue_id).delete()

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
        projects: list[str] | None = None,
    ) -> list[Issue]:
        """Search for issues matching the given criteria.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            projects: Optional list of specific projects to analyze

        """
        if projects is None:
            projects = self.get_core_connectivity_projects_keys()
        projects_keys = ",".join([project.key for project in projects])

        jql = (
            f"project in ({projects_keys}) "
            f'AND resolved >= "{start_date.strftime("%Y-%m-%d")}" '
            f'AND resolved <= "{end_date.strftime("%Y-%m-%d")}" '
            f"AND type not in ({IssueType.EPIC}, {IssueType.INITIATIVE}) "
            f'AND status != "{IssueStatus.WONT_DO}" '
            'AND project != "Core Connectivity Intake"'
        )

        return self._fetch_issues(jql)

    def get_parent_issue(self, issue_id: str) -> str | None:
        """Get the parent issue (epic or initiative) of a given issue."""
        issue = self.jira.issue(issue_id, expand="parent")
        parent_field = "parent"
        if parent_field and hasattr(issue.fields, parent_field):
            parent_key = getattr(issue.fields, parent_field)
            if isinstance(parent_key, str) or hasattr(parent_key, "key"):
                return parent_key
        return None

    def get_child_issues_keys(self, issue_id: str) -> set[str]:
        """Get all child issues (stories, tasks, bugs) of a given issue."""
        issue = self.jira.issue(issue_id, expand="issuelinks")
        child_keys = set()
        for issue.link in issue.fields.issuelinks:
            if hasattr(issue.link, "outwardIssue"):
                child_keys.add(issue.link.outwardIssue.key)
            elif hasattr(issue.link, "inwardIssue"):
                child_keys.add(issue.link.inwardIssue.key)

        return child_keys

    def get_account_id(self, email: str | None = None) -> str:
        """Get the account ID for a user from their email address."""
        if email is None:
            return self.jira.current_user()
        response = self.jira._session.get(
            f"{self.jira.server_url}/rest/api/3/user/search", params={"query": email}
        )
        response.raise_for_status()
        users = response.json()
        if not users:
            raise ValueError(f"No user found with email: {email}")
        return users[0]["accountId"]

    def get_project_id(self, project_key: str) -> int:
        """Get the numeric ID of a project from its key."""
        response = self.jira._session.get(
            f"{self.jira.server_url}/rest/api/3/project/{project_key}"
        )
        response.raise_for_status()
        data = response.json()
        return int(data["id"])

    def create_filter(self, name: str, jql: str, owner_account_id: str) -> JiraFilter:
        """Create a Jira Filter using the Jira API."""
        response = self.jira._session.post(
            f"{self.jira.server_url}/rest/api/3/filter",
            json={"name": name, "jql": jql, "sharePermissions": [{"type": "authenticated"}]},
        )
        response.raise_for_status()
        data = response.json()
        return JiraFilter(
            id=str(data["id"]),
            name=data["name"],
            jql=data["jql"],
            owner_account_id=data["owner"]["accountId"],
        )

    def create_jira_plan(self, request: JiraPlanRequest) -> JiraPlanResponse:
        """Create a Jira Plan using the Jira API."""
        response = self.jira._session.post(
            f"{self.jira.server_url}/rest/api/3/plans/plan",
            json={
                "name": request.name,
                "issueSources": request.issue_sources,
                "scheduling": request.scheduling,
                "leadAccountId": request.lead_account_id,
                "permissions": request.permissions,
                "exclusionRules": request.exclusion_rules,
                "customFields": request.custom_fields,
            },
        )
        response.raise_for_status()
        plan_id = response.json()
        return JiraPlanResponse(
            id=plan_id, name=request.name, url=f"{self.jira.server_url}/jira/plans/{plan_id}"
        )

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
                map_issue(issue, self.engineering_work_taxonomy) for issue in issues_batch
            )
            pos += len(issues_batch)

        return issues_all
