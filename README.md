# Metrics Application

A Python application for analyzing and visualizing engineering metrics using a hexagonal architecture pattern.

## Architecture

This application follows the hexagonal architecture (also known as ports and adapters) pattern to maintain clean separation of concerns and dependency inversion. The architecture is organized into three main layers:

### 1. Domain Layer (Core)

Located in `src/domain/`, this layer contains:
- Pure business logic and domain models
- Interface definitions (ports)
- No dependencies on external frameworks or services

Key components:
- `models.py`: Domain entities (JiraIssue, ProjectComposition, WeeklyTrend)
- `interfaces.py`: Protocol definitions for ports
- `services/analytics.py`: Core business logic implementation

### 2. Primary Adapters (Driving)

Located in `src/adapters/primary/`, these adapt external input to the domain:
- CLI interface using Typer
- Handles user interaction and command parsing
- Depends on domain interfaces, not implementations

### 3. Secondary Adapters (Driven)

Located in `src/adapters/secondary/`, these adapt the domain to external services:
- Jira adapter for data retrieval and transformation
- Visualization adapter for generating charts
- Implements domain interfaces, allowing the core to remain isolated

## Dependency Flow

```
Primary Adapters → Domain ← Secondary Adapters
```

The domain layer defines interfaces (ports) that adapters must implement. This ensures:
- The domain remains isolated and focused on business logic
- External dependencies are pluggable and replaceable
- Testing is simplified through mock implementations

## Usage

The application provides CLI commands for analyzing engineering metrics:

```bash
# Analyze team metrics
python -m src.cli.entry analyze-teams --weeks 4 --output-dir analysis_output

# List available teams
python -m src.cli.entry list-teams
```

## Development

### Adding New Features

1. Start with the domain layer:
   - Define new models in `domain/models.py`
   - Define new interfaces in `domain/interfaces.py`
   - Implement core logic in `domain/services/`

2. Implement adapters:
   - Primary adapters in `adapters/primary/` for new user interfaces
   - Secondary adapters in `adapters/secondary/` for external services

3. Wire everything in the composition root:
   - Update `adapters/primary/cli/commands.py` to compose new components

### Testing

The hexagonal architecture makes testing easier:
- Domain logic can be tested in isolation
- Adapters can be tested with mock implementations of domain interfaces
- Integration tests can use real implementations while keeping the domain pure
