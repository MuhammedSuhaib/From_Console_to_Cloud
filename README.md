# Interactive CLI Todo Application

An interactive command-line interface todo application built with Python. This is an in-memory implementation where todos are stored only during the application session.

## Features

- Interactive menu system for adding, listing, completing, editing, and deleting todos
- Filter todos by completion status
- Rich terminal interface with tables and formatting
- Simple in-memory storage (data resets on each run)
- Cross-platform compatibility

## Requirements

- Python 3.10+
- uv package manager (recommended)

## Installation

This project uses uv as the recommended package manager.

Using uv:
```bash
# Clone the repository
git clone <repository-url>

# Navigate to the project directory
cd cli-todo

# Install dependencies with uv
uv sync
```

Alternatively with pip:
```bash
pip install -e .
```

## Usage

The application provides an interactive menu-based interface:

### Interactive Mode
```bash
python -m src.main
# or if installed with the console script:
todo
```

This launches an interactive menu where you can:
- Add new todos with title and description
- List all todos with a formatted table
- Mark todos as completed
- Edit existing todos
- Delete todos

## Architecture

The application is a simple in-memory implementation with:
- `src/todo.py` - Contains the Todo class and TodoApp for in-memory storage
- `src/cli.py` - Contains the interactive CLI interface using questionary and rich
- `src/main.py` - Application entry point

## File Structure

```
src/
├── todo.py              # Todo classes and in-memory storage
├── cli.py               # Interactive CLI interface
├── main.py              # Application entry point
└── __init__.py          # Package initialization
```

## Testing

Run the tests using pytest:

With uv (recommended):
```bash
uv run python -m pytest tests/
```

Or with pip:
```bash
pip install pytest
python -m pytest tests/
```

## Note

This is an in-memory implementation, meaning todos are stored only during the application session. Data is not persisted between runs and will be lost when the application exits.
