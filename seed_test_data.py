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
    {
        "title": "论文选题拆解",
        "category": "学习",
        "tags": ["论文", "选题", "研究"],
        "description": "把一个模糊论文方向拆成可执行的研究选题。",
        "content": "请围绕{研究方向}，为{学习阶段}学生设计 {数量} 个论文选题。\n我的兴趣和限制：\n{输入内容}\n请输出：题目、研究问题、可行性、资料来源建议。",
    },
    {
        "title": "英语作文批改",
        "category": "学习",
        "tags": ["英语", "作文", "修改"],
        "description": "按考试或日常写作标准修改英文作文。",
        "content": "请以{考试类型}标准批改下面的英文作文。\n目标分数：{目标分数}\n作文内容：\n{输入内容}\n请输出：整体评价、语法问题、表达优化、修改后版本。",
    },
    {
        "title": "PPT 大纲生成",
        "category": "办公",
        "tags": ["PPT", "汇报", "大纲"],
        "description": "根据主题生成适合汇报或答辩的 PPT 结构。",
        "content": "请为主题「{主题}」生成一份 {页数} 页 PPT 大纲。\n使用场景：{场景}\n补充信息：\n{输入内容}\n请输出每页标题、核心内容和展示建议。",
    },
    {
        "title": "会议纪要整理",
        "category": "办公",
        "tags": ["会议", "纪要", "任务"],
        "description": "把会议记录整理成清晰纪要和行动项。",
        "content": "请把以下会议内容整理成{格式}会议纪要。\n会议主题：{主题}\n会议记录：\n{输入内容}\n请包含：会议结论、待办事项、负责人、截止时间。",
    },
    {
        "title": "邮件通知撰写",
        "category": "办公",
        "tags": ["邮件", "通知", "沟通"],
        "description": "生成正式或友好的邮件通知。",
        "content": "请帮我写一封{语气}风格的邮件。\n收件人：{收件人}\n邮件目的：{目的}\n关键信息：\n{输入内容}\n请包含：标题、正文、结尾。",
    },
    {
        "title": "短视频脚本生成",
        "category": "创作",
        "tags": ["短视频", "脚本", "内容创作"],
        "description": "根据主题生成短视频口播脚本。",
        "content": "请为{平台}平台生成一个{时长}短视频脚本。\n主题：{主题}\n受众：{目标受众}\n素材或观点：\n{输入内容}\n请输出：开头钩子、正文分镜、结尾引导。",
    },
    {
        "title": "社交媒体文案",
        "category": "创作",
        "tags": ["文案", "社交媒体", "种草"],
        "description": "生成适合小红书、朋友圈、公众号等平台的文案。",
        "content": "请为{平台}写一篇{风格}风格的社交媒体文案。\n主题：{主题}\n目标读者：{目标读者}\n内容素材：\n{输入内容}\n请输出标题、正文和标签建议。",
    },
    {
        "title": "商品对比决策",
        "category": "生活",
        "tags": ["购物", "对比", "决策"],
        "description": "帮助对比多个商品或方案，给出选择建议。",
        "content": "请帮我对比以下{商品类型}，预算是{预算}。\n我的需求优先级：{优先级}\n候选选项：\n{输入内容}\n请输出：对比表、适合人群、推荐选择和理由。",
    },
    {
        "title": "沟通表达优化",
        "category": "生活",
        "tags": ["沟通", "表达", "情绪"],
        "description": "把容易冒犯或混乱的话改成更清晰温和的表达。",
        "content": "请把下面的话改写成{语气}、更容易被接受的表达。\n沟通对象：{对象}\n原话或想表达的意思：\n{输入内容}\n请输出：优化版本、表达策略、需要避免的话。",
    },
    {
        "title": "读书报告生成",
        "category": "学习",
        "tags": ["读书", "报告", "总结"],
        "description": "根据书籍内容生成读书报告。",
        "content": "请根据以下内容生成一份{字数}左右的读书报告。\n书名：{书名}\n重点要求：{要求}\n阅读笔记：\n{输入内容}\n请包含：内容概括、核心观点、个人感受、现实启发。",
    },
    {
        "title": "简历经历优化",
        "category": "职业",
        "tags": ["简历", "求职", "优化"],
        "description": "把普通经历改写成更适合简历的表达。",
        "content": "请把下面的经历优化成适合{岗位}岗位简历的项目描述。\n我的角色：{角色}\n原始经历：\n{输入内容}\n请输出：STAR 结构拆解、简历 bullet、可量化表达建议。",
    },
    {
        "title": "项目需求分析",
        "category": "编程",
        "tags": ["需求分析", "项目", "开发"],
        "description": "把一个项目想法拆成模块、数据对象和接口。",
        "content": "请帮我分析这个{项目类型}项目需求。\n目标用户：{目标用户}\n项目想法：\n{输入内容}\n请输出：核心功能、业务对象、页面结构、接口建议、第一阶段范围。",
    },
    {
        "title": "阶段复盘报告",
        "category": "工作",
        "tags": ["复盘", "总结", "改进"],
        "description": "把一段经历整理成阶段复盘。",
        "content": "请根据以下内容生成一份{周期}复盘报告。\n复盘对象：{对象}\n原始记录：\n{输入内容}\n请包含：目标回顾、完成情况、问题原因、改进动作。",
    },
    {
        "title": "考试复习计划",
        "category": "学习",
        "tags": ["考试", "复习", "计划"],
        "description": "根据考试时间和科目生成复习安排。",
        "content": "请为我制定一份{天数}考试复习计划。\n考试科目：{科目}\n当前基础：{当前基础}\n可用时间和薄弱点：\n{输入内容}\n请输出：每日安排、复习重点、检测方式。",
    },
    {
        "title": "一周饮食计划",
        "category": "健康",
        "tags": ["饮食", "健康", "计划"],
        "description": "根据目标和限制生成日常饮食建议。",
        "content": "请根据我的目标制定一份{周期}饮食计划。\n目标：{目标}\n饮食限制：{限制}\n个人情况：\n{输入内容}\n请输出：早餐、午餐、晚餐、加餐和注意事项。",
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
    {
        "title": "论文选题判断标准",
        "tags": ["论文", "选题", "研究"],
        "source": "测试数据",
        "content": "好的论文选题通常要满足三个条件：问题足够具体、资料能够获得、研究范围可控。过大的题目应拆成更小的问题。",
    },
    {
        "title": "英文作文修改顺序",
        "tags": ["英语", "作文", "修改"],
        "source": "测试数据",
        "content": "批改英文作文时可按内容完整性、结构连贯性、语法准确性、词汇多样性四个层次处理。不要只替换高级词，要先保证表达自然。",
    },
    {
        "title": "PPT 汇报结构",
        "tags": ["PPT", "汇报", "展示"],
        "source": "测试数据",
        "content": "常见 PPT 汇报结构可以是：背景问题、目标、方案、过程、结果、总结展望。每页只保留一个核心观点，避免堆满文字。",
    },
    {
        "title": "会议纪要行动项格式",
        "tags": ["会议", "纪要", "任务"],
        "source": "测试数据",
        "content": "会议纪要中的行动项最好写成：任务内容、负责人、截止时间、验收标准。这样后续追踪更清晰。",
    },
    {
        "title": "正式邮件基本结构",
        "tags": ["邮件", "通知", "沟通"],
        "source": "测试数据",
        "content": "正式邮件建议包含：简短问候、说明目的、列出关键信息、明确下一步动作、礼貌结尾。标题要让收件人一眼看懂主题。",
    },
    {
        "title": "短视频脚本三段式",
        "tags": ["短视频", "脚本", "创作"],
        "source": "测试数据",
        "content": "短视频脚本可以使用三段式：前 3 秒提出冲突或利益点，中间给出信息或故事，结尾引导评论、收藏或行动。",
    },
    {
        "title": "社交媒体标题技巧",
        "tags": ["文案", "社交媒体", "标题"],
        "source": "测试数据",
        "content": "社交媒体标题可以突出人群、痛点、收益或反差。例如“新手也能用”“三步解决”“我后悔没早点知道”。但不要夸大事实。",
    },
    {
        "title": "购物决策对比维度",
        "tags": ["购物", "对比", "决策"],
        "source": "测试数据",
        "content": "对比商品时可以从价格、核心功能、耐用性、售后、学习成本、真实使用场景几个维度判断。推荐理由要和用户优先级对应。",
    },
    {
        "title": "温和沟通表达原则",
        "tags": ["沟通", "表达", "情绪"],
        "source": "测试数据",
        "content": "温和沟通可以采用“事实 + 感受 + 需求 + 请求”的结构。先描述事实，避免直接评价对方人格或动机。",
    },
    {
        "title": "读书报告常见结构",
        "tags": ["读书", "报告", "总结"],
        "source": "测试数据",
        "content": "读书报告通常包括书籍基本信息、内容概括、核心观点、印象深刻片段、个人思考和现实启发。",
    },
    {
        "title": "简历 STAR 表达法",
        "tags": ["简历", "求职", "STAR"],
        "source": "测试数据",
        "content": "简历经历可以用 STAR 思路整理：背景 Situation、任务 Task、行动 Action、结果 Result。最终简历 bullet 要突出行动和结果。",
    },
    {
        "title": "项目需求拆解路径",
        "tags": ["需求分析", "项目", "开发"],
        "source": "测试数据",
        "content": "拆项目需求时可以先确认目标用户和核心场景，再拆业务对象、功能模块、页面入口、接口和数据表。第一版要控制范围。",
    },
    {
        "title": "复盘报告四问",
        "tags": ["复盘", "总结", "改进"],
        "source": "测试数据",
        "content": "复盘可以围绕四个问题：原计划是什么、实际发生了什么、为什么有差异、下一次怎么改进。",
    },
    {
        "title": "考试复习安排原则",
        "tags": ["考试", "复习", "计划"],
        "source": "测试数据",
        "content": "复习计划要把时间分给基础知识、错题整理、模拟检测和回顾巩固。薄弱项需要高频短时复习，而不是最后一天突击。",
    },
    {
        "title": "健康饮食基础提醒",
        "tags": ["饮食", "健康", "计划"],
        "source": "测试数据",
        "content": "日常饮食建议保证主食、蛋白质、蔬菜和水分摄入。控制极端节食，特殊疾病或医学目标应咨询专业人士。",
    },
    {
        "title": "AI 生成结果检查清单",
        "tags": ["AI", "检查", "质量"],
        "source": "测试数据",
        "content": "使用 AI 结果时建议检查：事实是否准确、语气是否合适、是否遗漏关键条件、是否存在过度承诺或不适合直接使用的内容。",
    },
    {
        "title": "课程设计答辩表达",
        "tags": ["课程设计", "答辩", "展示"],
        "source": "测试数据",
        "content": "课程设计答辩可以按项目背景、技术选型、功能模块、核心流程、遇到问题、改进方向来介绍。重点讲清楚自己做了什么。",
    },
    {
        "title": "Prompt 变量命名建议",
        "tags": ["Prompt", "变量", "模板"],
        "source": "测试数据",
        "content": "Prompt 变量名应简短明确，建议使用中文业务词，例如“语气”“目标读者”“输入内容”。不要使用含义模糊的 a、text1 这类名称。",
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
