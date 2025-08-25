import sqlite3
from os import listdir
from os.path import dirname, join
from typing import List

from src.models.ServiceModel import ServiceModel
from src.utils.logger import logger

DB_FOLDER = dirname(__file__)
MIGRATION_FOLDER = join(DB_FOLDER, "migrations")
DB_FILE = join(MIGRATION_FOLDER, "my_database.db")


def _get_conn():
    return sqlite3.connect(DB_FILE)


def run_migrations():
    conn = _get_conn()
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
    conn.commit()

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
        conn.commit()

    conn.close()
    logger.debug("✅ All migrations complete")


def save_service(items: List[ServiceModel], clear_existing=False):
    conn = _get_conn()
    cursor = conn.cursor()

    if clear_existing:
        cursor.execute("DELETE FROM services")

    for item in items:
        cursor.execute(
            "INSERT INTO services (name, href, icon, description, group_name) VALUES (?, ?, ?, ?, ?)",
            (item.name, item.href, item.icon, item.description, item.group_name),
        )

    conn.commit()
    conn.close()


def search_services(search: str, limit=5) -> List[ServiceModel]:
    try:
        conn = _get_conn()
        cursor = conn.cursor()

        if search.strip() == "":
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
                WHERE name LIKE ? OR description LIKE ?
                LIMIT ?
            """
            pattern = f"%{search}%"
            cursor.execute(query, (pattern, pattern, limit))

        rows = cursor.fetchall()
        conn.close()

        logger.debug("----------------------")
        logger.debug(rows)
        logger.debug("----------------------")

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
        logger.debug(f"Error searching services : {e}")
        return []
