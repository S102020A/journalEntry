import pandas as pd
import streamlit as st
from pages.upload.utils import *
from app import logger


def hard_del_session():
    for key in st.session_state.keys():
        del st.session_state[key]


st.title("Upload")

option = st.selectbox(
    label="Select an upload option",
    options=["MANUAL_JOURNAL_ENTRY_TRANSACTION", "MANUAL_BUDGET"],
    key="option_selectbox",
    index=1,
    on_change=hard_del_session,
)
st.session_state["table_name"] = option

uploaded_file = st.file_uploader(
    label=f"Upload a csv",
    type="csv",
    accept_multiple_files=False,
    key="file_uploader",
)

if uploaded_file is not None:
    if st.button("Clean Data", key="clean_data_btn"):
        st.session_state["show_clean_confirm"] = True

    if st.session_state.get("show_clean_confirm", False):
        yes, no = st.columns(2)
        st.session_state["show_clean_confirm"] = True

        if st.session_state.get("show_clean_confirm", False):
            with yes:
                if st.button("✅ Yes, proceed"):
                    st.session_state["is_clean"] = True
                    st.session_state["show_clean_confirm"] = False
                    st.rerun()
            with no:
                if st.button("❌ Cancel"):
                    st.session_state["is_clean"] = False
                    st.session_state["show_clean_confirm"] = False
                    st.rerun()

if st.session_state.get("is_clean", False):
    try:
        raw = pd.read_csv(uploaded_file, dtype=str, delimiter=",")

        st.markdown(
            "<h2 style='color: Bisque;'>Raw Uploaded Data</h2>", unsafe_allow_html=True
        )
        st.dataframe(raw.head())

        st.markdown(
            "<h2 style='color: Bisque;'>Raw Data Types</h2>", unsafe_allow_html=True
        )
        st.dataframe(pd.DataFrame(raw.dtypes, columns=["Data Type"]), height=200)

        # Try cleaning the data
        try:
            st.markdown(
                "<h2 style='color: DarkSalmon;'>Cleaned Data</h2>",
                unsafe_allow_html=True,
            )
            clean_data_df = clean_data(raw=raw)
            st.dataframe(clean_data_df)

            st.markdown(
                "<h2 style='color: DarkSalmon;'>Cleaned Data Types</h2>",
                unsafe_allow_html=True,
            )
            st.dataframe(
                pd.DataFrame(clean_data_df.dtypes, columns=["Data Type"]), height=200
            )

            # Ingest button
            if st.button("Ingest Data 🚀"):
                st.session_state["show_ingestion_confirm"] = True

            # Confirmation UI
            if st.session_state.get("show_ingestion_confirm", False):
                st.warning("Are you sure you want to ingest the data?")

                if st.button("✅ Yes, proceed", use_container_width=True):
                    st.info("🏃 Data ingestion started!")

                    try:
                        message = drop_data_from_minimum_date_created(clean_data_df)
                        st.success(message)

                        message = insert_data(clean_data_df.to_dict(orient="records"))
                        st.success(message)

                        st.markdown(
                            "<h2 style='color: IndianRed;'>Database Data Head</h2>",
                            unsafe_allow_html=True,
                        )
                        st.dataframe(show_head_from_db())

                        # Clear flag after success
                        st.session_state["show_ingestion_confirm"] = False

                    except Exception as e:
                        st.subheader("Data Ingestion Error")
                        st.error(f"{e}")
                        logger.error(e)

                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state["show_ingestion_confirm"] = False

        except Exception as e:
            st.subheader("Data Cleaning Error")
            st.error(f"{e}")
            logger.error(e)

    except Exception as e:
        st.subheader("File Read Error")
        st.error(f"{e}")
        logger.error(e)
