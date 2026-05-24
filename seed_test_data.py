import json
import sqlite3
from datetime import datetime
from pathlib import Path

from app.database import init_db


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"


def now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def tags_text(tags: list[str]) -> str:
    return json.dumps(tags, ensure_ascii=False)


TEMPLATES = [
    {
        "seed_key": "daily_schedule_planner",
        "title": "日程规划助手",
        "category": "个人效率",
        "tags": ["日程", "计划", "优先级"],
        "description": "把零散任务整理成可执行的日程安排，适合规划一天、一周或某个阶段的工作与生活事项。",
        "content": """你是一位擅长时间管理和现实规划的日程助手。

请根据我的输入，帮我制定一份{计划周期}的安排。

我的可用时间：
{可用时间}

我的精力状态：
{精力状态}

需要安排的事项：
{待安排事项}

请按以下要求输出：
1. 先判断哪些事情最重要、最紧急。
2. 把任务安排到合适的时间段。
3. 标出可以延后、合并或删减的事项。
4. 给出一份不过度理想化、能实际执行的计划。
5. 最后补充 3 条执行提醒。""",
    },
    {
        "seed_key": "study_notes_organizer",
        "title": "学习笔记整理",
        "category": "学习成长",
        "tags": ["学习", "笔记", "复习"],
        "description": "把课程、文章或零散笔记整理成便于理解和复习的学习材料。",
        "content": """你是一位学习教练，请帮我整理下面的学习材料。

学习主题：
{学习主题}

学习目标：
{学习目标}

学习材料：
{学习材料}

请输出：
1. 核心概念和简明解释。
2. 知识点之间的关系。
3. 关键例子或应用场景。
4. 容易混淆的地方。
5. 5 个自测问题和参考答案。
6. 下一步复习建议。""",
    },
    {
        "seed_key": "material_summary_extractor",
        "title": "资料总结与重点提取",
        "category": "信息整理",
        "tags": ["总结", "提炼", "资料"],
        "description": "从长文本或多段资料中提取重点、结论、待确认事项和可执行下一步。",
        "content": """请把下面的资料整理成一份清晰摘要。

资料类型：
{资料类型}

总结目的：
{总结目的}

目标读者：
{目标读者}

资料内容：
{资料内容}

请输出：
1. 一句话概括。
2. 关键要点。
3. 对目标读者最重要的信息。
4. 尚不明确或需要核验的内容。
5. 可执行的下一步。""",
    },
    {
        "seed_key": "article_polish_rewrite",
        "title": "文章润色改写",
        "category": "写作表达",
        "tags": ["润色", "改写", "写作"],
        "description": "在保留原意的前提下优化文章表达，让结构更顺、语气更稳、重点更清楚。",
        "content": """请帮我润色和改写下面的文字。

改写目标：
{改写目标}

目标读者：
{目标读者}

必须保留的内容：
{保留要求}

原文：
{原文}

请按以下方式处理：
1. 先指出原文最需要改进的 3 个问题。
2. 给出改写后的版本。
3. 列出关键修改说明。
4. 不改变原文核心意思，不补充未提供的事实。""",
    },
    {
        "seed_key": "weekly_report_organizer",
        "title": "工作周报整理",
        "category": "工作沟通",
        "tags": ["周报", "复盘", "汇报"],
        "description": "把零散工作记录整理成清晰、克制、面向协作的周报或阶段复盘。",
        "content": """请把下面的工作记录整理成一份清晰的周报。

角色：
{角色}

周期：
{周期}

目标读者：
{目标读者}

工作记录：
{工作记录}

请输出：
1. 本周期重点。
2. 已完成事项。
3. 关键进展与影响。
4. 问题、风险和阻塞。
5. 下周期计划。
6. 需要协作或决策的事项。""",
    },
    {
        "seed_key": "meeting_minutes_organizer",
        "title": "会议纪要整理",
        "category": "工作沟通",
        "tags": ["会议", "纪要", "行动项"],
        "description": "把会议记录整理成结论明确、责任清楚、便于跟进的会议纪要。",
        "content": """请根据下面的会议记录整理会议纪要。

会议主题：
{会议主题}

参会对象：
{参会对象}

会议记录：
{会议记录}

请输出：
1. 会议目标。
2. 已确认结论。
3. 关键讨论点。
4. 待办事项，包含负责人、完成标准和时间要求。
5. 待确认问题。
6. 下一次跟进建议。""",
    },
    {
        "seed_key": "communication_expression_optimizer",
        "title": "沟通表达优化",
        "category": "写作表达",
        "tags": ["沟通", "表达", "消息"],
        "description": "把想说的话改成更清楚、更得体、更容易推进事情的表达。",
        "content": """请帮我优化下面这段沟通表达。

沟通对象：
{沟通对象}

沟通目标：
{沟通目标}

原始表达：
{原始表达}

请输出：
1. 更直接清楚的版本。
2. 更委婉稳妥的版本。
3. 适合正式场景的版本。
4. 每个版本适合使用的场景。
5. 需要避免的表达风险。""",
    },
    {
        "seed_key": "travel_plan_builder",
        "title": "旅行攻略规划",
        "category": "生活助理",
        "tags": ["旅行", "攻略", "规划"],
        "description": "根据目的地、天数、预算和偏好规划更顺路、更现实的旅行安排。",
        "content": """请帮我规划一份旅行攻略。

目的地：
{目的地}

出行天数：
{出行天数}

预算范围：
{预算范围}

偏好和限制：
{偏好限制}

同行人和特殊需求：
{同行人和特殊需求}

请输出：
1. 每天的行程安排。
2. 交通和路线建议。
3. 餐饮和休息安排。
4. 预算分配建议。
5. 需要提前准备或核验的事项。
6. 如果时间或预算紧张，给出取舍建议。""",
    },
    {
        "seed_key": "product_comparison_decision",
        "title": "商品对比决策",
        "category": "生活助理",
        "tags": ["购物", "对比", "决策"],
        "description": "把购买需求和候选商品整理成对比表，帮助做出更稳妥的选择。",
        "content": """请帮我比较候选商品并给出购买建议。

购买需求：
{购买需求}

候选商品：
{候选商品}

关键标准：
{关键标准}

当前顾虑：
{当前顾虑}

请输出：
1. 我的真实需求判断。
2. 候选商品对比表。
3. 每个选项的优点、风险和适合人群。
4. 推荐选择和理由。
5. 不建议购买的情况。
6. 下单前需要核验的信息。""",
    },
    {
        "seed_key": "weekly_meal_planner",
        "title": "一周饮食计划",
        "category": "生活助理",
        "tags": ["饮食", "健康", "计划"],
        "description": "根据饮食目标、人数和限制安排一周菜单，同时兼顾准备成本和执行难度。",
        "content": """请帮我制定一份一周饮食计划。

饮食目标：
{饮食目标}

人数：
{人数}

预算范围：
{预算范围}

忌口或限制：
{忌口限制}

现有食材和烹饪条件：
{现有食材和烹饪条件}

请输出：
1. 一周早餐、午餐、晚餐安排。
2. 食材采购清单。
3. 可以提前准备的部分。
4. 替换方案。
5. 执行难度和注意事项。""",
    },
]


CONTEXT_CARDS = [
    {
        "seed_key": "background_promptstudio_daily_use",
        "type": "background",
        "title": "PromptStudio 日常使用方式",
        "tags": ["PromptStudio", "日常", "工作流"],
        "content": "模板适合保存高频任务的稳定结构，上下文卡片适合保存可复用的背景、规则、格式、示例和检查清单。日常使用时，先选模板，再按任务补充少量卡片，避免一次放入过多无关内容。",
    },
    {
        "seed_key": "background_personal_productivity_context",
        "type": "background",
        "title": "个人效率场景",
        "tags": ["效率", "计划", "任务"],
        "content": "个人效率类任务通常关注优先级、可用时间、精力状态和执行阻力。输出应帮助用户做取舍，而不是把所有事项都安排进去。",
    },
    {
        "seed_key": "background_life_assistant_context",
        "type": "background",
        "title": "生活助理场景",
        "tags": ["生活", "助理", "规划"],
        "content": "生活助理类任务需要考虑预算、时间、偏好、限制和准备成本。建议应贴近日常执行，不要只给理想化方案。",
    },
    {
        "seed_key": "background_decision_making_context",
        "type": "background",
        "title": "日常决策关注点",
        "tags": ["决策", "对比", "风险"],
        "content": "日常决策通常不是寻找绝对最优，而是在需求、成本、风险和个人偏好之间找到合适选择。输出应说明推荐理由，也要指出不适合选择的情况。",
    },
    {
        "seed_key": "background_learning_and_writing_context",
        "type": "background",
        "title": "学习与写作场景",
        "tags": ["学习", "写作", "整理"],
        "content": "学习和写作任务要优先帮助用户理解、组织和表达。输出应突出主线、关键概念、例子和可复习内容，不要只做机械摘要。",
    },
    {
        "seed_key": "rule_plan_with_buffer",
        "type": "rule",
        "title": "计划需要留缓冲",
        "tags": ["计划", "时间", "缓冲"],
        "content": "制定计划时，不要默认用户可以一直保持高效率。需要预留休息、切换任务和意外情况的时间；如果事项明显超出可用时间，要主动建议删减或延后。",
    },
    {
        "seed_key": "rule_prioritize_before_detail",
        "type": "rule",
        "title": "先排优先级",
        "tags": ["优先级", "任务", "取舍"],
        "content": "面对多项任务时，先区分重要紧急、重要不紧急、可委托、可延后。不要直接进入细节安排，否则容易把低价值事项也排得很满。",
    },
    {
        "seed_key": "rule_no_unverified_claims",
        "type": "rule",
        "title": "不补造未给信息",
        "tags": ["准确性", "事实", "边界"],
        "content": "不得把输入中没有提供的信息写成确定事实。涉及价格、营业时间、政策、健康、法律或其他可能变化的信息时，应提示用户自行核验或补充材料。",
    },
    {
        "seed_key": "rule_clear_natural_tone",
        "type": "rule",
        "title": "清楚自然的语气",
        "tags": ["语气", "表达", "写作"],
        "content": "默认语气应清楚、自然、克制。少用空泛口号和夸张赞美，优先给能直接使用的表达和步骤。",
    },
    {
        "seed_key": "rule_actionable_advice",
        "type": "rule",
        "title": "建议要能执行",
        "tags": ["建议", "执行", "行动"],
        "content": "建议应尽量写成具体动作，包含做什么、何时做、做到什么程度。避免只写提升效率、优化表达、注意健康这类抽象方向。",
    },
    {
        "seed_key": "rule_keep_user_constraints",
        "type": "rule",
        "title": "尊重用户限制",
        "tags": ["限制", "偏好", "约束"],
        "content": "用户提供的预算、时间、忌口、风格、目标读者和必须保留内容都应作为硬约束处理。如果建议与约束冲突，要说明原因并给替代方案。",
    },
    {
        "seed_key": "rule_when_information_missing",
        "type": "rule",
        "title": "信息不足时先说明",
        "tags": ["澄清", "假设", "不确定"],
        "content": "当关键信息缺失时，先说明缺口。如果用户需要直接产出，可以基于少量明确假设继续，但要把假设和待确认事项单独列出。",
    },
    {
        "seed_key": "format_daily_schedule",
        "type": "format",
        "title": "日程安排格式",
        "tags": ["格式", "日程", "计划"],
        "content": "日程建议按时间段输出，包含时间、任务、目的、注意事项。末尾列出可延后事项、缓冲时间和当天最重要的 1 到 3 件事。",
    },
    {
        "seed_key": "format_study_notes",
        "type": "format",
        "title": "学习笔记格式",
        "tags": ["格式", "学习", "笔记"],
        "content": "学习笔记建议包含主题概览、核心概念、概念关系、例子、常见误区、自测问题和复习建议。标题要短，方便后续回看。",
    },
    {
        "seed_key": "format_summary_brief",
        "type": "format",
        "title": "资料摘要格式",
        "tags": ["格式", "总结", "摘要"],
        "content": "资料摘要建议按一句话概括、关键要点、重要细节、待确认内容、下一步输出。长材料要优先总结对当前目的有帮助的信息。",
    },
    {
        "seed_key": "format_weekly_report",
        "type": "format",
        "title": "周报结构",
        "tags": ["格式", "周报", "汇报"],
        "content": "周报建议包含本周期重点、已完成事项、关键进展、问题风险、下周期计划和需要协作的事项。按结果归类，不按时间流水账排列。",
    },
    {
        "seed_key": "format_meeting_minutes",
        "type": "format",
        "title": "会议纪要结构",
        "tags": ["格式", "会议", "行动项"],
        "content": "会议纪要建议包含会议目标、已确认结论、关键讨论点、待办事项、待确认问题和下次跟进。行动项要写清负责人、完成标准和时间要求。",
    },
    {
        "seed_key": "format_comparison_table",
        "type": "format",
        "title": "对比选择表",
        "tags": ["格式", "对比", "决策"],
        "content": "对比多个选项时使用表格，列包含选项、适合情况、优点、风险、成本、推荐程度。表格后必须给出明确建议和选择理由。",
    },
    {
        "seed_key": "format_meal_plan",
        "type": "format",
        "title": "饮食计划格式",
        "tags": ["格式", "饮食", "计划"],
        "content": "饮食计划建议按日期列出三餐，另附采购清单、提前准备事项、替换方案和注意事项。不要给出难以采购或准备成本过高的安排。",
    },
    {
        "seed_key": "example_task_to_schedule",
        "type": "example",
        "title": "示例：模糊事项到日程安排",
        "tags": ["示例", "日程", "计划"],
        "content": "输入：写报告、买菜、运动、回消息、整理房间。输出应先判断优先级，再安排到时间段，并把低优先级事项放进可选清单。",
    },
    {
        "seed_key": "example_notes_to_review",
        "type": "example",
        "title": "示例：课堂笔记到复习材料",
        "tags": ["示例", "学习", "复习"],
        "content": "输入：一段课程笔记。输出应整理为核心概念、解释、例子、误区和自测题，方便复习，而不是只改写原文。",
    },
    {
        "seed_key": "example_raw_text_to_summary",
        "type": "example",
        "title": "示例：长资料到重点摘要",
        "tags": ["示例", "总结", "资料"],
        "content": "输入：多段会议材料或文章摘录。输出应先给一句话结论，再列关键要点、影响、待确认内容和下一步。",
    },
    {
        "seed_key": "example_sentence_to_message",
        "type": "example",
        "title": "示例：直接想法到得体表达",
        "tags": ["示例", "沟通", "表达"],
        "content": "输入：你怎么还没给我。优化后可以表达为：想确认一下这个事项目前的进展，方便我安排后续时间。这样更容易推进沟通。",
    },
    {
        "seed_key": "example_items_to_comparison",
        "type": "example",
        "title": "示例：候选商品到购买建议",
        "tags": ["示例", "购物", "决策"],
        "content": "输入：三个耳机型号和预算。输出应按需求、价格、续航、佩戴、风险和适合人群比较，最后给明确推荐。",
    },
    {
        "seed_key": "example_ingredients_to_meal_plan",
        "type": "example",
        "title": "示例：现有食材到菜单",
        "tags": ["示例", "饮食", "菜单"],
        "content": "输入：鸡蛋、番茄、青菜、鸡胸肉。输出应安排简单可执行的餐食，并说明哪些食材可提前处理、哪些可以替换。",
    },
    {
        "seed_key": "checklist_plan_before_execution",
        "type": "checklist",
        "title": "计划执行前检查",
        "tags": ["检查", "计划", "执行"],
        "content": "检查计划是否留出缓冲、是否有明确优先级、是否超出可用时间、是否包含下一步动作、是否把可延后事项单独列出。",
    },
    {
        "seed_key": "checklist_writing_before_send",
        "type": "checklist",
        "title": "发送前表达检查",
        "tags": ["检查", "沟通", "写作"],
        "content": "检查表达是否说明目的、是否语气合适、是否有多余情绪、是否给对方明确动作、是否容易被误解。",
    },
    {
        "seed_key": "checklist_summary_quality",
        "type": "checklist",
        "title": "摘要质量检查",
        "tags": ["检查", "摘要", "总结"],
        "content": "检查摘要是否保留核心信息、是否突出当前目的、是否区分事实和推断、是否遗漏关键限制、是否列出待确认内容。",
    },
    {
        "seed_key": "checklist_meeting_minutes",
        "type": "checklist",
        "title": "会议纪要检查",
        "tags": ["检查", "会议", "纪要"],
        "content": "检查纪要是否包含结论、行动项、负责人、完成标准、时间要求和待确认问题。没有明确负责人的事项不要写成已落实。",
    },
    {
        "seed_key": "checklist_decision_before_purchase",
        "type": "checklist",
        "title": "购买决策检查",
        "tags": ["检查", "购物", "决策"],
        "content": "检查推荐是否符合真实需求、预算和限制；是否说明风险；是否列出不建议购买的情况；是否提示下单前要核验的关键信息。",
    },
]


LEGACY_TEMPLATE_TITLE_TO_SEED_KEY = {
    "通用任务分析": "daily_schedule_planner",
    "学习笔记整理": "study_notes_organizer",
    "工作周报生成": "weekly_report_organizer",
    "工作复盘与周报汇报": "weekly_report_organizer",
    "项目需求拆解": "material_summary_extractor",
    "Prompt 优化": "communication_expression_optimizer",
}


LEGACY_TEMPLATE_TITLES_TO_DELETE = {
    "通用任务分析",
    "工作周报生成",
    "项目需求拆解",
    "Prompt 优化",
    "Prompt 需求澄清与模板生成",
    "Prompt 优化与失败诊断",
    "上下文卡片提炼器",
    "研究材料到决策简报",
    "产品需求拆解与 MVP 范围",
    "工作复盘与周报汇报",
    "代码学习解释",
    "健身计划建议",
    "面试准备清单",
    "论文选题拆解",
    "英语作文批改",
    "PPT 大纲生成",
    "邮件通知撰写",
    "短视频脚本生成",
    "社交媒体文案",
    "读书报告生成",
    "简历经历优化",
    "项目需求分析",
    "阶段复盘报告",
    "考试复习计划",
}


LEGACY_CONTEXT_CARD_TITLE_TO_SEED_KEY = {
    "PromptStudio 工作台使用模型": "background_promptstudio_daily_use",
    "项目背景：PromptStudio": "background_promptstudio_daily_use",
    "目标用户画像：知识工作者": "background_personal_productivity_context",
    "目标用户画像：个人知识工作者": "background_personal_productivity_context",
    "从想法到可执行输出": "background_life_assistant_context",
    "使用场景：从想法到可执行输出": "background_life_assistant_context",
    "对比决策表格式": "format_comparison_table",
    "行动清单格式": "format_daily_schedule",
    "示例：学习材料到复习卡片": "example_notes_to_review",
    "生成结果事实检查清单": "checklist_summary_quality",
    "交付前自检清单": "checklist_plan_before_execution",
}


LEGACY_CONTEXT_CARD_TITLES_TO_DELETE = {
    "上下文预算原则",
    "先澄清再生成",
    "事实与推断边界",
    "默认写作语气",
    "Few-shot 示例质量规则",
    "工程实现克制原则",
    "分层输出格式",
    "Prompt 模板规格",
    "示例：记录到结构化周报",
    "示例：想法到 MVP 范围",
    "示例：模糊 Prompt 到可评估 Prompt",
    "Prompt 质量检查清单",
    "事实准确性检查清单",
}


def _legacy_titles_for_seed_key(mapping: dict[str, str], seed_key: str) -> list[str]:
    return [title for title, mapped_seed_key in mapping.items() if mapped_seed_key == seed_key]


def _find_builtin_row(
    cursor: sqlite3.Cursor,
    table: str,
    seed_key: str,
    legacy_titles: list[str],
) -> sqlite3.Row | None:
    row = cursor.execute(
        f"SELECT * FROM {table} WHERE seed_key = ?",
        (seed_key,),
    ).fetchone()
    if row is not None:
        return row

    for title in legacy_titles:
        row = cursor.execute(
            f"SELECT * FROM {table} WHERE seed_key IS NULL AND title = ? ORDER BY id LIMIT 1",
            (title,),
        ).fetchone()
        if row is not None:
            return row

    return None


def _row_differs(row: sqlite3.Row, values: dict[str, str | None]) -> bool:
    return any(row[key] != value for key, value in values.items())


def upsert_template(cursor: sqlite3.Cursor, item: dict) -> str:
    values = {
        "seed_key": item["seed_key"],
        "title": item["title"],
        "category": item["category"],
        "tags": tags_text(item["tags"]),
        "content": item["content"],
        "description": item["description"],
    }
    row = _find_builtin_row(
        cursor,
        "prompt_templates",
        item["seed_key"],
        _legacy_titles_for_seed_key(LEGACY_TEMPLATE_TITLE_TO_SEED_KEY, item["seed_key"]),
    )
    current_time = now_text()

    if row is None:
        cursor.execute(
            """
            INSERT INTO prompt_templates (
                seed_key, title, category, tags, content, description, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                values["seed_key"],
                values["title"],
                values["category"],
                values["tags"],
                values["content"],
                values["description"],
                current_time,
                current_time,
            ),
        )
        return "inserted"

    if not _row_differs(row, values):
        return "unchanged"

    cursor.execute(
        """
        UPDATE prompt_templates
        SET seed_key = ?, title = ?, category = ?, tags = ?, content = ?, description = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            values["seed_key"],
            values["title"],
            values["category"],
            values["tags"],
            values["content"],
            values["description"],
            current_time,
            row["id"],
        ),
    )
    return "updated"


def upsert_context_card(cursor: sqlite3.Cursor, item: dict) -> str:
    values = {
        "seed_key": item["seed_key"],
        "type": item["type"],
        "title": item["title"],
        "tags": tags_text(item["tags"]),
        "content": item["content"],
    }
    row = _find_builtin_row(
        cursor,
        "context_cards",
        item["seed_key"],
        _legacy_titles_for_seed_key(LEGACY_CONTEXT_CARD_TITLE_TO_SEED_KEY, item["seed_key"]),
    )
    current_time = now_text()

    if row is None:
        cursor.execute(
            """
            INSERT INTO context_cards (
                seed_key, type, title, tags, content, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                values["seed_key"],
                values["type"],
                values["title"],
                values["tags"],
                values["content"],
                current_time,
                current_time,
            ),
        )
        return "inserted"

    if not _row_differs(row, values):
        return "unchanged"

    cursor.execute(
        """
        UPDATE context_cards
        SET seed_key = ?, type = ?, title = ?, tags = ?, content = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            values["seed_key"],
            values["type"],
            values["title"],
            values["tags"],
            values["content"],
            current_time,
            row["id"],
        ),
    )
    return "updated"


def _delete_legacy_rows(cursor: sqlite3.Cursor, table: str, titles: set[str]) -> int:
    if not titles:
        return 0
    placeholders = ", ".join("?" for _ in titles)
    cursor.execute(
        f"""
        DELETE FROM {table}
        WHERE seed_key IS NULL
        AND title IN ({placeholders})
        """,
        sorted(titles),
    )
    return cursor.rowcount


def _delete_stale_seed_key_rows(cursor: sqlite3.Cursor, table: str, current_seed_keys: set[str]) -> int:
    placeholders = ", ".join("?" for _ in current_seed_keys)
    cursor.execute(
        f"""
        DELETE FROM {table}
        WHERE seed_key IS NOT NULL
        AND seed_key NOT IN ({placeholders})
        """,
        sorted(current_seed_keys),
    )
    return cursor.rowcount


def _summarize_statuses(statuses: list[str]) -> tuple[int, int]:
    return statuses.count("inserted"), statuses.count("updated")


def main() -> None:
    init_db()

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            cursor = connection.cursor()

            template_statuses = [upsert_template(cursor, item) for item in TEMPLATES]
            card_statuses = [upsert_context_card(cursor, item) for item in CONTEXT_CARDS]
            deleted_stale_templates = _delete_stale_seed_key_rows(
                cursor, "prompt_templates", {item["seed_key"] for item in TEMPLATES}
            )
            deleted_stale_cards = _delete_stale_seed_key_rows(
                cursor, "context_cards", {item["seed_key"] for item in CONTEXT_CARDS}
            )
            deleted_legacy_templates = _delete_legacy_rows(
                cursor, "prompt_templates", LEGACY_TEMPLATE_TITLES_TO_DELETE
            )
            deleted_legacy_cards = _delete_legacy_rows(
                cursor, "context_cards", LEGACY_CONTEXT_CARD_TITLES_TO_DELETE
            )

            template_count = cursor.execute("SELECT COUNT(*) FROM prompt_templates").fetchone()[0]
            card_count = cursor.execute("SELECT COUNT(*) FROM context_cards").fetchone()[0]
            type_counts = cursor.execute(
                "SELECT type, COUNT(*) FROM context_cards GROUP BY type ORDER BY type"
            ).fetchall()
    finally:
        connection.close()

    inserted_templates, updated_templates = _summarize_statuses(template_statuses)
    inserted_context_cards, updated_context_cards = _summarize_statuses(card_statuses)

    print(f"新增模板：{inserted_templates} 条，更新模板：{updated_templates} 条")
    print(f"清理旧版内置模板：{deleted_stale_templates} 条")
    print(f"清理旧版模板：{deleted_legacy_templates} 条")
    print(f"新增上下文卡片：{inserted_context_cards} 条，更新上下文卡片：{updated_context_cards} 条")
    print(f"清理旧版内置上下文卡片：{deleted_stale_cards} 条")
    print(f"清理旧版上下文卡片：{deleted_legacy_cards} 条")
    print(f"当前模板总数：{template_count} 条")
    print(f"当前上下文卡片总数：{card_count} 条")
    print("卡片类型分布：" + ", ".join(f"{name}={count}" for name, count in type_counts))


if __name__ == "__main__":
    main()
