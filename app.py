import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import io

st.set_page_config(page_title="Legal Record Demo System", layout="wide")

st.title("Legal Record Review & Chronology System")
st.caption("Demo platform for medical-legal document analysis")

# ---------------- Sidebar Customization ----------------
st.sidebar.header("Customization Rules")

duplicate_handling = st.sidebar.selectbox(
    "Duplicate Page Handling",
    ["Move to end of chronology", "Separate duplicates tab", "Flag but keep in place", "Delete duplicates (not recommended)"]
)

preserve_bates = st.sidebar.checkbox("Preserve Bates Numbers", value=True)
firm_rules = st.sidebar.text_area("Firm-Specific Rules (Optional)", placeholder="Example: Always flag missing consent forms\nExample: Separate psych records into own tab")

# ---------------- File Upload ----------------
st.header("Upload Records")
uploaded_files = st.file_uploader("Upload medical or legal PDFs", type=["pdf"], accept_multiple_files=True)

# ---------------- Helper Functions ----------------
def hash_file(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

def simulate_page_quality():
    import random
    return random.choice(["High Quality Scan", "Moderate Scan", "Poor Scan (OCR Errors Likely)"])

# ---------------- Processing ----------------
if uploaded_files:
    st.success(f"{len(uploaded_files)} files uploaded successfully.")

    file_data = []
    hashes = set()
    duplicates = []

    for file in uploaded_files:
        bytes_data = file.read()
        file_hash = hash_file(bytes_data)

        page_quality = simulate_page_quality()
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "Filename": file.name,
            "Hash": file_hash,
            "Upload Time": upload_time,
            "Scan Quality": page_quality,
            "Bates Preserved": preserve_bates
        }

        if file_hash in hashes:
            duplicates.append(record)
        else:
            hashes.add(file_hash)
            file_data.append(record)

    df = pd.DataFrame(file_data)
    dup_df = pd.DataFrame(duplicates)

    st.subheader("Processed Records")
    st.dataframe(df, use_container_width=True)

    # ---------------- Duplicate Handling ----------------
    st.subheader("Duplicate Records")

    if duplicate_handling == "Separate duplicates tab":
        st.info("Duplicates have been placed in a separate tab below.")
        st.dataframe(dup_df, use_container_width=True)

    elif duplicate_handling == "Move to end of chronology":
        st.info("Duplicates will appear at the end of the chronology but will not be deleted.")
        combined = pd.concat([df, dup_df])
        st.dataframe(combined, use_container_width=True)

    elif duplicate_handling == "Flag but keep in place":
        st.info("Duplicates will be flagged but kept in their original positions.")
        df["Duplicate"] = df["Hash"].isin(dup_df["Hash"])
        st.dataframe(df, use_container_width=True)

    elif duplicate_handling == "Delete duplicates (not recommended)":
        st.warning("Duplicates will be deleted (demo only).")
        st.dataframe(df, use_container_width=True)

    # ---------------- Chronology ----------------
    st.subheader("Generated Chronology (Demo View)")
    st.write("This represents a simplified chronological listing of records.")

    df["Date"] = pd.to_datetime(df["Upload Time"])
    chronology = df.sort_values(by="Date")
    st.dataframe(chronology[["Filename", "Date", "Scan Quality"]], use_container_width=True)

    # ---------------- Charts ----------------
    st.subheader("Trend Analysis (Demo)")

    chart_type = st.selectbox("Select Trend Type", ["Labs", "Vitals", "Hospitalizations"])

    demo_chart_data = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=10),
        "Value": [98, 101, 99, 102, 104, 100, 103, 105, 107, 106]
    })

    fig, ax = plt.subplots()
    ax.plot(demo_chart_data["Date"], demo_chart_data["Value"])
    ax.set_title(f"{chart_type} Trend Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    st.pyplot(fig)

    # ---------------- Metadata ----------------
    st.subheader("Project Metadata")
    st.write("Creation Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.write("Owner:", "User-created system")
    st.write("Firm Rules Applied:", firm_rules or "None specified")

else:
    st.info("Upload files to begin processing.")
