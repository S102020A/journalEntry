import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

AGGRID_CSS = {
    ".ag-root": {"background-color": "#030326", "color": "#FDFDFC"},
    ".ag-header": {"background-color": "#030326", "color": "#FDFDFC"},
    ".ag-cell": {"background-color": "#030326", "color": "#FDFDFC"},
    ".ag-row": {"background-color": "#030326", "color": "#FDFDFC"},
    ".ag-paging-panel": {"background-color": "#030326", "color": "#FDFDFC"},
}


def get_ag_grid_instance(raw_data: pd.DataFrame) -> AgGrid:
    # Build grid options
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
        custom_css=AGGRID_CSS,
    )

    return grid_response
