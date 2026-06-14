"""Tool Use（函数调用）的工具定义与分发。

- TOOL_SPECS: 交给大模型的工具清单（JSON Schema），描述每个工具的名字、用途和参数。
  description 写得越清楚，模型越知道「什么时候该调、传什么参数」。
- dispatch_tool: 把模型选中的工具名 + 参数，路由到真正的服务函数并执行，返回 JSON 文本。
"""

import json

from app.models.schemas import (
    ContextCardCreate,
    ContextCardRecommendRequest,
    ContextCardUpdate,
    GenerateRequest,
    GenerationHistoryCreate,
    PromptTemplateCreate,
    PromptTemplateUpdate,
)
from app.services.context_card_service import (
    create_context_card,
    delete_context_card,
    get_context_card_by_id,
    recommend_context_cards,
    update_context_card,
)
from app.services.generate_service import generate_prompt
from app.services.history_service import create_history, list_history
from app.services.template_service import (
    create_template,
    delete_template,
    get_template_by_id,
    recommend_templates,
    update_template,
)


TOOL_SPECS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_context_cards",
            "description": (
                "根据需求文本，从上下文卡片库检索最相关的卡片。"
                "卡片类型包括：背景资料、写作规则、输出格式、参考示例、检查清单。"
                "当用户想找资料、规则、示例或参考时调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "用于检索的需求描述文本",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回卡片数量上限，默认 5",
                        "minimum": 1,
                        "maximum": 20,
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_prompt_templates",
            "description": (
                "按需求语义检索已保存的 Prompt 模板(按意思找，不只是关键词)。"
                "当用户想找、套用或参考某类 Prompt 模板时调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "需求描述文本，用于语义检索",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回模板数量上限，默认 5",
                        "minimum": 1,
                        "maximum": 20,
                    },
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_context_card",
            "description": (
                "创建一张新的上下文卡片并存入卡片库（写操作）。"
                "当用户明确要求新增 / 保存一张卡片时调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "卡片类型",
                        "enum": ["background", "rule", "format", "example", "checklist"],
                    },
                    "title": {"type": "string", "description": "卡片标题"},
                    "content": {"type": "string", "description": "卡片正文内容"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "标签列表，可选",
                    },
                },
                "required": ["type", "title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_with_template",
            "description": (
                "用指定的 Prompt 模板填入变量、挂载上下文卡片，组装出一份完整的 Prompt 草稿。"
                "通常需要先用 search_prompt_templates 拿到模板 id，"
                "用 search_context_cards 拿到卡片 id，再调用本工具。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "integer",
                        "description": "模板 id（来自 search_prompt_templates）",
                    },
                    "variables": {
                        "type": "object",
                        "description": '模板变量的键值对，例如 {"材料": "..."}',
                    },
                    "context_card_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要挂载的上下文卡片 id 列表（来自 search_context_cards），可选",
                    },
                },
                "required": ["template_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_context_card",
            "description": (
                "修改一张已有的上下文卡片(写操作)。只需提供要改的字段，未提供的保持不变。"
                "先用 search_context_cards 拿到卡片 id。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "要修改的卡片 id"},
                    "type": {
                        "type": "string",
                        "description": "卡片类型，可选",
                        "enum": ["background", "rule", "format", "example", "checklist"],
                    },
                    "title": {"type": "string", "description": "新标题，可选"},
                    "content": {"type": "string", "description": "新正文，可选"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "新标签，可选",
                    },
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_context_card",
            "description": "删除一张上下文卡片(写操作，不可恢复)。先用 search_context_cards 确认 id。",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "要删除的卡片 id"},
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_prompt_template",
            "description": "创建一个新的 Prompt 模板(写操作)。模板内容里可用 {变量名} 作占位符。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "模板标题"},
                    "content": {"type": "string", "description": "模板内容，可含 {变量} 占位符"},
                    "category": {"type": "string", "description": "分类，可选"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "标签，可选",
                    },
                    "description": {"type": "string", "description": "模板说明，可选"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_prompt_template",
            "description": (
                "修改一个已有的 Prompt 模板(写操作)。只需提供要改的字段，未提供的保持不变。"
                "先用 search_prompt_templates 拿到 id。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "要修改的模板 id"},
                    "title": {"type": "string", "description": "新标题，可选"},
                    "content": {"type": "string", "description": "新内容，可选"},
                    "category": {"type": "string", "description": "新分类，可选"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "新标签，可选",
                    },
                    "description": {"type": "string", "description": "新说明，可选"},
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_prompt_template",
            "description": "删除一个 Prompt 模板(写操作，不可恢复)。先用 search_prompt_templates 确认 id。",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "要删除的模板 id"},
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_history",
            "description": (
                "把一份生成好的 Prompt 保存到生成历史(写操作)。"
                "通常在 draft_with_template 之后，用同一个 template_id 和最终 Prompt 调用。"
                "template_id 必须是已存在的模板。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "integer", "description": "来源模板 id（必须存在）"},
                    "final_prompt": {"type": "string", "description": "要保存的最终 Prompt 全文"},
                    "variables": {"type": "object", "description": "模板变量键值对，可选"},
                    "context_card_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "挂载的卡片 id，可选",
                    },
                },
                "required": ["template_id", "final_prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_history",
            "description": "列出最近保存的生成历史(读)。",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "返回条数，默认 10"},
                },
            },
        },
    },
]


def _tool_search_context_cards(arguments: dict) -> str:
    request = ContextCardRecommendRequest(
        text=arguments.get("text", ""),
        limit=arguments.get("limit", 5),
    )
    cards = recommend_context_cards(request)  # 语义检索(已是唯一实现)
    return json.dumps(
        [
            {"id": card.id, "type": card.type, "title": card.title, "content": card.content}
            for card in cards
        ],
        ensure_ascii=False,
    )


def _tool_search_prompt_templates(arguments: dict) -> str:
    templates = recommend_templates(
        arguments.get("keyword", ""),
        arguments.get("limit", 5),
    )
    return json.dumps(
        [
            {"id": item.id, "title": item.title, "category": item.category, "content": item.content}
            for item in templates
        ],
        ensure_ascii=False,
    )


def _tool_create_context_card(arguments: dict) -> str:
    card = create_context_card(
        ContextCardCreate(
            type=arguments.get("type", "background"),
            title=arguments.get("title", ""),
            content=arguments.get("content", ""),
            tags=arguments.get("tags", []),
        )
    )
    return json.dumps(
        {"created": True, "id": card.id, "type": card.type, "title": card.title},
        ensure_ascii=False,
    )


def _tool_draft_with_template(arguments: dict) -> str:
    result = generate_prompt(
        GenerateRequest(
            template_id=arguments.get("template_id"),
            variables=arguments.get("variables") or {},
            context_card_ids=arguments.get("context_card_ids") or [],
        )
    )
    return json.dumps(
        {"final_prompt": result.final_prompt, "missing_variables": result.missing_variables},
        ensure_ascii=False,
    )


def _tool_update_context_card(arguments: dict) -> str:
    # 部分更新:先取现值,只覆盖传进来的字段(不存在的 id 会抛 ContextCardNotFoundError)
    current = get_context_card_by_id(arguments.get("id"))
    updated = update_context_card(
        arguments.get("id"),
        ContextCardUpdate(
            type=arguments.get("type", current.type),
            title=arguments.get("title", current.title),
            content=arguments.get("content", current.content),
            tags=arguments.get("tags", current.tags),
        ),
    )
    return json.dumps(
        {"updated": True, "id": updated.id, "title": updated.title, "type": updated.type},
        ensure_ascii=False,
    )


def _tool_delete_context_card(arguments: dict) -> str:
    card_id = arguments.get("id")
    delete_context_card(card_id)  # 不存在会抛 ContextCardNotFoundError
    return json.dumps({"deleted": True, "id": card_id}, ensure_ascii=False)


def _tool_create_prompt_template(arguments: dict) -> str:
    template = create_template(
        PromptTemplateCreate(
            title=arguments.get("title", ""),
            content=arguments.get("content", ""),
            category=arguments.get("category"),
            tags=arguments.get("tags", []),
            description=arguments.get("description"),
        )
    )
    return json.dumps({"created": True, "id": template.id, "title": template.title}, ensure_ascii=False)


def _tool_update_prompt_template(arguments: dict) -> str:
    current = get_template_by_id(arguments.get("id"))  # 不存在会抛 TemplateNotFoundError
    updated = update_template(
        arguments.get("id"),
        PromptTemplateUpdate(
            title=arguments.get("title", current.title),
            content=arguments.get("content", current.content),
            category=arguments.get("category", current.category),
            tags=arguments.get("tags", current.tags),
            description=arguments.get("description", current.description),
        ),
    )
    return json.dumps({"updated": True, "id": updated.id, "title": updated.title}, ensure_ascii=False)


def _tool_delete_prompt_template(arguments: dict) -> str:
    template_id = arguments.get("id")
    delete_template(template_id)  # 不存在会抛 TemplateNotFoundError
    return json.dumps({"deleted": True, "id": template_id}, ensure_ascii=False)


def _tool_save_to_history(arguments: dict) -> str:
    record = create_history(
        GenerationHistoryCreate(
            template_id=arguments.get("template_id"),
            final_prompt=arguments.get("final_prompt", ""),
            variables=arguments.get("variables") or {},
            context_card_ids=arguments.get("context_card_ids") or [],
        )
    )
    return json.dumps({"saved": True, "id": record.id}, ensure_ascii=False)


def _tool_list_history(arguments: dict) -> str:
    records = list_history(limit=arguments.get("limit", 10))
    return json.dumps(
        [
            {
                "id": record.id,
                "template_id": record.template_id,
                "final_prompt": record.final_prompt,
                "created_at": record.created_at,
            }
            for record in records
        ],
        ensure_ascii=False,
    )


# 写工具：会改数据库，必须用户授权(allow_write)才放行；其余为只读工具，随时可调。
WRITE_TOOLS = {
    "create_context_card",
    "update_context_card",
    "delete_context_card",
    "create_prompt_template",
    "update_prompt_template",
    "delete_prompt_template",
    "save_to_history",
}

_TOOL_DISPATCH = {
    "search_context_cards": _tool_search_context_cards,
    "search_prompt_templates": _tool_search_prompt_templates,
    "create_context_card": _tool_create_context_card,
    "update_context_card": _tool_update_context_card,
    "delete_context_card": _tool_delete_context_card,
    "draft_with_template": _tool_draft_with_template,
    "create_prompt_template": _tool_create_prompt_template,
    "update_prompt_template": _tool_update_prompt_template,
    "delete_prompt_template": _tool_delete_prompt_template,
    "save_to_history": _tool_save_to_history,
    "list_history": _tool_list_history,
}


def dispatch_tool(name: str, arguments: dict, allow_write: bool = False) -> str:
    """执行工具并返回 JSON 文本。

    - 写工具(WRITE_TOOLS)会改数据库，只有用户授权(allow_write=True)才放行，
      否则直接拒绝、不碰数据。这道"安全闸"放在代码层，不依赖模型自觉。
    - 工具内部出错不中断对话，把错误信息回传给模型，让它自己决定下一步
      （换参数重试 / 改用别的工具 / 直接说明情况）。
    """
    if name in WRITE_TOOLS and not allow_write:
        return json.dumps(
            {"error": "用户未授权写操作，已拒绝。请提示用户开启“允许修改数据”后重试。"},
            ensure_ascii=False,
        )
    handler = _TOOL_DISPATCH.get(name)
    if handler is None:
        return json.dumps({"error": f"未知工具：{name}"}, ensure_ascii=False)
    try:
        return handler(arguments)
    except Exception as error:  # noqa: BLE001 - 工具层的兜底，错误回传给模型而非抛出
        return json.dumps({"error": f"工具执行失败：{error}"}, ensure_ascii=False)
