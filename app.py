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

    mode = st.selectbox(
        "Mode",
        ["Hybrid", "Preserve", "Split"]
    )

    if st.button("Create Case"):

        if new_case_name:

            create_case(new_case_name, mode)

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
        "Facility Chart",
        "Administration",
        "Duplicates",
        "Template / Chronology",
        "Labs & Trends",
        "Export"
    ])

    # ---------------- Upload Tab ---------------- #
    with tabs[0]:

        st.subheader("Upload Records")

        additional_files = st.file_uploader(
            "Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True
        )

        st.info(
            "Uploaded records will automatically process, "
            "split into pages, detect duplicates, "
            "and route pages into the correct tabs."
        )

        if st.button("Process Upload"):

            if additional_files:

                existing_hashes = set()

                total_pages = 0
                duplicate_count = 0

                for file in additional_files:

                    master_path = save_master_pdf(case_id, file)

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
                            duplicate_count += 1

                        else:

                            category = "facility"

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
                    f"Processing Complete | "
                    f"{total_pages} pages processed | "
                    f"{duplicate_count} duplicates detected."
                )

                st.rerun()

            else:

                st.warning("Upload at least one PDF.")

    # ---------------- Facility Tab ---------------- #
    with tabs[1]:

        st.subheader("Facility Records")

        st.caption(
            "Primary clinical and treatment records."
        )

        pages = get_pages_by_category(
            case_id,
            "facility"
        )

        if not pages:

            st.info("No facility records detected.")

        for page in pages:

            colA, colB = st.columns([4, 1])

            colA.write(
                f"Page {page[1]} (Doc {page[2]})"
            )

            action = colB.selectbox(
                "Action",
                [
                    "Keep",
                    "Move to Admin",
                    "Move to Duplicates"
                ],
                key=f"facility_action_{page[0]}"
            )

            if action == "Move to Admin":

                update_page_category(
                    page[0],
                    "admin"
                )

                st.rerun()

            elif action == "Move to Duplicates":

                update_page_category(
                    page[0],
                    "duplicate"
                )

                st.rerun()

    # ---------------- Admin Tab ---------------- #
    with tabs[2]:

        st.subheader("Administrative Records")

        st.caption(
            "Billing, authorization, and non-clinical records."
        )

        pages = get_pages_by_category(
            case_id,
            "admin"
        )

        if not pages:

            st.info("No administrative records.")

        for page in pages:

            colA, colB = st.columns([4, 1])

            colA.write(
                f"Page {page[1]} (Doc {page[2]})"
            )

            action = colB.selectbox(
                "Action",
                [
                    "Keep",
                    "Move to Facility",
                    "Move to Duplicates"
                ],
                key=f"admin_action_{page[0]}"
            )

            if action == "Move to Facility":

                update_page_category(
                    page[0],
                    "facility"
                )

                st.rerun()

            elif action == "Move to Duplicates":

                update_page_category(
                    page[0],
                    "duplicate"
                )

                st.rerun()

    # ---------------- Duplicate Tab ---------------- #
    with tabs[3]:

        st.subheader("Duplicate Pages")

        st.caption(
            "Duplicates are automatically detected during processing."
        )

        pages = get_pages_by_category(
            case_id,
            "duplicate"
        )

        if not pages:

            st.info("No duplicates detected.")

        for page in pages:

            colA, colB = st.columns([4, 1])

            colA.write(
                f"Page {page[1]} (Doc {page[2]})"
            )

            action = colB.selectbox(
                "Action",
                [
                    "Keep in Duplicates",
                    "Move to Facility",
                    "Move to Admin"
                ],
                key=f"dup_action_{page[0]}"
            )

            if action == "Move to Facility":

                update_page_category(
                    page[0],
                    "facility"
                )

                st.rerun()

            elif action == "Move to Admin":

                update_page_category(
                    page[0],
                    "admin"
                )

                st.rerun()

    # ---------------- Template Tab ---------------- #
    with tabs[4]:

        st.subheader(
            "Upload Firm Template or Past Chronology"
        )

        template_file = st.file_uploader(
            "Upload Template PDF",
            type=["pdf"]
        )

        if template_file:

            st.success(
                "Template uploaded successfully."
            )

            st.info(
                "Chronology automation and "
                "template-driven sorting "
                "will integrate next."
            )

    # ---------------- Labs & Trends ---------------- #
    with tabs[5]:

        st.subheader(
            "Manual Lab Entry & Trend Graph"
        )

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

            st.write("Lab Entries:")

            st.dataframe(
                st.session_state.lab_data
            )

            fig, ax = plt.subplots()

            ax.plot(
                pd.to_datetime(
                    st.session_state.lab_data["Date"]
                ),
                st.session_state.lab_data["Value"],
            )

            ax.set_xlabel("Date")
            ax.set_ylabel("Value")
            ax.set_title("Lab Trend")

            st.pyplot(fig)

    # ---------------- Export ---------------- #
    with tabs[6]:

        st.subheader("Export")

        st.info(
            "Export builder reconnecting in next phase."
        )
