from wine_analysis_hplc_uv import definitions
import duckdb as db

with open(
    "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/xgboost_modeling/test_db_query.sql",
    "r",
) as f:
    q = f.read()

    con = db.connect(definitions.DB_PATH)

    con.sql(q).show()
