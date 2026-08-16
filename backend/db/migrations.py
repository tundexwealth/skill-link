"""Small, idempotent schema upgrades for SQLite and PostgreSQL installations."""
from sqlalchemy import inspect, text

from db.base import Base
from models import AuthSession, Rating  # noqa: F401 - registers the table with Base


PROVIDER_COLUMNS = {
    "user_id": "INTEGER",
    "website": "VARCHAR",
    "linkedin_url": "VARCHAR",
    "about": "TEXT",
    "logo_url": "VARCHAR",
    "cover_image": "VARCHAR",
    "email": "VARCHAR",
    "is_imported": "BOOLEAN NOT NULL DEFAULT false",
    "imported_from": "VARCHAR",
    "verified": "BOOLEAN NOT NULL DEFAULT false",
    "created_at": "TIMESTAMP",
}

USER_COLUMNS = {
    "is_admin": "BOOLEAN NOT NULL DEFAULT false",
}


def ensure_schema(engine) -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        if "providers" in tables:
            existing_columns = {column["name"] for column in inspector.get_columns("providers")}
            for name, column_definition in PROVIDER_COLUMNS.items():
                if name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE providers ADD COLUMN {name} {column_definition}"))
            connection.execute(
                text("CREATE UNIQUE INDEX IF NOT EXISTS ix_providers_user_id ON providers (user_id)")
            )

        if "users" in tables:
            existing_columns = {column["name"] for column in inspector.get_columns("users")}
            for name, column_definition in USER_COLUMNS.items():
                if name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {column_definition}"))
