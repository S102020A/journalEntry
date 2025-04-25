import streamlit as st
from utils.db_manager import get_connection

# Connect to the database
conn = get_connection()
cursor = conn.cursor()

# Query for dropdown options
cursor.execute("SELECT id, name FROM finance.grouping ORDER BY created_at DESC;")
results = cursor.fetchall()

# Start form
with st.form("category_form"):
    st.subheader("Select or Create Category")

    if results:
        # Create a dictionary of id: name pairs
        options = {row[0]: row[1] for row in results}

        selected_id = st.selectbox(
            "Choose a category:",
            options.keys(),
            format_func=lambda x: options[x],
        )
    else:
        st.selectbox("Choose a category:", ["No categories available"], disabled=True)
        selected_id = None

    # Allow user to create a new category
    new_category = st.text_input("Or create a new category:")

    # Submit button
    submitted = st.form_submit_button("Submit")

    if submitted:
        if new_category:
            # Insert new category into the database
            cursor.execute(
                "INSERT INTO finance.grouping (name) VALUES (%s) RETURNING id;",
                (new_category,),
            )
            conn.commit()
            new_id = cursor.fetchone()[0]
            st.success(f"New category '{new_category}' created with ID {new_id}")
        elif selected_id:
            st.success(
                f"Selected Category ID: {selected_id}, Name: {options[selected_id]}"
            )
        else:
            st.warning("Please select or create a category.")
