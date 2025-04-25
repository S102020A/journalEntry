import streamlit as st
import yaml
from utils.db_manager import get_connection

# Connect to the database
conn = get_connection()
cursor = conn.cursor()

# Query for dropdown options
cursor.execute("SELECT id, name FROM finance.grouping ORDER BY created_at DESC;")
results = cursor.fetchall()

template_data = {
    "ALL_ACCOUNTS": [
        {"ASSETS": ["NEW_ACCOUNT_GROUPING"]},
        "TOTAL_LIABILITIES",
        "NET ASSETS",
    ]
}


yaml_string = yaml.dump(template_data, sort_keys=False)

st.download_button(
    label="Download YAML Template",
    data=yaml_string,
    file_name="template.yaml",
    mime="text/yaml",
)

st.code(yaml_string, language="yaml")

with st.form("New Grouping"):
    st.write("Inside form")

    group_name = st.text_input("Name of Grouping")
    dimension = st.selectbox(
        "Select dimension", options=["account", "business_unit", "rad"]
    )
    uploaded_file = st.file_uploader(label="Json uploader", type="json")

    submitted = st.form_submit_button("Submit")

    if submitted:
        st.write("Form submitted!")
        st.write("Group Name:", group_name)
        st.write("Dimension:", dimension)
        if uploaded_file is not None:
            st.write("Uploaded File Name:", uploaded_file.name)
        else:
            st.write("No file uploaded.")
