import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.adapters.primary.cli.entry import app

runner = CliRunner()


@pytest.mark.integration
def test_projects_analyze(tmp_path) -> None:
    """Test the 'projects analyze' command."""
    # Setup: Save current analysis output if it exists
    analysis_dir = Path("analysis_output")
    backup_dir = tmp_path / "backup"
    backup_dir.mkdir()

    if analysis_dir.exists():
        shutil.copytree(
            analysis_dir, backup_dir / "analysis_output", dirs_exist_ok=True,
        )

    try:
        # Execute command
        result = runner.invoke(
            app,
            ["projects", "analyze", "--start-date=2025-01-01"],
            catch_exceptions=False,
        )

        # Check exit code
        assert result.exit_code == 0

        # Check output
        assert "Analysis complete!" in result.stdout

        # Compare output files with fixtures
        for filename in [
            "engineering_taxonomy.csv",
            "lead_time.html",
            "team_composition.html",
            "weekly_trends.html",
        ]:
            actual = analysis_dir / filename
            expected = Path("tests/fixtures/analysis_output") / filename
            assert actual.exists(), f"Missing output file: {filename}"
            assert expected.exists(), f"Missing fixture file: {filename}"
            assert actual.read_text() == expected.read_text(), (
                f"Content mismatch in {filename}"
            )

    finally:
        # Cleanup: Restore original files if they existed
        if (backup_dir / "analysis_output").exists():
            shutil.rmtree(analysis_dir, ignore_errors=True)
            shutil.copytree(
                backup_dir / "analysis_output", analysis_dir, dirs_exist_ok=True,
            )


@pytest.mark.integration
def test_projects_list() -> None:
    """Test the 'projects list' command."""
    # Execute command
    result = runner.invoke(app, ["projects", "list"], catch_exceptions=False)

    # Check exit code
    assert result.exit_code == 0

    # Check output
    assert len(result.stdout.strip()) > 0  # Should have some output
    assert "Project:" in result.stdout  # Basic header should be present
