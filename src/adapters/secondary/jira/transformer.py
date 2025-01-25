from collections import defaultdict
from typing import List

from ....domain.interfaces import DataTransformer
from ....domain.models import JiraIssue, ProjectComposition, WeeklyTrend


class JiraDataTransformer(DataTransformer):
    """
    Jira-specific implementation of the DataTransformer interface.
    Handles transformation of Jira issues into analysis-ready formats.
    """

    def calculate_project_composition(
        self, issues: List[JiraIssue]
    ) -> List[ProjectComposition]:
        """Transform issues into project composition data."""
        # Group issues by project and category
        project_categories = defaultdict(lambda: defaultdict(list))
        for issue in issues:
            project_categories[issue.project_name][issue.category].append(issue)

        # Calculate composition for each project
        compositions = []
        for project, categories in project_categories.items():
            total_issues = sum(len(issues) for issues in categories.values())

            for category, category_issues in categories.items():
                count = len(category_issues)
                percentage = (count / total_issues * 100) if total_issues > 0 else 0

                compositions.append(
                    ProjectComposition(
                        project=project,
                        category=category,
                        count=count,
                        total_count=total_issues,
                        percentage=percentage,
                        issues=category_issues,
                    )
                )

        return compositions

    def calculate_weekly_trends(self, issues: List[JiraIssue]) -> List[WeeklyTrend]:
        """Transform issues into weekly trend data."""
        # Group issues by week, project, and category
        weekly_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for issue in issues:
            if issue.resolved_date:
                # Get the ISO week number (1-53)
                week = issue.resolved_date.isocalendar()[1]
                weekly_data[week][issue.project_name][issue.category] += 1

        # Convert to list of WeeklyTrend objects
        trends = []
        for week in sorted(weekly_data.keys()):
            for project, categories in weekly_data[week].items():
                for category, count in categories.items():
                    trends.append(
                        WeeklyTrend(
                            week=week,
                            project=project,
                            category=category,
                            count=count,
                        )
                    )

        return trends
