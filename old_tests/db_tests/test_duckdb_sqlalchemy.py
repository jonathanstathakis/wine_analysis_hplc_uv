import pytest
from sqlalchemy import create_engine, text
import duckdb

engine = create_engine("duckdb:///:memory:")

# one method of managing the connection context

with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    conn.execute(text("Create TABLE some_table ( x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x,y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    conn.commit()
    conn.execute(text("SELECT * FROM some_table"))

    print(result.all())

# another method. .begin handles commit and rollback implicitely at the end of the execution statement
# inserting values into placeholders is done in .text as a dictionary of values in the parameters kwarg.
with engine.begin() as conn:
    conn.execute(
        statement=text("INSERT INTO some_table (x, y) VALUES (:x,:y)"),
        parameters=[{"x": 6, "y": 8}, {"x": 9, "y": 10}],
    )

# create a table. The Metadata object serves to represent a collection of tables, best to have 1 per application. Below is a modified implementation of the example given by [SQLAlchemy](https://docs.sqlalchemy.org/en/20/tutorial/metadata.html) provided by [duckdb-engine](https://pypi.org/project/duckdb-engine/#usage). modification is to do with the differences between DuckDB and what SQLAlchemy expects.

from sqlalchemy import (
    create_engine,
    MetaData,
    Sequence,
    Table,
    Column,
    Integer,
    text,
    String,
)

engine = create_engine("duckdb:///:memory:")
metadata_obj = MetaData()
user_id_seq = Sequence("user_id_seq")
users_table = Table(
    "user_account",
    metadata_obj,
    Column(
        "id",
        Integer,
        user_id_seq,
        server_default=user_id_seq.next_value(),
        primary_key=True,
    ),
)

from sqlalchemy import ForeignKey

address_table = Table(
    "address",
    metadata_obj,
    Column(
        "id",
        Integer,
        user_id_seq,
        server_default=user_id_seq.next_value(),
        primary_key=True,
    ),
    # refers to the primary key defined in the first table
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String, nullable=False),
)

# actually insert the tables into the db
# to use with duckdb, defne a duckdb engine

metadata_obj.create_all(engine)

### ORM Example

from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


class SomeTable(Base):
    __tablename__ = "some_table"
    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


# Create the defined tables
Base.metadata.create_all(engine)

## Table Reflection

# define some_table


Base.metadata.create_all(engine)
print(Base.metadata.tables.keys())
some_table = Table("some_table", Base.metadata, autoload_with=engine)
print(repr(some_table))
