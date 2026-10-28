
from sqlalchemy import inspect

from database.db import Base, engine
from database import models  # Ensure all models are registered


NEW_COLUMNS = {
    "blockchain_status": "VARCHAR(30)",
    "blockchain_registry_address": "VARCHAR(100)",
    "blockchain_transaction_hash": "VARCHAR(100)",
    "blockchain_report_hash": "VARCHAR(100)",
    "blockchain_error": "VARCHAR(2000)",
}


def migrate():
    # Create any missing tables without deleting existing data.
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        columns = {
            column["name"]
            for column in inspect(connection).get_columns("assessments")
        }

        for name, sql_type in NEW_COLUMNS.items():
            if name not in columns:
                connection.exec_driver_sql(
                    f"ALTER TABLE assessments ADD COLUMN {name} {sql_type}"
                )
                print(f"Added column: {name}")
            else:
                print(f"Already exists: {name}")

    print("Assessment publication migration completed.")


if __name__ == "__main__":
    migrate()
