from pathlib import Path
import duckdb


def connect(db_path: Path, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path), read_only=read_only)
