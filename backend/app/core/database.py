from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    run_lightweight_sqlite_migrations()


def run_lightweight_sqlite_migrations() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    additions = {
        "raffle": {
            "winner_number": "INTEGER",
            "winner_registered_at": "DATETIME",
        },
        "reservation": {
            "wompi_transaction_id": "VARCHAR",
            "reminder_sent_at": "DATETIME",
            "paid_at": "DATETIME",
        },
    }
    with engine.begin() as connection:
        for table_name, columns in additions.items():
            existing = {row[1] for row in connection.exec_driver_sql(f"PRAGMA table_info({table_name})")}
            for column_name, column_type in columns.items():
                if column_name not in existing:
                    connection.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        connection.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_active_reservation_number "
            "ON reservation (raffle_id, number) WHERE status IN ('pending', 'paid')"
        )


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
