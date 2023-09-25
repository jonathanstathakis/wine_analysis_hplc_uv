import duckdb as db
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.db_methods import pivot_wine_data, get_data


def gd():
    con = db.connect(definitions.DB_PATH)
    get_data.get_wine_data(
        con, detection=("cuprac",), wavelength=("450",), varietal=("shiraz",)
    )
    df = pivot_wine_data.pivot_wine_data(con)
    return df
