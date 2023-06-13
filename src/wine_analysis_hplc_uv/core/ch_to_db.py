from wine_analysis_hplc_uv.definitions import DB_DIR, LIB_DIR

from wine_analysis_hplc_uv.chemstation import (
    ch_metadata_tbl_cleaner,
    chemstationprocessor,
)

# chemstation


def ch_to_db(lib_path: str, mtadata_tbl: str, sc_tbl: str, db_path: str):
    ch = chemstationprocessor.ChemstationProcessor(lib_path=lib_path)
    ch.to_db(db_filepath=db_path, ch_metadata_tblname=mtadata_tbl, ch_sc_tblname=sc_tbl)
    return None


def main():
    lib_path = LIB_DIR
    db_path = DB_DIR
    metadata_tbl = "chemstation_metadata"
    sc_tbl = "sample_tracker"
    ch_to_db(lib_path, mtadata_tbl=metadata_tbl, sc_tbl=sc_tbl, db_path=db_path)


if __name__ == "__main__":
    main()
