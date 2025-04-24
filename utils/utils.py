import pandas as pd
import snowflake.connector
import streamlit as st
import sqlite3
from datetime import date


def clean_data(raw: pd.DataFrame):
    df = raw.copy()

    # make column names spaces to _ and uppercase
    df.columns = df.columns.str.replace(" ", "_").str.replace("-", "_").str.upper()

    # convert nans to none
    df = df.map(lambda value: None if pd.isna(value) else value)

    # map amount values to a decimal numeric
    df["AMOUNT"] = (
        df["AMOUNT"]
        .astype(str)
        .map(lambda value: pd.to_numeric(str(value).replace(",", "")))
        .map("{:.2f}".format)
    )

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

        # if list is empty make the value none
        rad_data = rad_data if len(rad_data) != 0 else None
        row["RAD_DATA"] = str(rad_data)

        for key_to_remove in keys_to_remove:
            # Check if the key still exists before deleting
            if key_to_remove in row:
                del row[key_to_remove]

    clean = pd.DataFrame(list_of_dicts)

    return clean


def drop_data_from_minimum_date_created(df: pd.DataFrame) -> None:
    """
    Deletes all rows from the MANUAL_JOURNAL_ENTRY_TRANSACTION table
    where the DATE_CREATED is greater than or equal to the provided date.

    Args:
        min_date_created: The minimum date (inclusive) from which to drop data.
    """
    clean_data_copy = df.copy()
    clean_data_copy["DATE_CREATED"] = pd.to_datetime(
        clean_data_copy["DATE_CREATED"], format="%m/%d/%Y"
    ).dt.date
    min_date = clean_data_copy["DATE_CREATED"].min()
    min_date_str = min_date.strftime("%m/%d/%Y")
    conn = sqlite3.connect("test_data/main.db")
    cursor = conn.cursor()

    try:
        sql = "DELETE FROM MANUAL_JOURNAL_ENTRY_TRANSACTION WHERE DATE_CREATED >= ?"
        cursor.execute(sql, (min_date_str,))
        rows_deleted = conn.total_changes
        conn.commit()
        st.success(
            f"{rows_deleted} Deleted rows with DATE_CREATED on or after {min_date_str}."
        )
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return rows_deleted


def insert_data(data_to_insert: list[dict]) -> int:
    """Inserts a single row of data into the SQLite table."""
    conn = None  # Initialize conn outside the try block
    cursor = None  # Initialize cursor outside the try block
    rows_inserted = 0

    success_placeholder = st.empty()

    try:
        table_name = "MANUAL_JOURNAL_ENTRY_TRANSACTION"
        conn = sqlite3.connect("test_data/main.db")
        cursor = conn.cursor()

        sql = f"""
            SELECT name
            FROM pragma_table_info('MANUAL_JOURNAL_ENTRY_TRANSACTION')
            WHERE pk = 0 AND dflt_value IS NULL;
        """
        cursor.execute(sql)
        column_names = [col[0] for col in cursor.fetchall()]

        cleaned_data = []
        for row in data_to_insert:
            cleaned_row = {}
            for col_name in column_names:
                if col_name in row:
                    cleaned_row[col_name] = row[col_name]
            cleaned_data.append(cleaned_row)

        for row in cleaned_data:
            columns = ", ".join(row.keys())
            placeholders = ", ".join(["?"] * len(row))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            values = tuple(row.values())

            try:
                cursor.execute(query, values)
                success_placeholder.success(
                    f"Successfully inserted row: {', '.join([f'{k}: {v}' for k, v in row.items()])}"
                )
            except Exception as e:
                raise e

        success_placeholder.empty()
        rows_inserted = conn.total_changes
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error inserting data into {table_name}: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return rows_inserted
