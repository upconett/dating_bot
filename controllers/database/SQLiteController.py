from controllers.database import SQLAlchemyController


class SQLiteController(SQLAlchemyController):
    def __init__(self, path_to_database: str, base_model: "Base"):
        super().__init__(path_to_database, base_model)
