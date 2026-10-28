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
    # جدول تنظیمات گروه
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id BIGINT PRIMARY KEY,
            lock_link BOOLEAN DEFAULT FALSE,
            welcome_enabled BOOLEAN DEFAULT TRUE,
            lock_gif BOOLEAN DEFAULT FALSE,
            lock_sticker BOOLEAN DEFAULT FALSE,
            lock_photo BOOLEAN DEFAULT FALSE,
            lock_video BOOLEAN DEFAULT FALSE,
            lock_video_note BOOLEAN DEFAULT FALSE,
            lock_media BOOLEAN DEFAULT FALSE
        )
    """)
    # اضافه کردن ستون‌ها اگه از قبل جدول وجود داشت
    for col in ['lock_gif', 'lock_sticker', 'lock_photo', 'lock_video', 'lock_video_note', 'lock_media']:
        try:
            cur.execute(f"ALTER TABLE group_settings ADD COLUMN {col} BOOLEAN DEFAULT FALSE")
            conn.commit()
        except Exception:
            conn.rollback()
            
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized.")
