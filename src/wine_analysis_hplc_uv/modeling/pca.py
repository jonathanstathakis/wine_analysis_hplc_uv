"""

"""

import duckdb as db
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv import definitions


def get_sc_rel(con):
    return db_methods.get_sc_rel(con)
