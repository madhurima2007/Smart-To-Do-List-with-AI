from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from .services import analytics_summary


CHARTS_DIR = Path(__file__).resolve().parent.parent / "static" / "charts"


def generate_charts() -> dict[str, str]:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    summary = analytics_summary()

    daily_path = CHARTS_DIR / "tasks_per_day.png"
    status_path = CHARTS_DIR / "status_breakdown.png"

    days = list(summary["tasks_per_day"].keys())
    counts = list(summary["tasks_per_day"].values())

    plt.figure(figsize=(8, 4.5))
    plt.plot(days, counts, marker="o", color="#1f6feb", linewidth=2)
    plt.title("Tasks Completed Per Day")
    plt.xlabel("Date")
    plt.ylabel("Completed Tasks")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(daily_path)
    plt.close()

    labels = list(summary["status_breakdown"].keys())
    values = list(summary["status_breakdown"].values())
    if sum(values) == 0:
        labels = ["No Tasks"]
        values = [1]
    plt.figure(figsize=(5, 5))
    colors = ["#2da44e", "#d29922"] if len(values) > 1 else ["#9a6700"]
    plt.pie(values, labels=labels, autopct="%1.0f%%", startangle=90, colors=colors)
    plt.title("Completed vs Pending")
    plt.tight_layout()
    plt.savefig(status_path)
    plt.close()

    return {
        "daily_chart": daily_path.name,
        "status_chart": status_path.name,
    }
