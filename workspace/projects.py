"""Persist study and research projects in a local SQLite database."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile


@dataclass(frozen=True)
class Project:
    """Identify a project and describe what the user wnats to learn."""

    id: int
    name: str
    purpose: str


@dataclass(frozen=True)
class SavedDocument:
    """Identify an original PDF registered under project."""

    id: int
    name: str
    relative_path: str


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

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects_documents (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER NOT NULL REFERENCES projects(id),
                    name TEXT NOT NULL,
                    relative_path TEXT NOT NULL UNIQUE
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
                "SELECT id, name, purpose FROM projects ORDER BY id DESC"
            ).fetchall()

        return [Project(*row) for row in rows]


    def save_documents(self, project_id: int, name: str, content: bytes) -> bool:
        """Save a validated PDF once per project and return whether it was added."""
        digest = sha256(content).hexdigest()
        relative_path = f"documents/{project_id}/{digest}.pdf"
        target = self.database.parent / relative_path

        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute("PRAGMA foreign_keys = ON")
            cursor = connection.execute(
                """
                INSERTO INTO projects_documents (project_id, name, relative_path)
                VALUES(?, ?, ?)
                ON CONFLICT(relative_path) DO NOTHING
                """,
                (project_id, name, relative_path)
            )

            if cursor.rowcount == 0:
                return False

            target.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
                temporary_path = Path(temporary.name)
                try:
                    temporary.write(content)
                    temporary.close()
                    temporary_path.replace(target)
                finally:
                    temporary_path.unlink(missing_ok=True)

        return True


    def list_documents(self, project_id: int) -> list[SavedDocument]:
        """Return the selected project's saved PDFs, newest first."""
        with closing(sqlite3.connect(self.database)) as connection:
            rows = connection.execute(
                """
                SELECT id, name, relative_path
                FROM projects_documents
                WHERE project_id = ?
                ORDER BY id DESC
                """,
                (project_id,),
            ).fetchall()

        return [SavedDocument(*row) for row in rows]


    def read_document(self, document: SavedDocument) -> bytes:
        """Read the original bytes a registered PDF."""
        return (self.database.parent / document.relative_path).read_bytes()

