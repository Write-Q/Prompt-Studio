from sqlite3 import Row

from app.database import get_connection
from app.models.schemas import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)
from app.services.common import deserialize_tags, now_text, serialize_tags


class TemplateNotFoundError(Exception):
    pass


TEMPLATE_COLUMNS = "id, title, category, tags, content, description, is_favorite, created_at, updated_at"


def _template_from_row(row: Row) -> PromptTemplateResponse:
    return PromptTemplateResponse(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        tags=deserialize_tags(row["tags"]),
        content=row["content"],
        description=row["description"],
        is_favorite=bool(row["is_favorite"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_template(payload: PromptTemplateCreate) -> PromptTemplateResponse:
    current_time = now_text()
    with get_connection() as connection:
        row = connection.execute(
            f"""
            INSERT INTO prompt_templates (
                title, category, tags, content, description, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING {TEMPLATE_COLUMNS}
            """,
            (
                payload.title,
                payload.category,
                serialize_tags(payload.tags),
                payload.content,
                payload.description,
                current_time,
                current_time,
            ),
        ).fetchone()
        connection.commit()
    return _template_from_row(row)


def list_templates(
    category: str | None = None,
    keyword: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[PromptTemplateResponse]:
    sql = f"SELECT {TEMPLATE_COLUMNS} FROM prompt_templates WHERE 1 = 1"
    params: list = []

    if category and category.strip():
        sql += " AND category = ?"
        params.append(category.strip())

    if keyword and keyword.strip():
        pattern = f"%{keyword.strip()}%"
        sql += """
            AND (
                title LIKE ?
                OR content LIKE ?
                OR description LIKE ?
                OR tags LIKE ?
            )
        """
        params.extend([pattern, pattern, pattern, pattern])

    sql += " ORDER BY is_favorite DESC, updated_at DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([max(1, min(limit, 500)), max(0, offset)])

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    return [_template_from_row(row) for row in rows]


def get_template_by_id(template_id: int) -> PromptTemplateResponse:
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT {TEMPLATE_COLUMNS} FROM prompt_templates WHERE id = ?",
            (template_id,),
        ).fetchone()

    if row is None:
        raise TemplateNotFoundError(f"ID 为 {template_id} 的模板不存在")

    return _template_from_row(row)


def update_template(
    template_id: int,
    payload: PromptTemplateUpdate,
) -> PromptTemplateResponse:
    current_time = now_text()
    with get_connection() as connection:
        row = connection.execute(
            f"""
            UPDATE prompt_templates
            SET title = ?, category = ?, tags = ?, content = ?, description = ?, updated_at = ?
            WHERE id = ?
            RETURNING {TEMPLATE_COLUMNS}
            """,
            (
                payload.title,
                payload.category,
                serialize_tags(payload.tags),
                payload.content,
                payload.description,
                current_time,
                template_id,
            ),
        ).fetchone()
        connection.commit()

    if row is None:
        raise TemplateNotFoundError(f"ID 为 {template_id} 的模板不存在")

    return _template_from_row(row)


def set_template_favorite(template_id: int, is_favorite: bool) -> PromptTemplateResponse:
    current_time = now_text()
    with get_connection() as connection:
        row = connection.execute(
            f"""
            UPDATE prompt_templates
            SET is_favorite = ?, updated_at = ?
            WHERE id = ?
            RETURNING {TEMPLATE_COLUMNS}
            """,
            (
                1 if is_favorite else 0,
                current_time,
                template_id,
            ),
        ).fetchone()
        connection.commit()

    if row is None:
        raise TemplateNotFoundError(f"ID 为 {template_id} 的模板不存在")

    return _template_from_row(row)


def delete_template(template_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM prompt_templates WHERE id = ?",
            (template_id,),
        )
        connection.commit()

    if cursor.rowcount == 0:
        raise TemplateNotFoundError(f"ID 为 {template_id} 的模板不存在")

    return True
