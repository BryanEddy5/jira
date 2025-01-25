"""
CLI entry point for the metrics application.
Uses the hexagonal architecture pattern with adapters for clean separation of concerns.
"""

from ..adapters.primary.cli.commands import app

if __name__ == "__main__":
    app()
