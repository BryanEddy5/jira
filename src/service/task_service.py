from jira import JIRA
from datetime import datetime
from typing import List
import polars as pl
import plotly.express as px


class TaskService:
    def __init__(self, jira: JIRA):
        self.jira = jira
        self.project = "project"
        self.engineering_work_taxonomy = "customfield_11173"

    def get_all_projects(self) -> List[str]:
        """Get list of all projects from Jira."""
        jql = 'category in ("core connectivity") and created >= -30d order by created DESC'
        projects = set()

        # Search for issues and extract unique project names
        issues = self.jira.search_issues(
            jql,
            maxResults=1000,
            fields=[
                self.engineering_work_taxonomy,
                "project",
            ],  # Assuming project field is available
        )

        for issue in issues:
            if hasattr(issue.fields, self.engineering_work_taxonomy):
                project = str(issue.fields.project.name)
                if project:
                    projects.add(project)

        return sorted(list(project))

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
        for project in projects:
            jql = (
                f'category = "Core Connectivity" '
                f'AND resolved >= "{start_date.strftime("%Y-%m-%d")}" '
                f'AND resolved <= "{end_date.strftime("%Y-%m-%d")}" '
                "ORDER BY resolved DESC"
            )

            issues = self.jira.search_issues(
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
                ],
            )

            for issue in issues:
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
                    }
                )

        # Convert to DataFrame for easier analysis
        df = pl.DataFrame(all_data)
        if not df.is_empty():
            df = df.with_columns(
                [
                    pl.col("resolved").str.strptime(pl.Datetime),
                    pl.col("resolved")
                    .str.strptime(pl.Datetime)
                    .dt.week()
                    .alias("week"),
                ]
            )

        return df

    def visualize_project_composition(
        self, df: pl.DataFrame, output_path: str = "project_composition.html"
    ) -> None:
        """
        Create an interactive bar chart of project work composition.

        Args:
            df: DataFrame containing project work data
            output_path: Path to save the visualization HTML file
        """
        if df.is_empty():
            raise ValueError("No data available for visualization")

        # Calculate composition percentages
        composition = (
            df.groupby(["project", "category",])
            .agg(pl.count().alias("count"))
            .join(df.groupby("project").agg(pl.count().alias("count_total")), on="project")
            .with_columns(
                (pl.col("count") / pl.col("count_total") * 100).round().alias("percentage")
            )
        )

        # Create stacked bar chart
        fig = px.bar(
            composition,
            x="project",
            y="percentage",
            color="category",
            title="Engineering Work Taxonomy by project",
            labels={
                "percentage": "Percentage of Work",
                "category": "Work Category",
            },
            height=600,
            barmode="stack",
            text="percentage",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        fig.update_layout(legend_traceorder="reversed")

        fig.write_html(output_path)

    def analyze_weekly_trends(
        self, df: pl.DataFrame, output_path: str = "weekly_trends.html"
    ) -> None:
        """
        Create an interactive line chart showing weekly work composition trends.

        Args:
            df: DataFrame containing project work data
            output_path: Path to save the visualization HTML file
        """
        if df.is_empty():
            raise ValueError("No data available for visualization")

        weekly_composition = df.groupby(["week", "project", "category"]).agg(
            pl.count().alias("count")
        )

        fig = px.line(
            weekly_composition,
            x="week",
            y="count",
            color="category",
            facet_col="project",
            facet_col_wrap=2,
            title="Weekly Work Composition Trends by Project",
            labels={
                "count": "Number of Issues",
                "week": "Week",
                "category": "Work Category",
            },
            height=800,
        )

        fig.write_html(output_path)
