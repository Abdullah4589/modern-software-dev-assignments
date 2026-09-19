from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"

NOTE_COLUMNS = "id, content, created_at"
ACTION_ITEM_COLUMNS = "id, note_id, text, done, created_at"

SCHEMA = (
    """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """,
    """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """,
)


def ensure_data_directory_exists() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def _transaction() -> Iterator[sqlite3.Connection]:
    """Yield a connection that commits on success, rolls back on error, and always closes.

    `with sqlite3.Connection` alone only manages the transaction; it does not close.
    """
    connection = get_connection()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def _fetch_all(query: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
    with _transaction() as connection:
        return connection.execute(query, params).fetchall()


def _fetch_one(query: str, params: Sequence[Any] = ()) -> sqlite3.Row | None:
    with _transaction() as connection:
        return connection.execute(query, params).fetchone()


def _execute(query: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
    """Run a single write statement; the returned cursor exposes lastrowid and rowcount."""
    with _transaction() as connection:
        return connection.execute(query, params)


def init_db() -> None:
    with _transaction() as connection:
        for statement in SCHEMA:
            connection.execute(statement)


def insert_note(content: str) -> int:
    return int(_execute("INSERT INTO notes (content) VALUES (?)", (content,)).lastrowid)


def list_notes() -> list[sqlite3.Row]:
    return _fetch_all(f"SELECT {NOTE_COLUMNS} FROM notes ORDER BY id DESC")


def get_note(note_id: int) -> sqlite3.Row | None:
    return _fetch_one(f"SELECT {NOTE_COLUMNS} FROM notes WHERE id = ?", (note_id,))


def insert_action_items(items: list[str], note_id: int | None = None) -> list[int]:
    # One transaction for the whole batch, so a failure part-way inserts nothing.
    with _transaction() as connection:
        return [
            int(
                connection.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                ).lastrowid
            )
            for item in items
        ]


def list_action_items(note_id: int | None = None) -> list[sqlite3.Row]:
    query = f"SELECT {ACTION_ITEM_COLUMNS} FROM action_items"
    params: tuple[Any, ...] = ()
    if note_id is not None:
        query += " WHERE note_id = ?"
        params = (note_id,)
    return _fetch_all(query + " ORDER BY id DESC", params)


def mark_action_item_done(action_item_id: int, done: bool) -> bool:
    """Return True if the action item existed and was updated."""
    with _transaction() as connection:
        cursor = connection.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        return cursor.rowcount > 0
