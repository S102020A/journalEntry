import pandas as pd
import snowflake.connector
import streamlit as st
import sqlite3


def clean_data(raw: pd.DataFrame):
    df = raw.copy()

    # make column names spaces to _ and uppercase
    df.columns = df.columns.str.replace(" ", "_").str.upper()

    # convert nans to none
    df = df.map(lambda value: None if pd.isna(value) else value)

    # create a single RAD_DATA column to encapuslate an optional array of rad data
    cols_to_scope = []

    for col_name in df.columns:
        if "RAD" in col_name:
            cols_to_scope.append(col_name)

    list_of_dicts = df.to_dict(orient="records")

    for row in list_of_dicts:
        keys_to_remove = []
        rad_data = []

        for col_name in row.keys():
            if "RAD" in col_name:
                keys_to_remove.append(col_name)
                is_rad_id_value = row[col_name]

                # check if RAD value exists
                if is_rad_id_value:
                    rad_type_id = col_name.replace("_RAD", "")
                    rad_id = row[col_name]
                    rad_slice = {"RAD_TYPE_ID": rad_type_id, "RAD_ID": rad_id}
                    rad_data.append(rad_slice)

        row["RAD_DATA"] = rad_data
        for key_to_remove in keys_to_remove:
            # Check if the key still exists before deleting
            if key_to_remove in row:
                del row[key_to_remove]

    clean = pd.DataFrame(list_of_dicts)

    return clean


def insert_data(data_to_insert: list[dict]):
    """Inserts data into the specified Snowflake table."""
    try:
        table_name = "MANUAL_JOURNAL_ENTRY_TRANSACTION"
        # conn = snowflake.connector.connect(
        #     user=st.secrets["snowflake"]["user"],
        #     account=st.secrets["snowflake"]["account"],
        #     authenticator=st.secrets["snowflake"]["authenticator"],
        #     warehouse=st.secrets["snowflake"]["warehouse"],
        #     database=st.secrets["snowflake"]["database"],
        #     schema=st.secrets["snowflake"]["schema"],
        #     role=st.secrets["snowflake"]["role"],
        # )
        conn = sqlite3.connect("test_data/main.db")

        with conn.cursor() as cur:
            columns = ", ".join(data_to_insert.keys())
            placeholders = ", ".join(["%s"] * len(data_to_insert))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            values = tuple(data_to_insert.values())
            cur.execute(query, values)
            conn.commit()
            st.success(f"Data successfully inserted into table: {table_name}")
    except snowflake.connector.errors.ProgrammingError as e:
        st.error(f"Error inserting data into {table_name}: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
