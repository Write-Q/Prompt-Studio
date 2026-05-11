import json
from datetime import datetime

from app.database import get_connection
from app.models.schemas import (
    KnowledgeSnippetCreate,
    KnowledgeSnippetResponse,
    KnowledgeSnippetUpdate,
)


class SnippetNotFoundError(Exception):
    """
    知识片段不存在异常。

    后续路由层会把这个异常转换成 HTTP 404。
    """


def _get_current_time_text() -> str:
    """
    生成当前时间文本。
    """
    return datetime.now().isoformat(timespec="seconds")


def _serialize_tags(tags: list[str]) -> str:
    """
    把标签列表转换成数据库可存储的 JSON 字符串。
    """
    return json.dumps(tags, ensure_ascii=False)


def _deserialize_tags(tags_text: str | None) -> list[str]:
    """
    把数据库里的标签文本还原成列表。
    """
    if not tags_text:
        return []

    try:
        parsed_value = json.loads(tags_text)
        if isinstance(parsed_value, list):
            return [str(tag).strip() for tag in parsed_value if str(tag).strip()]
    except json.JSONDecodeError:
        pass

    raw_tags = tags_text.replace("，", ",").split(",")
    return [tag.strip() for tag in raw_tags if tag.strip()]


def _build_snippet_response(row: dict) -> KnowledgeSnippetResponse:
    """
    把数据库查询结果转换成知识片段响应模型。
    """
    return KnowledgeSnippetResponse(
        id=row["id"],
        title=row["title"],
        tags=_deserialize_tags(row["tags"]),
        content=row["content"],
        source=row["source"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_snippet(payload: KnowledgeSnippetCreate) -> KnowledgeSnippetResponse:
    """
    新增一个知识片段。
    """
    current_time = _get_current_time_text()

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO knowledge_snippets (
                title,
                tags,
                content,
                source,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                _serialize_tags(payload.tags),
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
    """
    获取知识片段列表，并支持标签筛选和关键词搜索。

    当前关键词搜索会匹配：
    - title
    - content
    - source
    - tags
    """
    sql = """
        SELECT
            id,
            title,
            tags,
            content,
            source,
            created_at,
            updated_at
        FROM knowledge_snippets
        WHERE 1 = 1
    """
    params: list[str] = []

    if tag and tag.strip():
        sql += " AND tags LIKE ?"
        params.append(f"%{tag.strip()}%")

    if keyword and keyword.strip():
        keyword_text = f"%{keyword.strip()}%"
        sql += """
            AND (
                title LIKE ?
                OR content LIKE ?
                OR source LIKE ?
                OR tags LIKE ?
            )
        """
        params.extend([keyword_text, keyword_text, keyword_text, keyword_text])

    sql += " ORDER BY updated_at DESC, id DESC"

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return [_build_snippet_response(row) for row in rows]


def get_snippet_by_id(snippet_id: int) -> KnowledgeSnippetResponse:
    """
    根据 id 获取单个知识片段详情。
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                id,
                title,
                tags,
                content,
                source,
                created_at,
                updated_at
            FROM knowledge_snippets
            WHERE id = ?
            """,
            (snippet_id,),
        )
        row = cursor.fetchone()

    if row is None:
        raise SnippetNotFoundError(f"ID 为 {snippet_id} 的知识片段不存在")

    return _build_snippet_response(row)


def update_snippet(
    snippet_id: int,
    payload: KnowledgeSnippetUpdate,
) -> KnowledgeSnippetResponse:
    """
    更新指定知识片段。
    """
    current_time = _get_current_time_text()

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE knowledge_snippets
            SET
                title = ?,
                tags = ?,
                content = ?,
                source = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                payload.title,
                _serialize_tags(payload.tags),
                payload.content,
                payload.source,
                current_time,
                snippet_id,
            ),
        )
        connection.commit()

        if cursor.rowcount == 0:
            raise SnippetNotFoundError(f"ID 为 {snippet_id} 的知识片段不存在")

    return get_snippet_by_id(snippet_id)


def delete_snippet(snippet_id: int) -> bool:
    """
    删除指定知识片段。
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM knowledge_snippets WHERE id = ?",
            (snippet_id,),
        )
        connection.commit()

        if cursor.rowcount == 0:
            raise SnippetNotFoundError(f"ID 为 {snippet_id} 的知识片段不存在")

    return True
