import pandas as pd
import streamlit as st
from utils.utils import *


st.title("Manual Journal Entry Transaction Upload")
uploaded_file = st.file_uploader(
    "Upload a CSV from the Query Report MANUAL_JOURNAL_TRANSACTION_ENTRY",
    type="csv",
    accept_multiple_files=False,
)

if uploaded_file is not None:
    raw = pd.read_csv(uploaded_file, dtype=str)
    st.subheader("Raw Uploaded Data")
    st.dataframe(raw.head())

    st.subheader("Raw Data Types")
    dtypes_df = pd.DataFrame(raw.dtypes, columns=["Data Type"])
    st.dataframe(dtypes_df, height=200)

    try:
        st.subheader("Clean Data")
        clean_data = clean_data(raw)
        st.dataframe(clean_data)
    except Exception as e:
        st.subheader("Data Cleaning Error")
        st.error(f"{e}")

    if st.button("Ingest Data", icon="🚀"):
        st.session_state.show_confirm = True

    if st.session_state.get("show_confirm", False):
        st.warning("Are you sure you want to ingest the data?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, proceed"):
                st.success("Data ingestion started!")

                try:
                    clean_data_rows = clean_data.to_dict(orient="records")
                    insert_data(clean_data_rows)
                except Exception as e:
                    st.subheader("Data Ingestion Error")
                    st.error(f"{e}")

                st.session_state.show_confirm = False  # Reset state
        with col2:
            if st.button("❌ Cancel"):
                st.info("Action cancelled.")
                st.session_state.show_confirm = False  # Reset state
