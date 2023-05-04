import duckdb as db
def test_spectra_df():
    con = db.connect('wine_auth_db.db')

    query_1 = """
    SELECT A.*,
        sub_query.name_ct
    FROM
        spectrums A
    JOIN (
        SELECT
            hash_key,
            name_ct
        FROM
            super_table
        LIMIT
        1    
    ) sub_query
    ON
        A.hash_key = sub_query.hash_key;
    """

    return con.sql(query_1).df()