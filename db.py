import sqlite3

DB_NAME = "cases.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            mode TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            filename TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            document_id INTEGER,
            page_number INTEGER,
            category TEXT,
            file_path TEXT,
            hash TEXT,
            manual_override INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
def create_case(name, mode, created_by="system"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO cases (name, status, mode, created_by) VALUES (?, ?, ?, ?)",
        (name, "active", mode, created_by),
    )

    case_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return case_id


def insert_document(case_id, filename):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO documents (case_id, filename) VALUES (?, ?)",
        (case_id, filename),
    )

    document_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return document_id


def insert_page(case_id, document_id, page_number, file_path, page_hash):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pages 
        (case_id, document_id, page_number, category, file_path, hash)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (case_id, document_id, page_number, "facility", file_path, page_hash),
    )

    conn.commit()
    conn.close()
