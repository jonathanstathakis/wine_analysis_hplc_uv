import os
from wine_analysis_hplc_uv.definitions import (
    DB_PATH,
    LIB_DIR,
    CH_META_TBL_NAME,
    CH_DATA_TBL_NAME,
)
from wine_analysis_hplc_uv.chemstation import chemstationprocessor, logger


def ch_to_db(lib_path: str, mtadata_tbl: str, sc_tbl: str, con: str):
    assert os.path.exists(lib_path)
    ch = chemstationprocessor.ChemstationProcessor(lib_path=lib_path)
    ch.to_db(con=con, ch_metadata_tblname=mtadata_tbl, ch_sc_tblname=sc_tbl)
    return None


def main():
    lib_path = LIB_DIR
    db_path = DB_PATH
    metadata_tbl = CH_META_TBL_NAME
    sc_tbl = CH_DATA_TBL_NAME
    ch_to_db(lib_path, mtadata_tbl=metadata_tbl, sc_tbl=sc_tbl, con=con)


if __name__ == "__main__":
    main()
