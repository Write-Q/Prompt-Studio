"""种子数据机制：让别人本地部署时"开箱即用、直接沿用数据库"。

设计：
- 数据以 JSON 文本存在 seed/ 目录（真相源，进 git，可无限扩充，不受数据库二进制限制）。
- 首次启动若数据库为空 → 自动从 JSON 灌入（seed_if_empty）。非破坏性：库里已有数据就跳过，
  绝不覆盖别人后来添加的内容。
- export_to_seed：把当前数据库导出成 seed/*.json，方便你在 UI 里编辑后再分发。

命令行：
    python -m app.seed            # 库为空则灌入种子
    python -m app.seed --export   # 把当前数据库导出成 seed/*.json
"""

import json
from pathlib import Path

from app.database import BASE_DIR, get_connection, init_db
from app.services.common import deserialize_tags, now_text, serialize_tags


SEED_DIR = BASE_DIR / "seed"


def _load_json(seed_dir: Path, name: str) -> list[dict]:
    path = seed_dir / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def database_is_empty() -> bool:
    with get_connection() as connection:
        templates = connection.execute("SELECT COUNT(*) FROM prompt_templates").fetchone()[0]
        cards = connection.execute("SELECT COUNT(*) FROM context_cards").fetchone()[0]
    return templates == 0 and cards == 0


def _insert_templates(connection, rows: list[dict]) -> None:
    now = now_text()
    connection.executemany(
        """
        INSERT INTO prompt_templates
            (title, category, tags, content, description, is_favorite, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["title"],
                row.get("category"),
                serialize_tags(row.get("tags", [])),
                row["content"],
                row.get("description"),
                int(row.get("is_favorite", 0)),
                now,
                now,
            )
            for row in rows
        ],
    )


def _insert_cards(connection, rows: list[dict]) -> None:
    now = now_text()
    connection.executemany(
        """
        INSERT INTO context_cards (type, title, tags, content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row.get("type", "background"),
                row["title"],
                serialize_tags(row.get("tags", [])),
                row["content"],
                now,
                now,
            )
            for row in rows
        ],
    )


def seed_if_empty(seed_dir: Path = SEED_DIR) -> int:
    """仅当数据库为空时，从 seed_dir 灌入数据。返回插入行数（0 表示已有数据、跳过）。"""
    if not database_is_empty():
        return 0
    templates = _load_json(seed_dir, "templates.json")
    cards = _load_json(seed_dir, "context_cards.json")
    with get_connection() as connection:
        _insert_templates(connection, templates)
        _insert_cards(connection, cards)
        connection.commit()
    return len(templates) + len(cards)


def export_to_seed(seed_dir: Path = SEED_DIR) -> tuple[int, int]:
    """把当前数据库内容导出成 seed/*.json，便于你编辑数据后再分发。"""
    seed_dir.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        templates = [
            {
                "title": row["title"],
                "category": row["category"],
                "tags": deserialize_tags(row["tags"]),
                "content": row["content"],
                "description": row["description"],
                "is_favorite": bool(row["is_favorite"]),
            }
            for row in connection.execute("SELECT * FROM prompt_templates ORDER BY id")
        ]
        cards = [
            {
                "type": row["type"],
                "title": row["title"],
                "tags": deserialize_tags(row["tags"]),
                "content": row["content"],
            }
            for row in connection.execute("SELECT * FROM context_cards ORDER BY id")
        ]
    (seed_dir / "templates.json").write_text(
        json.dumps(templates, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (seed_dir / "context_cards.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(templates), len(cards)


if __name__ == "__main__":
    import sys

    init_db()
    if "--export" in sys.argv:
        template_count, card_count = export_to_seed()
        print(f"已导出 {template_count} 个模板 + {card_count} 张卡片 → {SEED_DIR}")
    else:
        inserted = seed_if_empty()
        print(f"已灌入 {inserted} 条种子数据 → {SEED_DIR}" if inserted else "数据库已有数据，跳过灌入")
