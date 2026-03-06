"""Run Alembic migrations locally using a synchronous DB driver (psycopg).

Use this script on Windows when ``alembic upgrade head`` fails with
WinError 64 / connection reset (asyncpg + asyncio issue). The script
uses the same config and migrations as env.py but connects via psycopg
instead of asyncpg.

Usage (from project root):

    uv run python scripts/run_migrations_local.py

    # or with explicit env:
    ENV=local uv run python scripts/run_migrations_local.py

Requires: psycopg (pip install "psycopg[binary]" or in pyproject.toml).
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from alembic import context
from alembic.config import Config
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from config.database import Base
from config.settings import Settings
from models import *  # noqa: F401

target_metadata = Base.metadata


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


def main() -> None:
    settings = Settings.load()
    db_url = settings.database_settings.url()
    sync_url = db_url.replace('postgresql+asyncpg://', 'postgresql+psycopg://')

    alembic_ini = _PROJECT_ROOT / 'models' / 'alembic.ini'
    alembic_cfg = Config(str(alembic_ini))
    context.config = alembic_cfg

    engine = create_engine(sync_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        do_run_migrations(connection)


if __name__ == '__main__':
    main()
