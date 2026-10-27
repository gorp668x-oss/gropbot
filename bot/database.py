import psycopg
from psycopg.rows import dict_row
from bot.config import DATABASE_URL

def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set! Check Railway Variables.")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized.")
