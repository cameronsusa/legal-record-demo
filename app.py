import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

from processing import detect_duplicate


# ================= PAGE CONFIG ================= #
st.set_page_config(
    page_title="Litigation Record Engine",
    layout="wide"
)

st.title("Litigation Record Engine")

init_db()


# ================= SESSION STATE ================= #
if "view" not in st.session_state:
    st.session_state.view = "dashboard"

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None


# ================= DASHBOARD ================= #
if st.session_state.view == "dashboard":

    st.header("Case Dashboard")

    col1, col2 = st.columns(2)

    # -------- ACTIVE CASES -------- #
    with col1:

        st.subheader("Active Cases")

        active_cases = get_cases("active")

        if not active_cases:
            st.info("No active cases.")

        for case in active_cases:

            if st.button(
                f"Open: {case[1]}",
                key=f"active_{case[0]}"
            ):

                st.session_state.selected_case = case[0]
                st.session_state.view = "workspace"

                st.rerun()

    # -------- ARCHIVED CASES -------- #
    with col2:

        st.subheader("Past Cases")

        archived_cases = get_cases("archived")

        if not archived_cases:
            st.info("No past cases.")

        for case in archived_cases:

            if st.button(
                f"Open: {case[1]}",
                key=f"archived_{case[0]}"
            ):

                st.session_state.selected_case = case[0]
                st.session_state.view = "workspace"

                st.rerun()

    st.divider()

    # -------- CREATE NEW CASE -------- #
    st.subheader("Create New Case")

    new_case_name = st.text_input("Case Name")

    mode = st.selectbox(
        "Mode",
        ["Hybrid", "Preserve", "Split"]
    )

    if st.button("Create Case"):

        if new_case_name:

            create_case(
                new_case_name,
                mode
            )

            st.success("Case created.")

            st.rerun()

        else:

            st.warning("Enter a case name.")


# ================= WORKSPACE ================= #
elif st.session_state.view == "workspace":

    case_id = st.session_state.selected_case

    st.header(f"Case Workspace – ID {case_id}")

    top1, top2 = st.columns(2)

    with top1:

        if st.button("Back to Dashboard"):

            st.session_state.view = "dashboard"
            st.session_state.selected_case = None

            st.rerun()

    with top2:

        if st.button("Toggle Active / Past"):

            toggle_case_status(case_id)

            st.success("Case status updated.")

            st.rerun()

    # ================= TABS ================= #
    tabs = st.tabs([
        "Upload Records",
        "Chronology Workspace",
        "Administrative",
        "Duplicates",
        "Templates",
        "Labs & Trends",
        "Export"
    ])

    # ================= UPLOAD TAB ================= #
    with tabs[0]:

        st.subheader("Upload Medical Records")

        uploaded_files = st.file_uploader(
            "Upload PDF Files",
            type=["pdf"],
            accept_multiple_files=True
        )

        st.info(
            "Files will automatically process, "
            "detect duplicates, and route pages."
        )

        if st.button("Process Uploads"):

            if uploaded_files:

                existing_hashes = set()

                total_pages = 0
                duplicate_pages = 0

                for file in uploaded_files:

                    master_path = save_master_pdf(
                        case_id,
                        file
                    )

                    page_data = split_pdf_into_pages(
                        case_id,
                        master_path
                    )

                    doc_id = insert_document(
                        case_id,
                        file.name
                    )

                    for page in page_data:

                        total_pages += 1

                        is_duplicate = detect_duplicate(
                            page["hash"],
                            existing_hashes
                        )

                        if is_duplicate:

                            category = "duplicate"
                            duplicate_pages += 1

                        else:

                            category = "chronology"

                            existing_hashes.add(
                                page["hash"]
                            )

                        insert_page(
                            case_id,
                            doc_id,
                            page["page_number"],
                            page["file_path"],
                            page["hash"],
                            category
                        )

                st.success(
                    f"{total_pages} pages processed | "
                    f"{duplicate_pages} duplicates detected."
                )

                st.rerun()

            else:

                st.warning(
                    "Please upload at least one PDF."
                )

    # ================= CHRONOLOGY TAB ================= #
    with tabs[1]:

        st.subheader("Chronology Workspace")

        pages = get_pages_by_category(
            case_id,
            "chronology"
        )

        if not pages:

            st.info("No chronology pages.")

        for page in pages:

            col1, col2 = st.columns([5, 2])

            with col1:

                st.write(
                    f"Page {page[1]} | "
                    f"Document {page[2]}"
                )

            with col2:

                action = st.selectbox(
                    "Action",
                    [
                        "Keep",
                        "Move to Duplicates",
                        "Move to Administrative"
                    ],
                    key=f"chrono_{page[0]}"
                )

                if action == "Move to Duplicates":

                    update_page_category(
                        page[0],
                        "duplicate"
                    )

                    st.rerun()

                elif action == "Move to Administrative":

                    update_page_category(
                        page[0],
                        "admin"
                    )

                    st.rerun()

    # ================= ADMIN TAB ================= #
    with tabs[2]:

        st.subheader("Administrative Records")

        pages = get_pages_by_category(
            case_id,
            "admin"
        )

        if not pages:

            st.info("No admin records.")

        for page in pages:

            col1, col2 = st.columns([5, 2])

            with col1:

                st.write(
                    f"Page {page[1]} | "
                    f"Document {page[2]}"
                )

            with col2:

                action = st.selectbox(
                    "Action",
                    [
                        "Keep",
                        "Move to Chronology",
                        "Move to Duplicates"
                    ],
                    key=f"admin_{page[0]}"
                )

                if action == "Move to Chronology":

                    update_page_category(
                        page[0],
                        "chronology"
                    )

                    st.rerun()

                elif action == "Move to Duplicates":

                    update_page_category(
                        page[0],
                        "duplicate"
                    )

                    st.rerun()

    # ================= DUPLICATES TAB ================= #
    with tabs[3]:

        st.subheader("Duplicate Pages")

        pages = get_pages_by_category(
            case_id,
            "duplicate"
        )

        if not pages:

            st.info("No duplicates detected.")

        for page in pages:

            col1, col2 = st.columns([5, 2])

            with col1:

                st.write(
                    f"Page {page[1]} | "
                    f"Document {page[2]}"
                )

            with col2:

                action = st.selectbox(
                    "Action",
                    [
                        "Keep Duplicate",
                        "Move to Chronology",
                        "Move to Administrative"
                    ],
                    key=f"dup_{page[0]}"
                )

                if action == "Move to Chronology":

                    update_page_category(
                        page[0],
                        "chronology"
                    )

                    st.rerun()

                elif action == "Move to Administrative":

                    update_page_category(
                        page[0],
                        "admin"
                    )

                    st.rerun()

    # ================= TEMPLATE TAB ================= #
    with tabs[4]:

        st.subheader("Templates")

        template_file = st.file_uploader(
            "Upload Template PDF",
            type=["pdf"]
        )

        if template_file:

            st.success(
                "Template uploaded."
            )

    # ================= LABS TAB ================= #
    with tabs[5]:

        st.subheader("Labs & Trends")

        if "lab_data" not in st.session_state:

            st.session_state.lab_data = pd.DataFrame(
                columns=["Date", "Value"]
            )

        date = st.date_input("Lab Date")

        value = st.number_input("Lab Value")

        if st.button("Add Lab Entry"):

            new_row = pd.DataFrame(
                [[date, value]],
                columns=["Date", "Value"]
            )

            st.session_state.lab_data = pd.concat(
                [
                    st.session_state.lab_data,
                    new_row
                ],
                ignore_index=True
            )

        if not st.session_state.lab_data.empty:

            st.dataframe(
                st.session_state.lab_data
            )

            fig, ax = plt.subplots()

            ax.plot(
                pd.to_datetime(
                    st.session_state.lab_data["Date"]
                ),
                st.session_state.lab_data["Value"]
            )

            ax.set_title("Lab Trend")

            ax.set_xlabel("Date")

            ax.set_ylabel("Value")

            st.pyplot(fig)

    # ================= EXPORT TAB ================= #
    with tabs[6]:

        st.subheader("Export Builder")

        st.warning(
            "Chronology PDF export "
            "coming next."
        )

        st.info(
            "Planned exports:\n"
            "- Chronology PDF\n"
            "- Duplicate appendix\n"
            "- Bates preservation\n"
            "- Case summaries"
        )
