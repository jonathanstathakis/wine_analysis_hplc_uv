from wine_analysis_hplc_uv.etl.build_library.sampletracker.st_cleaner import STCleaner
from wine_analysis_hplc_uv import definitions
import duckdb as db
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


def clean_st_to_db(con):
    st_cleaner = STCleaner()
    st_cleaner.clean_st(con.sql(f"select * from {definitions.Raw_tbls.ST}").df())
    st_cleaner.to_db(con=con, tbl_name=definitions.Clean_tbls.ST)


def main():
    con = db.connect(definitions.DB_PATH)
    clean_st_to_db(con)


if __name__ == "__main__":
    main()
