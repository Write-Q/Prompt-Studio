import os
from pathlib import Path

import psycopg

BASE_DIR = Path(__file__).resolve().parent.parent  # 供 seed.py 定位 seed/ 目录

# 连接串:默认指向本地 Docker 里的 Postgres(可用环境变量覆盖)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:promptstudio@localhost:5432/promptstudio",
)


class _Row(dict):
    """同时支持 row["name"] 和 row[0]，像 sqlite3.Row，减少服务层改动。"""

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def _row_factory(cursor):
    columns = [col.name for col in cursor.description] if cursor.description else []

    def make(values):
        return _Row(zip(columns, values))

    return make


class AppConnection:
    """包一层 psycopg 连接，对齐原 sqlite3 用法:
    - 把服务层的 `?` 占位符翻译成 psycopg 的 `%s`
    - 行支持按名/按位两种访问
    - with 退出时关闭连接
    """

    def __init__(self, raw: psycopg.Connection):
        self._raw = raw

    def execute(self, sql: str, params=()):
        return self._raw.execute(sql.replace("?", "%s"), params)

    def executemany(self, sql: str, seq):
        cursor = self._raw.cursor()
        cursor.executemany(sql.replace("?", "%s"), seq)
        return cursor

    def commit(self):
        self._raw.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._raw.close()
        return False


def get_connection() -> AppConnection:
    raw = psycopg.connect(DATABASE_URL, row_factory=_row_factory)
    return AppConnection(raw)


_SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS prompt_templates (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT,
    tags TEXT,
    content TEXT NOT NULL,
    description TEXT,
    is_favorite INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    updated_at TEXT,
    embedding vector(512)
);

CREATE TABLE IF NOT EXISTS context_cards (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    tags TEXT,
    content TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT,
    embedding vector(512)
);

CREATE TABLE IF NOT EXISTS generation_history (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    variables_json TEXT,
    context_card_ids TEXT,
    final_prompt TEXT NOT NULL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_context_cards_type ON context_cards(type);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX IF NOT EXISTS idx_generation_history_created_at ON generation_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conv_messages_cid ON conversation_messages(conversation_id, id);
CREATE INDEX IF NOT EXISTS idx_context_cards_embedding ON context_cards USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_embedding ON prompt_templates USING hnsw (embedding vector_cosine_ops);
"""


def init_db() -> None:
    with get_connection() as connection:
        for statement in _SCHEMA.split(";"):
            statement = statement.strip()
            if statement:
                connection.execute(statement)
        connection.commit()


if __name__ == "__main__":
    init_db()
    print("数据库初始化完成（PostgreSQL + pgvector）")
