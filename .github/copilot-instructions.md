# GitHub Copilot Instructions for GOOSE

This file provides guidance to GitHub Copilot when working with the GOOSE repository.

## Project Overview

GOOSE (Opens workOut for SEU undErgraduates) is a Python tool that helps SEU students upload workout data to servers. The project features:

- **Language**: Python 3.9+
- **UI Framework**: Textual (Terminal User Interface)
- **Architecture**: Layered architecture with clear separation of concerns
- **License**: GPLv3

## Development Setup

### Installation

Always use Python 3.9 or higher. The recommended setup uses `uv` for package management:

```bash
# Using uv (recommended)
uv venv .venv --python=3.9
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync

# Using pip (alternative)
pip install -r requirements.txt
```

### Running the Application

```bash
python GOOSE.py
# or on macOS/Linux with executable permissions
./GOOSE.py
```

## Testing

Always run tests before making changes to understand baseline behavior:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_filename.py

# Run with verbose output
pytest -v
```

## Code Quality Standards

**IMPORTANT**: All PRs must pass linting checks. Always run linting before committing:

```bash
# Check code with Ruff
ruff check .

# Auto-fix safe issues
ruff check --fix .

# Format code with Black
black .

# Sort imports
isort .
```

### Code Style Conventions

- **Line length**: 100 characters (enforced)
- **Indentation**: 4 spaces (no tabs)
- **Variable names**: mixedCase is allowed (existing API contract)
- **Module names**: PascalCase is allowed (existing file structure)

## Architecture

The codebase follows a layered architecture pattern:

### Layer Structure

1. **UI Layer** (`src/ui/`): User interfaces
   - `tui/`: Textual-based Terminal UI
   - `cli/`: Command-line interface handlers using questionary

2. **Service Layer** (`src/service/main_service.py`): Business logic
   - Central `Service` class coordinates between UI and infrastructure
   - Handles workflow logic, data validation, and orchestration

3. **Model Layer** (`src/model/`): Data structures using Pydantic
   - `User`: User authentication and configuration
   - `Route`: Workout route definitions
   - `Track`: GPS track data structures
   - `UploadData`: Data format for server uploads

4. **Infrastructure Layer** (`src/infrastructure/`):
   - `api_client.py`: HTTP client for server communication
   - `model_storage.py`: YAML-based persistence layer
   - `constants.py`: Application-wide constants
   - `exceptions.py`: Custom exception definitions

### Key Design Patterns

- **Dependency Injection**: Service layer receives infrastructure components
- **Repository Pattern**: `YAMLModelStorage` abstracts data persistence
- **Model-View Pattern**: TUI screens separated from business logic
- **Configuration Management**: YAML files in `config/` directory

### Important Files

- `GOOSE.py`: Entry point that initializes and runs the TUI application
- `src/service/main_service.py`: Core business logic implementation
- `src/ui/tui/app.py`: Main TUI application structure
- `src/infrastructure/api_client.py`: Server communication logic
- `config/`: Configuration files (headers.yaml, route_group.yaml, user.yaml)
- `resources/`: Static data (route boundaries, default tracks)

## Development Guidelines

### When Adding New Features

1. Always validate changes with existing tests first
2. Add new tests for new functionality
3. Run linting before committing
4. Ensure code follows the layered architecture
5. Update documentation if the feature affects user-facing behavior

### When Fixing Bugs

1. Write a test that reproduces the bug
2. Fix the bug with minimal changes
3. Verify the test passes
4. Run the full test suite to ensure no regressions

### Configuration Files

- Authentication tokens are stored in `config/user.yaml`
- Workout routes are defined in `config/route_group.yaml`
- Route boundaries are in `resources/boundaries/`
- The project uses YAML for all configuration files

### Important Constraints

- The project deliberately avoids distributing executables to prevent abuse
- Custom track generation is done via the PRTS web tool (https://prts.烫烫烫的锟斤拷.top)
- The application uses Textual's reactive programming model for UI updates
- All data persistence uses YAML format through the `YAMLModelStorage` abstraction

## Common Tasks

### Adding a New Model

1. Create the model in `src/model/` using Pydantic
2. Add validation logic using Pydantic validators
3. Update `YAMLModelStorage` if persistence is needed
4. Add tests in `tests/`

### Adding a New UI Screen

1. Create screen in `src/ui/tui/screens/`
2. Follow Textual's reactive programming patterns
3. Connect to Service layer for business logic
4. Avoid direct infrastructure calls from UI

### Modifying API Client

1. Changes should be in `src/infrastructure/api_client.py`
2. Maintain separation from business logic
3. Use httpx/requests for HTTP communication
4. Handle errors appropriately

## Testing Strategy

- Unit tests for models, validators, and utilities
- Integration tests for CLI workflows
- Mock external API calls in tests
- Test both success and error paths

## Tools and Dependencies

- **Textual**: Terminal UI framework
- **Pydantic**: Data validation and models
- **httpx/requests**: HTTP client libraries
- **PyYAML**: YAML parsing
- **questionary**: CLI prompts
- **pytest**: Testing framework
- **ruff, black, isort**: Code quality tools
