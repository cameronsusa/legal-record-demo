import streamlit as st
from db import init_db

st.set_page_config(page_title="Litigation Record Engine", layout="wide")

init_db()

st.title("Litigation Record Engine v2.0")
st.success("Database initialized successfully.")
