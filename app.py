import streamlit as st
from db import (
    init_db,
    create_case,
    insert_document,
    insert_page,
    get_cases,
    toggle_case_status,
    get_pages_by_category,
    update_page_category,
)
from storage import save_master_pdf, split_pdf_into_pages

st.set_page_config(page_title="Litigation Record Engine", layout="wide")
init_db()

st.title("Litigation Record Engine v2.1")

# Sidebar Navigation
st.sidebar.header("Cases")

active_cases = get_cases("active")
archived_cases = get_cases("archived")

selected_case = None

st.sidebar.subheader("Active Cases")
for case in active_cases:
    if st.sidebar.button(case[1], key=f"active_{case[0]}"):
        selected_case = case[0]

st.sidebar.subheader("Past Cases")
for case in archived_cases:
    if st.sidebar.button(case[1], key=f"archived_{case[0]}"):
        selected_case = case[0]

st.sidebar.divider()

# New Case Section
st.sidebar.subheader("Create New Case")
new_case_name = st.sidebar.text_input("Case Name")
mode = st.sidebar.selectbox("Mode", ["Hybrid", "Preserve", "Split"])
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if st.sidebar.button("Create Case"):
    if new_case_name and uploaded_file:
        case_id = create_case(new_case_name, mode)
        master_path = save_master_pdf(case_id, uploaded_file)
        page_data = split_pdf_into_pages(case_id, master_path)
        doc_id = insert_document(case_id, uploaded_file.name)
        for page in page_data:
            insert_page(case_id, doc_id, page["page_number"], page["file_path"], page["hash"])
        st.sidebar.success("Case created.")
    else:
        st.sidebar.warning("Provide name + file.")

# Main Workspace
if selected_case:

    st.header(f"Case ID: {selected_case}")

    if st.button("Toggle Active / Past"):
        toggle_case_status(selected_case)
        st.experimental_rerun()

    tab1, tab2, tab3 = st.tabs(["Facility Chart", "Administration", "Duplicates"])

    with tab1:
        pages = get_pages_by_category(selected_case, "facility")
        st.subheader("Facility Pages")
        for page in pages:
            col1, col2 = st.columns([3, 1])
            col1.write(f"Page {page[1]}")
            if col2.button("Move to Admin", key=f"f_{page[0]}"):
                update_page_category(page[0], "admin")
                st.experimental_rerun()

    with tab2:
        pages = get_pages_by_category(selected_case, "admin")
        st.subheader("Administrative Pages")
        for page in pages:
            col1, col2 = st.columns([3, 1])
            col1.write(f"Page {page[1]}")
            if col2.button("Move to Facility", key=f"a_{page[0]}"):
                update_page_category(page[0], "facility")
                st.experimental_rerun()

    with tab3:
        pages = get_pages_by_category(selected_case, "duplicate")
        st.subheader("Duplicate Pages")
        for page in pages:
            st.write(f"Page {page[1]}")
