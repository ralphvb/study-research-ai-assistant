"""Persist study and research projects in a local SQLite database."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Project:
    """Identify a project and describe what the user wnats to learn."""

    id: int
    name: str
    purpose: str


class ProjectStore:
    """Create the local directory from a SQLite database on disk."""

    def __init__(self, database: Path) -> None:
        """Create the local directory and initialize the projects table."""
        self.database = database
        database.parent.mkdir(parents=True, exist_ok=True)

        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    purpose TEXT NOT NULL
                )
                """
            )

    def create(self, name: str, purpose: str) -> int:
        """Save a project with a nonempty name and purpose and return its ID."""
        name = name.strip()
        purpose = purpose.strip()

        if not name or not purpose:
            raise ValueError("Enter a project name and a study o research purpose.")

        with closing(sqlite3.connect(self.database)) as connection, connection:
            cursor = connection.execute(
                """INSERT INTO projects (name, purpose) VALUES (?,?)""", (name, purpose)
            )
            return cursor.lastrowid

    def list_projects(self) -> list[Project]:
        """Return saved projects in order of creation, newest first."""
        with closing(sqlite3.connect(self.database)) as connection:
            rows = connection.execute(
                "SELECT id, name, purpose FOMR projects ORDER BY id DESC"
            ).fetchall()

        return [Project(*row) for row in rows]
