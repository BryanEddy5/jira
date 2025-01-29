"""Service for creating and managing Jira Plans."""

from typing import Set, Tuple

from src.adapters.secondary.jira.jira_adapter import JiraAdapter
from src.adapters.secondary.jira.models import JiraPlanRequest, JiraPlanResponse
from src.domain.models import Issue, JiraPlan


class JiraPlanService:
    """Service for creating and managing Jira Plans."""

    def __init__(self, jira_adapter: JiraAdapter) -> None:
        """Initialize JiraPlanService with a JIRA adapter."""
        self.jira_adapter = jira_adapter

    def create_plan(
        self, issue_ids: list[str], name: str, lead_email: str | None = None
    ) -> Tuple[JiraPlan, JiraPlanResponse]:
        """Create a Jira Plan from a list of issue IDs.

        This method will:
        1. Get the root issues from the provided IDs
        2. Recursively get all parent issues (epics, initiatives)
        3. Recursively get all child issues (stories, tasks, bugs)
        4. Generate a JQL query that includes all related issues
        """
        # First get all related issues and their JQL
        plan = self._get_related_issues(issue_ids)

        # Get account ID from email
        lead_account_id = self.jira_adapter.get_account_id(lead_email)

        # Create a filter with the JQL
        filter_name = f"Filter for plan: {name}"
        jira_filter = self.jira_adapter.create_filter(
            name=filter_name, jql=plan.jql, owner_account_id=lead_account_id
        )

        # Create the Jira Plan using the filter
        request = JiraPlanRequest(
            name=name,
            issue_sources=[{"type": "Filter", "value": jira_filter.id}],
            scheduling={
                "dependencies": "Sequential",
                "endDate": {"type": "DueDate"},
                "estimation": "Days",
                "inferredDates": "ReleaseDates",
                "startDate": {"type": "TargetStartDate"},
            },
            lead_account_id=lead_account_id,
            permissions=[
                {"holder": {"type": "AccountId", "value": lead_account_id}, "type": "Edit"}
            ],
        )

        response = self.jira_adapter.create_jira_plan(request)
        return plan, response

    def _get_related_issues(self, issue_ids: list[str]) -> JiraPlan:
        """Get all related issues for the given issue IDs."""
        # Get root issues
        root_issues = [self.jira_adapter.get_issue(id) for id in issue_ids]

        # Get parent issues recursively
        parent_issues: list[Issue] = []
        parent_keys: Set[str] = set()
        for issue in root_issues:
            self._get_parent_issues_recursive(issue.key, parent_issues, parent_keys)

        # Get child issues recursively
        child_issues: list[Issue] = []
        child_keys: Set[str] = set()
        for issue in root_issues + parent_issues:
            self._get_child_issues_recursive(issue.key, child_keys)

        # Generate JQL
        all_keys = (
            [issue.key for issue in root_issues]
            + [issue.key for issue in parent_issues]
            + list(child_keys)
        )
        jql = f"key in ({','.join(all_keys)})"

        return JiraPlan(
            root_issues=root_issues, parent_issues=parent_issues, child_issues=child_issues, jql=jql
        )

    def _get_parent_issues_recursive(
        self, issue_key: str, parent_issues: list[Issue], seen_keys: Set[str]
    ) -> None:
        """Recursively get all parent issues of a given issue."""
        if issue_key in seen_keys:
            return

        parent = self.jira_adapter.get_parent_issue(issue_key)
        if parent:
            seen_keys.add(parent.key)
            parent_issues.append(parent)
            self._get_parent_issues_recursive(parent.key, parent_issues, seen_keys)

    def _get_child_issues_recursive(
        self, issue_key: str, seen_keys: Set[str]
    ) -> set[str]:
        """Recursively get all child issues of a given issue."""
        if issue_key in seen_keys:
            return

        children_keys = self.jira_adapter.get_child_issues_keys(issue_key)
        for child_key in children_keys:
            if child_key not in seen_keys:
                seen_keys.add(child_key)
                self._get_child_issues_recursive(child_key, seen_keys)
