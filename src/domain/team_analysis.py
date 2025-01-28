import plotly.express as px
import polars as pl

from src.domain.models import IssueAnalytics


class TeamAnalysis:
    def _to_dataframe(self, analytics_data: list[IssueAnalytics]) -> pl.DataFrame:
        """Convert IssueAnalytics list to DataFrame with calculated week column."""
        if not analytics_data:
            return pl.DataFrame()

        df = pl.DataFrame([vars(analytics) for analytics in analytics_data])
        if not df.is_empty():
            df = df.with_columns(
                [
                    pl.col("resolved")
                    .str.strptime(pl.Datetime)
                    .dt.week()
                    .alias("week"),
                ],
            )
        return df.unique()

    def visualize_project_composition(
        self,
        analytics_data: list[IssueAnalytics],
        output_path: str = "project_composition.html",
    ) -> None:
        """Create an interactive bar chart of project work composition.

        Args:
            df: DataFrame containing project work data
            output_path: Path to save the visualization HTML file

        """
        df = self._to_dataframe(analytics_data)
        if df.is_empty():
            msg = "No data available for visualization"
            raise ValueError(msg)

        # Calculate composition percentages
        composition = (
            (
                df.groupby(["project", "category", "week"])
                .agg(pl.count().alias("count"))
                .join(
                    df.groupby(["project", "week"]).agg(
                        pl.count().alias("count_total"),
                    ),
                    on=["project", "week"],
                )
                .with_columns(
                    (pl.col("count") / pl.col("count_total") * 100)
                    .round()
                    .alias("percentage"),
                )
            )
            .sort("project")
            .sort("week")
        )

        # Create stacked bar chart
        fig = (
            px.bar(
                composition,
                x="project",
                y="percentage",
                color="category",
                title="Engineering Work Taxonomy by project",
                facet_col="week",
                facet_col_wrap=1,
                labels={
                    "percentage": "Percentage of Work",
                    "category": "Work Category",
                    "project": "Project",
                    "Week": "Week",
                },
                barmode="stack",
                height=2000,
                text="percentage",
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            .update_layout(legend_traceorder="reversed")
            .update_traces(texttemplate="%{text:.0f}%", textposition="inside")
            .for_each_xaxis(lambda x: x.update(showticklabels=True))
        )

        fig.write_html(output_path)

    def visualize_project_lead_time(
        self,
        analytics_data: list[IssueAnalytics],
        output_path: str = "project_lead_time.html",
    ) -> None:
        """Create an interactive bar chart showing total lead time by project and category.

        Args:
            df: DataFrame containing project work data
            output_path: Path to save the visualization HTML file

        """
        df = self._to_dataframe(analytics_data)
        if df.is_empty():
            msg = "No data available for visualization"
            raise ValueError(msg)

        # Calculate total lead time for each project/category/week
        composition = (
            (
                df.groupby(["project", "category", "week"]).agg(
                    pl.col("lead_time_hours").sum().round(1).alias("total_lead_time"),
                )
            )
            .sort("project")
            .sort("week")
        )

        # Create stacked bar chart
        fig = (
            px.bar(
                composition,
                x="project",
                y="total_lead_time",
                color="category",
                title="Lead Time by Project and Category",
                facet_col="week",
                facet_col_wrap=1,
                labels={
                    "total_lead_time": "Total Lead Time (Hours)",
                    "category": "Work Category",
                    "project": "Project",
                    "Week": "Week",
                },
                barmode="stack",
                height=2000,
                text="total_lead_time",
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            .update_layout(legend_traceorder="reversed")
            .update_traces(texttemplate="%{text:.1f}", textposition="inside")
            .for_each_xaxis(lambda x: x.update(showticklabels=True))
        )

        fig.write_html(output_path)

    def analyze_weekly_trends(
        self,
        analytics_data: list[IssueAnalytics],
        output_path: str = "weekly_trends.html",
    ) -> None:
        """Create an interactive line chart showing weekly work composition trends.

        Args:
            df: DataFrame containing project work data
            output_path: Path to save the visualization HTML file

        """
        df = self._to_dataframe(analytics_data)
        if df.is_empty():
            msg = "No data available for visualization"
            raise ValueError(msg)

        composition = (
            df.groupby(
                [
                    "week",
                    "category",
                ],
            )
            .agg(pl.count().alias("count"))
            .join(df.groupby("week").agg(pl.count().alias("count_total")), on="week")
            .with_columns(
                (pl.col("count") / pl.col("count_total") * 100)
                .round()
                .alias("percentage"),
            )
        ).sort("week")

        fig = (
            px.line(
                composition,
                x="week",
                y="percentage",
                color="category",
                facet_col_wrap=2,
                title="Weekly Work Composition Trends",
                labels={
                    "percentage": "Percentage of Issues",
                    "week": "Week",
                    "category": "Work Category",
                },
                text="percentage",
                height=800,
            ).update_traces(texttemplate="%{text:.0f}%")
        ).update_xaxes(type="category")

        fig.write_html(output_path)

    def write_to_csv(
        self,
        analytics_data: list[IssueAnalytics],
        output_path: str = "analysis_output/engineering_taxonomy.csv",
    ) -> None:
        """Write DataFrame to CSV file."""
        df = self._to_dataframe(analytics_data)
        df.write_csv(output_path)
