from __future__ import annotations

from .database import init_db
from .services import TaskCreate, complete_task, create_task, delete_task, get_smart_suggestion, list_tasks


def _show_tasks() -> None:
    tasks = list_tasks()
    if not tasks:
        print("No tasks yet.")
        return

    print("\nYour tasks:")
    for task in tasks:
        overdue = " | OVERDUE" if task["is_overdue"] else ""
        deadline = task["deadline"] or "No deadline"
        print(
            f'#{task["id"]} | {task["title"]} | {task["priority"]} | {deadline} | {task["status"]}{overdue}'
        )


def _add_task() -> None:
    title = input("Task title: ").strip()
    description = input("Description: ").strip()
    priority = input("Priority (Low/Medium/High): ").strip().title() or "Medium"
    deadline = input("Deadline (YYYY-MM-DD or blank): ").strip() or None
    create_task(TaskCreate(title=title, description=description, priority=priority, deadline=deadline))
    print("Task added.")


def _complete_task() -> None:
    task_id = int(input("Task id to complete: ").strip())
    minutes_spent = int(input("Minutes spent: ").strip() or "0")
    complete_task(task_id, minutes_spent)
    print("Task marked complete.")


def _delete_task() -> None:
    task_id = int(input("Task id to delete: ").strip())
    delete_task(task_id)
    print("Task deleted.")


def run_cli() -> None:
    init_db()
    while True:
        print("\nSmart To-Do CLI")
        print("1. View tasks")
        print("2. Add task")
        print("3. Complete task")
        print("4. Delete task")
        print("5. Smart suggestion")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            _show_tasks()
        elif choice == "2":
            _add_task()
        elif choice == "3":
            _complete_task()
        elif choice == "4":
            _delete_task()
        elif choice == "5":
            print(get_smart_suggestion())
        elif choice == "6":
            break
        else:
            print("Invalid choice. Try again.")
