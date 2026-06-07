from sqlite3 import Row

from app.database import get_connection
from app.models.schemas import (
    ContextCardCreate,
    ContextCardRecommendRequest,
    ContextCardResponse,
    ContextCardType,
    ContextCardUpdate,
)
from app.services.common import deserialize_tags, now_text, serialize_tags


class ContextCardNotFoundError(Exception):
    pass


CONTEXT_CARD_COLUMNS = "id, type, title, tags, content, created_at, updated_at"


def _card_from_row(row: Row) -> ContextCardResponse:
    return ContextCardResponse(
        id=row["id"],
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
        row = connection.execute(
            f"""
            INSERT INTO context_cards (
                type, title, tags, content, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING {CONTEXT_CARD_COLUMNS}
            """,
            (
                payload.type,
                payload.title,
                serialize_tags(payload.tags),
                payload.content,
                current_time,
                current_time,
            ),
        ).fetchone()
        connection.commit()
    return _card_from_row(row)


def list_context_cards(
    type: ContextCardType | None = None,
    tag: str | None = None,
    keyword: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[ContextCardResponse]:
    sql = f"SELECT {CONTEXT_CARD_COLUMNS} FROM context_cards WHERE 1 = 1"
    params: list = []

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

    sql += " ORDER BY updated_at DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([max(1, min(limit, 500)), max(0, offset)])

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    return [_card_from_row(row) for row in rows]


def _ngrams(text: str, min_size: int = 2, max_size: int = 4) -> set[str]:
    text = "".join(text.lower().split())
    return {
        text[index : index + size]
        for size in range(min_size, max_size + 1)
        for index in range(max(0, len(text) - size + 1))
    }


def _recommend_score(card: ContextCardResponse, text: str) -> int:
    query = "".join(text.lower().split())
    tags = [tag.lower() for tag in card.tags]
    title_terms = _ngrams(card.title)
    content_terms = _ngrams(card.content)
    return (
        sum(5 for tag in tags if tag and tag in query)
        + sum(3 for term in title_terms if term in query)
        + sum(1 for term in content_terms if term in query)
    )


def recommend_context_cards(payload: ContextCardRecommendRequest) -> list[ContextCardResponse]:
    cards = list_context_cards(limit=500)
    scored = [(_recommend_score(card, payload.text), card) for card in cards]
    matches = [(score, card) for score, card in scored if score > 0]
    matches.sort(key=lambda item: (-item[0], item[1].id))
    return [card for _, card in matches[: payload.limit]]


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
    current_time = now_text()
    with get_connection() as connection:
        row = connection.execute(
            f"""
            UPDATE context_cards
            SET type = ?, title = ?, tags = ?, content = ?, updated_at = ?
            WHERE id = ?
            RETURNING {CONTEXT_CARD_COLUMNS}
            """,
            (
                payload.type,
                payload.title,
                serialize_tags(payload.tags),
                payload.content,
                current_time,
                card_id,
            ),
        ).fetchone()
        connection.commit()

    if row is None:
        raise ContextCardNotFoundError(f"ID 为 {card_id} 的上下文卡片不存在")

    return _card_from_row(row)


def delete_context_card(card_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM context_cards WHERE id = ?", (card_id,))
        connection.commit()

    if cursor.rowcount == 0:
        raise ContextCardNotFoundError(f"ID 为 {card_id} 的上下文卡片不存在")

    return True
