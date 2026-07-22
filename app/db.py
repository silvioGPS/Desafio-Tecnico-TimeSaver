from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

DEFAULT_USER = {
    "username": "admin",
    "email": "admin@timersaver.com.br",
}


class DatabaseUnavailable(RuntimeError):
    pass


def _database_path() -> Path:
    return Path(current_app.config["DATABASE_PATH"])


def _open_connection() -> sqlite3.Connection:
    try:
        database_path = _database_path()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as exc:
        raise DatabaseUnavailable(str(exc)) from exc


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = _open_connection()
    return g.db


def close_db(_: Exception | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db() -> None:
    connection = _open_connection()
    try:
        connection.executescript(SCHEMA_SQL)
        connection.commit()
    finally:
        connection.close()


def seed_default_user(password_hash: str) -> None:
    connection = _open_connection()
    try:
        connection.executescript(SCHEMA_SQL)
        existing = connection.execute("SELECT id FROM users WHERE username = ? OR email = ?", (DEFAULT_USER["username"], DEFAULT_USER["email"])).fetchone()
        if existing is None:
            connection.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (DEFAULT_USER["username"], DEFAULT_USER["email"], password_hash),
            )
        connection.commit()
    finally:
        connection.close()


def get_user_by_identifier(identifier: str):
    try:
        connection = get_db()
        return connection.execute(
            """
            SELECT id, username, email, password_hash
            FROM users
            WHERE lower(username) = lower(?) OR lower(email) = lower(?)
            LIMIT 1
            """,
            (identifier, identifier),
        ).fetchone()
    except sqlite3.Error as exc:
        raise DatabaseUnavailable(str(exc)) from exc