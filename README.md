# Smart To-Do List with AI + Analytics

An advanced Python productivity project built from your requirements. It includes:

- A CLI app for quick task management
- A Flask web app with a clean dashboard
- SQLite storage for tasks and productivity sessions
- Analytics charts using matplotlib
- Smart task suggestions based on priority and deadlines

## Features

- Add, delete, and complete tasks
- Track priority, deadlines, and overdue work
- Record time spent on completed tasks
- View completion rate and productivity trends
- Get a "do this first" suggestion

## Project Structure

```text
app.py
run_cli.py
requirements.txt
smart_todo/
templates/
static/
data/
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the CLI

```bash
python run_cli.py
```

## Run the Web App

```bash
python app.py
```

Then open `http://127.0.0.1:5000`

## Smart Logic

The app suggests what to work on first by checking:

1. Overdue tasks
2. Priority level
3. Nearest deadline

## Analytics

The analytics dashboard shows:

- Tasks completed per day
- Completion rate
- Average time spent per completed task
- Best time window based on completion patterns
