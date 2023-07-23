"""
A module to contain an ORM based workflow with duckdb and sqlalchemy including table creation, table reflection, insertions, selections, updates, deletions and joins.

TODO:
- [ ] table creation
- [ ] table reflection
- [ ] insertion
- [ ] selection
- [ ] updates
- [ ] deletion
- [ ] joins
"""

from sqlalchemy import (
    create_engine,
    MetaData,
    Sequence,
    Table,
    Column,
    Integer,
    text,
    String,
    ForeignKey,
)

from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase

engine = create_engine("duckdb:///:memory:", echo=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


# Create the defined tables
Base.metadata.create_all(engine)

## Table Reflection


# define some_table
class SomeTable(Base):
    __tablename__ = "some_table"
    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


some_table = Table("some_table", Base.metadata, autoload_with=engine)
# print(repr(some_table))

## Table Insertion

"""
Insert rows into a table by instantiating a new class object of the defined table class with values for each column class object. Source: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#tutorial-inserting-orm

"""
# create entries
squidward = User(name="squidward", fullname="Squidward Tentacles")
krabs = User(name="krabs", fullname="Eugene H. Krabs")

# create a session
from sqlalchemy.orm import Session

session = Session(engine)
session.add(squidward)
session.add(krabs)
# print("session currently contains:\n", session.new)

## Selection from Identity Map

some_squidward = session.get(User, 1)

# add the entries to the db
session.commit()
print(squidward.id)

## Delete entry

patrick = User(name="patrick", fullname="Patrick Star")
session.add(patrick)
session.commit()
print(patrick.id)
some_patrick = session.get(User, 3)
print(some_patrick)

session.delete(patrick)

# see if deletion worked
from sqlalchemy import select

session.execute(select(User).where(User.name == "patrick")).first()
print(patrick in session)

import pandas as pd

df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

df.to_sql("df_table", con=engine, if_exists="replace")

test_tbl = Table("test_tbl")
# pd.read_sql_table('df_table', con=engine)
