from typing import List
import pandas as pd
import plotly.express as px
from ..domain.interfaces import ChartGenerator
from ..domain.models import ProjectComposition, WeeklyTrend
from ..templates.visualization import get_bar_chart_template


class VisualizationService(ChartGenerator):
    """Implementation of ChartGenerator using Plotly."""

    def create_project_composition_chart(
        self, composition_data: List[ProjectComposition], output_path: str
    ) -> None:
        """
        Create an interactive bar chart of project work composition.

        Args:
            composition_data: List of ProjectComposition objects
            output_path: Path to save the visualization HTML file
        """
        if not composition_data:
            raise ValueError("No data available for visualization")

        # Convert to format suitable for Plotly
        plot_data = []
        for comp in composition_data:
            # Prepare the custom data for click events
            issues_data = {
                "keys": [issue.key for issue in comp.issues],
                "types": [issue.issue_type for issue in comp.issues],
                "urls": [issue.url for issue in comp.issues],
                "dates": [
                    issue.resolved_date.strftime("%Y-%m-%d %H:%M:%S")
                    if issue.resolved_date else ""
                    for issue in comp.issues
                ]
            }

            plot_data.append({
                "project": comp.project,
                "category": comp.category,
                "percentage": comp.percentage,
                "issues": str(issues_data["keys"]),
                "types": str(issues_data["types"]),
                "urls": str(issues_data["urls"]),
                "resolved_dates": str(issues_data["dates"])
            })

        # Create DataFrame for plotting
        df = pd.DataFrame(plot_data)

        # Create stacked bar chart
        fig = px.bar(
            df,
            x="project",
            y="percentage",
            color="category",
            title="Engineering Work Taxonomy by Project",
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

        # Add click event handling
        fig.update_traces(
            customdata=df[["issues", "types", "urls", "resolved_dates"]].values,
            hovertemplate="<br>".join([
                "Project: %{x}",
                "Category: %{color}",
                "Percentage: %{y}%",
                "<extra></extra>"
            ])
        )

        # Generate the HTML content using the template
        plotly_html = fig.to_html(full_html=False, include_plotlyjs=True)
        html_content = get_bar_chart_template(plotly_html)

        # Write the complete HTML to file
        with open(output_path, 'w') as f:
            f.write(html_content)

    def create_weekly_trends_chart(
        self, trend_data: List[WeeklyTrend], output_path: str
    ) -> None:
        """
        Create an interactive line chart showing weekly work composition trends.

        Args:
            trend_data: List of WeeklyTrend objects
            output_path: Path to save the visualization HTML file
        """
        if not trend_data:
            raise ValueError("No data available for visualization")

        # Convert to DataFrame for plotting
        df = pd.DataFrame([
            {
                "week": trend.week,
                "project": trend.project,
                "category": trend.category,
                "count": trend.count
            }
            for trend in trend_data
        ])

        fig = px.line(
            df,
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
