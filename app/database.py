import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "planner.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

@contextmanager
def connection():
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn 
        conn.commit()
    except Exception:
        conn.rollback()
        raise         
    finally:
        conn.close()

def init_db():
    with connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deadline TEXT NOT NULL,
                estimated_minutes INTEGER NOT NULL CHECK(estimated_minutes > 0),
                priority TEXT NOT NULL CHECK(priority IN ('low','medium','high')),
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS day_settings(
                target_date TEXT PRIMARY KEY,
                available_start TEXT NOT NULL,
                available_end TEXT NOT NULL,
                daily_limit_minutes INTEGER NOT NULL CHECK(daily_limit_minutes > 0 AND daily_limit_minutes <= 720),
                break_minutes INTEGER NOT NULL CHECK(break_minutes >= 0 AND break_minutes <= 60)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fixed_events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_date TEXT NOT NULL,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL CHECK(start_time < end_time)
            )
        """)

