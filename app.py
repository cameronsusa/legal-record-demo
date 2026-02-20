import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Legal Medical Record Intelligence", layout="wide")

# --------------------------
# Sidebar Navigation
# --------------------------
st.sidebar.title("Legal Record Intelligence")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Records",
        "Templates",
        "Labs & Trends",
        "Duplicates",
        "Administration",
        "Tools & Customization"
    ]
)

# --------------------------
# Dashboard
# --------------------------
if menu == "Dashboard":
    st.title("Medical Record Intelligence Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Records Processed", "1,248")
    col2.metric("Flagged Entries", "17")
    col3.metric("Duplicate Pages", "9")

    st.subheader("Chronology Preview")

    df = pd.DataFrame({
        "Date": pd.date_range(start="2025-01-01", periods=10),
        "Event": ["ED Visit", "Lab Result", "PT Session", "MD Note", "OT Eval",
                  "Lab Result", "Hospitalization", "PT Session", "Discharge", "Follow-up"]
    })

    st.dataframe(df, use_container_width=True)

# --------------------------
# Upload Records
# --------------------------
elif menu == "Upload Records":
    st.title("Upload Medical Records")

    uploaded_files = st.file_uploader(
        "Upload Medical Records (PDF or Image)",
        type=["pdf", "png", "jpg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully.")
        st.info("Processing engine would analyze dates, disciplines, and chronology here.")

# --------------------------
# Templates
# --------------------------
elif menu == "Templates":
    st.title("Template Configuration")

    tier = st.radio("Subscription Tier", ["Basic (Generic Template)", "Premium (Past Approved Case Model)"])

    if tier == "Basic (Generic Template)":
        st.file_uploader("Upload Generic One-Page Template", type=["pdf", "docx"])

    else:
        st.file_uploader("Upload Previously Approved Case Model", type=["pdf", "docx"])

    st.info("System will align extracted content to template structure.")

# --------------------------
# Labs & Trends
# --------------------------
elif menu == "Labs & Trends":
    st.title("Lab & Vital Trends")

    dates = pd.date_range(start="2025-01-01", periods=10)
    lab_values = np.random.randint(80, 140, size=10)

    df = pd.DataFrame({"Date": dates, "Glucose": lab_values})

    st.line_chart(df.set_index("Date"))

# --------------------------
# Duplicates
# --------------------------
elif menu == "Duplicates":
    st.title("Duplicate Page Management")

    st.warning("Duplicates are preserved for review. BATES numbering remains unaffected.")

    duplicates = pd.DataFrame({
        "Page": ["BATES_0012", "BATES_0045", "BATES_0102"],
        "Reason": ["Exact match", "Near match", "Scanned duplicate"]
    })

    st.dataframe(duplicates, use_container_width=True)

# --------------------------
# Administration
# --------------------------
elif menu == "Administration":
    st.title("User Role Management")

    role = st.selectbox("Select Role", ["Nurse", "Attorney", "Partner", "Paralegal"])

    permissions = {
        "Nurse": "View + Comment",
        "Attorney": "View + Edit",
        "Partner": "Full Access",
        "Paralegal": "View Only"
    }

    st.info(f"{role} permissions: {permissions[role]}")

    st.subheader("Audit Log")
    st.write("• 02/18/2026 - PT section edited")
    st.write("• 02/17/2026 - Duplicate moved to bottom")
    st.write("• 02/15/2026 - Template updated")

# --------------------------
# Tools & Customization
# --------------------------
elif menu == "Tools & Customization":
    st.title("Customization & Rule Builder")

    remove_dupes = st.checkbox("Automatically Remove Exact Duplicates")
    normalize_dates = st.checkbox("Normalize All Date Formats")
    move_dupes = st.checkbox("Move Duplicates to End of Chronology")
    separate_folder = st.checkbox("Move Duplicates to Separate Folder")

    st.subheader("Firm Rule Builder")

    rule_name = st.text_input("Rule Name")
    rule_condition = st.text_input("If Document Contains...")
    rule_action = st.text_input("Then Move To Section...")

    if st.button("Save Rule"):
        st.success("Rule saved successfully.")
