# CLI Todo Application

A simple command-line interface todo application built with Python that runs interactively in the terminal.

## How to Run

```bash
python -m src.main
```

This launches an interactive menu where you can:
- Add, list, complete, edit, and delete todos
- Filter todos by completion status
- View todos in a formatted table

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
