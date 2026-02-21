import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import uuid

# -----------------------------
# PAGE CONFIG + DARK THEME
# -----------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
body { background-color: #111827; color: #F3F4F6; }
.stApp { background-color: #111827; }
section[data-testid="stSidebar"] { background-color: #1F2937; }
div.stButton > button {
    background-color: #3B82F6;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "cases" not in st.session_state:
    st.session_state.cases = {}

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None

# -----------------------------
# CASE STRUCTURE
# -----------------------------
def create_case(name):
    st.session_state.cases[name] = {
        "status": "Active",
        "records": [],
        "templates": [],
        "labs": [],
        "flags": [],
        "duplicates": [],
        "blanks": [],
        "custom_rules": []
    }

# -----------------------------
# SIDEBAR CASE MANAGER
# -----------------------------
st.sidebar.title("CASE MANAGER")

active_cases = [c for c in st.session_state.cases if st.session_state.cases[c]["status"] == "Active"]
past_cases = [c for c in st.session_state.cases if st.session_state.cases[c]["status"] == "Past"]

st.sidebar.subheader("Active Cases")
for case in active_cases:
    if st.sidebar.button(f"🟢 {case}", key=f"active_{case}"):
        st.session_state.selected_case = case

st.sidebar.subheader("Past Cases")
for case in past_cases:
    if st.sidebar.button(f"🔵 {case}", key=f"past_{case}"):
        st.session_state.selected_case = case

new_case_name = st.sidebar.text_input("New Case Name")
if st.sidebar.button("Create Case"):
    if new_case_name:
        create_case(new_case_name)
        st.session_state.selected_case = new_case_name

st.sidebar.markdown("---")

# -----------------------------
# NAVIGATION
# -----------------------------
if st.session_state.selected_case:
    page = st.sidebar.radio("Navigate", [
        "Dashboard",
        "Upload Records",
        "Templates",
        "Labs & Trends",
        "Duplicates / Blank Pages",
        "Review & Flags",
        "Administration",
        "Tools & Customization"
    ])
else:
    st.title("Create or Select a Case to Begin")
    st.stop()

case_data = st.session_state.cases[st.session_state.selected_case]

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":
    st.title(f"Case: {st.session_state.selected_case}")

    col1, col2 = st.columns(2)

    if case_data["status"] == "Active":
        if col1.button("Move to Past"):
            case_data["status"] = "Past"
    else:
        if col1.button("Move to Active"):
            case_data["status"] = "Active"

    st.markdown("---")

    st.warning("""
    DISCLAIMER:
    This tool assists medical-legal review and does not replace professional judgment.
    All outputs must be reviewed by qualified personnel before legal use.
    """)

# -----------------------------
# UPLOAD RECORDS
# -----------------------------
elif page == "Upload Records":
    st.title("Upload Records")

    uploaded_file = st.file_uploader("Upload PDF or Document")

    if uploaded_file:
        case_data["records"].append(uploaded_file.name)
        st.success(f"{uploaded_file.name} added to case.")

    st.write("Uploaded Records:", case_data["records"])

# -----------------------------
# TEMPLATES
# -----------------------------
elif page == "Templates":
    st.title("Templates")

    template_file = st.file_uploader("Upload Template Structure")

    if template_file:
        case_data["templates"].append(template_file.name)
        st.success("Template uploaded.")

    st.write("Saved Templates:", case_data["templates"])

# -----------------------------
# LABS & TRENDS
# -----------------------------
elif page == "Labs & Trends":
    st.title("Labs & Trends")

    labs = {
        "CBC": ["WBC","RBC","HGB","HCT","Platelets","MCV","MCH","RDW"],
        "CMP": ["Sodium","Potassium","Chloride","CO2","BUN","Creatinine","Glucose","AST","ALT","ALP","Bilirubin"],
        "Inflammatory": ["CRP","ESR","Procalcitonin"]
    }

    category = st.selectbox("Category", list(labs.keys()))
    selected_lab = st.selectbox("Lab Test", labs[category])

    # Simulated data
    dates = pd.date_range(start="2023-01-01", periods=12)
    values = [5,7,6,12,8,9,11,10,13,7,6,8]

    df = pd.DataFrame({"Date": dates, "Value": values})

    fig, ax = plt.subplots(figsize=(14,6))
    ax.plot(df["Date"], df["Value"], marker="o")

    ax.set_title(selected_lab + " Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

# -----------------------------
# DUPLICATES / BLANKS
# -----------------------------
elif page == "Duplicates / Blank Pages":
    st.title("Duplicates & Blank Pages")

    if st.button("Simulate Duplicate Detection"):
        case_data["duplicates"].append("BATES_0045")
        st.success("Duplicate detected.")

    st.write("Duplicates:", case_data["duplicates"])

    if st.button("Simulate Blank Page Detection"):
        case_data["blanks"].append("BATES_0102")
        st.success("Blank page detected.")

    st.write("Blank Pages:", case_data["blanks"])

# -----------------------------
# REVIEW & FLAGS
# -----------------------------
elif page == "Review & Flags":
    st.title("Flagged Items")

    if st.button("Add Test Flag"):
        case_data["flags"].append({
            "Item": "WBC",
            "Reason": "High value",
            "Status": "Pending"
        })

    for i, flag in enumerate(case_data["flags"]):
        st.write(flag["Item"], "-", flag["Reason"])
        status = st.selectbox(
            "Status",
            ["Pending","Completed","Dismissed"],
            key=f"flag_{i}"
        )
        case_data["flags"][i]["Status"] = status

# -----------------------------
# ADMINISTRATION
# -----------------------------
elif page == "Administration":
    st.title("Administration")

    roles = ["Nurse","Attorney","Partner","Paralegal"]
    selected_role = st.selectbox("User Role", roles)

    st.write(f"Permissions for {selected_role} would be configured here.")

# -----------------------------
# TOOLS & CUSTOMIZATION
# -----------------------------
elif page == "Tools & Customization":
    st.title("Customization")

    export_policy = st.selectbox(
        "Export Policy",
        ["Block if flags pending","Include flag summary","Allow regardless"]
    )

    custom_rule = st.text_area("Add Firm Custom Rule")

    if st.button("Save Rule"):
        case_data["custom_rules"].append(custom_rule)

    st.write("Saved Rules:", case_data["custom_rules"])
