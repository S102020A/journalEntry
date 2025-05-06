from pydantic import BaseModel
from utils.db_manager import get_connection
import json
import psycopg2
import pandas as pd
import streamlit as st
from datetime import date
from constants.constants import (
    ManualJournalEntryTransaction,
    ManualBudget,
)


def convert_date_cols(model: BaseModel, df: pd.DataFrame) -> pd.DataFrame:
    for field_name, field in model.__pydantic_fields__.items():

        field_type = field.annotation

        if field_type is date:
            try:
                df[field_name] = pd.to_datetime(
                    df[field_name], format="%m/%d/%Y"
                ).dt.date
            except Exception as e:
                print(f"Error converting column '{field_name}' to datetime: {e}")
                raise Exception()
    return df


def validate_column_names(column_names: list[str], model: BaseModel) -> dict:
    columns = list(model.__pydantic_fields__.keys())
    missing_from_df = [col for col in columns if col not in column_names]

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
        model = ManualJournalEntryTransaction
    elif table_name == "MANUAL_BUDGET":
        model = ManualBudget
    else:
        st.error(f"Unknown table name: {table_name}.  Cannot validate columns.")
        st.stop()

    # make column names spaces to _ and uppercase
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(".", "")
        .str.lower()
    )

    # validate columns
    validate_column_names(column_names=df.columns.to_list(), model=model)

    # convert date columns to pd.date
    df = convert_date_cols(df=df, model=model)

    # convert nans to none
    df = df.map(lambda value: None if pd.isna(value) else value)

    # map amount values to a decimal numeric
    df["amount"] = (
        df["amount"]
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
            if "rad" in col_name:
                keys_to_remove.append(col_name)
                is_rad_id_value = row[col_name]

                # check if RAD value exists
                if is_rad_id_value:
                    rad_type_id = col_name.replace("_rad", "")
                    rad_id = row[col_name]
                    rad_slice = {"rad_type_id": rad_type_id, "rad_id": rad_id}
                    rad_data.append(rad_slice)

        # encode to json object or none if arr is empty
        if len(rad_data) != 0:
            row["rad_data"] = json.dumps(rad_data, allow_nan=False)
        else:
            row["rad_data"] = None

        # finally remove the RAD columns before insertion
        for key_to_remove in keys_to_remove:
            if key_to_remove in row:
                del row[key_to_remove]

    clean = pd.DataFrame(list_of_dicts)

    return clean


def drop_conditional_rows_from_accounting_date(clean_data_df: pd.DataFrame) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    # create two seperate sql drop statements for each table
    minimum_accounting_date = clean_data_df["accounting_date"].min()
    sql = f"delete from finance.{st.session_state["table_name"]} where accounting_date >= %s"

    try:
        cursor.execute(sql, (minimum_accounting_date,))
        rows_dropped = cursor.rowcount
        conn.commit()

        return_message = f"💧 {rows_dropped} rows dropped."
        return return_message
    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"While dropping data from minimum date an error occured: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_data(data_to_insert: list[dict]) -> str:
    """Inserts a single row of data into the SQLite table."""
    rows_inserted = 0
    success_placeholder = st.empty()

    try:
        conn = get_connection()

        cursor = conn.cursor()
        for row in data_to_insert:
            columns = ", ".join([f'"{col}"' for col in row.keys()])
            placeholders = ", ".join(["%s"] * len(row))
            query = f'INSERT INTO FINANCE.{st.session_state["table_name"]} ({columns}) VALUES ({placeholders})'
            values = tuple(row.values())

            try:
                cursor.execute(query, values)
                success_placeholder.success(
                    f"Successfully inserted row {rows_inserted}"
                )
                rows_inserted += 1
            except Exception as e:
                raise e

        success_placeholder.empty()
        conn.commit()

        return_message = (
            f"📥 {rows_inserted} rows/s inserted into {st.session_state["table_name"]}"
        )
        return return_message

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


def show_head_from_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = f'select * from finance.{st.session_state["table_name"]} order by id limit 5;'
        cursor.execute(query)

        # cast the results into a dataframe
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
        conn.commit()
        return df
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise Exception(
            f"Error fetching top data from {st.session_state["table_name"]}: {e}"
        )
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
