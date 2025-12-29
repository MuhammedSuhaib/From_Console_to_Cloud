"""
Interactive CLI interface for todo application using questionary and rich
"""
import questionary
from rich.console import Console
from rich.table import Table
from .todo import TodoApp


class TodoCLI:
    def __init__(self):
        self.app = TodoApp()
        self.console = Console()

    def run(self, args=None):
        """Run the interactive CLI."""
        # Only run interactive mode
        try:
            self._run_interactive_mode()
        except Exception as e:
            # If interactive mode fails (e.g., due to terminal issues), show error
            self.console.print(f"[red]Error starting interactive mode: {e}[/red]")
            self.console.print("[yellow]Please run in a terminal that supports interactive prompts.[/yellow]")

    def _run_interactive_mode(self):
        """Run the interactive menu system."""
        self.console.print("[bold cyan]Welcome to Todo CLI![/bold cyan]")

        while True:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "Add Todo",
                    "List Todos",
                    "Complete Todo",
                    "Edit Todo",
                    "Delete Todo",
                    "Exit",
                ],
            ).ask()

            if choice == "Add Todo":
                self._add_todo_interactive()
            elif choice == "List Todos":
                self._list_todos_interactive()
            elif choice == "Complete Todo":
                self._complete_todo_interactive()
            elif choice == "Edit Todo":
                self._edit_todo_interactive()
            elif choice == "Delete Todo":
                self._delete_todo_interactive()
            elif choice == "Exit" or choice is None:
                self.console.print("[bold cyan]Goodbye![/bold cyan]")
                break

    def _add_todo_interactive(self):
        """Add a todo interactively."""
        title = questionary.text("Enter todo title:").ask()
        if not title:
            self.console.print("[yellow]Todo title cannot be empty![/yellow]")
            return

        description = questionary.text("Enter todo description (optional):").ask() or ""

        try:
            todo = self.app.add_todo(title, description)
            self.console.print(f"[green]Added todo: {todo.title} (ID: {todo.id})[/green]")
        except ValueError as e:
            self.console.print(f"[red]Error: {e}[/red]")

    def _list_todos_interactive(self):
        """List todos interactively."""
        filter_choice = questionary.select(
            "Filter todos:",
            choices=[
                "All Todos",
                "Completed Only",
                "Pending Only",
            ],
        ).ask()

        completed = None
        if filter_choice == "Completed Only":
            completed = True
        elif filter_choice == "Pending Only":
            completed = False

        todos = self.app.list_todos(completed=completed)

        if todos:
            table = Table(title=f"{filter_choice}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Status", style="magenta")
            table.add_column("Title", style="green")
            table.add_column("Description", style="yellow")

            for todo in todos:
                status = "✓" if todo.completed else "○"
                table.add_row(
                    str(todo.id),
                    status,
                    todo.title,
                    todo.description
                )

            self.console.print(table)
        else:
            self.console.print("[yellow]No todos found.[/yellow]")

    def _complete_todo_interactive(self):
        """Complete a todo interactively."""
        todos = self.app.list_todos(completed=False)

        if not todos:
            self.console.print("[yellow]No pending todos to complete.[/yellow]")
            return

        choices = [f"{todo.id}: {todo.title}" for todo in todos]
        choice = questionary.select("Select todo to complete:", choices=choices).ask()

        if choice:
            todo_id = int(choice.split(':')[0])
            try:
                self.app.complete_todo(todo_id)
                self.console.print(f"[green]Marked todo {todo_id} as completed![/green]")
            except ValueError as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _edit_todo_interactive(self):
        """Edit a todo interactively."""
        todos = self.app.list_todos()

        if not todos:
            self.console.print("[yellow]No todos to edit.[/yellow]")
            return

        choices = [f"{todo.id}: {todo.title}" for todo in todos]
        choice = questionary.select("Select todo to edit:", choices=choices).ask()

        if choice:
            todo_id = int(choice.split(':')[0])

            # Get current todo
            current_todo = self.app.get_todo(todo_id)

            # Ask for new values, keeping current ones as defaults
            new_title = questionary.text("Enter new title:", default=current_todo.title).ask()
            new_description = questionary.text("Enter new description:", default=current_todo.description).ask()

            try:
                self.app.update_todo(todo_id, new_title, new_description)
                self.console.print(f"[green]Updated todo {todo_id}![/green]")
            except ValueError as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _delete_todo_interactive(self):
        """Delete a todo interactively."""
        todos = self.app.list_todos()

        if not todos:
            self.console.print("[yellow]No todos to delete.[/yellow]")
            return

        choices = [f"{todo.id}: {todo.title}" for todo in todos]
        choice = questionary.select("Select todo to delete:", choices=choices).ask()

        if choice:
            todo_id = int(choice.split(':')[0])
            confirm = questionary.confirm(f"Are you sure you want to delete todo {todo_id}?").ask()

            if confirm:
                try:
                    self.app.delete_todo(todo_id)
                    self.console.print(f"[green]Deleted todo {todo_id}![/green]")
                except ValueError as e:
                    self.console.print(f"[red]Error: {e}[/red]")


def main():
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()