import json

from app.database import get_connection
from app.models.schemas import GenerationHistoryCreate, GenerationHistoryResponse
from app.services.common import now_text
from app.services.template_service import get_template_by_id


class HistoryNotFoundError(Exception):
    pass


def _safe_json_loads(value: str | None, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _build_history_response(row) -> GenerationHistoryResponse:
    return GenerationHistoryResponse(
        id=row["id"],
        template_id=row["template_id"],
        variables=_safe_json_loads(row["variables_json"], {}),
        context_card_ids=_safe_json_loads(row["context_card_ids"], []),
        final_prompt=row["final_prompt"],
        created_at=row["created_at"],
    )


def list_history(limit: int = 20) -> list[GenerationHistoryResponse]:
    safe_limit = max(1, min(limit, 100))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, template_id, variables_json, context_card_ids, final_prompt, created_at
            FROM generation_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()

    return [_build_history_response(row) for row in rows]


def create_history(payload: GenerationHistoryCreate) -> GenerationHistoryResponse:
    get_template_by_id(payload.template_id)

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO generation_history (
                template_id, variables_json, context_card_ids, final_prompt, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.template_id,
                json.dumps(payload.variables, ensure_ascii=False),
                json.dumps(payload.context_card_ids, ensure_ascii=False),
                payload.final_prompt,
                now_text(),
            ),
        )
        connection.commit()
        history_id = cursor.lastrowid

    return get_history_by_id(history_id)


def get_history_by_id(history_id: int) -> GenerationHistoryResponse:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, template_id, variables_json, context_card_ids, final_prompt, created_at
            FROM generation_history
            WHERE id = ?
            """,
            (history_id,),
        ).fetchone()

    if row is None:
        raise HistoryNotFoundError(f"ID 为 {history_id} 的历史记录不存在")

    return _build_history_response(row)


def delete_history(history_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM generation_history WHERE id = ?", (history_id,))
        connection.commit()

    if cursor.rowcount == 0:
        raise HistoryNotFoundError(f"ID 为 {history_id} 的历史记录不存在")

    return True
