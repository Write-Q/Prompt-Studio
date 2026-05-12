from sqlite3 import Row

from app.database import get_connection
from app.models.schemas import (
    KnowledgeSnippetCreate,
    KnowledgeSnippetResponse,
    KnowledgeSnippetUpdate,
)
from app.services.common import deserialize_tags, now_text, serialize_tags


class SnippetNotFoundError(Exception):
    pass


SNIPPET_COLUMNS = "id, title, tags, content, source, created_at, updated_at"


def _snippet_from_row(row: Row) -> KnowledgeSnippetResponse:
    return KnowledgeSnippetResponse(
        id=row["id"],
        title=row["title"],
        tags=deserialize_tags(row["tags"]),
        content=row["content"],
        source=row["source"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_snippet(payload: KnowledgeSnippetCreate) -> KnowledgeSnippetResponse:
    current_time = now_text()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO knowledge_snippets (
                title, tags, content, source, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                serialize_tags(payload.tags),
                payload.content,
                payload.source,
                current_time,
                current_time,
            ),
        )
        connection.commit()
        snippet_id = cursor.lastrowid

    return get_snippet_by_id(snippet_id)


def list_snippets(
    tag: str | None = None,
    keyword: str | None = None,
) -> list[KnowledgeSnippetResponse]:
    sql = f"SELECT {SNIPPET_COLUMNS} FROM knowledge_snippets WHERE 1 = 1"
    params: list[str] = []

    if tag and tag.strip():
        sql += " AND tags LIKE ?"
        params.append(f"%{tag.strip()}%")

    if keyword and keyword.strip():
        pattern = f"%{keyword.strip()}%"
        sql += """
            AND (
                title LIKE ?
                OR content LIKE ?
                OR source LIKE ?
                OR tags LIKE ?
            )
        """
        params.extend([pattern, pattern, pattern, pattern])

    sql += " ORDER BY updated_at DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    return [_snippet_from_row(row) for row in rows]


def get_snippet_by_id(snippet_id: int) -> KnowledgeSnippetResponse:
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT {SNIPPET_COLUMNS} FROM knowledge_snippets WHERE id = ?",
            (snippet_id,),
        ).fetchone()

    if row is None:
        raise SnippetNotFoundError(f"ID 为 {snippet_id} 的知识片段不存在")

    return _snippet_from_row(row)


def update_snippet(
    snippet_id: int,
    payload: KnowledgeSnippetUpdate,
) -> KnowledgeSnippetResponse:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE knowledge_snippets
            SET title = ?, tags = ?, content = ?, source = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                payload.title,
                serialize_tags(payload.tags),
                payload.content,
                payload.source,
                now_text(),
                snippet_id,
            ),
        )
        connection.commit()

        if cursor.rowcount == 0:
            raise SnippetNotFoundError(f"ID 为 {snippet_id} 的知识片段不存在")

    return get_snippet_by_id(snippet_id)


def delete_snippet(snippet_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM knowledge_snippets WHERE id = ?",
            (snippet_id,),
        )
        connection.commit()

    if cursor.rowcount == 0:
        raise SnippetNotFoundError(f"ID 为 {snippet_id} 的知识片段不存在")

    return True
