from __future__ import annotations

import base64
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from .services import analytics_summary


def _figure_to_base64() -> str:
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def generate_charts() -> dict[str, str]:
    summary = analytics_summary()

    days = list(summary["tasks_per_day"].keys())
    counts = list(summary["tasks_per_day"].values())
    if not days:
        days = ["No data"]
        counts = [0]

    plt.figure(figsize=(8, 4.5))
    plt.plot(days, counts, marker="o", color="#1f6feb", linewidth=2)
    plt.title("Tasks Completed Per Day")
    plt.xlabel("Date")
    plt.ylabel("Completed Tasks")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    daily_chart = _figure_to_base64()

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
    status_chart = _figure_to_base64()

    return {
        "daily_chart": daily_chart,
        "status_chart": status_chart,
    }
