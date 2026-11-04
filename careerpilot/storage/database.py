"""Database connection and initialization module for SQLite."""
import sqlite3
from pathlib import Path
from careerpilot.core.config import settings

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db_path(custom_url: str | None = None) -> str:
    url = custom_url or settings.database_url
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return url


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Create a configured SQLite connection with foreign keys enabled."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str | None = None) -> None:
    """Initialize database tables and indexes from schema.sql."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(schema_sql)
    finally:
        conn.close()
