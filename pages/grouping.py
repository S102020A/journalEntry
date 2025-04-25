import streamlit as st
import streamlit as st
import pandas as pd

# Initialize a DataFrame in session state if it doesn't exist
if "editable_df" not in st.session_state:
    st.session_state["editable_df"] = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6], "col3": ["a", "b", "c"]}
    )


def handle_data_change():
    """This function is called when a cell in the data editor is changed."""
    edited_data = st.session_state["editable_df"]
    st.write("DataFrame after edit:")
    st.dataframe(edited_data)

    # You can perform actions based on the edited data here
    # For example, calculate a new column:
    try:
        edited_data["sum"] = edited_data["col1"] + edited_data["col2"]
        st.write("DataFrame with sum:")
        st.dataframe(edited_data)
    except TypeError:
        st.warning("Cannot calculate sum because non-numeric values were entered.")


st.title("Interactive DataFrame Editor")

edited_df = st.data_editor(
    st.session_state["editable_df"],
    num_rows="dynamic",
    on_change=handle_data_change,
    key="data_editor",
)

# Update the session state with the edited DataFrame
st.session_state["editable_df"] = edited_df

st.write("Original DataFrame (stored in session state):")
st.dataframe(st.session_state["editable_df"])
