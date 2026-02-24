import os
import hashlib
from PyPDF2 import PdfReader, PdfWriter

BASE_DIR = "cases"

def ensure_base_dir():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

def create_case_folder(case_id):
    ensure_base_dir()
    case_path = os.path.join(BASE_DIR, f"case_{case_id}")
    master_path = os.path.join(case_path, "master")
    pages_path = os.path.join(case_path, "pages")
    exports_path = os.path.join(case_path, "exports")

    os.makedirs(master_path, exist_ok=True)
    os.makedirs(pages_path, exist_ok=True)
    os.makedirs(exports_path, exist_ok=True)

    return case_path

def save_master_pdf(case_id, uploaded_file):
    case_path = create_case_folder(case_id)
    master_path = os.path.join(case_path, "master", uploaded_file.name)

    with open(master_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return master_path

def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def split_pdf_into_pages(case_id, pdf_path):
    case_path = create_case_folder(case_id)
    pages_dir = os.path.join(case_path, "pages")

    reader = PdfReader(pdf_path)
    page_data = []

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        page_filename = f"page_{i+1}.pdf"
        page_path = os.path.join(pages_dir, page_filename)

        with open(page_path, "wb") as f:
            writer.write(f)

        page_hash = calculate_hash(page_path)

        page_data.append({
            "page_number": i + 1,
            "file_path": page_path,
            "hash": page_hash
        })

    return page_data
