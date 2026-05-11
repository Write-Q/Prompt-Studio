import json
import sqlite3
from datetime import datetime
from pathlib import Path


# 当前脚本位于项目根目录，所以可以直接定位到 data/app.db
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"


def now_text() -> str:
    """生成统一的当前时间字符串。"""
    return datetime.now().isoformat(timespec="seconds")


def tags_text(tags: list[str]) -> str:
    """把 Python 列表转换成数据库里保存的 JSON 字符串。"""
    return json.dumps(tags, ensure_ascii=False)


def insert_template_if_missing(cursor: sqlite3.Cursor, item: dict) -> bool:
    """
    插入 Prompt 模板测试数据。

    这里用 title 判断是否已经存在，避免重复运行脚本时插入重复数据。
    """
    exists = cursor.execute(
        "SELECT id FROM prompt_templates WHERE title = ?",
        (item["title"],),
    ).fetchone()

    if exists:
        return False

    current_time = now_text()
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
            item["title"],
            item["category"],
            tags_text(item["tags"]),
            item["content"],
            item["description"],
            current_time,
            current_time,
        ),
    )
    return True


def insert_snippet_if_missing(cursor: sqlite3.Cursor, item: dict) -> bool:
    """
    插入知识片段测试数据。

    同样用 title 判断是否已存在，保证脚本可以安全重复运行。
    """
    exists = cursor.execute(
        "SELECT id FROM knowledge_snippets WHERE title = ?",
        (item["title"],),
    ).fetchone()

    if exists:
        return False

    current_time = now_text()
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
            item["title"],
            tags_text(item["tags"]),
            item["content"],
            item["source"],
            current_time,
            current_time,
        ),
    )
    return True


TEMPLATES = [
    {
        "title": "日程规划助手",
        "category": "生活",
        "tags": ["时间管理", "计划", "生活"],
        "description": "把一段杂乱安排整理成清晰的每日计划。",
        "content": "请根据以下事项，为我制定一份{日期}的日程安排。我的优先级是{优先级}，可用时间是{可用时间}。\n事项：\n{输入内容}\n请输出：时间段、具体任务、注意事项。",
    },
    {
        "title": "学习笔记整理",
        "category": "学习",
        "tags": ["学习", "笔记", "总结"],
        "description": "把课堂或阅读内容整理成结构化学习笔记。",
        "content": "请把下面的学习内容整理成{风格}的笔记，重点面向{学习阶段}学生。\n内容：\n{输入内容}\n请包含：核心概念、关键例子、容易混淆点、复习建议。",
    },
    {
        "title": "文章润色改写",
        "category": "写作",
        "tags": ["写作", "润色", "表达"],
        "description": "按指定语气润色一段文字。",
        "content": "请将以下文字改写成{语气}风格，长度控制在{长度}，目标读者是{目标读者}。\n原文：\n{输入内容}\n请保留原意，让表达更自然。",
    },
    {
        "title": "工作周报生成",
        "category": "工作",
        "tags": ["周报", "工作", "汇报"],
        "description": "根据零散工作记录生成一份周报。",
        "content": "请根据以下工作记录，生成一份{周期}工作周报。\n角色：{角色}\n工作记录：\n{输入内容}\n请包含：本周完成、遇到问题、下周计划、需要协助。",
    },
    {
        "title": "代码学习解释",
        "category": "编程",
        "tags": ["代码", "学习", "解释"],
        "description": "用适合初学者的方式解释代码。",
        "content": "请用{讲解深度}的方式解释下面这段代码，默认我会{已有基础}。\n代码：\n{输入内容}\n请按照：整体作用、逐段解释、关键语法、常见错误来说明。",
    },
    {
        "title": "健身计划建议",
        "category": "健康",
        "tags": ["健身", "健康", "计划"],
        "description": "根据目标生成一份基础健身计划。",
        "content": "请根据我的情况制定一份{周期}健身计划。\n目标：{目标}\n可用器械：{器械}\n身体情况：{输入内容}\n请给出训练安排、注意事项和恢复建议。",
    },
    {
        "title": "旅行攻略规划",
        "category": "生活",
        "tags": ["旅行", "攻略", "预算"],
        "description": "根据目的地和偏好生成旅行计划。",
        "content": "请为我规划一份{天数}旅行攻略。\n目的地：{目的地}\n预算：{预算}\n偏好：{输入内容}\n请包含路线、餐饮、交通、注意事项。",
    },
    {
        "title": "面试准备清单",
        "category": "职业",
        "tags": ["面试", "求职", "准备"],
        "description": "根据岗位生成面试准备建议。",
        "content": "请帮我准备{岗位}岗位的面试。\n我的背景：{输入内容}\n目标公司类型：{公司类型}\n请输出：常见问题、回答思路、项目复盘重点、临场提醒。",
    },
]


SNIPPETS = [
    {
        "title": "日程规划基本原则",
        "tags": ["时间管理", "计划", "生活"],
        "source": "测试数据",
        "content": "安排日程时建议先固定不可移动事项，再安排高优先级任务，最后预留缓冲时间。任务不要排满，避免计划一变就整体失控。",
    },
    {
        "title": "学习笔记四段法",
        "tags": ["学习", "笔记", "总结"],
        "source": "测试数据",
        "content": "一份好笔记可以分成四部分：概念解释、例子说明、易错点、复习问题。这样既方便理解，也方便后续复盘。",
    },
    {
        "title": "文字润色检查点",
        "tags": ["写作", "润色", "表达"],
        "source": "测试数据",
        "content": "润色时优先检查语义是否清楚，再检查句子是否顺滑，最后调整语气。不要为了华丽表达牺牲准确性。",
    },
    {
        "title": "周报常见结构",
        "tags": ["周报", "工作", "汇报"],
        "source": "测试数据",
        "content": "周报可以采用：本周完成、关键成果、问题风险、下周计划、需要支持。内容要具体，尽量用结果和数据表达。",
    },
    {
        "title": "代码解释给初学者的顺序",
        "tags": ["代码", "学习", "解释"],
        "source": "测试数据",
        "content": "解释代码时先讲它解决什么问题，再讲输入输出，最后逐段说明实现。不要一开始就进入语法细节，否则初学者容易迷路。",
    },
    {
        "title": "健身计划安全提醒",
        "tags": ["健身", "健康", "计划"],
        "source": "测试数据",
        "content": "健身计划应循序渐进。新手优先保证动作标准和恢复时间，避免一开始追求过高强度。如果有疾病或疼痛，应先咨询专业人士。",
    },
    {
        "title": "旅行规划优先级",
        "tags": ["旅行", "攻略", "预算"],
        "source": "测试数据",
        "content": "旅行规划建议先确定预算和交通，再安排住宿和景点。热门景点要提前查看预约规则，行程中最好保留半天弹性时间。",
    },
    {
        "title": "面试项目复盘要点",
        "tags": ["面试", "求职", "项目"],
        "source": "测试数据",
        "content": "项目复盘可以按背景、目标、方案、难点、结果、反思来讲。重点突出你负责了什么、解决了什么问题、产生了什么价值。",
    },
    {
        "title": "Prompt 编写基础原则",
        "tags": ["Prompt", "模板", "规则"],
        "source": "测试数据",
        "content": "一个清晰的 Prompt 通常包含角色、任务、输入、约束和输出格式。变量占位符要命名清楚，例如 {语气}、{长度}、{输入内容}。",
    },
    {
        "title": "总结类任务输出格式",
        "tags": ["总结", "结构化", "输出"],
        "source": "测试数据",
        "content": "总结类任务可以要求输出：一句话概括、要点列表、行动建议。这样结果更容易阅读，也更方便复制到其他场景中使用。",
    },
]


def main() -> None:
    """写入测试数据并输出插入结果。"""
    inserted_templates = 0
    inserted_snippets = 0

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        for item in TEMPLATES:
            if insert_template_if_missing(cursor, item):
                inserted_templates += 1

        for item in SNIPPETS:
            if insert_snippet_if_missing(cursor, item):
                inserted_snippets += 1

        connection.commit()

        template_count = cursor.execute(
            "SELECT COUNT(*) FROM prompt_templates"
        ).fetchone()[0]
        snippet_count = cursor.execute(
            "SELECT COUNT(*) FROM knowledge_snippets"
        ).fetchone()[0]

    print(f"新增模板：{inserted_templates} 条")
    print(f"新增知识片段：{inserted_snippets} 条")
    print(f"当前模板总数：{template_count} 条")
    print(f"当前知识片段总数：{snippet_count} 条")


if __name__ == "__main__":
    main()
