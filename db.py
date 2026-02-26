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

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT
        )
    """)

    # CASES
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

    # DOCUMENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            filename TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # PAGES
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

    # Add display_order safely
    if not column_exists(cursor, "pages", "display_order"):
        cursor.execute("ALTER TABLE pages ADD COLUMN display_order INTEGER DEFAULT 0")

    # FIRM SETTINGS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS firm_settings (
            id INTEGER PRIMARY KEY,
            group_lock_default INTEGER DEFAULT 1,
            duplicate_detection_enabled INTEGER DEFAULT 1
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM firm_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO firm_settings (group_lock_default, duplicate_detection_enabled)
            VALUES (1, 1)
        """)

    # CASE SETTINGS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_settings (
            case_id INTEGER PRIMARY KEY,
            group_lock_override INTEGER,
            inherit_firm_settings INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


# ------------------ CASE FUNCTIONS ------------------ #

def create_case(name, mode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cases (name, mode, status) VALUES (?, ?, 'active')",
        (name, mode),
    )
    case_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return case_id


def get_cases(status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM cases WHERE status=?", (status,))
    cases = cursor.fetchall()
    conn.close()
    return cases


def toggle_case_status(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM cases WHERE id=?", (case_id,))
    current = cursor.fetchone()[0]
    new_status = "archived" if current == "active" else "active"
    cursor.execute("UPDATE cases SET status=? WHERE id=?", (new_status, case_id))
    conn.commit()
    conn.close()


# ------------------ DOCUMENT FUNCTIONS ------------------ #

def insert_document(case_id, filename):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (case_id, filename) VALUES (?, ?)",
        (case_id, filename),
    )
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def insert_page(case_id, document_id, page_number, file_path, hash_value):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO pages (case_id, document_id, page_number, file_path, hash, display_order) VALUES (?, ?, ?, ?, ?, ?)",
        (case_id, document_id, page_number, file_path, hash_value, page_number),
    )

    conn.commit()
    conn.close()


def get_pages_by_category(case_id, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, page_number, document_id FROM pages WHERE case_id=? AND category=? ORDER BY display_order ASC",
        (case_id, category),
    )
    pages = cursor.fetchall()
    conn.close()
    return pages


def update_page_category(page_id, new_category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pages SET category=?, manual_override=1 WHERE id=?",
        (new_category, page_id),
    )
    conn.commit()
    conn.close()


def get_pages_by_document(case_id, document_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM pages WHERE case_id=? AND document_id=?",
        (case_id, document_id),
    )
    pages = cursor.fetchall()
    conn.close()
    return [p[0] for p in pages]
