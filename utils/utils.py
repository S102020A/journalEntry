import pandas as pd
import snowflake.connector
import streamlit as st


def clean_data(raw: pd.DataFrame):
    df = raw.copy()
    df.columns = df.columns.str.replace(" ", "_").str.upper()

    def nan_to_none(value):
        if pd.isna(value):
            return None
        return value

    df = df.applymap(nan_to_none)

    # create a simple unqiue id
    df["ROW_ID"] = (
        df["ENTRY_ID"].astype(str)
        + "_"
        + df["ENTRY_DETAIL_ID"].astype(str)
        + "_"
        + df["SEQNO"].astype(str)
    )

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
            if key_to_remove in row:  # Check if the key still exists before deleting
                del row[key_to_remove]

    clean = pd.DataFrame(list_of_dicts)

    return clean


def insert_data(data_to_insert: list[dict]):
    """Inserts data into the specified Snowflake table."""
    try:
        table_name = "MANUAL_JOURNAL_ENTRY_TRANSACTION"
        conn = snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            account=st.secrets["snowflake"]["account"],
            authenticator=st.secrets["snowflake"]["authenticator"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            role=st.secrets["snowflake"]["role"],
        )
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
