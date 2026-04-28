from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from .database import get_connection


PRIORITY_RANK = {"High": 3, "Medium": 2, "Low": 1}
TIME_BUCKETS = {
    "Morning": range(5, 12),
    "Afternoon": range(12, 17),
    "Evening": range(17, 22),
    "Night": range(22, 24),
    "Late Night": range(0, 5),
}


@dataclass
class TaskCreate:
    title: str
    description: str
    priority: str
    deadline: str | None


def _utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def create_task(task: TaskCreate) -> int:
    if task.priority not in PRIORITY_RANK:
        raise ValueError("Priority must be Low, Medium, or High.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, description, priority, deadline, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
            """,
            (task.title, task.description, task.priority, task.deadline, _utc_now()),
        )
        return int(cursor.lastrowid)


def list_tasks() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                title,
                description,
                priority,
                deadline,
                status,
                created_at,
                completed_at,
                CASE
                    WHEN deadline IS NOT NULL AND date(deadline) < date('now') AND status = 'pending'
                    THEN 1
                    ELSE 0
                END AS is_overdue
            FROM tasks
            ORDER BY
                CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                END,
                CASE
                    WHEN deadline IS NULL THEN 1
                    ELSE 0
                END,
                deadline ASC,
                created_at ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_task(task_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def complete_task(task_id: int, minutes_spent: int) -> None:
    existing = get_task(task_id)
    if existing is None:
        raise ValueError("Task not found.")
    if existing["status"] == "completed":
        return

    completed_at = _utc_now()
    started_at = (datetime.fromisoformat(completed_at) - timedelta(minutes=minutes_spent)).isoformat()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET status = 'completed', completed_at = ?
            WHERE id = ? AND status != 'completed'
            """,
            (completed_at, task_id),
        )
        connection.execute(
            """
            INSERT INTO task_sessions (task_id, started_at, ended_at, minutes_spent)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, started_at, completed_at, minutes_spent),
        )


def get_task(task_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return dict(row) if row else None


def get_smart_suggestion() -> str:
    tasks = [task for task in list_tasks() if task["status"] == "pending"]
    if not tasks:
        return "You are all caught up. Add a new goal to keep the momentum going."

    def score(task: dict) -> tuple[int, int, str]:
        deadline = task["deadline"] or "9999-12-31"
        overdue_bonus = 50 if task["is_overdue"] else 0
        return (-(PRIORITY_RANK[task["priority"]] * 10 + overdue_bonus), 0, deadline)

    best_task = sorted(tasks, key=score)[0]
    if best_task["is_overdue"]:
        return f'Start "{best_task["title"]}" first because it is overdue and marked {best_task["priority"]} priority.'
    if best_task["deadline"]:
        return f'Start "{best_task["title"]}" first because it has a {best_task["priority"].lower()} priority and the nearest deadline.'
    return f'Start "{best_task["title"]}" first because it has the highest priority in your list.'


def _bucket_from_hour(hour: int) -> str:
    for label, hours in TIME_BUCKETS.items():
        if hour in hours:
            return label
    return "Unknown"


def analytics_summary() -> dict:
    tasks = list_tasks()
    completed = [task for task in tasks if task["status"] == "completed"]
    pending = [task for task in tasks if task["status"] == "pending"]

    with get_connection() as connection:
        session_rows = connection.execute(
            """
            SELECT task_id, ended_at, minutes_spent
            FROM task_sessions
            ORDER BY ended_at ASC
            """
        ).fetchall()

    sessions = [dict(row) for row in session_rows]
    daily_counter: Counter[str] = Counter()
    bucket_counter: Counter[str] = Counter()
    total_minutes = 0

    for session in sessions:
        ended_at = datetime.fromisoformat(session["ended_at"])
        day_key = ended_at.date().isoformat()
        daily_counter[day_key] += 1
        bucket_counter[_bucket_from_hour(ended_at.hour)] += 1
        total_minutes += session["minutes_spent"]

    completion_rate = round((len(completed) / len(tasks) * 100), 1) if tasks else 0.0
    avg_minutes = round(total_minutes / len(completed), 1) if completed else 0.0
    best_window = bucket_counter.most_common(1)[0][0] if bucket_counter else "Not enough data yet"

    return {
        "total_tasks": len(tasks),
        "completed_tasks": len(completed),
        "pending_tasks": len(pending),
        "overdue_tasks": len([task for task in pending if task["is_overdue"]]),
        "completion_rate": completion_rate,
        "average_minutes": avg_minutes,
        "best_window": best_window,
        "tasks_per_day": dict(sorted(daily_counter.items())),
        "status_breakdown": {
            "Completed": len(completed),
            "Pending": len(pending),
        },
    }


def seed_sample_data() -> None:
    if list_tasks():
        return

    sample_tasks = [
        TaskCreate("Finish Flask dashboard", "Build charts page for the app", "High", "2026-04-30"),
        TaskCreate("Prepare interview notes", "Summarize key backend topics", "Medium", "2026-05-02"),
        TaskCreate("Morning workout", "30 minutes of movement", "Low", None),
    ]

    created_ids: list[int] = []
    for task in sample_tasks:
        created_ids.append(create_task(task))

    complete_task(created_ids[2], 35)
    complete_task(created_ids[1], 90)
