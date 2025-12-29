"""
Main entry point for the interactive todo application
"""
import sys
from .cli import TodoCLI


def main():
    # Run in interactive mode
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()