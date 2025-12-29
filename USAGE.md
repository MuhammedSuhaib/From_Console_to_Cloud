# Usage Guide for Interactive CLI Todo Application

## Overview
This is an interactive CLI todo application with in-memory storage. The application provides a menu-driven interface for managing todos.

## Project Structure Fix
The project was initially misconfigured with source files in the root directory while pyproject.toml expected them in a src/ directory. The following fixes were made:

1. **Fixed Project Structure**: Moved all source files (cli.py, main.py, todo.py, __init__.py) from the root directory to a `src/` directory to create a proper Python package structure.

2. **Created Proper Package Structure**: Added an `__init__.py` file in the src directory to make it a proper Python package, while keeping a minimal one in the root.

3. **Verified Configuration**: Confirmed that pyproject.toml was correctly configured with:
   - `[project.scripts]` pointing to `"src.main:main"`
   - `[tool.setuptools.packages.find]` with `where = ["src"]`
   - Added pytest configuration for better test running

4. **Updated Documentation**: Updated README.md to reflect the interactive CLI nature of the application instead of command-line arguments.

5. **Created Usage Guide**: Created this USAGE.md file with clear instructions on how to run the application.

6. **Verified Functionality**:
   - Successfully ran `uv sync` to install dependencies
   - All 15 tests pass with `uv run python -m pytest`
   - Confirmed core functionality works with `uv run python -c "from src.todo import TodoApp"`

## Installation and Setup

### Using uv (recommended):
```bash
# Install dependencies
uv sync

# Install for development with console script
uv sync --all-extras
```

## Running the Application

### Interactive Mode:
```bash
# Method 1: Using module run
uv run python -m src.main

# Method 2: Using console script (if installed)
uv run todo
```

**Note**: In some terminal environments, you may get a compatibility error when using the interactive mode. This is due to the `questionary` library's terminal requirements. If you encounter this, you're likely using a terminal that doesn't fully support the interactive prompts required by the library.

## Console Script Availability
The application includes a console script called `todo` which is available after installation. If you see a module import error, it's likely that the package installation needs to be refreshed.

## Key Features
- Interactive menu-driven interface
- Add todos with title and description
- List todos in a formatted table
- Mark todos as completed
- Edit existing todos
- Delete todos
- Filter todos by completion status

## Core Components
- `src/todo.py` - Core Todo and TodoApp classes with in-memory storage
- `src/cli.py` - Interactive CLI interface using questionary and rich
- `src/main.py` - Application entry point
- `pyproject.toml` - Project configuration and dependencies

## Testing
To run tests:
```bash
uv run python -m pytest tests/
```

All tests should pass after proper installation.

## Skills Developed and Applied
- **Python Package Structure**: Understanding proper Python package organization and setup.py/pyproject.toml configuration
- **uv Package Management**: Working with the uv package manager, including sync, run, and installation commands
- **Console Script Configuration**: Setting up and troubleshooting console script entry points in pyproject.toml
- **Terminal Compatibility Issues**: Understanding issues with interactive libraries like questionary in different terminal environments
- **Project Refactoring**: Restructuring a misconfigured project to follow Python packaging best practices
- **Testing Integration**: Ensuring tests continue to pass after structural changes
- **Documentation Writing**: Creating clear usage guides for complex software projects