"""多轮会话的持久化管理（存 SQLite，按 conversation_id 区分，多个会话并存）。

只存"对话本身"(user / assistant 消息),不存工具调用的中间往返——
下一轮只需要看到"谁问了什么、助手答了什么"。
"""

from app.database import get_connection
from app.services.common import now_text


def append_message(conversation_id: str, role: str, content: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversation_messages (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, content, now_text()),
        )
        connection.commit()


def get_recent_messages(conversation_id: str, limit: int = 20) -> list[dict]:
    """取该会话最近 limit 条消息（滑动窗口），按时间正序返回。"""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (conversation_id, max(1, limit)),
        ).fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]


def get_history(conversation_id: str) -> list[dict]:
    """取该会话的完整历史（供前端展示）。"""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content, created_at FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_id,),
        ).fetchall()
    return [
        {"role": row["role"], "content": row["content"], "created_at": row["created_at"]}
        for row in rows
    ]


def list_conversations() -> list[dict]:
    """列出所有会话：标题取第一条用户消息，附带消息数和最近更新时间。"""
    sql = """
        SELECT c.conversation_id,
               c.message_count,
               c.updated_at,
               (SELECT content FROM conversation_messages m
                WHERE m.conversation_id = c.conversation_id AND m.role = 'user'
                ORDER BY m.id LIMIT 1) AS title
        FROM (
            SELECT conversation_id, COUNT(*) AS message_count, MAX(created_at) AS updated_at
            FROM conversation_messages
            GROUP BY conversation_id
        ) c
        ORDER BY c.updated_at DESC, c.conversation_id DESC
    """
    with get_connection() as connection:
        rows = connection.execute(sql).fetchall()
    return [
        {
            "conversation_id": row["conversation_id"],
            "title": row["title"],
            "message_count": row["message_count"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


def delete_conversation(conversation_id: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM conversation_messages WHERE conversation_id = ?",
            (conversation_id,),
        )
        connection.commit()
    return cursor.rowcount > 0
