import sqlite3


DB_NAME = "litigation_records.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


# ---------------- INITIALIZE DATABASE ---------------- #
def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    # -------- Cases Table -------- #
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT DEFAULT 'active',
            mode TEXT
        )
        """
    )

    # -------- Documents Table -------- #
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            filename TEXT
        )
        """
    )

    # -------- Pages Table -------- #
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            document_id INTEGER,
            page_number INTEGER,
            file_path TEXT,
            hash TEXT,
            display_order INTEGER,
            category TEXT DEFAULT 'facility'
        )
        """
    )

    conn.commit()

    conn.close()


# ---------------- CREATE CASE ---------------- #
def create_case(name, mode):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO cases (name, mode)
        VALUES (?, ?)
        """,
        (name, mode),
    )

    conn.commit()

    conn.close()


# ---------------- GET CASES ---------------- #
def get_cases(status):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM cases
        WHERE status = ?
        """,
        (status,),
    )

    cases = cursor.fetchall()

    conn.close()

    return cases


# ---------------- TOGGLE CASE STATUS ---------------- #
def toggle_case_status(case_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status
        FROM cases
        WHERE id = ?
        """,
        (case_id,),
    )

    current_status = cursor.fetchone()[0]

    new_status = (
        "archived"
        if current_status == "active"
        else "active"
    )

    cursor.execute(
        """
        UPDATE cases
        SET status = ?
        WHERE id = ?
        """,
        (new_status, case_id),
    )

    conn.commit()

    conn.close()


# ---------------- INSERT DOCUMENT ---------------- #
def insert_document(case_id, filename):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            case_id,
            filename
        )
        VALUES (?, ?)
        """,
        (case_id, filename),
    )

    doc_id = cursor.lastrowid

    conn.commit()

    conn.close()

    return doc_id


# ---------------- INSERT PAGE ---------------- #
def insert_page(
    case_id,
    document_id,
    page_number,
    file_path,
    hash_value,
    category="facility"
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pages (
            case_id,
            document_id,
            page_number,
            file_path,
            hash,
            display_order,
            category
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_id,
            document_id,
            page_number,
            file_path,
            hash_value,
            page_number,
            category,
        ),
    )

    conn.commit()

    conn.close()


# ---------------- GET PAGES BY CATEGORY ---------------- #
def get_pages_by_category(case_id, category):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            page_number,
            document_id,
            file_path,
            category
        FROM pages
        WHERE case_id = ?
        AND category = ?
        ORDER BY display_order
        """,
        (case_id, category),
    )

    pages = cursor.fetchall()

    conn.close()

    return pages


# ---------------- UPDATE PAGE CATEGORY ---------------- #
def update_page_category(page_id, new_category):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE pages
        SET category = ?
        WHERE id = ?
        """,
        (new_category, page_id),
    )

    conn.commit()

    conn.close()
