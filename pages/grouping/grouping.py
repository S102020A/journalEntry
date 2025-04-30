import streamlit as st
import pandas as pd
import json
from utils.ag_grid import *
from utils.db_manager import get_connection
from pages.grouping.utils import *

# instructions container
with st.container():
    st.markdown("<h1 style=" ">📃 Instructions</h1>", unsafe_allow_html=True)
    instructions = """
        There are three types of groupings that can be created: Account, Business Unit, and Report.

        Both Account and Business Unit groupings perform validation to ensure that all of 
        their respective child components are included. For example, if a grouping is missing a required 
        component like the CASH account, a warning will be generated.

        Despite these warnings, incomplete groupings may still be saved to the database.
    """
    st.write(instructions)

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


# create a container for database management console
with st.container():
    st.markdown("<h1>📎 Data Management Console</h1>", unsafe_allow_html=True)

    # main management console
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
                    SELECT id, name, grouping::TEXT, dimension, created_by
                    FROM finance.grouping
                    WHERE is_active = TRUE
                    ORDER BY created_at DESC;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        raw_data = pd.DataFrame(data, columns=columns)
        grid_response = get_ag_grid_instance(raw_data)

        selected = grid_response["selected_rows"]
        if selected is not None:
            row = selected.to_dict("records")[0]

            read_json = json.loads(row["grouping"])
            read_json_str = json.dumps(read_json, indent=4, sort_keys=False)
            name = row["name"]
            st.download_button(
                label=f'📥 Download "{name}" json grouping',
                data=read_json_str,
                file_name=f"{name}.json",
                mime="json",
                key="readDownloadBtn",
            )

            create, view, update, delete = st.tabs(
                ["🆕 Create", "👁️ View", "✏️ Update", "🗑️ Delete"]
            )

            with create:
                with st.form("createForm"):
                    st.write("Insert New Grouping")

                    name = st.text_input("Name of Grouping")
                    created_by = st.text_input("Created By")
                    dimension = st.selectbox(
                        "Select dimension",
                        options=["account", "business_unit", "report"],
                    )
                    uploaded_json_file = st.file_uploader(
                        label="Json uploader", type="json"
                    )
                    submitted = st.form_submit_button("Submit")

                    if submitted and validate_form(
                        name, created_by, dimension, uploaded_json_file
                    ):
                        parsed_json = json.load(uploaded_json_file)
                        json_str = json.dumps(parsed_json)
                        cursor.execute(
                            """
                                INSERT INTO finance.grouping (name, dimension, grouping, created_by) VALUES (%s, %s, %s, %s)
                            """,
                            (name, dimension, json_str, created_by),
                        )
                        conn.commit()

                        st.success("Grouping successfully inserted into the database!")
                        st.rerun()

            with view:
                with st.expander("Click to expand json"):
                    st.code(read_json_str, language="json")

            with update:
                with st.form("updateForm"):

                    st.write(f"Update {name} Grouping")

                    name = st.text_input("Name of Grouping", value=row["name"])
                    created_by = st.text_input("Created By", value=row["created_by"])
                    picklist = {"account": 1, "business_unit": 2, "report": 3}
                    options = list(picklist.keys())
                    default_index = (
                        options.index(row["dimension"])
                        if row["dimension"] in options
                        else 0
                    )
                    dimension = st.selectbox(
                        "Select dimension", options=options, index=default_index
                    )
                    uploaded_json_file = st.file_uploader(
                        label=f"Json uploader for {row['name']}", type="json"
                    )
                    submitted = st.form_submit_button("Submit")

                    if submitted and validate_form(
                        name, created_by, dimension, uploaded_json_file
                    ):
                        parsed_json = json.load(uploaded_json_file)
                        json_str = json.dumps(parsed_json)
                        update_query = """
                            UPDATE finance.grouping
                            SET name = %s, dimension = %s, grouping = %s, created_by = %s
                            WHERE id = %s;
                        """

                        cursor.execute(
                            update_query,
                            (
                                name,
                                dimension,
                                json_str,
                                created_by,
                                row["id"],
                            ),
                        )
                        conn.commit()

                        st.success("Grouping successfully updated into the database!")
                        st.rerun()

            with delete:
                with st.expander("⚠️ Confirm Deletion"):
                    confirm = st.checkbox(f"Yes, delete row with ID {row['id']}")

                    if confirm:
                        if st.button("🗑️ Delete Now"):
                            cursor.execute(
                                "UPDATE finance.grouping SET is_active = FALSE WHERE id = %s;",
                                (row["id"],),
                            )
                            conn.commit()
                            st.success(f"Soft-deleted row with ID {row['id']}")
                            st.rerun()

    except Exception as error:
        st.error(error)
