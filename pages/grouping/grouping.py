import streamlit as st
import pandas as pd
import json
from utils.db_manager import get_connection
from pages.grouping.utils import *

# Connect to the database
conn = get_connection()
cursor = conn.cursor()

# have a template to look and feel the data
template_data = {
    "ALL_ACCOUNTS": [{"ASSETS": ["NEW_ACCOUNT"]}, "TOTAL_LIABILITIES", "NET ASSETS"]
}

json_string = json.dumps(template_data, indent=4, sort_keys=False)

st.download_button(
    label="Download JSON Template",
    data=json_string,
    file_name="template.json",
    mime="json",
)

st.code(json_string, language="json")


create, read, update, delete = st.tabs(["✍️ Create", "📖 Read", "✏️ Update", "🗑️ Delete"])


with create:
    with st.form("New Grouping"):
        st.write("Insert New Grouping")

        group_name = st.text_input("Name of Grouping")
        created_by = st.text_input("Created By")
        dimension = st.selectbox(
            "Select dimension", options=["account", "business_unit", "rad"]
        )
        uploaded_json_file = st.file_uploader(label="Json uploader", type="json")
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not group_name:
                st.error("Please enter a name for the grouping.")
            elif not dimension:
                st.error("Please select a dimension.")
            elif uploaded_json_file is None:
                st.error("Please upload a JSON file.")
            elif not created_by:
                st.error("Please enter who you are.")
            else:
                parsed_json = json.load(uploaded_json_file)
                json_str = json.dumps(parsed_json)
                cursor.execute(
                    """
                    INSERT INTO finance.grouping (name, dimension, grouping, created_by) VALUES (%s, %s, %s, %s)
                """,
                    (group_name, dimension, json_str, created_by),
                )
                conn.commit()

                st.success("Grouping successfully inserted into the database!")

with read:
    cursor.execute("SELECT * FROM finance.grouping ORDER BY created_at DESC;")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    raw_data = pd.DataFrame(data, columns=columns)
    st.dataframe(raw_data, use_container_width=True)

with update:
    pass

with delete:
    pass
