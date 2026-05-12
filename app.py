import streamlit as st

st.set_page_config(layout="wide")

st.title("NEW LITIGATION ENGINE")

tabs = st.tabs([
    "Upload Records",
    "Chronology Workspace",
    "Administrative",
    "Duplicates",
    "Export"
])

with tabs[0]:
    st.header("UPLOAD TAB WORKING")

with tabs[1]:
    st.header("CHRONOLOGY TAB WORKING")

with tabs[2]:
    st.header("ADMIN TAB WORKING")

with tabs[3]:
    st.header("DUPLICATES TAB WORKING")

with tabs[4]:
    st.header("EXPORT TAB WORKING")
