import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


class AppConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, factory=AppConnection)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_column(cursor: sqlite3.Cursor, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in cursor.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _migrate_context_cards_without_source(cursor: sqlite3.Cursor) -> None:
    columns = {row["name"] for row in cursor.execute("PRAGMA table_info(context_cards)")}
    if "source" not in columns:
        return

    cursor.execute("DROP INDEX IF EXISTS idx_context_cards_seed_key")
    cursor.execute(
        """
        CREATE TABLE context_cards_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seed_key TEXT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            tags TEXT,
            content TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO context_cards_new (
            id, seed_key, type, title, tags, content, created_at, updated_at
        )
        SELECT id, seed_key, type, title, tags, content, created_at, updated_at
        FROM context_cards
        """
    )
    cursor.execute("DROP TABLE context_cards")
    cursor.execute("ALTER TABLE context_cards_new RENAME TO context_cards")


def init_db() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                content TEXT NOT NULL,
                description TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        _ensure_column(cursor, "prompt_templates", "seed_key", "TEXT")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS context_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seed_key TEXT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                tags TEXT,
                content TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        _ensure_column(cursor, "context_cards", "seed_key", "TEXT")
        _migrate_context_cards_without_source(cursor)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                variables_json TEXT,
                context_card_ids TEXT,
                final_prompt TEXT NOT NULL,
                created_at TEXT
            )
            """
        )
        _ensure_column(cursor, "generation_history", "context_card_ids", "TEXT")
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_prompt_templates_seed_key
            ON prompt_templates(seed_key)
            WHERE seed_key IS NOT NULL
            """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_context_cards_seed_key
            ON context_cards(seed_key)
            WHERE seed_key IS NOT NULL
            """
        )
        connection.commit()


if __name__ == "__main__":
    init_db()
    print(f"数据库初始化完成：{DB_PATH}")
