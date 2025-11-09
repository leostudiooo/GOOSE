# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GOOSE (Opens workOut for SEU undErgraduates) is a Python tool that helps SEU students upload workout data to servers. It uses a Terminal User Interface (TUI) built with Textual and supports Python 3.9+.

## Common Development Commands

### Setup and Installation
```bash
# Using uv (recommended)
uv venv .venv --python=3.9
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync

# Using pip
pip install -r requirements.txt
```

### Running the Application
```bash
python GOOSE.py
# or
./GOOSE.py  # if executable permissions set
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_filename.py

# Run with verbose output
pytest -v
```

## Architecture Overview

The codebase follows a layered architecture pattern:

### Layer Structure
1. **UI Layer** (`src/ui/`): Terminal UI (Textual) and CLI handlers
   - `tui/app.py`: Main TUI application class `GOOSEApp`
   - `tui/screens/`: Individual screens for different functionalities
   - `cli/`: CLI interaction handlers using questionary

2. **Service Layer** (`src/service/main_service.py`): Business logic
   - Central `Service` class that coordinates between UI and infrastructure
   - Handles workflow logic, data validation, and orchestration

3. **Model Layer** (`src/model/`): Data structures using Pydantic
   - `User`: User authentication and configuration
   - `Route`: Workout route definitions
   - `Track`: GPS track data structures
   - `UploadData`: Data format for server uploads

4. **Infrastructure Layer** (`src/infrastructure/`):
   - `api_client.py`: HTTP client for server communication using httpx/requests
   - `model_storage.py`: YAML-based persistence layer
   - `constants.py`: Application-wide constants and configuration
   - `exceptions.py`: Custom exception definitions

### Key Design Patterns
- **Dependency Injection**: Service layer receives infrastructure components
- **Repository Pattern**: `YAMLModelStorage` abstracts data persistence
- **Model-View Pattern**: TUI screens separated from business logic
- **Configuration Management**: YAML files in `config/` for user settings and static data

### Data Flow
1. User interacts with TUI screens
2. TUI calls Service layer methods
3. Service orchestrates between Model objects and Infrastructure
4. Infrastructure handles external APIs and file persistence
5. Results flow back through layers to update UI

### Important Files to Understand
- `GOOSE.py`: Entry point that initializes and runs the TUI application
- `src/service/main_service.py`: Core business logic implementation
- `src/ui/tui/app.py`: Main TUI application structure
- `src/infrastructure/api_client.py`: Server communication logic
- `config/`: Configuration files (headers.yaml, route_group.yaml, user.yaml)
- `resources/`: Static data (route boundaries, default tracks)

### Development Considerations
- The project uses Textual's reactive programming model for UI updates
- Authentication tokens are stored in `config/user.yaml`
- Workout routes are predefined in `config/route_group.yaml` with corresponding boundary data in `resources/boundaries/`
- The project deliberately avoids distributing executables to prevent abuse
- PRTS web tool (https://prts.烫烫烫的锟斤拷.top) is used for creating custom tracks