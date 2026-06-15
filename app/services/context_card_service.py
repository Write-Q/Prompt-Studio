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
    card = _card_from_row(row)
    _set_card_embedding_safe(card.id, _card_embed_text(card))
    return card


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


def recommend_context_cards(payload: ContextCardRecommendRequest) -> list[ContextCardResponse]:
    """语义检索:用 pgvector 余弦距离(<=>)，阈值过滤后取前 limit 张(走 HNSW 索引)。"""
    from app.services.embedding import SIMILARITY_THRESHOLD, embed, to_pgvector

    query_vector = to_pgvector(embed(payload.text, is_query=True))
    max_distance = 1 - SIMILARITY_THRESHOLD  # 余弦距离 = 1 - 余弦相似度
    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT {CONTEXT_CARD_COLUMNS}
            FROM context_cards
            WHERE embedding IS NOT NULL AND (embedding <=> ?::vector) <= ?
            ORDER BY embedding <=> ?::vector
            LIMIT ?
            """,
            (query_vector, max_distance, query_vector, payload.limit),
        ).fetchall()
    return [_card_from_row(row) for row in rows]


def _card_embed_text(card: ContextCardResponse) -> str:
    return f"{card.title}\n{card.content}"


def _set_card_embedding_safe(card_id: int, text: str) -> None:
    """给单张卡片写 embedding；失败(模型没装/出错)也不阻断创建/更新。"""
    try:
        from app.services.embedding import embed, to_pgvector

        vector = to_pgvector(embed(text))
        with get_connection() as connection:
            connection.execute(
                "UPDATE context_cards SET embedding = ?::vector WHERE id = ?", (vector, card_id)
            )
            connection.commit()
    except Exception:  # noqa: BLE001 - embedding 是增强项，不该影响主流程
        pass


def backfill_card_embeddings() -> int:
    """给所有还没有 embedding 的卡片批量补上。返回补的条数。"""
    from app.services.embedding import embed_documents, to_pgvector

    with get_connection() as connection:
        rows = connection.execute(
            f"SELECT {CONTEXT_CARD_COLUMNS} FROM context_cards WHERE embedding IS NULL"
        ).fetchall()

    cards = [_card_from_row(row) for row in rows]
    if not cards:
        return 0

    vectors = embed_documents([_card_embed_text(card) for card in cards])
    with get_connection() as connection:
        for card, vector in zip(cards, vectors):
            connection.execute(
                "UPDATE context_cards SET embedding = ?::vector WHERE id = ?",
                (to_pgvector(vector), card.id),
            )
        connection.commit()
    return len(cards)


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

    card = _card_from_row(row)
    _set_card_embedding_safe(card.id, _card_embed_text(card))
    return card


def delete_context_card(card_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM context_cards WHERE id = ?", (card_id,))
        connection.commit()

    if cursor.rowcount == 0:
        raise ContextCardNotFoundError(f"ID 为 {card_id} 的上下文卡片不存在")

    return True
