import os
import duckdb as db

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.etl.build_library.chemstation import chemstationprocessor


def ch_to_db(lib_path: str, mtadata_tbl: str, sc_tbl: str, con: str):
    assert os.path.exists(lib_path)
    ch = chemstationprocessor.ChemstationProcessor(lib_path=lib_path)
    ch.to_db(con=con, ch_metadata_tblname=mtadata_tbl, ch_sc_tblname=sc_tbl)
    return None


def main():
    lib_path = definitions.LIB_DIR
    db_path = definitions.DB_PATH
    metadata_tbl = definitions.Raw_tbls.CH_META
    sc_tbl = definitions.Raw_tbls.CH_DATA
    con = db.connect(db_path)
    ch_to_db(lib_path, mtadata_tbl=metadata_tbl, sc_tbl=sc_tbl, con=con)


if __name__ == "__main__":
    main()
