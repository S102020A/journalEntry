import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

custom_css = {
    ".ag-root": {"background-color": "#0e1117"},
    ".ag-header": {"background-color": "#0e1117"},
    ".ag-cell": {"background-color": "#0e1117"},
    ".ag-row": {"background-color": "#0e1117"},
}


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
        custom_css=custom_css,
    )

    return grid_response


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
        custom_css=custom_css,
    )

    return grid_response


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
        custom_css=custom_css,
    )

    return grid_response
