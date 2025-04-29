import streamlit as st
import pandas as pd
import json
from utils.ag_grid import *
from utils.db_manager import get_connection
from pages.grouping.utils import *

# Connect to the database
conn = get_connection()
cursor = conn.cursor()

with st.container():
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

    create, read, update, delete = st.tabs(
        ["✍️ Create", "📖 Read", "✏️ Update", "🗑️ Delete"]
    )

with create:
    try:
        with st.form("New Grouping"):
            st.write("Insert New Grouping")

            group_name = st.text_input("Name of Grouping")
            created_by = st.text_input("Created By")
            dimension = st.selectbox(
                "Select dimension", options=["account", "business_unit"]
            )
            uploaded_json_file = st.file_uploader(label="Json uploader", type="json")
            submitted = st.form_submit_button("Submit")

            if submitted and validate_form(
                group_name, created_by, dimension, uploaded_json_file
            ):
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
    except Exception as error:
        st.error(error)

with read:
    try:
        query = """
                SELECT id, name, grouping::TEXT, dimension, created_by
                FROM finance.grouping
                ORDER BY created_at DESC;
            """
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        raw_data = pd.DataFrame(data, columns=columns)
        grid_response = get_read_ag_grid(raw_data)
    except Exception as error:
        st.error(error)

with update:
    try:
        query = """
                SELECT id, name, dimension, created_by
                FROM finance.grouping
                ORDER BY created_at DESC;
            """
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        raw_data = pd.DataFrame(data, columns=columns)
        grid_response = get_update_ag_grid(raw_data)

        # obtain in a fram the updated dataframe
        updated_data = pd.DataFrame(grid_response["data"]).reset_index(drop=True)
        original_data = raw_data.reset_index(drop=True)

        if not updated_data.equals(original_data):
            changes = updated_data.compare(
                original_data, keep_shape=True, keep_equal=True
            )
            modified_indices = changes.dropna(how="all").index.tolist()

            if modified_indices:
                st.success(f"Updating {len(modified_indices)} modified row(s)...")

                for i in modified_indices:
                    update_row_in_database(updated_data.loc[i].to_dict())

                st.info("Data updated in DB. Refreshing...")
                st.rerun()
    except Exception as error:
        st.error(error)

with delete:
    try:
        # Fetch data
        query = """
            SELECT id, name, grouping::TEXT, dimension, created_by
            FROM finance.grouping
            ORDER BY created_at DESC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        raw_data = pd.DataFrame(data, columns=columns)

        # instantiate the grid
        grid_response = get_delete_ag_grid(raw_data)

        # Check if a row is selected
        selected = grid_response["selected_rows"]
        if selected is not None:
            selected_id = int(selected.iloc[0]["id"])
            if st.button(f"Delete Selected ID {selected_id}"):
                cursor.execute(
                    "DELETE FROM finance.grouping WHERE id = %s;", (selected_id,)
                )
                conn.commit()
                st.success(f"Deleted row with ID {selected_id}")
                st.rerun()
    except Exception as error:
        st.error(error)
