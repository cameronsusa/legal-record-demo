import sqlite3

DB_NAME = "cases.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT
        )
    """)

    # Cases table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT DEFAULT 'active',
            mode TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            filename TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Pages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            document_id INTEGER,
            page_number INTEGER,
            category TEXT DEFAULT 'facility',
            file_path TEXT,
            hash TEXT,
            manual_override INTEGER DEFAULT 0
        )
    """)

    # Add display_order if missing
    if not column_exists(cursor, "pages", "display_order"):
        cursor.execute("ALTER TABLE pages ADD COLUMN display_order INTEGER DEFAULT 0")

    # Firm settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS firm_settings (
            id INTEGER PRIMARY KEY,
            group_lock_default INTEGER DEFAULT 1,
            duplicate_detection_enabled INTEGER DEFAULT 1
        )
    """)

    # Insert default firm settings if empty
    cursor.execute("SELECT COUNT(*) FROM firm_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO firm_settings (group_lock_default, duplicate_detection_enabled)
            VALUES (1, 1)
        """)

    # Case settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_settings (
            case_id INTEGER PRIMARY KEY,
            group_lock_override INTEGER,
            inherit_firm_settings INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
