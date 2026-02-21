import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import uuid
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIG + DARK THEME
# ---------------------------------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
body { background-color: #111827; color: #F3F4F6; }
.stApp { background-color: #111827; }
section[data-testid="stSidebar"] { background-color: #1F2937; }
div.stButton > button {
    background-color: #3B82F6;
    color: white;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION INIT
# ---------------------------------------------------
if "cases" not in st.session_state:
    st.session_state.cases = {}

if "templates" not in st.session_state:
    st.session_state.templates = {}

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None

if "confirm_replace" not in st.session_state:
    st.session_state.confirm_replace = False

# ---------------------------------------------------
# CASE CREATION
# ---------------------------------------------------
def create_case(name):
    st.session_state.cases[name] = {
        "status": "Active",
        "structure": None,
        "template_origin": None,
        "structure_last_modified": None,
        "records": [],
        "labs": [],
        "duplicates": [],
        "flags": [],
        "custom_rules": []
    }

# ---------------------------------------------------
# SIDEBAR CASE MANAGER
# ---------------------------------------------------
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

new_case = st.sidebar.text_input("New Case Name")
if st.sidebar.button("Create Case"):
    if new_case and new_case not in st.session_state.cases:
        create_case(new_case)
        st.session_state.selected_case = new_case

if not st.session_state.selected_case:
    st.title("Create or Select a Case to Begin")
    st.stop()

case_data = st.session_state.cases[st.session_state.selected_case]

# ---------------------------------------------------
# NAVIGATION
# ---------------------------------------------------
page = st.sidebar.radio("Navigate", [
    "Dashboard",
    "Upload Records",
    "Templates",
    "Labs & Trends",
    "Duplicates",
    "Review & Flags",
    "Tools & Customization"
])

# ===================================================
# DASHBOARD
# ===================================================
if page == "Dashboard":

    st.title(f"Case: {st.session_state.selected_case}")

    if case_data["status"] == "Active":
        if st.button("Move to Past"):
            case_data["status"] = "Past"
    else:
        if st.button("Move to Active"):
            case_data["status"] = "Active"

    st.markdown("---")
    st.subheader("Case Structure")

    if case_data["structure"]:

        for i, section in enumerate(case_data["structure"]):

            col1, col2, col3, col4 = st.columns([6,1,1,1])
            col1.write(f"{i+1}. {section}")

            if col2.button("↑", key=f"up_{i}"):
                if i > 0:
                    case_data["structure"][i], case_data["structure"][i-1] = \
                        case_data["structure"][i-1], case_data["structure"][i]
                    st.experimental_rerun()

            if col3.button("↓", key=f"down_{i}"):
                if i < len(case_data["structure"]) - 1:
                    case_data["structure"][i], case_data["structure"][i+1] = \
                        case_data["structure"][i+1], case_data["structure"][i]
                    st.experimental_rerun()

            if col4.button("X", key=f"del_{i}"):
                case_data["structure"].pop(i)
                st.experimental_rerun()

        new_section = st.text_input("Add Section")
        if st.button("Add Section"):
            if new_section.strip():
                case_data["structure"].append(new_section.strip())
                case_data["structure_last_modified"] = datetime.now()

    else:
        st.info("No structure applied yet.")

    st.markdown("---")
    st.warning("This tool assists medical-legal organization and does not replace professional review.")

# ===================================================
# UPLOAD RECORDS
# ===================================================
elif page == "Upload Records":

    st.title("Upload Records")

    uploaded = st.file_uploader("Upload PDF or Document")

    if uploaded:
        case_data["records"].append(uploaded.name)
        st.success(f"{uploaded.name} added.")

    st.write("Uploaded Records:", case_data["records"])

# ===================================================
# TEMPLATES
# ===================================================
elif page == "Templates":

    st.title("Structural Templates")

    st.subheader("Paste Simple Outline")
    simple_text = st.text_area("One section per line")

    if st.button("Save Simple Structure"):
        if simple_text.strip():
            sections = [line.strip() for line in simple_text.split("\n") if line.strip()]
            template_name = f"Template_{uuid.uuid4().hex[:6]}"
            st.session_state.templates[template_name] = sections
            st.success(f"Saved as {template_name}")

    st.markdown("---")

    st.subheader("Upload Past Chronology")
    uploaded = st.file_uploader("Upload Document")

    if uploaded:
        simulated_sections = [
            "Emergency Department",
            "ICU Admission",
            "Surgical Course",
            "Complications",
            "Discharge Summary",
            "Labs",
            "Duplicate Appendix"
        ]
        template_name = f"Chronology_{uuid.uuid4().hex[:6]}"
        st.session_state.templates[template_name] = simulated_sections
        st.success(f"Structure saved as {template_name}")

    st.markdown("---")

    if st.session_state.templates:
        template_choice = st.selectbox("Select Template", list(st.session_state.templates.keys()))

        if st.button("Apply Template to This Case"):

            if case_data["structure"] and not st.session_state.confirm_replace:
                st.session_state.confirm_replace = True
                st.warning("Structure exists. Click again to confirm replacement.")
            else:
                case_data["structure"] = st.session_state.templates[template_choice].copy()
                case_data["template_origin"] = template_choice
                case_data["structure_last_modified"] = datetime.now()
                st.session_state.confirm_replace = False
                st.success("Template applied.")

# ===================================================
# LABS
# ===================================================
elif page == "Labs & Trends":

    st.title("Lab Trends")

    labs = {
        "CBC": ["WBC","RBC","HGB","HCT","Platelets"],
        "CMP": ["Sodium","Potassium","Creatinine","Glucose"],
        "Inflammatory": ["CRP","ESR"]
    }

    category = st.selectbox("Category", list(labs.keys()))
    selected_lab = st.selectbox("Lab", labs[category])

    dates = pd.date_range(start="2023-01-01", periods=12)
    values = [5,7,6,12,8,9,11,10,13,7,6,8]

    df = pd.DataFrame({"Date": dates, "Value": values})

    fig, ax = plt.subplots(figsize=(14,6))
    ax.plot(df["Date"], df["Value"], marker="o")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ===================================================
# DUPLICATES
# ===================================================
elif page == "Duplicates":

    st.title("Duplicate Detection")

    if st.button("Simulate Duplicate"):
        case_data["duplicates"].append(f"BATES_{uuid.uuid4().hex[:4]}")
        st.success("Duplicate added.")

    st.write(case_data["duplicates"])

# ===================================================
# REVIEW
# ===================================================
elif page == "Review & Flags":

    st.title("Flags")

    if st.button("Add Test Flag"):
        case_data["flags"].append({"item":"Lab Value","status":"Pending"})

    for i, flag in enumerate(case_data["flags"]):
        status = st.selectbox(
            "Status",
            ["Pending","Completed","Dismissed"],
            key=f"flag_{i}"
        )
        case_data["flags"][i]["status"] = status

# ===================================================
# TOOLS
# ===================================================
elif page == "Tools & Customization":

    st.title("Customization")

    custom_rule = st.text_area("Add Firm Rule")

    if st.button("Save Rule"):
        case_data["custom_rules"].append(custom_rule)

    st.write("Saved Rules:", case_data["custom_rules"])
