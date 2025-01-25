def get_bar_chart_template(plotly_chart_html: str) -> str:
    """
    Returns the HTML template for the bar chart visualization with table.

    Args:
        plotly_chart_html: The HTML string of the Plotly chart

    Returns:
        Complete HTML template as a string
    """
    return f"""
    <html>
    <head>
        <style>
            .container {{ display: flex; flex-direction: column; }}
            #issueTable {{ margin-top: 20px; border-collapse: collapse; width: 100%; }}
            #issueTable th, #issueTable td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            #issueTable th {{ background-color: #f2f2f2; }}
            #tableContainer {{ display: none; margin-top: 20px; }}
        </style>
        <script>
            function handleBarClick(data) {{
                const tableContainer = document.getElementById('tableContainer');
                const tableBody = document.getElementById('issueTableBody');

                // Clear existing table content
                tableBody.innerHTML = '';

                // Parse the data from the customdata
                const issues = data.customdata[0].replace(/[\\[\\]']/g, '').split(', ');
                const types = data.customdata[1].replace(/[\\[\\]']/g, '').split(', ');
                const urls = data.customdata[2].replace(/[\\[\\]']/g, '').split(', ');
                const dates = data.customdata[3].replace(/[\\[\\]']/g, '').split(', ');

                // Create table rows
                for (let i = 0; i < issues.length; i++) {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><a href="${{urls[i]}}" target="_blank">${{issues[i]}}</a></td>
                        <td>${{types[i]}}</td>
                        <td>${{dates[i]}}</td>
                    `;
                    tableBody.appendChild(row);
                }}

                // Show the table
                tableContainer.style.display = 'block';

                // Update title
                document.getElementById('tableTitle').textContent =
                    `Issues for ${{data.x}} - ${{data.fullData.color}}`;
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <div id="chart">
                {plotly_chart_html}
            </div>
            <div id="tableContainer">
                <h2 id="tableTitle"></h2>
                <table id="issueTable">
                    <thead>
                        <tr>
                            <th>Issue Key</th>
                            <th>Type</th>
                            <th>Resolved Date</th>
                        </tr>
                    </thead>
                    <tbody id="issueTableBody">
                    </tbody>
                </table>
            </div>
        </div>
        <script>
            // Add click event listeners to all bars
            document.getElementById('chart').on('plotly_click', function(data) {{
                const point = data.points[0];
                handleBarClick(point);
            }});
        </script>
    </body>
    </html>
    """
