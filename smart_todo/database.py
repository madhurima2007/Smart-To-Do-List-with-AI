from __future__ import annotations

import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RUNTIME_ROOT = Path(os.getenv("SMART_TODO_DATA_DIR", "/tmp" if os.getenv("VERCEL") else BASE_DIR / "data"))
DATA_DIR = RUNTIME_ROOT
DB_PATH = DATA_DIR / "smart_todo.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High')),
                deadline TEXT,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'completed')),
                created_at TEXT NOT NULL,
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS task_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT NOT NULL,
                minutes_spent INTEGER NOT NULL CHECK(minutes_spent >= 0),
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """
        )
