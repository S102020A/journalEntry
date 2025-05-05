import streamlit as st
import pandas as pd
from app import logger

st.title("📥 Trial Balance Upload")

# Upload file
uploaded_file = st.file_uploader(
    "Upload your Trial Balance (.csv only)", type=["csv"], key="fbkjsdhjfh"
)

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        logger.info(f"Trial Balance file '{uploaded_file.name}' uploaded successfully.")

        # Basic preview
        st.success("File uploaded successfully! Here's a preview:")
        st.dataframe(df)

        # Optional: validate expected columns
        expected_columns = {"Account", "Description", "Debit", "Credit"}
        if not expected_columns.issubset(df.columns):
            st.warning(
                f"Missing expected columns. Expected at least: {expected_columns}"
            )
            logger.warning(
                f"Uploaded file is missing some expected columns: {df.columns.tolist()}"
            )

    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        logger.error(f"Failed to read uploaded file: {e}")
else:
    st.info("Please upload a CSV file to proceed.")
