import streamlit as st
from utils.db_manager import get_connection


def find_leaf_nodes(obj):
    leaves = []
    if isinstance(obj, dict):
        for value in obj.values():
            leaves.extend(find_leaf_nodes(value))
    elif isinstance(obj, list):
        for item in obj:
            leaves.extend(find_leaf_nodes(item))
    else:
        leaves.append(obj)
    return leaves


def validate_form(group_name, created_by, dimension, uploaded_json_file):
    conn = get_connection()
    cursor = conn.cursor()

    if not group_name:
        st.error("Please enter a name for the grouping.")
        return False
    if not dimension:
        st.error("Please select a dimension.")
        return False
    if uploaded_json_file is None:
        st.error("Please upload a JSON file.")
        return False
    if not created_by:
        st.error("Please enter who you are.")
        return False

    cursor.execute("SELECT * FROM finance.grouping WHERE name = %s", (group_name,))
    if cursor.fetchone():
        st.error(f"Group name {group_name} already exists")
        return False

    cursor.execute("SELECT * FROM finance.grouping WHERE name = %s", (group_name,))
    if cursor.fetchone():
        st.error(f"Group name {group_name} already exists")
        return False

    return True


def update_row_in_database(row: dict):
    conn = get_connection()
    cursor = conn.cursor()

    update_query = """
        UPDATE finance.grouping
        SET name = %s, dimension = %s, created_by = %s
        WHERE id = %s;
    """
    cursor.execute(
        update_query,
        (row["name"], row["dimension"], row["created_by"], row["id"]),
    )
    conn.commit()
