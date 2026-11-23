"""Verify the Python runtime from the initial command-line entry point."""

import sys


def main() -> None:
    """Display the application name and the active Python runtime."""
    print("Study and research AI Assistant")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Python executable: {sys.executable}")


if __name__ == '__main__':
    main()