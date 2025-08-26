import sqlite3
from contextlib import contextmanager
from os import listdir
from os.path import dirname, join
from typing import List

from src.models.ServiceModel import ServiceModel
from src.utils.logger import logger
from src.utils.media import get_cache_path

DB_FOLDER = dirname(__file__)
MIGRATION_FOLDER = join(DB_FOLDER, "migrations")
DB_FILE = join(get_cache_path(), "ulauncher-homepage.db")


@contextmanager
def _get_conn():
    """Provide a transactional scope around a series of operations."""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def run_migrations():
    with _get_conn() as conn:
        cursor = conn.cursor()
        # Create migration table if not created
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Listing all SQL files in the migration directory.
        files = sorted(f for f in listdir(MIGRATION_FOLDER) if f.endswith(".sql"))

        for file in files:
            # Verify if the migration has already been executed.
            cursor.execute("SELECT * FROM migrations WHERE name = ?", (file,))
            if cursor.fetchone():
                logger.debug(f"Skipping already run migration: {file}")
                continue

            # Run SQL migration
            path_to_file = join(MIGRATION_FOLDER, file)
            with open(path_to_file, "r", encoding="utf-8") as f:
                sql = f.read()
            logger.debug(f"Running migration: {file}")
            cursor.executescript(sql)

            # Add file name to migration table
            cursor.execute("INSERT INTO migrations (name) VALUES (?)", (file,))

    logger.debug("✅ All migrations complete")


def save_service(items: List[ServiceModel], clear_existing=False):
    with _get_conn() as conn:
        cursor = conn.cursor()
        if clear_existing:
            cursor.execute("DELETE FROM services")

        for item in items:
            cursor.execute(
                "INSERT INTO services (name, href, icon, description, group_name) VALUES (?, ?, ?, ?, ?)",
                (item.name, item.href, item.icon, item.description, item.group_name),
            )


def search_services(search: str, limit=5) -> List[ServiceModel]:
    try:
        with _get_conn() as conn:
            cursor = conn.cursor()
            if not search.strip():
                query = """
                    SELECT name, href, icon, description, group_name
                    FROM services
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
            else:
                query = """
                    SELECT name, href, icon, description, group_name
                    FROM services
                    WHERE name LIKE ? OR description LIKE ? OR group_name LIKE ?
                    LIMIT ?
                """
                pattern = f"%{search}%"
                cursor.execute(query, (pattern, pattern, pattern, limit))

            rows = cursor.fetchall()

            return [
                ServiceModel(
                    name=row[0],
                    href=row[1],
                    icon=row[2],
                    description=row[3],
                    group_name=row[4],
                )
                for row in rows
            ]
    except sqlite3.OperationalError as e:
        logger.warning(f"Error searching services: {e}. Running migrations and retrying.")
        run_migrations()
        return []
