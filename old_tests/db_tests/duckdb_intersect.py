"""
Examine the behavior of duckdb.DuckDBPyRelation.intersect for comparing column contents.
"""

import pandas as pd
import duckdb as db

df1 = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
df2 = pd.DataFrame({"col1": [1, 2, 5], "col3": ["g", "h", "i"]})

with db.connect() as con:
    rel1 = con.from_df(df1)["col1"]
    rel2 = con.from_df(df2)["col1"]
    rel1.intersect(rel2).show()
