from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, Column, Sequence, Table
from sqlalchemy import String
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("duckdb:///:memory:", echo=False)


class Base(DeclarativeBase):
    pass


df1 = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})


class Tbl1(Base):
    __tablename__ = "test_table"
    col1 = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    col2: Mapped[str] = mapped_column(String)


df1.to_sql("tbl1", con=engine, if_exists="replace", index=False)

out_df = pd.read_sql_table("tbl1", con=engine)
print(out_df)
print(out_df.dtypes)

df2 = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

tbl1 = Table("tbl1", Base.metadata, autoload_with=engine)

print(repr(tbl1))
