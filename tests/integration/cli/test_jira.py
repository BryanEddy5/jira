import pytest
from typer.testing import CliRunner

from src.adapters.primary.cli.entry import app

runner = CliRunner()


@pytest.mark.integration
def test_health_check() -> None:
    """Test the 'jira health-check' command."""
    # Execute command
    result = runner.invoke(app, ["jira", "health-check"], catch_exceptions=False)

    # Check exit code
    assert result.exit_code == 0

    # Check output
    assert "JIRA API is accessible. https://shippo.atlassian.net" in result.stdout


@pytest.mark.integration
def test_get_issue() -> None:
    """Test the 'jira get-issue' command."""
    issue_key = "ATP-1708"
    issue_summary = "Fix PO Box format"

    # Execute command
    result = runner.invoke(
        app,
        ["jira", "get-issue", issue_key],
        catch_exceptions=False,
    )

    # Check exit code
    assert result.exit_code == 0

    # Check output
    assert issue_key in result.stdout  # Issue key should be in output
    assert issue_summary in result.stdout  # Basic issue details should be present


@pytest.mark.integration
def test_create_plan() -> None:
    """Test the 'jira create-plan' command."""
    issue_key = "ATP-1708"
    plan_name = "Test Integration Plan"
    lead_email = "bryan.eddy@shippo.com"  # Example email

    # Execute command
    result = runner.invoke(
        app,
        [
            "jira", "create-plan",
            issue_key,
            "--name", plan_name,
            "--lead-email", lead_email,
        ],
        catch_exceptions=False,
    )

    # Check exit code
    assert result.exit_code == 0

    # Check output contains issue details
    assert issue_key in result.stdout
    assert "Root Issues (1):" in result.stdout
    assert "Fix PO Box format" in result.stdout

    # Check Jira Plan creation success
    assert "Jira Plan created successfully:" in result.stdout
    assert f"Name: {plan_name}" in result.stdout
    assert "URL: https://shippo.atlassian.net/jira/plans/" in result.stdout
