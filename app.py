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

if "view" not in st.session_state:
    st.session_state.view = "dashboard"

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None


# ---------------- DASHBOARD ---------------- #
if st.session_state.view == "dashboard":

    st.title("Litigation Record Engine")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Active Cases")
        active_cases = get_cases("active")
        for case in active_cases:
            if st.button(f"Open: {case[1]}", key=f"open_{case[0]}"):
                st.session_state.selected_case = case[0]
                st.session_state.view = "workspace"
                st.rerun()

    with col2:
        st.subheader("Past Cases")
        archived_cases = get_cases("archived")
        for case in archived_cases:
            if st.button(f"Open: {case[1]}", key=f"arch_{case[0]}"):
                st.session_state.selected_case = case[0]
                st.session_state.view = "workspace"
                st.rerun()

    st.divider()
    st.subheader("Create New Case")

    new_case_name = st.text_input("Case Name")
    mode = st.selectbox("Mode", ["Hybrid", "Preserve", "Split"])
    uploaded_file = st.file_uploader("Upload Initial Master PDF", type=["pdf"])

    if st.button("Create Case"):
        if new_case_name:
            case_id = create_case(new_case_name, mode)
            if uploaded_file:
                master_path = save_master_pdf(case_id, uploaded_file)
                page_data = split_pdf_into_pages(case_id, master_path)
                doc_id = insert_document(case_id, uploaded_file.name)
                for page in page_data:
                    insert_page(case_id, doc_id, page["page_number"], page["file_path"], page["hash"])
            st.success("Case created.")
            st.rerun()
        else:
            st.warning("Enter case name.")


# ---------------- WORKSPACE ---------------- #
elif st.session_state.view == "workspace":

    case_id = st.session_state.selected_case

    st.title(f"Case Workspace – ID {case_id}")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Back to Dashboard"):
            st.session_state.view = "dashboard"
            st.session_state.selected_case = None
            st.rerun()

    with col2:
        if st.button("Toggle Active / Past"):
            toggle_case_status(case_id)
            st.success("Status updated.")

    tabs = st.tabs([
        "Upload Records",
        "Template",
        "Facility Chart",
        "Administration",
        "Duplicates",
        "Export"
    ])

    # -------- Upload Tab -------- #
    with tabs[0]:
        st.subheader("Upload Additional Records")
        additional_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

        if st.button("Process Upload"):
            if additional_files:
                for file in additional_files:
                    master_path = save_master_pdf(case_id, file)
                    page_data = split_pdf_into_pages(case_id, master_path)
                    doc_id = insert_document(case_id, file.name)
                    for page in page_data:
                        insert_page(case_id, doc_id, page["page_number"], page["file_path"], page["hash"])
                st.success("Files processed.")
                st.rerun()

    # -------- Template Tab -------- #
    with tabs[1]:
        st.subheader("Template / Chronology Structure")
        template_file = st.file_uploader("Upload Generic Template or Past Chronology", type=["pdf"])
        if template_file:
            st.success("Template uploaded (structure logic to be applied next phase).")

    # -------- Facility Tab -------- #
    with tabs[2]:
        st.subheader("Facility Records")
        pages = get_pages_by_category(case_id, "facility")
        for page in pages:
            colA, colB = st.columns([4, 1])
            colA.write(f"Page {page[1]}")
            if colB.button("Move to Admin", key=f"fac_{page[0]}"):
                update_page_category(page[0], "admin")
                st.rerun()

    # -------- Admin Tab -------- #
    with tabs[3]:
        st.subheader("Administrative Records")
        pages = get_pages_by_category(case_id, "admin")
        for page in pages:
            colA, colB = st.columns([4, 1])
            colA.write(f"Page {page[1]}")
            if colB.button("Move to Facility", key=f"adm_{page[0]}"):
                update_page_category(page[0], "facility")
                st.rerun()

    # -------- Duplicate Tab -------- #
    with tabs[4]:
        st.subheader("Duplicate Pages")
        pages = get_pages_by_category(case_id, "duplicate")
        for page in pages:
            st.write(f"Page {page[1]}")

    # -------- Export Tab -------- #
    with tabs[5]:
        st.subheader("Export")
        st.info("Export engine will be connected in next phase.")
