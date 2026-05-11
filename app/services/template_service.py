import json
from datetime import datetime

from app.database import get_connection
from app.models.schemas import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)


class TemplateNotFoundError(Exception):
    """
    模板不存在异常。

    后续路由层可以捕获这个异常，并转成 404 响应。
    """


def _get_current_time_text() -> str:
    """
    生成当前时间文本。

    当前先统一使用 ISO 格式字符串，
    这样数据库存储和接口返回都比较直观。
    """
    return datetime.now().isoformat(timespec="seconds")


def _serialize_tags(tags: list[str]) -> str:
    """
    把标签列表转换成数据库可存储的文本。

    虽然数据库里的 tags 字段是 TEXT，
    但我们不直接用逗号拼接，而是先存成 JSON 字符串，
    这样后续解析更稳定。
    """
    return json.dumps(tags, ensure_ascii=False)


def _deserialize_tags(tags_text: str | None) -> list[str]:
    """
    把数据库里的标签文本还原成列表。

    当前优先按 JSON 格式解析。
    如果后续遇到旧数据不是 JSON，也做一个逗号拆分兜底。
    """
    if not tags_text:
        return []

    try:
        parsed_value = json.loads(tags_text)
        if isinstance(parsed_value, list):
            return [str(tag).strip() for tag in parsed_value if str(tag).strip()]
    except json.JSONDecodeError:
        pass

    # 兜底兼容旧格式，例如 "写作,总结"
    raw_tags = tags_text.replace("，", ",").split(",")
    return [tag.strip() for tag in raw_tags if tag.strip()]


def _build_template_response(row: dict) -> PromptTemplateResponse:
    """
    把数据库查询结果转换成响应模型。

    这样服务层对外返回的数据结构就统一了，
    路由层不需要再手动拼字典。
    """
    return PromptTemplateResponse(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        tags=_deserialize_tags(row["tags"]),
        content=row["content"],
        description=row["description"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_template(payload: PromptTemplateCreate) -> PromptTemplateResponse:
    """
    新增一个 Prompt 模板。
    """
    current_time = _get_current_time_text()

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO prompt_templates (
                title,
                category,
                tags,
                content,
                description,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                payload.category,
                _serialize_tags(payload.tags),
                payload.content,
                payload.description,
                current_time,
                current_time,
            ),
        )
        connection.commit()
        template_id = cursor.lastrowid

    return get_template_by_id(template_id)


def list_templates(
    category: str | None = None,
    keyword: str | None = None,
) -> list[PromptTemplateResponse]:
    """
    获取模板列表，并支持分类筛选和关键词搜索。

    当前关键词搜索会匹配：
    - title
    - content
    - description
    - tags
    """
    sql = """
        SELECT
            id,
            title,
            category,
            tags,
            content,
            description,
            created_at,
            updated_at
        FROM prompt_templates
        WHERE 1 = 1
    """
    params: list[str] = []

    if category and category.strip():
        sql += " AND category = ?"
        params.append(category.strip())

    if keyword and keyword.strip():
        keyword_text = f"%{keyword.strip()}%"
        sql += """
            AND (
                title LIKE ?
                OR content LIKE ?
                OR description LIKE ?
                OR tags LIKE ?
            )
        """
        params.extend([keyword_text, keyword_text, keyword_text, keyword_text])

    sql += " ORDER BY updated_at DESC, id DESC"

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return [_build_template_response(row) for row in rows]


def get_template_by_id(template_id: int) -> PromptTemplateResponse:
    """
    根据 id 获取单个模板详情。
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                id,
                title,
                category,
                tags,
                content,
                description,
                created_at,
                updated_at
            FROM prompt_templates
            WHERE id = ?
            """,
            (template_id,),
        )
        row = cursor.fetchone()

    if row is None:
        raise TemplateNotFoundError(f"ID 为 {template_id} 的模板不存在")

    return _build_template_response(row)


def update_template(
    template_id: int,
    payload: PromptTemplateUpdate,
) -> PromptTemplateResponse:
    """
    更新指定模板。

    当前按“整条更新”的方式处理，
    也就是要求前端把完整字段一起提交过来。
    """
    current_time = _get_current_time_text()

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE prompt_templates
            SET
                title = ?,
                category = ?,
                tags = ?,
                content = ?,
                description = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                payload.title,
                payload.category,
                _serialize_tags(payload.tags),
                payload.content,
                payload.description,
                current_time,
                template_id,
            ),
        )
        connection.commit()

        if cursor.rowcount == 0:
            raise TemplateNotFoundError(f"ID 为 {template_id} 的模板不存在")

    return get_template_by_id(template_id)


def delete_template(template_id: int) -> bool:
    """
    删除指定模板。
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM prompt_templates WHERE id = ?",
            (template_id,),
        )
        connection.commit()

        if cursor.rowcount == 0:
            raise TemplateNotFoundError(f"ID 为 {template_id} 的模板不存在")

    return True
