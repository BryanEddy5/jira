from typer.testing import CliRunner
import pytest
from src.adapters.primary.cli.entry import app

runner = CliRunner()

@pytest.mark.integration
def test_health_check():
    """Test the 'jira health-check' command."""
    # Execute command
    result = runner.invoke(app, ["jira", "health-check"], catch_exceptions=False)

    # Check exit code
    assert result.exit_code == 0

    # Check output
    assert "JIRA API is accessible. https://shippo.atlassian.net" in result.stdout


@pytest.mark.integration
def test_get_issue():
    """Test the 'jira get-issue' command."""
    issue_key = "ATP-1708"
    issue_summary = "Fix PO Box format"

    # Execute command
    result = runner.invoke(app, ["jira", "get-issue", issue_key], catch_exceptions=False)

    # Check exit code
    assert result.exit_code == 0

    # Check output
    assert issue_key in result.stdout  # Issue key should be in output
    assert issue_summary in result.stdout  # Basic issue details should be present