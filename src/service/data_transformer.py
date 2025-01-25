from typing import List
from collections import defaultdict
from ..domain.interfaces import DataTransformer
from ..domain.models import JiraIssue, ProjectComposition, WeeklyTrend


class IssueDataTransformer(DataTransformer):
    """Transforms raw issue data into analysis-ready formats."""

    def calculate_project_composition(
        self, issues: List[JiraIssue]
    ) -> List[ProjectComposition]:
        """
        Transform issues into project composition data.

        Args:
            issues: List of JiraIssue objects

        Returns:
            List of ProjectComposition objects representing work distribution
        """
        # Group issues by project and category
        project_data = defaultdict(lambda: defaultdict(list))
        project_totals = defaultdict(int)

        for issue in issues:
            project_data[issue.project_name][issue.category].append(issue)
            project_totals[issue.project_name] += 1

        compositions = []
        for project, categories in project_data.items():
            total = project_totals[project]
            for category, category_issues in categories.items():
                count = len(category_issues)
                percentage = (count / total) * 100

                composition = ProjectComposition(
                    project=project,
                    category=category,
                    count=count,
                    total_count=total,
                    percentage=round(percentage, 2),
                    issues=category_issues
                )
                compositions.append(composition)

        return compositions

    def calculate_weekly_trends(
        self, issues: List[JiraIssue]
    ) -> List[WeeklyTrend]:
        """
        Transform issues into weekly trend data.

        Args:
            issues: List of JiraIssue objects

        Returns:
            List of WeeklyTrend objects showing work distribution over time
        """
        # Group issues by week, project, and category
        weekly_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for issue in issues:
            if issue.resolved_date:
                week = issue.resolved_date.isocalendar()[1]  # Get ISO week number
                weekly_data[week][issue.project_name][issue.category] += 1

        trends = []
        for week, projects in weekly_data.items():
            for project, categories in projects.items():
                for category, count in categories.items():
                    trend = WeeklyTrend(
                        week=week,
                        project=project,
                        category=category,
                        count=count
                    )
                    trends.append(trend)

        return sorted(trends, key=lambda x: (x.week, x.project, x.category))
