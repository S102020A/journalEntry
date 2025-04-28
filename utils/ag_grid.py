import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def inject_aggrid_styles(func):
    def wrapper(*args, **kwargs):
        st.markdown(
            """
            <style>
                <style>
                /* Override the inherited background at the highest level */
                .ag-root {
                    --ag-inherited-background-color: #0e1117 !important; /* Dark theme background */
                }

                /* Extra: Force all parts of the table to respect the background */
                .ag-root,
                .ag-header,
                .ag-row,
                .ag-cell {
                    background-color: var(--ag-inherited-background-color) !important;
                }
                </style>

            </style>
            """,
            unsafe_allow_html=True,
        )
        return func(*args, **kwargs)

    return wrapper


@inject_aggrid_styles
def get_delete_ag_grid(raw_data: pd.DataFrame):
    # Build grid options
    raw_data.columns = raw_data.columns.str.upper()
    gb = GridOptionsBuilder.from_dataframe(raw_data)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_pagination(enabled=True, paginationAutoPageSize=10)
    gb.configure_default_column(filter=True)
    grid_options = gb.build()

    # Display interactive grid
    grid_response = AgGrid(
        data=raw_data,
        gridOptions=grid_options,
        height=400,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
    )

    return grid_response


@inject_aggrid_styles
def get_update_ag_grid(raw_data: pd.DataFrame):
    # Build grid options
    raw_data.columns = raw_data.columns.str.upper()
    gb = GridOptionsBuilder.from_dataframe(raw_data)
    gb.configure_pagination(enabled=True, paginationAutoPageSize=10)
    gb.configure_default_column(filter=True, editable=True)
    gb.configure_column("ID", editable=False)
    grid_options = gb.build()

    # Display interactive grid
    grid_response = AgGrid(
        data=raw_data,
        gridOptions=grid_options,
        height=400,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
    )

    return grid_response


@inject_aggrid_styles
def get_read_ag_grid(raw_data: pd.DataFrame):
    # Build grid options
    raw_data.columns = raw_data.columns.str.upper()
    gb = GridOptionsBuilder.from_dataframe(raw_data)
    gb.configure_pagination(enabled=True, paginationAutoPageSize=10)
    gb.configure_default_column(editable=False)
    grid_options = gb.build()

    # Display interactive grid
    grid_response = AgGrid(
        data=raw_data,
        gridOptions=grid_options,
        height=400,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
    )

    return grid_response
