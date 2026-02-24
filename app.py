import streamlit as st
from db import init_db, create_case, insert_document, insert_page
from storage import save_master_pdf, split_pdf_into_pages

st.set_page_config(page_title="Litigation Record Engine", layout="wide")

init_db()

st.title("Litigation Record Engine v2.0")

st.header("Create New Case")

case_name = st.text_input("Case Name")
mode = st.selectbox("Record Handling Mode", ["Hybrid", "Preserve", "Split"])

uploaded_file = st.file_uploader("Upload Master PDF", type=["pdf"])

if st.button("Create Case and Process"):

    if not case_name:
        st.warning("Enter case name.")
    elif not uploaded_file:
        st.warning("Upload a PDF.")
    else:
        st.info("Creating case...")

        case_id = create_case(case_name, mode)

        st.info("Saving master PDF...")
        master_path = save_master_pdf(case_id, uploaded_file)

        st.info("Splitting pages...")
        page_data = split_pdf_into_pages(case_id, master_path)

        document_id = insert_document(case_id, uploaded_file.name)

        for page in page_data:
            insert_page(
                case_id,
                document_id,
                page["page_number"],
                page["file_path"],
                page["hash"],
            )

        st.success(f"Case {case_name} created successfully.")
        st.success(f"{len(page_data)} pages processed and stored.")
