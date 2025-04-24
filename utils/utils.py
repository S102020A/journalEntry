import toml
import json
import psycopg2
import pandas as pd
import streamlit as st
from constants.constants import (
    MANUAL_JOURNAL_ENTRY_TRANSACTION_COLS,
    MANUAL_BUDGET_COLS,
)


def get_database_credentials(toml_file_path):
    """Reads database credentials from a TOML file.

    Args:
        toml_file_path (str): The path to the TOML file.

    Returns:
        dict: A dictionary containing the database credentials, or None if the
              'postgres' section is not found.
    """
    try:
        with open(toml_file_path, "r") as f:
            config = toml.load(f)
            if "postgres" in config:
                return config["postgres"]
            else:
                print("Error: 'postgres' section not found in the TOML file.")
                return None
    except FileNotFoundError:
        raise Exception(f"Error: File not found at {toml_file_path}")
    except toml.TomlDecodeError as e:
        raise Exception("Error decoding TOML file: {e}")


def convert_date_cols(schema: dict, df: pd.DataFrame) -> pd.DataFrame:
    for col, data_type in schema.items():
        if data_type == "date" and col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col]).dt.date
            except Exception as e:
                print(f"Error converting column '{col}' to datetime: {e}")
                raise Exception()
    return df


def validate_column_names(column_names: list[str], schema: dict) -> dict:
    schema_column_names = list(schema.keys())
    missing_from_df = [col for col in schema_column_names if col not in column_names]

    if missing_from_df:
        error_message = (
            f"Column validation failed for table: {st.session_state["table_name"]}.\n"
        )
        if missing_from_df:
            error_message += f"Missing columns: {"\n".join(missing_from_df)}\n"
        raise Exception(error_message)


def clean_data(raw: pd.DataFrame):
    df = raw.copy()
    table_name = st.session_state["table_name"]

    # check if all columns are provided
    if table_name == "MANUAL_JOURNAL_ENTRY_TRANSACTION":
        schema = MANUAL_JOURNAL_ENTRY_TRANSACTION_COLS
    elif table_name == "MANUAL_BUDGET":
        schema = MANUAL_BUDGET_COLS
    else:
        st.error(f"Unknown table name: {table_name}.  Cannot validate columns.")
        st.stop()

    # make column names spaces to _ and uppercase
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(".", "")
        .str.upper()
    )

    # validate columns
    validate_column_names(column_names=df.columns.to_list(), schema=schema)

    # convert date columns to pd.date
    df = convert_date_cols(df=df, schema=schema)

    # convert nans to none
    df = df.map(lambda value: None if pd.isna(value) else value)

    # map amount values to a decimal numeric
    df["AMOUNT"] = (
        df["AMOUNT"]
        .astype(str)
        .map(lambda value: pd.to_numeric(str(value).replace(",", "")))
        .map("{:.2f}".format)
        .astype(float)
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

        # encode to json object or none if arr is empty
        if len(rad_data) != 0:
            row["RAD_DATA"] = json.dumps(rad_data, allow_nan=False)
        else:
            row["RAD_DATA"] = None

        # finally remove the RAD columns before insertion
        for key_to_remove in keys_to_remove:
            if key_to_remove in row:
                del row[key_to_remove]

    clean = pd.DataFrame(list_of_dicts)

    return clean


def drop_data_from_minimum_date_created(df: pd.DataFrame) -> None:
    clean_data_copy = df.copy()
    min_date = clean_data_copy["ACCOUNTING_DATE"].min()
    credentials = get_database_credentials(".streamlit/secrets.toml")
    conn = psycopg2.connect(**credentials)
    cursor = conn.cursor()

    try:
        sql = f'DELETE FROM FINANCE."{st.session_state["table_name"]}" WHERE "ACCOUNTING_DATE" >= %s'
        cursor.execute(sql, (min_date,))
        rows_deleted = cursor.rowcount
        conn.commit()
        st.success(
            f"{rows_deleted} Deleted rows with DATE_CREATED on or after {min_date}."
        )
    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"While dropping data from minimum date an error occured: {e}")
    finally:
        cursor.close()
        conn.close()
    return rows_deleted


def insert_data(data_to_insert: list[dict]):
    """Inserts a single row of data into the SQLite table."""
    rows_inserted = 1
    success_placeholder = st.empty()

    try:
        credentials = get_database_credentials(".streamlit/secrets.toml")
        conn = psycopg2.connect(**credentials)

        cursor = conn.cursor()
        for row in data_to_insert:
            columns = ", ".join([f'"{col}"' for col in row.keys()])
            placeholders = ", ".join(["%s"] * len(row))
            query = f'INSERT INTO FINANCE."{st.session_state["table_name"]}" ({columns}) VALUES ({placeholders})'
            values = tuple(row.values())

            try:
                cursor.execute(query, values)
                success_placeholder.success(
                    f"Successfully inserted row {rows_inserted}"
                )
                ++rows_inserted
            except Exception as e:
                raise e

        success_placeholder.empty()
        rows_inserted = cursor.rowcount
        conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise Exception(
            f"Error inserting data into {st.session_state["table_name"]}: {e}"
        )
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
