from sqlite3 import Row

from app.database import get_connection
from app.models.schemas import ContextCardCreate, ContextCardResponse, ContextCardType, ContextCardUpdate
from app.services.common import deserialize_tags, now_text, serialize_tags


class ContextCardNotFoundError(Exception):
    pass


CONTEXT_CARD_COLUMNS = "id, seed_key, type, title, tags, content, created_at, updated_at"


def _card_from_row(row: Row) -> ContextCardResponse:
    return ContextCardResponse(
        id=row["id"],
        seed_key=row["seed_key"],
        type=row["type"],
        title=row["title"],
        tags=deserialize_tags(row["tags"]),
        content=row["content"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_context_card(payload: ContextCardCreate) -> ContextCardResponse:
    current_time = now_text()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO context_cards (
                type, title, tags, content, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.type,
                payload.title,
                serialize_tags(payload.tags),
                payload.content,
                current_time,
                current_time,
            ),
        )
        connection.commit()
        card_id = cursor.lastrowid

    return get_context_card_by_id(card_id)


def list_context_cards(
    type: ContextCardType | None = None,
    tag: str | None = None,
    keyword: str | None = None,
) -> list[ContextCardResponse]:
    sql = f"SELECT {CONTEXT_CARD_COLUMNS} FROM context_cards WHERE 1 = 1"
    params: list[str] = []

    if type:
        sql += " AND type = ?"
        params.append(type)

    if tag and tag.strip():
        sql += " AND tags LIKE ?"
        params.append(f"%{tag.strip()}%")

    if keyword and keyword.strip():
        pattern = f"%{keyword.strip()}%"
        sql += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
        params.extend([pattern, pattern, pattern])

    sql += " ORDER BY updated_at DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    return [_card_from_row(row) for row in rows]


def get_context_card_by_id(card_id: int) -> ContextCardResponse:
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT {CONTEXT_CARD_COLUMNS} FROM context_cards WHERE id = ?",
            (card_id,),
        ).fetchone()

    if row is None:
        raise ContextCardNotFoundError(f"ID 为 {card_id} 的上下文卡片不存在")

    return _card_from_row(row)


def update_context_card(card_id: int, payload: ContextCardUpdate) -> ContextCardResponse:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE context_cards
            SET type = ?, title = ?, tags = ?, content = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                payload.type,
                payload.title,
                serialize_tags(payload.tags),
                payload.content,
                now_text(),
                card_id,
            ),
        )
        connection.commit()

    if cursor.rowcount == 0:
        raise ContextCardNotFoundError(f"ID 为 {card_id} 的上下文卡片不存在")

    return get_context_card_by_id(card_id)


def delete_context_card(card_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM context_cards WHERE id = ?", (card_id,))
        connection.commit()

    if cursor.rowcount == 0:
        raise ContextCardNotFoundError(f"ID 为 {card_id} 的上下文卡片不存在")

    return True
