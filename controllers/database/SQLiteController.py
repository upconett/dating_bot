from controllers.database import SQLAlchemyController


class SQLiteController(SQLAlchemyController):
    def __init__(self, path_to_database: str):
        db_string = "sqlite+aiosqlite:///"+path_to_database
        super().__init__(db_string)
