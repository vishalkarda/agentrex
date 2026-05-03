import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


def create_checkpointer(db_path: str = "data/checkpoints.db") -> SqliteSaver:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_file), check_same_thread=False)
    return SqliteSaver(connection)
