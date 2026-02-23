import streamlit as st
import os
import hashlib
import shutil
import json
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter

APP_VERSION = "2.0 Phase 1"

BASE_DIR = "cases"
ACTIVE_DIR = os.path.join(BASE_DIR, "Active")
PAST_DIR = os.path.join(BASE_DIR, "Past")

os.makedirs(ACTIVE_DIR, exist_ok=True)
os.makedirs(PAST_DIR, exist_ok=True)

# --------------------------------------------------------
# Utility Functions
# --------------------------------------------------------

def hash_page(page):
    return hashlib.sha256(page.extract_text().encode("utf-8")).hexdigest()

def save_metadata(case_path, metadata):
    with open(os.path.join(case_path, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

def load_metadata(case_path):
    path = os.path.join(case_path, "metadata.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def create_case_structure(case_name):
    case_path = os.path.join(ACTIVE_DIR, case_name)
    os.makedirs(case_path, exist_ok=True)
    for folder in ["raw_uploads", "facility", "administration", "duplicates"]:
        os.makedirs(os.path.join(case_path, folder), exist_ok=True)
    save_metadata(case_path, {"created": str(datetime.now())})
    return case_path

def move_case(case_name, to_past=True):
    src = os.path.join(ACTIVE_DIR, case_name) if to_past else os.path.join(PAST_DIR, case_name)
    dest = os.path.join(PAST_DIR, case_name) if to_past else os.path.join(ACTIVE_DIR, case_name)
    shutil.move(src, dest)

def export_folder(folder_path, output_name):
    writer = PdfWriter()
    for file in sorted(os.listdir(folder_path)):
        reader = PdfReader(os.path.join(folder_path, file))
        for page in reader.pages:
            writer.add_page(page)
    output_path = os.path.join(folder_path, output_name)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

# --------------------------------------------------------
# Duplicate & Admin Detection Logic
# --------------------------------------------------------

ADMIN_KEYWORDS = ["agreement", "waiver", "insurance", "signature", "policy"]

def process_records(case_path):
    raw_path = os.path.join(case_path, "raw_uploads")
    facility_path = os.path.join(case_path, "facility")
    admin_path = os.path.join(case_path, "administration")
    dup_path = os.path.join(case_path, "duplicates")

    seen_hashes = set()

    for file in os.listdir(raw_path):
        if not file.endswith(".pdf"):
            continue

        reader = PdfReader(os.path.join(raw_path, file))
        writer = PdfWriter()
        doc_text = ""

        for page in reader.pages:
            text = page.extract_text() or ""
            doc_text += text
            page_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

            if page_hash in seen_hashes:
                writer_dup = PdfWriter()
                writer_dup.add_page(page)
                dup_file = os.path.join(dup_path, f"dup_{file}")
                with open(dup_file, "wb") as f:
                    writer_dup.write(f)
                continue
            else:
                seen_hashes.add(page_hash)
                writer.add_page(page)

        target_path = facility_path
        for keyword in ADMIN_KEYWORDS:
            if keyword.lower() in doc_text.lower():
                target_path = admin_path
                break

        if len(writer.pages) > 0:
            output_file = os.path.join(target_path, file)
            with open(output_file, "wb") as f:
                writer.write(f)

# --------------------------------------------------------
# UI
# --------------------------------------------------------

st.set_page_config(page_title="Legal Record Engine", layout="wide")
st.title(f"Legal Record Engine – Version {APP_VERSION}")

tab1, tab2, tab3, tab4 = st.tabs(["Cases", "Upload Records", "Process & Review", "Exports"])

# --------------------------------------------------------
# TAB 1 – CASE MANAGEMENT
# --------------------------------------------------------

with tab1:
    st.header("Active Cases")
    active_cases = os.listdir(ACTIVE_DIR)

    new_case = st.text_input("Create New Case")
    if st.button("Create Case"):
        if new_case:
            create_case_structure(new_case)
            st.success("Case Created")

    for case in active_cases:
        col1, col2 = st.columns([4,1])
        col1.write(case)
        if col2.button("Move to Past", key=f"move_{case}"):
            move_case(case, to_past=True)
            st.success(f"{case} moved to Past")

    st.divider()
    st.header("Past Cases")
    past_cases = os.listdir(PAST_DIR)

    for case in past_cases:
        col1, col2 = st.columns([4,1])
        col1.write(case)
        if col2.button("Restore", key=f"restore_{case}"):
            move_case(case, to_past=False)
            st.success(f"{case} restored")

# --------------------------------------------------------
# TAB 2 – UPLOAD
# --------------------------------------------------------

with tab2:
    st.header("Upload Records")

    case_select = st.selectbox("Select Active Case", os.listdir(ACTIVE_DIR))
    if case_select:
        uploaded_files = st.file_uploader("Upload PDF Records", type="pdf", accept_multiple_files=True)

        if uploaded_files:
            raw_path = os.path.join(ACTIVE_DIR, case_select, "raw_uploads")
            for file in uploaded_files:
                with open(os.path.join(raw_path, file.name), "wb") as f:
                    f.write(file.getbuffer())
            st.success("Files uploaded to raw storage")

# --------------------------------------------------------
# TAB 3 – PROCESS
# --------------------------------------------------------

with tab3:
    st.header("Process & Review")

    case_select = st.selectbox("Select Case to Process", os.listdir(ACTIVE_DIR), key="process_select")

    if st.button("Process Records"):
        case_path = os.path.join(ACTIVE_DIR, case_select)
        process_records(case_path)
        st.success("Processing Complete")

    if case_select:
        case_path = os.path.join(ACTIVE_DIR, case_select)

        st.subheader("Facility Files")
        st.write(os.listdir(os.path.join(case_path, "facility")))

        st.subheader("Administrative Files")
        st.write(os.listdir(os.path.join(case_path, "administration")))

        st.subheader("Duplicate Files")
        st.write(os.listdir(os.path.join(case_path, "duplicates")))

# --------------------------------------------------------
# TAB 4 – EXPORT
# --------------------------------------------------------

with tab4:
    st.header("Export Files")

    case_select = st.selectbox("Select Case", os.listdir(ACTIVE_DIR), key="export_select")

    if case_select:
        case_path = os.path.join(ACTIVE_DIR, case_select)

        if st.button("Export Facility Chart"):
            path = export_folder(os.path.join(case_path, "facility"), "facility_export.pdf")
            st.success(f"Exported: {path}")

        if st.button("Export Administration"):
            path = export_folder(os.path.join(case_path, "administration"), "admin_export.pdf")
            st.success(f"Exported: {path}")

        if st.button("Export Duplicates"):
            path = export_folder(os.path.join(case_path, "duplicates"), "duplicates_export.pdf")
            st.success(f"Exported: {path}")
