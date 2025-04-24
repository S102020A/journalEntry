import pandas as pd
import streamlit as st
from utils.utils import *

st.title("Upload")

option = st.selectbox(
    label="Select an upload option",
    options=["MANUAL_JOURNAL_ENTRY_TRANSACTION", "MANUAL_BUDGET"],
    key="option_selectbox",
)

st.session_state["table_name"] = option

uploaded_file = st.file_uploader(
    f"Upload a CSV from the Query Report {option}",
    type="csv",
    accept_multiple_files=False,
    key="file_uploader",
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
        clean_data = clean_data(raw=raw)
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
                    # drop all rows from the minimum date from supplied rows
                    drop_data_from_minimum_date_created(clean_data)
                    insert_data(clean_data.to_dict(orient="records"))
                except Exception as e:
                    st.subheader("Data Ingestion Error")
                    st.error(f"{e}")

                st.session_state.show_confirm = False  # Reset state
        with col2:
            if st.button("❌ Cancel"):
                st.info("Action cancelled.")
                st.session_state.show_confirm = False  # Reset state
