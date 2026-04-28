from smart_todo.cli import run_cli
from smart_todo.database import init_db
from smart_todo.services import seed_sample_data


if __name__ == "__main__":
    init_db()
    seed_sample_data()
    run_cli()
