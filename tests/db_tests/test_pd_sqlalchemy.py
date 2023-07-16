from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, Integer, Column, Sequence
from sqlalchemy import String
from sqlalchemy import create_engine, text
import pandas as pd


class Base(DeclarativeBase):
    pass


class TestTbl1(Base):
    __tablename__ = "test_table_1"
    pkey = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    col2: Mapped[str] = mapped_column(String)
    forkey: Mapped[int] = mapped_column(Integer, ForeignKey("test_table_2.pkey"))


class TestTbl2(Base):
    __tablename__ = "test_table_2"
    pkey = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    col3: Mapped[str] = mapped_column(String)
    forkey: Mapped[int] = mapped_column(Integer, ForeignKey("test_table_1.pkey"))


engine = create_engine("duckdb:///:memory:", echo=False)

Base.metadata.create_all(engine)

df1 = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
df2 = pd.DataFrame({"col1": [1, 2, 3], "col3": ["g", "h", "i"]})

from sqlalchemy.types import Integer, String

tbl1_name = "tbl_1"
tbl2_name = "tbl_2"

df_schema = {"col1": Integer, "col2": String(64)}

df1.to_sql(tbl1_name, con=engine, if_exists="replace", index=False)
df2.to_sql(tbl2_name, con=engine, if_exists="replace", index=False)

from sqlalchemy import inspect, Table, select

inspector = inspect(engine)

assert tbl1_name and tbl2_name in inspector.get_table_names()

# join the tables

tbl1 = Table(tbl1_name, Base.metadata, autoload_with=engine)
tbl2 = Table(tbl2_name, Base.metadata, autoload_with=engine)

join_tbl = tbl1.join(tbl2, onclause=tbl1.c.col1 == tbl2.c.col1)

stmt = select("*").select_from(join_tbl)

join_df = pd.read_sql(stmt, engine)

print(join_df)

from sqlalchemy import inspect


def describe_table(engine, table_name):
    inspector = inspect(engine)
    for column in inspector.get_columns(table_name):
        print("Column: %s" % column["name"])
        print("Type: %s" % column["type"])
        print("Nullable: %s" % column["nullable"])
        print("Default: %s" % column["default"])
        print()
