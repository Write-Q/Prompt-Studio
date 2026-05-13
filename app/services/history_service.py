import json

from app.database import get_connection
from app.models.schemas import GenerationHistoryCreate, GenerationHistoryResponse
from app.services.common import now_text
from app.services.template_service import get_template_by_id


class HistoryNotFoundError(Exception):
    """
    历史记录不存在异常。

    路由层会把它转换成 404 响应。
    """


def _safe_json_loads(value: str | None, default):
    """
    安全解析 JSON 字符串。

    历史表中的 variables_json、snippet_ids 都是 TEXT，
    读取时需要从字符串还原成 Python 数据结构。
    """
    if not value:
        return default

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _build_history_response(row) -> GenerationHistoryResponse:
    """
    把数据库行转换成前端需要的历史记录响应结构。
    """
    return GenerationHistoryResponse(
        id=row["id"],
        template_id=row["template_id"],
        variables=_safe_json_loads(row["variables_json"], {}),
        snippet_ids=_safe_json_loads(row["snippet_ids"], []),
        final_prompt=row["final_prompt"],
        created_at=row["created_at"],
    )


def list_history(limit: int = 20) -> list[GenerationHistoryResponse]:
    """
    获取最近的生成历史列表。

    当前先只做倒序列表，limit 用来避免一次返回过多内容。
    """
    safe_limit = max(1, min(limit, 100))

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                id,
                template_id,
                variables_json,
                snippet_ids,
                final_prompt,
                created_at
            FROM generation_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        )
        rows = cursor.fetchall()

    return [_build_history_response(row) for row in rows]


def create_history(payload: GenerationHistoryCreate) -> GenerationHistoryResponse:
    """
    手动保存用户当前确认的预生成 Prompt。
    """
    get_template_by_id(payload.template_id)

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO generation_history (
                template_id, variables_json, snippet_ids, final_prompt, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.template_id,
                json.dumps(payload.variables, ensure_ascii=False),
                json.dumps(payload.snippet_ids, ensure_ascii=False),
                payload.final_prompt,
                now_text(),
            ),
        )
        connection.commit()
        history_id = cursor.lastrowid

    return get_history_by_id(history_id)


def get_history_by_id(history_id: int) -> GenerationHistoryResponse:
    """
    根据 ID 获取单条生成历史详情。
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                id,
                template_id,
                variables_json,
                snippet_ids,
                final_prompt,
                created_at
            FROM generation_history
            WHERE id = ?
            """,
            (history_id,),
        )
        row = cursor.fetchone()

    if row is None:
        raise HistoryNotFoundError(f"ID 为 {history_id} 的历史记录不存在")

    return _build_history_response(row)


def delete_history(history_id: int) -> bool:
    """
    删除指定生成历史。

    这里只删除 generation_history 表中的记录，
    不会删除模板或知识片段。
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM generation_history WHERE id = ?",
            (history_id,),
        )
        connection.commit()

        if cursor.rowcount == 0:
            raise HistoryNotFoundError(f"ID 为 {history_id} 的历史记录不存在")

    return True
