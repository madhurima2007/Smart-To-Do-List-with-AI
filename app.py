from __future__ import annotations

from flask import Flask, redirect, render_template, request, url_for

from smart_todo.charts import generate_charts
from smart_todo.database import init_db
from smart_todo.services import (
    TaskCreate,
    analytics_summary,
    complete_task,
    create_task,
    delete_task,
    get_smart_suggestion,
    list_tasks,
    seed_sample_data,
)


app = Flask(__name__)


@app.route("/")
def home():
    return render_template(
        "index.html",
        tasks=list_tasks(),
        suggestion=get_smart_suggestion(),
    )


@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        create_task(
            TaskCreate(
                title=request.form["title"].strip(),
                description=request.form.get("description", "").strip(),
                priority=request.form["priority"],
                deadline=request.form.get("deadline") or None,
            )
        )
        return redirect(url_for("home"))
    return render_template("add_task.html")


@app.post("/complete/<int:task_id>")
def mark_complete(task_id: int):
    minutes_spent = int(request.form.get("minutes_spent", 0) or 0)
    complete_task(task_id, minutes_spent)
    return redirect(url_for("home"))


@app.post("/delete/<int:task_id>")
def remove_task(task_id: int):
    delete_task(task_id)
    return redirect(url_for("home"))


@app.route("/analytics")
def analytics():
    chart_files = generate_charts()
    return render_template(
        "analytics.html",
        summary=analytics_summary(),
        charts=chart_files,
    )


def create_app() -> Flask:
    init_db()
    seed_sample_data()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
