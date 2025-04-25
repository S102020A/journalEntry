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
    st.markdown(
        "<h2 style='color: Bisque;'>Raw Uploaded Data</h2>", unsafe_allow_html=True
    )
    st.dataframe(raw.head())

    st.markdown(
        "<h2 style='color: Bisque;'>Raw Data Types</h2>", unsafe_allow_html=True
    )
    dtypes_df = pd.DataFrame(raw.dtypes, columns=["Data Type"])
    st.dataframe(dtypes_df, height=200)

    try:
        st.markdown(
            "<h2 style='color: DarkSalmon;'>Cleaned Data</h2>", unsafe_allow_html=True
        )
        clean_data = clean_data(raw=raw)
        st.dataframe(clean_data)

        st.markdown(
            "<h2 style='color: DarkSalmon;'>Cleaned Data Types</h2>",
            unsafe_allow_html=True,
        )
        dtypes_df = pd.DataFrame(clean_data.dtypes, columns=["Data Type"])
        st.dataframe(dtypes_df, height=200)
    except Exception as e:
        st.subheader("Data Cleaning Error")
        st.error(f"{e}")

    # Initialize session state if it doesn't exist
    if "show_confirm" not in st.session_state:
        st.session_state.show_confirm = False
    if "proceed_ingestion" not in st.session_state:
        st.session_state.proceed_ingestion = False

    if st.button("Ingest Data", icon="🚀"):
        st.session_state.show_confirm = True

    if st.session_state.get("show_confirm", False):
        st.warning("Are you sure you want to ingest the data?")
        proceed, cancel = st.columns(2)
        with proceed:
            if st.button("✅ Yes, proceed"):
                st.info("🏃 Data ingestion started!")
                st.session_state.proceed_ingestion = True
                st.session_state.show_confirm = False
                st.rerun()
        with cancel:
            if st.button("❌ Cancel"):
                st.info("Action cancelled.")
                st.session_state.show_confirm = False
                st.session_state.proceed_ingestion = False
                st.rerun()

    # Data ingestion logic - This should ONLY run if proceed_ingestion is True
    if st.session_state.get("proceed_ingestion", False):
        with st.container():
            try:
                # Call the data processing functions
                message = drop_data_from_minimum_date_created(clean_data)
                st.success(message)

                message = insert_data(clean_data.to_dict(orient="records"))
                st.success(message)

                # Show data from the database
                st.markdown(
                    "<h2 style='color: IndianRed;'>Database Data Head</h2>",
                    unsafe_allow_html=True,
                )
                st.dataframe(show_head_from_db())
            except Exception as e:
                st.subheader("Data Ingestion Error")
                st.error(f"{e}")


def clear_session_and_cache():
    # Clear session state
    st.session_state.clear()
    # Clear cache
    st.cache_resource.clear()
    st.cache_data.clear()
    st.rerun()  # Rerun the app to reflect the cleared state


# Example usage:
if st.button("Clear Session and Cache", icon="🧹", type="primary"):
    clear_session_and_cache()


@st.cache_data
def my_cached_data(count):
    print("Running my_cached_data")  # check when the function runs
    return count * 2
