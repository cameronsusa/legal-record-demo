import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.lib.pagesizes import letter
from io import BytesIO

# -----------------------------
# DARK ENTERPRISE THEME
# -----------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
body {
    background-color: #111827;
    color: #F3F4F6;
}
.stApp {
    background-color: #111827;
}
section[data-testid="stSidebar"] {
    background-color: #1F2937;
}
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
if "flags" not in st.session_state:
    st.session_state.flags = []

if "export_mode" not in st.session_state:
    st.session_state.export_mode = "Include Flag Summary"

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("Medical-Legal Platform")
page = st.sidebar.radio("Navigate", [
    "Dashboard",
    "Labs & Trends",
    "Flagged Items",
    "Tools & Customization"
])

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":
    st.title("Medical-Legal Record Analysis Platform")

    st.markdown("### Case Overview")
    st.info("Upload records and analyze labs under the Labs & Trends tab.")

    st.markdown("---")

    st.warning("""
    DISCLAIMER:
    This software is intended solely as a support tool to assist medical-legal review.
    It does not replace professional medical judgment or legal review.
    Automated extraction and analysis may contain inaccuracies.
    All outputs must be independently reviewed by qualified personnel.
    """)

# -----------------------------
# LABS & TRENDS
# -----------------------------
elif page == "Labs & Trends":
    st.title("Lab Trends")

    category = st.selectbox("Lab Category", ["CBC", "CMP", "Inflammatory"])

    lab_options = {
        "CBC": ["WBC", "Hemoglobin", "Platelets"],
        "CMP": ["Sodium", "Potassium", "Creatinine"],
        "Inflammatory": ["CRP", "ESR"]
    }

    selected_lab = st.selectbox("Select Lab Test", lab_options[category])

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    # Simulated Data
    dates = pd.date_range(start="2023-01-01", periods=10)
    values = [5, 6, 12, 14, 7, 8, 9, 15, 10, 11]

    df = pd.DataFrame({"Date": dates, "Value": values})

    # Reference Range Simulation
    ref_low = 4
    ref_high = 10

    if selected_lab == "CRP":
        ref_low = None
        ref_high = None

    if ref_low is None:
        ref_low = 0
        ref_high = 5
        st.warning(
            "Range not found or analyzed accurately by software. "
            "Average standard medical range applied: 0-5*"
        )

        st.session_state.flags.append({
            "Item": selected_lab,
            "Reason": "Reference range auto-applied",
            "Status": "Pending",
            "Comment": ""
        })

    fig, ax = plt.subplots()

    ax.plot(df["Date"], df["Value"], marker="o")

    ax.axhspan(ref_low, ref_high, alpha=0.2)

    for i in range(len(df)):
        if df["Value"][i] > ref_high:
            ax.plot(df["Date"][i], df["Value"][i], "ro")
        elif df["Value"][i] < ref_low:
            ax.plot(df["Date"][i], df["Value"][i], "bo")
        else:
            ax.plot(df["Date"][i], df["Value"][i], "go")

    ax.set_title(selected_lab + " Trend")
    st.pyplot(fig)

    if st.button("Add Significant Event"):
        st.success("Event marker functionality placeholder")

# -----------------------------
# FLAGGED ITEMS
# -----------------------------
elif page == "Flagged Items":
    st.title("Flagged Items for Review")

    if not st.session_state.flags:
        st.success("No flagged items.")
    else:
        for i, flag in enumerate(st.session_state.flags):
            st.markdown(f"### {flag['Item']}")
            st.write("Reason:", flag["Reason"])

            status = st.selectbox(
                "Status",
                ["Pending", "Completed", "Dismissed", "Other"],
                key=f"status_{i}"
            )

            comment = st.text_input("Comment", key=f"comment_{i}")

            complete = st.checkbox("Mark Complete", key=f"complete_{i}")

            if complete:
                st.session_state.flags[i]["Status"] = "Completed"

# -----------------------------
# TOOLS & CUSTOMIZATION
# -----------------------------
elif page == "Tools & Customization":
    st.title("Export & Settings")

    export_mode = st.selectbox(
        "Export Behavior",
        [
            "Block export if unresolved flags",
            "Include Flag Summary",
            "Allow export regardless"
        ]
    )

    st.session_state.export_mode = export_mode

    if st.button("Export Chronology as PDF"):

        unresolved = [
            f for f in st.session_state.flags
            if f["Status"] != "Completed"
        ]

        if export_mode == "Block export if unresolved flags" and unresolved:
            st.error("Resolve all flags before exporting.")
        else:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("Chronology Report", styles["Heading1"]))
            elements.append(Spacer(1, 0.25 * inch))

            if export_mode == "Include Flag Summary" and st.session_state.flags:
                elements.append(Paragraph("Flag Summary", styles["Heading2"]))
                elements.append(Spacer(1, 0.2 * inch))
                for flag in st.session_state.flags:
                    elements.append(
                        Paragraph(
                            f"{flag['Item']} - {flag['Reason']} - {flag['Status']}",
                            styles["Normal"]
                        )
                    )

            doc.build(elements)
            st.success("Export ready.")
            st.download_button(
                "Download PDF",
                buffer.getvalue(),
                "chronology.pdf"
            )
