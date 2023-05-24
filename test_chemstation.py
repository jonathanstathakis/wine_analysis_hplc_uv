"""

"""
import os

from wine_analysis_hplc_uv.chemstation import process_chemstation


def main():
    process_chemstation.chemstation(
        data_lib_path="/Users/jonathan/mres_thesis/wine_analysis_hplc_uv.py/data/cuprac_data",
        db_filepath=os.path.join(os.getcwd(), "test.db"),
        ch_metadata_tblname="test",
        ch_sc_tblname="test",
    )

    return None


if __name__ == "__main__":
    main()
