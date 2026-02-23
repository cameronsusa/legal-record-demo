import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io

st.set_page_config(page_title="Med-Legal Case Organizer v1.8", layout="wide")

# --------------------------
# THEME
# --------------------------
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #ffffff; }
h1,h2,h3 { color: #ffffff; }
.block-container { padding-top: 2rem; }
.sidebar .sidebar-content { background-color: #111827; }
</style>
""", unsafe_allow_html=True)

st.title("Med-Legal Case Organizer - Version 1.8")

# --------------------------
# SESSION STATE
# --------------------------
if "cases" not in st.session_state:
    st.session_state.cases = {}

if "current_case" not in st.session_state:
    st.session_state.current_case = None

# --------------------------
# CASE MANAGEMENT
# --------------------------
st.sidebar.header("Case Management")

case_status = st.sidebar.radio("View Cases", ["New Case", "Active Cases", "Past Cases"])

if case_status == "New Case":
    case_name = st.sidebar.text_input("Create New Case")
    if st.sidebar.button("Create Case"):
        st.session_state.cases[case_name] = {
            "status": "Active",
            "template": [],
            "records": None,
            "labs": {},
            "notes": [],
            "duplicates": []
        }
        st.session_state.current_case = case_name

if case_status == "Active Cases":
    for c in st.session_state.cases:
        if st.session_state.cases[c]["status"] == "Active":
            if st.sidebar.button(f"🟢 {c}"):
                st.session_state.current_case = c

if case_status == "Past Cases":
    for c in st.session_state.cases:
        if st.session_state.cases[c]["status"] == "Past":
            if st.sidebar.button(f"🔵 {c}"):
                st.session_state.current_case = c

if st.session_state.current_case:
    case = st.session_state.cases[st.session_state.current_case]
    st.subheader(f"Current Case: {st.session_state.current_case}")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Upload",
        "Template Builder",
        "Labs & Trends",
        "Duplicates / Blanks",
        "Administration",
        "Export"
    ])

    # --------------------------
    # UPLOAD TAB
    # --------------------------
    with tab1:
        st.subheader("Upload Records")

        records = st.file_uploader("Upload Medical Records (PDF, TXT, CSV)", type=["pdf","txt","csv"])
        if records:
            case["records"] = records
            st.success("Records Uploaded")

        template_file = st.file_uploader("Upload Generic Template or Past Chronology", type=["txt","docx"])
        if template_file:
            content = template_file.read().decode("utf-8", errors="ignore")
            case["template"] = content.split("\n")
            st.success("Template Imported")

    # --------------------------
    # TEMPLATE BUILDER
    # --------------------------
    with tab2:
        st.subheader("Template Sections")

        new_section = st.text_input("Add Section")
        if st.button("Add Section"):
            case["template"].append(new_section)

        for i, sec in enumerate(case["template"]):
            col1, col2, col3 = st.columns([6,1,1])
            col1.write(sec)
            if col2.button("⬆️", key=f"up{i}"):
                if i > 0:
                    case["template"][i], case["template"][i-1] = case["template"][i-1], case["template"][i]
            if col3.button("⬇️", key=f"down{i}"):
                if i < len(case["template"]) - 1:
                    case["template"][i], case["template"][i+1] = case["template"][i+1], case["template"][i]

    # --------------------------
    # LABS SECTION
    # --------------------------
    with tab3:
        st.subheader("Lab Entry")

        lab_panels = {
            "BMP": ["Sodium","Potassium","Chloride","CO2","BUN","Creatinine","Glucose"],
            "Liver Panel": ["AST","ALT","Alk Phos","Total Bilirubin","Albumin"],
            "CBC": ["WBC","Hgb","Hct","Platelets","MCV","MCH","MCHC"],
            "Coagulation": ["PT","INR","aPTT"],
            "Blood Gas": ["pH","pCO2","pO2","HCO3","Lactate"],
            "Inflammatory": ["CRP","ESR","D-Dimer","LDH"],
            "Biopsy": ["Specimen Type","Pathology Result"],
            "Autoimmune/Tumor Markers": ["ANA","RF","CA-125","CEA"]
        }

        selected_panel = st.selectbox("Select Panel", list(lab_panels.keys()))

        if selected_panel not in case["labs"]:
            case["labs"][selected_panel] = []

        with st.form("lab_form"):
            date = st.date_input("Date")
            values = {}
            for test in lab_panels[selected_panel]:
                values[test] = st.text_input(test)
            custom_lab = st.text_input("Add Custom Lab (Optional)")
            submit = st.form_submit_button("Add Entry")

            if submit:
                values["Date"] = date
                if custom_lab:
                    values["Custom"] = custom_lab
                case["labs"][selected_panel].append(values)
                st.success("Lab Entry Added")

        if st.button("Auto Generate Graph"):
            if case["labs"][selected_panel]:
                df = pd.DataFrame(case["labs"][selected_panel])
                if "Date" in df:
                    df = df.sort_values("Date")
                    numeric_cols = df.select_dtypes(include=['object'])
                    fig, ax = plt.subplots()
                    for col in df.columns:
                        if col != "Date":
                            try:
                                df[col] = pd.to_numeric(df[col])
                                ax.plot(df["Date"], df[col])
                            except:
                                pass
                    ax.tick_params(axis='x', rotation=45)
                    st.pyplot(fig)

    # --------------------------
    # DUPLICATES TAB
    # --------------------------
    with tab4:
        st.subheader("Duplicate / Blank Review")
        if case["records"]:
            st.write("Scanning records...")
            st.info("Duplicate detection placeholder - logic expandable")
        else:
            st.warning("Upload records first.")

    # --------------------------
    # ADMIN
    # --------------------------
    with tab5:
        st.subheader("Administration")
        new_status = st.selectbox("Change Case Status", ["Active","Past"])
        if st.button("Update Status"):
            case["status"] = new_status
            st.success("Status Updated")

        firm_customization = st.text_area("Firm Customization Notes")
        if st.button("Save Customization"):
            case["notes"].append(firm_customization)

    # --------------------------
    # EXPORT
    # --------------------------
    with tab6:
        st.subheader("Export Case File")

        export_data = {
            "Template": case["template"],
            "Labs": case["labs"],
            "Notes": case["notes"]
        }

        export_bytes = io.BytesIO()
        export_bytes.write(str(export_data).encode())
        st.download_button(
            label="Download Compiled Case File",
            data=export_bytes.getvalue(),
            file_name=f"{st.session_state.current_case}_compiled.txt"
        )

# --------------------------
# DISCLAIMER
# --------------------------
st.markdown("---")
st.warning("""
This software is a medical-legal organizational aid only.
It does not replace professional medical or legal review.
Data parsing may contain errors.
Final review must be conducted by qualified staff.
Use at your own discretion.
""")
