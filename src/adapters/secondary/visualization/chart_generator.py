from typing import List
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ....domain.interfaces import ChartGenerator
from ....domain.models import ProjectComposition, WeeklyTrend


class PlotlyChartGenerator(ChartGenerator):
    """
    Plotly-based implementation of the ChartGenerator interface.
    Handles visualization generation using Plotly.
    """

    def create_project_composition_chart(
        self, composition_data: List[ProjectComposition], output_path: str
    ) -> None:
        """Generate project composition visualization."""
        # Group data by project
        project_data = {}
        for item in composition_data:
            if item.project not in project_data:
                project_data[item.project] = {"categories": [], "percentages": []}
            project_data[item.project]["categories"].append(item.category)
            project_data[item.project]["percentages"].append(item.percentage)

        # Create subplots
        fig = make_subplots(
            rows=len(project_data),
            cols=1,
            subplot_titles=list(project_data.keys()),
            vertical_spacing=0.05,
        )

        # Add bar traces for each project
        for idx, (project, data) in enumerate(project_data.items(), start=1):
            fig.add_trace(
                go.Bar(
                    name=project,
                    x=data["categories"],
                    y=data["percentages"],
                    text=[f"{p:.1f}%" for p in data["percentages"]],
                    textposition="auto",
                ),
                row=idx,
                col=1,
            )

        # Update layout
        fig.update_layout(
            height=300 * len(project_data),
            showlegend=False,
            title_text="Engineering Work Composition by Team",
        )

        # Save to file
        fig.write_html(output_path)

    def create_weekly_trends_chart(
        self, trend_data: List[WeeklyTrend], output_path: str
    ) -> None:
        """Generate weekly trends visualization."""
        # Group data by project and category
        project_category_data = {}
        for item in trend_data:
            key = (item.project, item.category)
            if key not in project_category_data:
                project_category_data[key] = {"weeks": [], "counts": []}
            project_category_data[key]["weeks"].append(f"Week {item.week}")
            project_category_data[key]["counts"].append(item.count)

        # Create figure
        fig = go.Figure()

        # Add line traces for each project-category combination
        for (project, category), data in project_category_data.items():
            fig.add_trace(
                go.Scatter(
                    name=f"{project} - {category}",
                    x=data["weeks"],
                    y=data["counts"],
                    mode="lines+markers",
                )
            )

        # Update layout
        fig.update_layout(
            title="Weekly Trends by Team and Category",
            xaxis_title="Week",
            yaxis_title="Count",
            height=600,
        )

        # Save to file
        fig.write_html(output_path)
