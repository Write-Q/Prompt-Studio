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


TEMPLATE_COLUMNS = """
    id, seed_key, title, category, tags, content, description, created_at, updated_at
"""


def _template_from_row(row: Row) -> PromptTemplateResponse:
    return PromptTemplateResponse(
        id=row["id"],
        seed_key=row["seed_key"],
        title=row["title"],
        category=row["category"],
        tags=deserialize_tags(row["tags"]),
        content=row["content"],
        description=row["description"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_template(payload: PromptTemplateCreate) -> PromptTemplateResponse:
    current_time = now_text()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO prompt_templates (
                title, category, tags, content, description, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
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
        )
        connection.commit()
        template_id = cursor.lastrowid

    return PromptTemplateResponse(
        id=template_id,
        seed_key=None,
        title=payload.title,
        category=payload.category,
        tags=list(payload.tags),
        content=payload.content,
        description=payload.description,
        created_at=current_time,
        updated_at=current_time,
    )


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

    sql += " ORDER BY updated_at DESC, id DESC LIMIT ? OFFSET ?"
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
            """
            UPDATE prompt_templates
            SET title = ?, category = ?, tags = ?, content = ?, description = ?, updated_at = ?
            WHERE id = ?
            RETURNING seed_key, created_at
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

    return PromptTemplateResponse(
        id=template_id,
        seed_key=row["seed_key"],
        title=payload.title,
        category=payload.category,
        tags=list(payload.tags),
        content=payload.content,
        description=payload.description,
        created_at=row["created_at"],
        updated_at=current_time,
    )


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
