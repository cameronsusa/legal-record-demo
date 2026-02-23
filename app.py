import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import uuid

st.set_page_config(layout="wide")

# -------------------------------
# SESSION INITIALIZATION
# -------------------------------

if "cases" not in st.session_state:
    st.session_state.cases = {}

if "active_case" not in st.session_state:
    st.session_state.active_case = None

# -------------------------------
# DEFAULT TEMPLATE SECTIONS
# -------------------------------

DEFAULT_TEMPLATE = [
    "Chief Complaint",
    "History of Present Illness",
    "Past Medical History",
    "Medications",
    "Allergies",
    "Labs",
    "Imaging",
    "Procedures",
    "Hospital Course",
    "Disposition"
]

# -------------------------------
# LAB PANEL DEFINITIONS
# -------------------------------

LAB_PANELS = {
    "CBC": {
        "WBC": (4.0, 11.0),
        "RBC": (4.2, 5.9),
        "Hemoglobin": (12, 17.5),
        "Hematocrit": (36, 52),
        "Platelets": (150, 400),
        "MCV": (80, 100),
        "MCH": (27, 33),
        "MCHC": (32, 36),
        "RDW": (11, 15),
        "Neutrophils": (40, 70),
        "Lymphocytes": (20, 40),
        "Monocytes": (2, 8),
        "Eosinophils": (1, 4),
        "Basophils": (0, 1)
    },
    "CMP - Electrolytes": {
        "Sodium": (135, 145),
        "Potassium": (3.5, 5.0),
        "Chloride": (98, 106),
        "CO2": (22, 29)
    },
    "CMP - Renal": {
        "BUN": (7, 20),
        "Creatinine": (0.6, 1.3),
        "eGFR": (60, 120)
    },
    "CMP - Liver": {
        "AST": (10, 40),
        "ALT": (7, 56),
        "Alkaline Phosphatase": (44, 147),
        "Total Bilirubin": (0.1, 1.2),
        "Albumin": (3.5, 5.0),
        "Total Protein": (6.0, 8.3)
    },
    "Inflammatory": {
        "CRP": (0, 1),
        "ESR": (0, 20),
        "Procalcitonin": (0, 0.1),
        "D-Dimer": (0, 0.5),
        "LDH": (140, 280)
    },
    "Anticoagulation": {
        "PT": (11, 13.5),
        "INR": (0.8, 1.2),
        "aPTT": (25, 35)
    },
    "Blood Gas": {
        "pH": (7.35, 7.45),
        "pCO2": (35, 45),
        "pO2": (75, 100),
        "HCO3": (22, 26),
        "Lactate": (0.5, 2.2)
    }
}

# -------------------------------
# CASE CREATION
# -------------------------------

st.sidebar.title("Cases")

if st.sidebar.button("New Case"):
    case_id = str(uuid.uuid4())
    st.session_state.cases[case_id] = {
        "name": f"Case {len(st.session_state.cases)+1}",
        "status": "Active",
        "template": DEFAULT_TEMPLATE.copy(),
        "labs": [],
        "chronology": ""
    }
    st.session_state.active_case = case_id

# Display cases
for cid, case in st.session_state.cases.items():
    color = "green" if case["status"] == "Active" else "gray"
    if st.sidebar.button(case["name"], key=cid):
        st.session_state.active_case = cid

if st.session_state.active_case is None:
    st.title("Select or Create a Case")
    st.stop()

case = st.session_state.cases[st.session_state.active_case]

# -------------------------------
# MAIN TABS
# -------------------------------

tabs = st.tabs([
    "Template Builder",
    "Upload Records",
    "Labs & Trends",
    "Review",
    "Administration"
])

# -------------------------------
# TEMPLATE BUILDER
# -------------------------------

with tabs[0]:
    st.subheader("Template Builder")

    for i, section in enumerate(case["template"]):
        col1, col2, col3 = st.columns([6,1,1])
        col1.write(section)
        if col2.button("↑", key=f"up_{i}") and i > 0:
            case["template"][i], case["template"][i-1] = case["template"][i-1], case["template"][i]
            st.rerun()
        if col3.button("↓", key=f"down_{i}") and i < len(case["template"])-1:
            case["template"][i], case["template"][i+1] = case["template"][i+1], case["template"][i]
            st.rerun()

    new_section = st.text_input("Add Section")
    if st.button("Add Section"):
        if new_section:
            case["template"].append(new_section)

# -------------------------------
# UPLOAD RECORDS
# -------------------------------

with tabs[1]:
    st.subheader("Upload Records")
    uploaded = st.file_uploader("Upload PDF or CSV", type=["pdf","csv"])
    if uploaded:
        st.success("File uploaded (Parsing module placeholder)")

# -------------------------------
# LABS & TRENDS
# -------------------------------

with tabs[2]:
    st.subheader("Labs & Trends")

    panel_choice = st.selectbox("Select Panel", list(LAB_PANELS.keys()))
    lab_choice = st.selectbox("Select Lab", list(LAB_PANELS[panel_choice].keys()))

    date = st.date_input("Date", datetime.date.today())
    value = st.number_input("Lab Value")

    if st.button("Add Lab"):
        case["labs"].append({
            "panel": panel_choice,
            "lab": lab_choice,
            "date": date,
            "value": value
        })

    df = pd.DataFrame(case["labs"])
    if not df.empty:
        df = df[df["lab"] == lab_choice]
        df = df.sort_values("date")

        st.dataframe(df)

        plt.figure()
        plt.plot(df["date"], df["value"])
        plt.xticks(rotation=45)
        plt.title(lab_choice)
        plt.tight_layout()
        st.pyplot(plt)

# -------------------------------
# REVIEW TAB
# -------------------------------

with tabs[3]:
    st.subheader("Flagged Items")
    st.write("Reviewer checklist placeholder")

# -------------------------------
# ADMIN TAB
# -------------------------------

with tabs[4]:
    st.subheader("Administration")
    if st.button("Mark Case Complete"):
        case["status"] = "Completed"
    st.write("Case Status:", case["status"])

# -------------------------------
# DISCLAIMER
# -------------------------------

st.markdown("---")
st.warning("""
This tool is intended to assist in medical-legal case organization. 
It does not replace professional medical review. 
Errors may be present. Final review must be performed by qualified personnel.
""")
