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


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                content TEXT NOT NULL,
                description TEXT,
                is_favorite INTEGER NOT NULL DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS context_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                tags TEXT,
                content TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                variables_json TEXT,
                context_card_ids TEXT,
                final_prompt TEXT NOT NULL,
                created_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_generation_history_created_at
            ON generation_history(created_at DESC);

            CREATE INDEX IF NOT EXISTS idx_prompt_templates_category
            ON prompt_templates(category);

            CREATE INDEX IF NOT EXISTS idx_context_cards_type
            ON context_cards(type);

            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_conv_messages_cid
            ON conversation_messages(conversation_id, id);
            """
        )
        _ensure_column(connection, "context_cards", "embedding", "TEXT")
        _ensure_column(connection, "prompt_templates", "embedding", "TEXT")
        connection.commit()


def _ensure_column(connection, table: str, column: str, coltype: str) -> None:
    """幂等加列:已有库也能补上新列(SQLite ALTER 不支持 IF NOT EXISTS)。"""
    existing = [row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")


if __name__ == "__main__":
    init_db()
    print(f"数据库初始化完成：{DB_PATH}")
