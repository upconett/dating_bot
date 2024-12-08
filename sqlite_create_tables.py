import sys
from sqlalchemy import create_engine
from controllers.database.sqlalchemy.models import *
from controllers.database.sqlalchemy import Base


def create_tables(database_path: str):
    engine = create_engine("sqlite:///"+database_path)
    Base.metadata.create_all(engine)
    print(f"Tables for {database_path} Created!")


if __name__ == "__main__":
    try:
        database_path = sys.argv[1]
        create_tables(database_path)
    except Exception as ex:
        print(ex)
        print("Enter database_path as first argument:\n> py sqlite_create_tables.py some_database_path.db")
