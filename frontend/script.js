const state = {
  templates: [],
  contextCards: [],
  history: [],
  activeView: "dashboard",
  selectedTemplateId: null,
  selectedContextCardIds: new Set(),
  editingTemplateId: null,
  editingContextCardId: null,
};

const fallbackTemplates = [];
const fallbackContextCards = [];

fallbackTemplates.splice(
  0,
  fallbackTemplates.length,
  {
    id: 1001,
    seed_key: "daily_schedule_planner",
    title: "日程规划助手",
    category: "个人效率",
    tags: ["日程", "计划", "优先级"],
    content: "你是一位擅长时间管理和现实规划的日程助手。\n\n请根据我的输入，帮我制定一份{计划周期}的安排。\n\n我的可用时间：\n{可用时间}\n\n我的精力状态：\n{精力状态}\n\n需要安排的事项：\n{待安排事项}\n\n请按以下要求输出：\n1. 先判断哪些事情最重要、最紧急。\n2. 把任务安排到合适的时间段。\n3. 标出可以延后、合并或删减的事项。\n4. 给出一份不过度理想化、能实际执行的计划。\n5. 最后补充 3 条执行提醒。",
    description: "把零散任务整理成可执行的日程安排，适合规划一天、一周或某个阶段的工作与生活事项。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1002,
    seed_key: "study_notes_organizer",
    title: "学习笔记整理",
    category: "学习成长",
    tags: ["学习", "笔记", "复习"],
    content: "你是一位学习教练，请帮我整理下面的学习材料。\n\n学习主题：\n{学习主题}\n\n学习目标：\n{学习目标}\n\n学习材料：\n{学习材料}\n\n请输出：\n1. 核心概念和简明解释。\n2. 知识点之间的关系。\n3. 关键例子或应用场景。\n4. 容易混淆的地方。\n5. 5 个自测问题和参考答案。\n6. 下一步复习建议。",
    description: "把课程、文章或零散笔记整理成便于理解和复习的学习材料。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1003,
    seed_key: "material_summary_extractor",
    title: "资料总结与重点提取",
    category: "信息整理",
    tags: ["总结", "提炼", "资料"],
    content: "请把下面的资料整理成一份清晰摘要。\n\n资料类型：\n{资料类型}\n\n总结目的：\n{总结目的}\n\n目标读者：\n{目标读者}\n\n资料内容：\n{资料内容}\n\n请输出：\n1. 一句话概括。\n2. 关键要点。\n3. 对目标读者最重要的信息。\n4. 尚不明确或需要核验的内容。\n5. 可执行的下一步。",
    description: "从长文本或多段资料中提取重点、结论、待确认事项和可执行下一步。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1004,
    seed_key: "article_polish_rewrite",
    title: "文章润色改写",
    category: "写作表达",
    tags: ["润色", "改写", "写作"],
    content: "请帮我润色和改写下面的文字。\n\n改写目标：\n{改写目标}\n\n目标读者：\n{目标读者}\n\n必须保留的内容：\n{保留要求}\n\n原文：\n{原文}\n\n请按以下方式处理：\n1. 先指出原文最需要改进的 3 个问题。\n2. 给出改写后的版本。\n3. 列出关键修改说明。\n4. 不改变原文核心意思，不补充未提供的事实。",
    description: "在保留原意的前提下优化文章表达，让结构更顺、语气更稳、重点更清楚。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1005,
    seed_key: "weekly_report_organizer",
    title: "工作周报整理",
    category: "工作沟通",
    tags: ["周报", "复盘", "汇报"],
    content: "请把下面的工作记录整理成一份清晰的周报。\n\n角色：\n{角色}\n\n周期：\n{周期}\n\n目标读者：\n{目标读者}\n\n工作记录：\n{工作记录}\n\n请输出：\n1. 本周期重点。\n2. 已完成事项。\n3. 关键进展与影响。\n4. 问题、风险和阻塞。\n5. 下周期计划。\n6. 需要协作或决策的事项。",
    description: "把零散工作记录整理成清晰、克制、面向协作的周报或阶段复盘。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1006,
    seed_key: "meeting_minutes_organizer",
    title: "会议纪要整理",
    category: "工作沟通",
    tags: ["会议", "纪要", "行动项"],
    content: "请根据下面的会议记录整理会议纪要。\n\n会议主题：\n{会议主题}\n\n参会对象：\n{参会对象}\n\n会议记录：\n{会议记录}\n\n请输出：\n1. 会议目标。\n2. 已确认结论。\n3. 关键讨论点。\n4. 待办事项，包含负责人、完成标准和时间要求。\n5. 待确认问题。\n6. 下一次跟进建议。",
    description: "把会议记录整理成结论明确、责任清楚、便于跟进的会议纪要。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1007,
    seed_key: "communication_expression_optimizer",
    title: "沟通表达优化",
    category: "写作表达",
    tags: ["沟通", "表达", "消息"],
    content: "请帮我优化下面这段沟通表达。\n\n沟通对象：\n{沟通对象}\n\n沟通目标：\n{沟通目标}\n\n原始表达：\n{原始表达}\n\n请输出：\n1. 更直接清楚的版本。\n2. 更委婉稳妥的版本。\n3. 适合正式场景的版本。\n4. 每个版本适合使用的场景。\n5. 需要避免的表达风险。",
    description: "把想说的话改成更清楚、更得体、更容易推进事情的表达。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1008,
    seed_key: "travel_plan_builder",
    title: "旅行攻略规划",
    category: "生活助理",
    tags: ["旅行", "攻略", "规划"],
    content: "请帮我规划一份旅行攻略。\n\n目的地：\n{目的地}\n\n出行天数：\n{出行天数}\n\n预算范围：\n{预算范围}\n\n偏好和限制：\n{偏好限制}\n\n同行人和特殊需求：\n{同行人和特殊需求}\n\n请输出：\n1. 每天的行程安排。\n2. 交通和路线建议。\n3. 餐饮和休息安排。\n4. 预算分配建议。\n5. 需要提前准备或核验的事项。\n6. 如果时间或预算紧张，给出取舍建议。",
    description: "根据目的地、天数、预算和偏好规划更顺路、更现实的旅行安排。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1009,
    seed_key: "product_comparison_decision",
    title: "商品对比决策",
    category: "生活助理",
    tags: ["购物", "对比", "决策"],
    content: "请帮我比较候选商品并给出购买建议。\n\n购买需求：\n{购买需求}\n\n候选商品：\n{候选商品}\n\n关键标准：\n{关键标准}\n\n当前顾虑：\n{当前顾虑}\n\n请输出：\n1. 我的真实需求判断。\n2. 候选商品对比表。\n3. 每个选项的优点、风险和适合人群。\n4. 推荐选择和理由。\n5. 不建议购买的情况。\n6. 下单前需要核验的信息。",
    description: "把购买需求和候选商品整理成对比表，帮助做出更稳妥的选择。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1010,
    seed_key: "weekly_meal_planner",
    title: "一周饮食计划",
    category: "生活助理",
    tags: ["饮食", "健康", "计划"],
    content: "请帮我制定一份一周饮食计划。\n\n饮食目标：\n{饮食目标}\n\n人数：\n{人数}\n\n预算范围：\n{预算范围}\n\n忌口或限制：\n{忌口限制}\n\n现有食材和烹饪条件：\n{现有食材和烹饪条件}\n\n请输出：\n1. 一周早餐、午餐、晚餐安排。\n2. 食材采购清单。\n3. 可以提前准备的部分。\n4. 替换方案。\n5. 执行难度和注意事项。",
    description: "根据饮食目标、人数和限制安排一周菜单，同时兼顾准备成本和执行难度。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
);

fallbackContextCards.splice(
  0,
  fallbackContextCards.length,
  {
    id: 2001,
    seed_key: "background_promptstudio_daily_use",
    type: "background",
    title: "PromptStudio 日常使用方式",
    tags: ["PromptStudio", "日常", "工作流"],
    content: "模板适合保存高频任务的稳定结构，上下文卡片适合保存可复用的背景、规则、格式、示例和检查清单。日常使用时，先选模板，再按任务补充少量卡片，避免一次放入过多无关内容。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2002,
    seed_key: "background_personal_productivity_context",
    type: "background",
    title: "个人效率场景",
    tags: ["效率", "计划", "任务"],
    content: "个人效率类任务通常关注优先级、可用时间、精力状态和执行阻力。输出应帮助用户做取舍，而不是把所有事项都安排进去。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2003,
    seed_key: "background_life_assistant_context",
    type: "background",
    title: "生活助理场景",
    tags: ["生活", "助理", "规划"],
    content: "生活助理类任务需要考虑预算、时间、偏好、限制和准备成本。建议应贴近日常执行，不要只给理想化方案。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2004,
    seed_key: "background_decision_making_context",
    type: "background",
    title: "日常决策关注点",
    tags: ["决策", "对比", "风险"],
    content: "日常决策通常不是寻找绝对最优，而是在需求、成本、风险和个人偏好之间找到合适选择。输出应说明推荐理由，也要指出不适合选择的情况。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2005,
    seed_key: "background_learning_and_writing_context",
    type: "background",
    title: "学习与写作场景",
    tags: ["学习", "写作", "整理"],
    content: "学习和写作任务要优先帮助用户理解、组织和表达。输出应突出主线、关键概念、例子和可复习内容，不要只做机械摘要。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2006,
    seed_key: "rule_plan_with_buffer",
    type: "rule",
    title: "计划需要留缓冲",
    tags: ["计划", "时间", "缓冲"],
    content: "制定计划时，不要默认用户可以一直保持高效率。需要预留休息、切换任务和意外情况的时间；如果事项明显超出可用时间，要主动建议删减或延后。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2007,
    seed_key: "rule_prioritize_before_detail",
    type: "rule",
    title: "先排优先级",
    tags: ["优先级", "任务", "取舍"],
    content: "面对多项任务时，先区分重要紧急、重要不紧急、可委托、可延后。不要直接进入细节安排，否则容易把低价值事项也排得很满。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2008,
    seed_key: "rule_no_unverified_claims",
    type: "rule",
    title: "不补造未给信息",
    tags: ["准确性", "事实", "边界"],
    content: "不得把输入中没有提供的信息写成确定事实。涉及价格、营业时间、政策、健康、法律或其他可能变化的信息时，应提示用户自行核验或补充材料。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2009,
    seed_key: "rule_clear_natural_tone",
    type: "rule",
    title: "清楚自然的语气",
    tags: ["语气", "表达", "写作"],
    content: "默认语气应清楚、自然、克制。少用空泛口号和夸张赞美，优先给能直接使用的表达和步骤。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2010,
    seed_key: "rule_actionable_advice",
    type: "rule",
    title: "建议要能执行",
    tags: ["建议", "执行", "行动"],
    content: "建议应尽量写成具体动作，包含做什么、何时做、做到什么程度。避免只写提升效率、优化表达、注意健康这类抽象方向。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2011,
    seed_key: "rule_keep_user_constraints",
    type: "rule",
    title: "尊重用户限制",
    tags: ["限制", "偏好", "约束"],
    content: "用户提供的预算、时间、忌口、风格、目标读者和必须保留内容都应作为硬约束处理。如果建议与约束冲突，要说明原因并给替代方案。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2012,
    seed_key: "rule_when_information_missing",
    type: "rule",
    title: "信息不足时先说明",
    tags: ["澄清", "假设", "不确定"],
    content: "当关键信息缺失时，先说明缺口。如果用户需要直接产出，可以基于少量明确假设继续，但要把假设和待确认事项单独列出。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2013,
    seed_key: "format_daily_schedule",
    type: "format",
    title: "日程安排格式",
    tags: ["格式", "日程", "计划"],
    content: "日程建议按时间段输出，包含时间、任务、目的、注意事项。末尾列出可延后事项、缓冲时间和当天最重要的 1 到 3 件事。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2014,
    seed_key: "format_study_notes",
    type: "format",
    title: "学习笔记格式",
    tags: ["格式", "学习", "笔记"],
    content: "学习笔记建议包含主题概览、核心概念、概念关系、例子、常见误区、自测问题和复习建议。标题要短，方便后续回看。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2015,
    seed_key: "format_summary_brief",
    type: "format",
    title: "资料摘要格式",
    tags: ["格式", "总结", "摘要"],
    content: "资料摘要建议按一句话概括、关键要点、重要细节、待确认内容、下一步输出。长材料要优先总结对当前目的有帮助的信息。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2016,
    seed_key: "format_weekly_report",
    type: "format",
    title: "周报结构",
    tags: ["格式", "周报", "汇报"],
    content: "周报建议包含本周期重点、已完成事项、关键进展、问题风险、下周期计划和需要协作的事项。按结果归类，不按时间流水账排列。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2017,
    seed_key: "format_meeting_minutes",
    type: "format",
    title: "会议纪要结构",
    tags: ["格式", "会议", "行动项"],
    content: "会议纪要建议包含会议目标、已确认结论、关键讨论点、待办事项、待确认问题和下次跟进。行动项要写清负责人、完成标准和时间要求。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2018,
    seed_key: "format_comparison_table",
    type: "format",
    title: "对比选择表",
    tags: ["格式", "对比", "决策"],
    content: "对比多个选项时使用表格，列包含选项、适合情况、优点、风险、成本、推荐程度。表格后必须给出明确建议和选择理由。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2019,
    seed_key: "format_meal_plan",
    type: "format",
    title: "饮食计划格式",
    tags: ["格式", "饮食", "计划"],
    content: "饮食计划建议按日期列出三餐，另附采购清单、提前准备事项、替换方案和注意事项。不要给出难以采购或准备成本过高的安排。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2020,
    seed_key: "example_task_to_schedule",
    type: "example",
    title: "示例：模糊事项到日程安排",
    tags: ["示例", "日程", "计划"],
    content: "输入：写报告、买菜、运动、回消息、整理房间。输出应先判断优先级，再安排到时间段，并把低优先级事项放进可选清单。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2021,
    seed_key: "example_notes_to_review",
    type: "example",
    title: "示例：课堂笔记到复习材料",
    tags: ["示例", "学习", "复习"],
    content: "输入：一段课程笔记。输出应整理为核心概念、解释、例子、误区和自测题，方便复习，而不是只改写原文。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2022,
    seed_key: "example_raw_text_to_summary",
    type: "example",
    title: "示例：长资料到重点摘要",
    tags: ["示例", "总结", "资料"],
    content: "输入：多段会议材料或文章摘录。输出应先给一句话结论，再列关键要点、影响、待确认内容和下一步。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2023,
    seed_key: "example_sentence_to_message",
    type: "example",
    title: "示例：直接想法到得体表达",
    tags: ["示例", "沟通", "表达"],
    content: "输入：你怎么还没给我。优化后可以表达为：想确认一下这个事项目前的进展，方便我安排后续时间。这样更容易推进沟通。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2024,
    seed_key: "example_items_to_comparison",
    type: "example",
    title: "示例：候选商品到购买建议",
    tags: ["示例", "购物", "决策"],
    content: "输入：三个耳机型号和预算。输出应按需求、价格、续航、佩戴、风险和适合人群比较，最后给明确推荐。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2025,
    seed_key: "example_ingredients_to_meal_plan",
    type: "example",
    title: "示例：现有食材到菜单",
    tags: ["示例", "饮食", "菜单"],
    content: "输入：鸡蛋、番茄、青菜、鸡胸肉。输出应安排简单可执行的餐食，并说明哪些食材可提前处理、哪些可以替换。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2026,
    seed_key: "checklist_plan_before_execution",
    type: "checklist",
    title: "计划执行前检查",
    tags: ["检查", "计划", "执行"],
    content: "检查计划是否留出缓冲、是否有明确优先级、是否超出可用时间、是否包含下一步动作、是否把可延后事项单独列出。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2027,
    seed_key: "checklist_writing_before_send",
    type: "checklist",
    title: "发送前表达检查",
    tags: ["检查", "沟通", "写作"],
    content: "检查表达是否说明目的、是否语气合适、是否有多余情绪、是否给对方明确动作、是否容易被误解。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2028,
    seed_key: "checklist_summary_quality",
    type: "checklist",
    title: "摘要质量检查",
    tags: ["检查", "摘要", "总结"],
    content: "检查摘要是否保留核心信息、是否突出当前目的、是否区分事实和推断、是否遗漏关键限制、是否列出待确认内容。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2029,
    seed_key: "checklist_meeting_minutes",
    type: "checklist",
    title: "会议纪要检查",
    tags: ["检查", "会议", "纪要"],
    content: "检查纪要是否包含结论、行动项、负责人、完成标准、时间要求和待确认问题。没有明确负责人的事项不要写成已落实。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2030,
    seed_key: "checklist_decision_before_purchase",
    type: "checklist",
    title: "购买决策检查",
    tags: ["检查", "购物", "决策"],
    content: "检查推荐是否符合真实需求、预算和限制；是否说明风险；是否列出不建议购买的情况；是否提示下单前要核验的关键信息。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
);

const contextCardTypeLabels = {
  background: "\u80cc\u666f\u8d44\u6599",
  rule: "\u5199\u4f5c\u89c4\u5219",
  format: "\u8f93\u51fa\u683c\u5f0f",
  example: "\u53c2\u8003\u793a\u4f8b",
  checklist: "\u68c0\u67e5\u6e05\u5355",
};

function contextCardTypeLabel(type) {
  return contextCardTypeLabels[type] || contextCardTypeLabels.background;
}

const pageMeta = {
  dashboard: ["仪表盘", "把模板、知识和灵感收进一个可复用的 AI 工作台。"],
  templates: ["提示词模板", "沉淀高频任务的结构，让好 Prompt 可以复用。"],
  contextCards: ["上下文卡片", "保存背景资料、写作规范和项目上下文。"],
  history: ["生成记录", "回收每次试验，不让好结果只出现一次。"],
  ai: ["AI 生成", "把预生成 Prompt 交给 DeepSeek，并查看流式回答。"],
};

const dateTimeFormatter = new Intl.DateTimeFormat("zh-CN", {
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

const elements = {
  mobileMenuButton: document.querySelector("#mobileMenuButton"),
  scrim: document.querySelector("#scrim"),
  pageTitle: document.querySelector("#pageTitle"),
  pageSubtitle: document.querySelector("#pageSubtitle"),
  navItems: document.querySelectorAll(".nav-item"),
  viewSections: document.querySelectorAll(".view-section"),
  refreshButton: document.querySelector("#refreshButton"),
  toast: document.querySelector("#toast"),
  apiStatus: document.querySelector("#apiStatus"),
  catStatusText: document.querySelector("#catStatusText"),
  consoleCat: document.querySelector(".console-cat"),

  contextCardCount: document.querySelector("#contextCardCount"),
  templateCount: document.querySelector("#templateCount"),
  historyCount: document.querySelector("#historyCount"),
  latestUpdate: document.querySelector("#latestUpdate"),

  quickTemplateSelect: document.querySelector("#quickTemplateSelect"),
  variableFields: document.querySelector("#variableFields"),
  variableCount: document.querySelector("#variableCount"),
  contextCardChoices: document.querySelector("#contextCardChoices"),
  selectedContextCardCount: document.querySelector("#selectedContextCardCount"),
  workflowSteps: document.querySelectorAll("[data-workflow-step]"),
  previewPromptButton: document.querySelector("#previewPromptButton"),
  savePromptButton: document.querySelector("#savePromptButton"),
  finalPrompt: document.querySelector("#finalPrompt"),
  promptHint: document.querySelector("#promptHint"),
  optimizePromptButton: document.querySelector("#optimizePromptButton"),
  optimizeBox: document.querySelector("#optimizeBox"),
  optimizeHint: document.querySelector("#optimizeHint"),
  optimizedPrompt: document.querySelector("#optimizedPrompt"),
  applyOptimizedButton: document.querySelector("#applyOptimizedButton"),
  copyOptimizedButton: document.querySelector("#copyOptimizedButton"),
  copyPromptButton: document.querySelector("#copyPromptButton"),
  pushToAiButton: document.querySelector("#pushToAiButton"),
  aiPromptInput: document.querySelector("#aiPromptInput"),

  templateForm: document.querySelector("#templateForm"),
  templateFormTitle: document.querySelector("#templateFormTitle"),
  templateTitle: document.querySelector("#templateTitle"),
  templateCategory: document.querySelector("#templateCategory"),
  templateTags: document.querySelector("#templateTags"),
  templateDescription: document.querySelector("#templateDescription"),
  templateContent: document.querySelector("#templateContent"),
  saveTemplateButton: document.querySelector("#saveTemplateButton"),
  cancelTemplateEditButton: document.querySelector("#cancelTemplateEditButton"),
  templateListCount: document.querySelector("#templateListCount"),
  templateList: document.querySelector("#templateList"),

  contextCardForm: document.querySelector("#contextCardForm"),
  contextCardFormTitle: document.querySelector("#contextCardFormTitle"),
  contextCardType: document.querySelector("#contextCardType"),
  contextCardTitle: document.querySelector("#contextCardTitle"),
  contextCardTags: document.querySelector("#contextCardTags"),
  contextCardContent: document.querySelector("#contextCardContent"),
  saveContextCardButton: document.querySelector("#saveContextCardButton"),
  cancelContextCardEditButton: document.querySelector("#cancelContextCardEditButton"),
  contextCardListCount: document.querySelector("#contextCardListCount"),
  contextCardList: document.querySelector("#contextCardList"),

  recentHistoryList: document.querySelector("#recentHistoryList"),
  historyList: document.querySelector("#historyList"),
  reloadHistoryButton: document.querySelector("#reloadHistoryButton"),

  askLlmButton: document.querySelector("#askLlmButton"),
  llmModel: document.querySelector("#llmModel"),
  llmTemperature: document.querySelector("#llmTemperature"),
  temperatureValue: document.querySelector("#temperatureValue"),
  llmHint: document.querySelector("#llmHint"),
  llmAnswer: document.querySelector("#llmAnswer"),
  copyAnswerButton: document.querySelector("#copyAnswerButton"),
  saveAnswerContextCardButton: document.querySelector("#saveAnswerContextCardButton"),
  terminalState: document.querySelector("#terminalState"),
  terminalProgress: document.querySelector("#terminalProgress"),
  answerStats: document.querySelector("#answerStats"),
  hoverTooltip: document.createElement("div"),
};

const customSelects = new Map();

elements.hoverTooltip.className = "hover-tooltip";
document.body.appendChild(elements.hoverTooltip);

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.classList.toggle("error", isError);
  elements.toast.classList.add("show");

  if (isError) {
    setCatMood("小猫发现了一处需要处理的问题。", "alert");
  }

  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2600);
}

function moveHoverTooltip(event) {
  if (!elements.hoverTooltip.classList.contains("show")) {
    return;
  }

  const margin = 14;
  const tooltipRect = elements.hoverTooltip.getBoundingClientRect();
  let left = event.clientX + margin;
  let top = event.clientY + margin;

  if (left + tooltipRect.width > window.innerWidth - margin) {
    left = event.clientX - tooltipRect.width - margin;
  }

  if (top + tooltipRect.height > window.innerHeight - margin) {
    top = event.clientY - tooltipRect.height - margin;
  }

  elements.hoverTooltip.style.left = `${Math.max(margin, left)}px`;
  elements.hoverTooltip.style.top = `${Math.max(margin, top)}px`;
}

function showHoverTooltip(target, event) {
  const text = target?.dataset?.tooltip?.trim();
  if (!text) {
    return;
  }

  elements.hoverTooltip.textContent = text;
  elements.hoverTooltip.classList.add("show");
  moveHoverTooltip(event);
}

function hideHoverTooltip() {
  elements.hoverTooltip.classList.remove("show");
}

function setApiStatus(message, mode = "pending") {
  elements.apiStatus.textContent = message;
  elements.apiStatus.classList.toggle("ok", mode === "ok");
  elements.apiStatus.classList.toggle("error", mode === "error");
}

function setCatMood(message, mood = "idle") {
  elements.catStatusText.textContent = message;
  elements.consoleCat.classList.remove("is-working", "is-happy", "is-alert");

  if (mood === "working") {
    elements.consoleCat.classList.add("is-working");
  }

  if (mood === "happy") {
    elements.consoleCat.classList.add("is-happy");
  }

  if (mood === "alert") {
    elements.consoleCat.classList.add("is-alert");
  }
}

function setWorkflowStep(activeStep = "compose") {
  const stepOrder = ["compose", "preview", "optimize", "save"];
  const activeIndex = Math.max(0, stepOrder.indexOf(activeStep));

  elements.workflowSteps.forEach((step) => {
    const index = stepOrder.indexOf(step.dataset.workflowStep);
    step.classList.toggle("is-active", index === activeIndex);
    step.classList.toggle("is-done", index >= 0 && index < activeIndex);
  });
}

function setTerminalStatus(label, progress = 0, isRunning = false, isError = false) {
  elements.terminalState.textContent = label;
  elements.terminalProgress.style.width = `${Math.max(0, Math.min(progress, 100))}%`;
  const wrapper = elements.terminalState.closest(".terminal-status");
  wrapper.classList.toggle("is-running", isRunning);
  wrapper.classList.toggle("is-error", isError);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function parseTags(text) {
  return text
    .replaceAll("，", ",")
    .replaceAll("、", ",")
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function extractVariables(content) {
  const variables = [];
  const matches = String(content ?? "").matchAll(/\{([^{}\s]+)\}/g);

  for (const match of matches) {
    if (!variables.includes(match[1])) {
      variables.push(match[1]);
    }
  }

  return variables;
}

function summarizeForHover(text, maxLength = 180) {
  const normalized = String(text || "").replace(/\s+/g, " ").trim();
  return normalized.length > maxLength
    ? `${normalized.slice(0, maxLength)}…`
    : normalized;
}

function templateHoverText(template) {
  const variables = extractVariables(template.content || "");
  return [
    template.description || summarizeForHover(template.content),
    template.category ? `分类：${template.category}` : "",
    (template.tags || []).length ? `标签：${template.tags.join("、")}` : "",
    variables.length ? `变量：${variables.join("、")}` : "",
  ].filter(Boolean).join("\n");
}

function contextCardHoverText(card) {
  return [
    `类型：${contextCardTypeLabel(card.type)}`,
    (card.tags || []).length ? `标签：${card.tags.join("、")}` : "",
    summarizeForHover(card.content),
  ].filter(Boolean).join("\n");
}

function templateForSelectOption(option) {
  return state.templates.find((item) => String(item.id) === String(option.value)) ?? null;
}

function templateSelectOptionSummary(option) {
  const template = templateForSelectOption(option);
  if (!template) {
    return "";
  }

  return [template.category, (template.tags || []).slice(0, 2).join(" / ")].filter(Boolean).join(" · ");
}

function templateSelectOptionDetail(option) {
  const template = templateForSelectOption(option);
  return template ? summarizeForHover(template.description || template.content, 76) : "";
}

function selectedOptionSummary(select, option, options) {
  if (!option) {
    return "";
  }

  if (options.summary) {
    return options.summary(option);
  }

  return option.dataset.summary || "";
}

function closeCustomSelectsExcept(exceptSelect = null) {
  customSelects.forEach((data, select) => {
    if (select === exceptSelect) {
      return;
    }
    data.root.classList.remove("open");
    data.trigger.setAttribute("aria-expanded", "false");
    data.activeIndex = -1;
  });
}

function closeCustomSelects() {
  closeCustomSelectsExcept();
}

function setActiveCustomOption(data, index) {
  const options = [...data.menu.querySelectorAll(".custom-select-option")];
  if (!options.length) {
    data.activeIndex = -1;
    return;
  }

  const nextIndex = (index + options.length) % options.length;
  data.activeIndex = nextIndex;

  options.forEach((option, optionIndex) => {
    option.classList.toggle("active", optionIndex === nextIndex);
  });
  options[nextIndex].scrollIntoView({ block: "nearest" });
}

function openCustomSelect(select) {
  const data = customSelects.get(select);
  if (!data) {
    return;
  }

  closeCustomSelectsExcept(select);
  data.root.classList.add("open");
  data.trigger.setAttribute("aria-expanded", "true");
  const selectedIndex = Math.max(0, [...select.options].findIndex((option) => option.value === select.value));
  setActiveCustomOption(data, selectedIndex);
}

function selectOption(select, value) {
  const data = customSelects.get(select);
  if (!data) {
    return;
  }

  select.value = value;
  refreshCustomSelect(select);
  closeCustomSelects();
  hideHoverTooltip();
  select.dispatchEvent(new Event("change", { bubbles: true }));
}

function refreshCustomSelect(select) {
  const data = customSelects.get(select);
  if (!data) {
    return;
  }

  const options = [...select.options];
  const selectedOption = select.selectedOptions[0] || options[0];
  const selectedSummary = selectedOptionSummary(select, selectedOption, data.options);

  data.value.textContent = selectedOption ? selectedOption.textContent : "暂无选项";
  data.summary.textContent = selectedSummary;
  data.summary.classList.toggle("is-empty", !selectedSummary);
  data.menu.innerHTML = options
    .map((option, index) => {
      const isSelected = option.value === select.value;
      const summary = data.options.summary ? data.options.summary(option) : option.dataset.summary || "";
      const detail = data.options.detail ? data.options.detail(option) : "";
      const optionClass = `custom-select-option${isSelected ? " selected" : ""}`;
      return `
        <button class="${optionClass}" type="button" role="option" data-select-value="${escapeHtml(option.value)}" data-option-index="${index}" aria-selected="${isSelected}">
          <span>${escapeHtml(option.textContent)}</span>
          ${summary ? `<small>${escapeHtml(summary)}</small>` : ""}
          ${detail ? `<em>${escapeHtml(detail)}</em>` : ""}
        </button>
      `;
    })
    .join("");
}

function enhanceSelect(select, options = {}) {
  if (!select || customSelects.has(select)) {
    return;
  }

  select.classList.add("native-select");
  select.setAttribute("aria-hidden", "true");
  select.tabIndex = -1;
  const root = document.createElement("div");
  root.className = `custom-select ${options.theme === "dark" ? "dark" : ""}`;
  root.setAttribute("data-custom-select-id", select.id);
  root.innerHTML = `
    <button class="custom-select-trigger" type="button" aria-haspopup="listbox" aria-expanded="false">
      <span class="custom-select-value"></span>
      <small class="custom-select-summary"></small>
      <b aria-hidden="true">⌄</b>
    </button>
    <div class="custom-select-menu" role="listbox"></div>
  `;
  select.insertAdjacentElement("afterend", root);

  const data = {
    select,
    root,
    trigger: root.querySelector(".custom-select-trigger"),
    value: root.querySelector(".custom-select-value"),
    summary: root.querySelector(".custom-select-summary"),
    menu: root.querySelector(".custom-select-menu"),
    options,
    activeIndex: -1,
  };
  customSelects.set(select, data);

  data.trigger.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (data.root.classList.contains("open")) {
      closeCustomSelects();
    } else {
      openCustomSelect(select);
    }
  });

  data.root.addEventListener("click", (event) => {
    const optionButton = event.target.closest(".custom-select-option");
    if (!optionButton) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    selectOption(select, optionButton.dataset.selectValue);
  });

  data.root.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeCustomSelects();
      data.trigger.focus();
      return;
    }

    if (event.key === "Enter" && data.root.classList.contains("open") && data.activeIndex >= 0) {
      const activeOption = data.menu.querySelectorAll(".custom-select-option")[data.activeIndex];
      if (activeOption) {
        event.preventDefault();
        selectOption(select, activeOption.dataset.selectValue);
      }
      return;
    }

    if (["Enter", " ", "ArrowDown", "ArrowUp"].includes(event.key)) {
      event.preventDefault();
      if (!data.root.classList.contains("open")) {
        openCustomSelect(select);
        return;
      }
      setActiveCustomOption(data, data.activeIndex + (event.key === "ArrowUp" ? -1 : 1));
    }
  });

  refreshCustomSelect(select);
}

function initializeCustomSelects() {
  enhanceSelect(elements.quickTemplateSelect, {
    summary: templateSelectOptionSummary,
    detail: templateSelectOptionDetail,
  });
  enhanceSelect(elements.contextCardType);
  enhanceSelect(elements.llmModel, { theme: "dark" });
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    try {
      const parsed = JSON.parse(text);
      throw new Error(parsed.detail || text || `请求失败：${response.status}`);
    } catch {
      throw new Error(text || `请求失败：${response.status}`);
    }
  }

  return response.json();
}

function getSelectedTemplate() {
  return state.templates.find((item) => item.id === state.selectedTemplateId) ?? null;
}

function syncSelectedTemplate() {
  if (!state.templates.some((item) => item.id === state.selectedTemplateId)) {
    state.selectedTemplateId = state.templates[0]?.id ?? null;
  }
}

function switchView(viewName) {
  state.activeView = viewName;
  const [title, subtitle] = pageMeta[viewName] || pageMeta.dashboard;

  elements.pageTitle.textContent = title;
  elements.pageSubtitle.textContent = subtitle;

  elements.navItems.forEach((item) => {
    item.classList.toggle("active", item.dataset.view === viewName);
  });

  elements.viewSections.forEach((section) => {
    section.classList.toggle("active", section.id === `${viewName}View`);
  });

  document.body.classList.remove("sidebar-open");
}

function formatDate(value) {
  if (!value || value === "本地示例") {
    return value || "--";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return dateTimeFormatter.format(date).replace(/\//g, "-");
}

function renderTags(tags = [], category = null) {
  const tagList = [...tags];
  if (category) {
    tagList.unshift(category);
  }

  if (!tagList.length) {
    return '<span class="tag">无标签</span>';
  }

  return tagList
    .map((tag, index) => `<span class="tag ${index === 0 && category ? "category" : ""}">${escapeHtml(tag)}</span>`)
    .join("");
}

function renderStats() {
  elements.contextCardCount.textContent = state.contextCards.length;
  elements.templateCount.textContent = state.templates.length;
  elements.historyCount.textContent = state.history.length;
  elements.latestUpdate.textContent = formatDate(state.history[0]?.created_at) || "--";
}

function renderTemplateSelect() {
  syncSelectedTemplate();

  if (!state.templates.length) {
    elements.quickTemplateSelect.innerHTML = '<option value="">暂无模板</option>';
    refreshCustomSelect(elements.quickTemplateSelect);
    renderVariables();
    return;
  }

  elements.quickTemplateSelect.innerHTML = state.templates
    .map((item) => `<option value="${item.id}">${escapeHtml(item.title)}</option>`)
    .join("");
  elements.quickTemplateSelect.value = String(state.selectedTemplateId);
  refreshCustomSelect(elements.quickTemplateSelect);
  renderVariables();
  updateWorkSurface();
}

function renderVariables() {
  const template = getSelectedTemplate();

  if (!template) {
    elements.variableFields.innerHTML = '<div class="empty-state">暂无模板变量。</div>';
    elements.variableCount.textContent = "0 个变量";
    return;
  }

  const variables = extractVariables(template.content);
  elements.variableCount.textContent = `${variables.length} 个变量`;

  if (!variables.length) {
    elements.variableFields.innerHTML = '<div class="empty-state">当前模板没有变量，生成时会直接使用模板内容。</div>';
    return;
  }

  elements.variableFields.innerHTML = variables
    .map((name) => `
      <label>
        ${escapeHtml(name)}
        <input data-variable-name="${escapeHtml(name)}" name="var_${escapeHtml(name)}" type="text" autocomplete="off" placeholder="">
      </label>
    `)
    .join("");
}

function renderContextCardChoices() {
  const contextCards = state.contextCards;

  if (!contextCards.length) {
    elements.contextCardChoices.innerHTML = '<div class="empty-state">暂无可选上下文卡片。</div>';
    elements.selectedContextCardCount.textContent = `已选 ${state.selectedContextCardIds.size} 个`;
    return;
  }

  elements.contextCardChoices.innerHTML = contextCards
    .map((item) => `
      <label class="choice-card has-hover-tip" data-tooltip="${escapeHtml(contextCardHoverText(item))}" tabindex="0">
        <input type="checkbox" name="contextCard_choice" value="${item.id}" data-context-card-choice ${state.selectedContextCardIds.has(item.id) ? "checked" : ""}>
        <span>
          <strong>${escapeHtml(item.title)}</strong>
          <small>${escapeHtml([contextCardTypeLabel(item.type), (item.tags || []).join(" / ")].filter(Boolean).join(" / "))}</small>
        </span>
      </label>
    `)
    .join("");
  updateSelectedContextCardCount();
  updateWorkSurface();
}

function renderTemplates() {
  const templates = state.templates;
  elements.templateListCount.textContent = `${templates.length} 个模板`;

  if (!templates.length) {
    elements.templateList.innerHTML = '<div class="empty-state">暂无模板。试着新建一个常用任务模板。</div>';
    return;
  }

  elements.templateList.innerHTML = templates
    .map((item) => `
      <article class="resource-card ${item.id === state.selectedTemplateId ? "active" : ""}" data-template-id="${item.id}">
        <div class="resource-row">
          <div>
            <div class="resource-title">${escapeHtml(item.title)}</div>
            <div class="resource-meta">${escapeHtml(item.description || item.content.slice(0, 86))}</div>
          </div>
          <div class="resource-actions">
            <button class="tiny-button secondary-button" type="button" data-use-template-id="${item.id}">使用</button>
            <button class="tiny-button secondary-button" type="button" data-edit-template-id="${item.id}">编辑</button>
            <button class="delete-button" type="button" data-delete-template-id="${item.id}">删除</button>
          </div>
        </div>
        <div class="tag-row">${renderTags(item.tags, item.category)}</div>
        <div class="resource-meta">更新：${escapeHtml(formatDate(item.updated_at))}</div>
      </article>
    `)
    .join("");
}

function renderContextCards() {
  const contextCards = state.contextCards;
  elements.contextCardListCount.textContent = `${contextCards.length} 个卡片`;

  if (!contextCards.length) {
    elements.contextCardList.innerHTML = '<div class="empty-state">暂无上下文卡片。可以先保存一条写作规范或项目背景。</div>';
    return;
  }

  elements.contextCardList.innerHTML = contextCards
    .map((item) => `
      <article class="resource-card">
        <div class="resource-row">
          <div>
            <div class="resource-title">${escapeHtml(item.title)}</div>
            <div class="resource-meta">${escapeHtml(contextCardTypeLabel(item.type))} / ${escapeHtml(item.content.slice(0, 94))}</div>
          </div>
          <div class="resource-actions">
            <button class="tiny-button secondary-button" type="button" data-toggle-context-card-id="${item.id}">
              ${state.selectedContextCardIds.has(item.id) ? "取消选择" : "加入生成"}
            </button>
            <button class="tiny-button secondary-button" type="button" data-edit-context-card-id="${item.id}">编辑</button>
            <button class="delete-button" type="button" data-delete-context-card-id="${item.id}">删除</button>
          </div>
        </div>
        <div class="tag-row">${renderTags(item.tags)}</div>
        <div class="resource-meta">更新：${escapeHtml(formatDate(item.updated_at))}</div>
      </article>
    `)
    .join("");
}

function historyCard(item) {
  const preview = item.final_prompt.length > 170
    ? `${item.final_prompt.slice(0, 170)}…`
    : item.final_prompt;

  return `
    <article class="record-card" data-history-id="${item.id}">
      <div class="record-row">
        <div>
          <div class="record-title">生成记录 #${item.id}</div>
          <div class="record-meta">${escapeHtml(formatDate(item.created_at))} · 模板 ${escapeHtml(item.template_id)}</div>
        </div>
        <div class="record-actions">
          <button class="tiny-button secondary-button" type="button" data-load-history-id="${item.id}">载入</button>
          <button class="tiny-button secondary-button" type="button" data-copy-history-id="${item.id}">复制</button>
          <button class="delete-button" type="button" data-delete-history-id="${item.id}">删除</button>
        </div>
      </div>
      <p class="record-meta">${escapeHtml(preview)}</p>
    </article>
  `;
}

function renderHistory() {
  const history = state.history;
  const recent = history.slice(0, 5);

  elements.recentHistoryList.innerHTML = recent.length
    ? recent.map(historyCard).join("")
    : '<div class="empty-state">暂无最近生成记录。</div>';

  elements.historyList.innerHTML = history.length
    ? history.map(historyCard).join("")
    : '<div class="empty-state">暂无历史记录。保存预生成 Prompt 后会出现在这里。</div>';
}

function renderAll() {
  renderStats();
  renderTemplateSelect();
  renderContextCardChoices();
  renderTemplates();
  renderContextCards();
  renderHistory();
  updateWorkSurface();
}

async function loadData() {
  setApiStatus("连接中", "pending");

  try {
    const [templates, contextCards, history] = await Promise.all([
      requestJson("/api/templates"),
      requestJson("/api/context-cards"),
      requestJson("/api/history?limit=50"),
    ]);

    state.templates = templates;
    state.contextCards = contextCards;
    state.history = history;
    syncSelectedTemplate();
    renderAll();
    setApiStatus("已连接", "ok");
    showToast("已连接 FastAPI 后端");
  } catch (error) {
    if (!state.templates.length) {
      state.templates = fallbackTemplates;
      state.contextCards = fallbackContextCards;
      state.history = [];
      syncSelectedTemplate();
    }

    renderAll();
    setApiStatus("离线演示", "error");
    showToast(`后端暂不可用，已载入演示数据：${error.message}`, true);
  }
}

async function loadHistory() {
  try {
    state.history = await requestJson("/api/history?limit=50");
    renderStats();
    renderHistory();
  } catch (error) {
    showToast(`刷新历史失败：${error.message}`, true);
  }
}

function collectVariables() {
  const variables = {};
  const inputs = elements.variableFields.querySelectorAll("[data-variable-name]");

  inputs.forEach((input) => {
    const name = input.dataset.variableName;
    variables[name] = input.value.trim();
  });

  return variables;
}

function getVariableStats() {
  const template = getSelectedTemplate();
  const names = template ? extractVariables(template.content) : [];
  const variables = collectVariables();
  const completed = names.filter((name) => String(variables[name] || "").trim()).length;

  return {
    total: names.length,
    completed,
    ratio: names.length ? completed / names.length : 1,
  };
}

function collectContextCardIds() {
  return Array.from(state.selectedContextCardIds);
}

function updateSelectedContextCardCount() {
  elements.selectedContextCardCount.textContent = `已选 ${state.selectedContextCardIds.size} 个`;
}

function updatePromptAssistant() {
  const variableStats = getVariableStats();
  const selectedCount = state.selectedContextCardIds.size;

  if (elements.finalPrompt.value.trim()) {
    elements.promptHint.textContent = `当前预生成 Prompt ${elements.finalPrompt.value.length} 个字符，可复制、优化或送去 AI。`;
    setCatMood("Prompt 已就绪，可以继续优化或生成。", "happy");
  } else if (variableStats.total && variableStats.ratio < 1) {
    elements.promptHint.textContent = `变量 ${variableStats.completed}/${variableStats.total}，已选卡片 ${selectedCount}。`;
    setCatMood("补齐变量后可以先预览 Prompt。");
  } else if (state.selectedContextCardIds.size === 0) {
    elements.promptHint.textContent = "可先预览 Prompt，也可以选择上下文卡片增加上下文。";
    setCatMood("材料已基本就绪，可以预览。");
  } else {
    elements.promptHint.textContent = `已选 ${selectedCount} 个上下文卡片，可预览 Prompt。`;
    setCatMood("上下文已挂载，可以预览。");
  }
}

function updateAnswerStats() {
  elements.answerStats.textContent = `${elements.llmAnswer.value.length} 字符`;
}

function updateWorkSurface() {
  updatePromptAssistant();
  updateAnswerStats();
}

function hideOptimizeBox() {
  elements.optimizeBox.classList.add("is-hidden");
  elements.optimizedPrompt.value = "";
  elements.optimizeHint.textContent = "由 LLM 优化，不会自动覆盖原 Prompt。";
}

async function previewPrompt() {
  const template = getSelectedTemplate();
  if (!template) {
    showToast("请先选择模板", true);
    return;
  }

  const payload = {
    template_id: template.id,
    variables: collectVariables(),
    context_card_ids: collectContextCardIds(),
    mode: "rule",
  };

  try {
    elements.previewPromptButton.disabled = true;
    setWorkflowStep("preview");
    elements.promptHint.textContent = "正在预览预生成 Prompt…";

    const result = await requestJson("/api/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    elements.finalPrompt.value = result.final_prompt;
    elements.aiPromptInput.value = result.final_prompt;
    hideOptimizeBox();

    const missingVariables = result.missing_variables || [];
    elements.promptHint.textContent = missingVariables.length
      ? `预生成 Prompt 已更新，未填写变量：${missingVariables.join("、")}。可继续编辑或保存当前草稿。`
      : "预生成 Prompt 已更新，可优化、复制、送去 AI 或保存到历史。";
    setCatMood("预生成 Prompt 已更新，保存由你决定。", "happy");
    showToast("预生成 Prompt 已更新");
    return result.final_prompt;
  } catch (error) {
    setWorkflowStep("compose");
    elements.promptHint.textContent = "预览失败，请稍后再试。";
    showToast(error.message, true);
    return "";
  } finally {
    elements.previewPromptButton.disabled = false;
  }
}

async function saveCurrentPrompt() {
  const template = getSelectedTemplate();
  const finalPrompt = elements.finalPrompt.value.trim();

  if (!template) {
    showToast("请先选择模板", true);
    return;
  }

  if (!finalPrompt) {
    showToast("暂无可保存的预生成 Prompt", true);
    return;
  }

  try {
    elements.savePromptButton.disabled = true;
    setWorkflowStep("save");
    elements.promptHint.textContent = "正在保存到历史…";

    const history = await requestJson("/api/history", {
      method: "POST",
      body: JSON.stringify({
        template_id: template.id,
        variables: collectVariables(),
        context_card_ids: collectContextCardIds(),
        final_prompt: finalPrompt,
      }),
    });

    await loadHistory();
    elements.promptHint.textContent = `已保存到历史 ID：${history.id}。`;
    setCatMood("这版预生成 Prompt 已收进历史。", "happy");
    showToast("预生成 Prompt 已保存到历史");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    elements.savePromptButton.disabled = false;
  }
}

async function optimizePrompt() {
  const prompt = elements.finalPrompt.value.trim() || await previewPrompt();
  if (!prompt.trim()) {
    showToast("暂无可优化的 Prompt", true);
    return;
  }

  try {
    elements.optimizePromptButton.disabled = true;
    setWorkflowStep("optimize");
    elements.optimizeHint.textContent = "正在调用 LLM 优化 Prompt…";
    elements.optimizeBox.classList.remove("is-hidden");
    setCatMood("正在把预生成 Prompt 打磨得更清楚。", "working");

    const result = await requestJson("/api/llm/optimize-prompt", {
      method: "POST",
      body: JSON.stringify({
        prompt,
        model: elements.llmModel.value || "deepseek-v4-flash",
        temperature: 0.2,
      }),
    });

    elements.optimizedPrompt.value = result.optimized_prompt;
    elements.optimizeHint.textContent = `优化完成，模型：${result.model}`;
    setCatMood("优化稿已准备好，可以采用或复制。", "happy");
    showToast("预生成 Prompt 优化完成");
  } catch (error) {
    elements.optimizeHint.textContent = error.message;
    showToast(error.message, true);
  } finally {
    elements.optimizePromptButton.disabled = false;
  }
}

function applyOptimizedPrompt() {
  const optimized = elements.optimizedPrompt.value.trim();
  if (!optimized) {
    showToast("暂无优化稿可采用", true);
    return;
  }

  elements.finalPrompt.value = optimized;
  elements.aiPromptInput.value = optimized;
  setWorkflowStep("save");
  elements.promptHint.textContent = "已采用优化稿，可送去 AI、复制或保存。";
  setCatMood("优化稿已放入工作台。", "happy");
}

async function copyText(text, message) {
  if (!String(text || "").trim()) {
    showToast("暂无可复制内容", true);
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const helper = document.createElement("textarea");
    helper.value = text;
    document.body.appendChild(helper);
    helper.select();
    document.execCommand("copy");
    helper.remove();
  }

  showToast(message);
}

function resetTemplateForm() {
  state.editingTemplateId = null;
  elements.templateForm.reset();
  elements.templateFormTitle.textContent = "新增模板";
  elements.saveTemplateButton.textContent = "保存模板";
  elements.cancelTemplateEditButton.classList.add("is-hidden");
}

function resetContextCardForm() {
  state.editingContextCardId = null;
  elements.contextCardForm.reset();
  elements.contextCardType.value = "background";
  refreshCustomSelect(elements.contextCardType);
  elements.contextCardFormTitle.textContent = "新增上下文卡片";
  elements.saveContextCardButton.textContent = "保存卡片";
  elements.cancelContextCardEditButton.classList.add("is-hidden");
}

async function saveTemplate(event) {
  event.preventDefault();

  const payload = {
    title: elements.templateTitle.value,
    category: elements.templateCategory.value || null,
    tags: parseTags(elements.templateTags.value),
    description: elements.templateDescription.value || null,
    content: elements.templateContent.value,
  };

  const isEditing = state.editingTemplateId !== null;
  const url = isEditing ? `/api/templates/${state.editingTemplateId}` : "/api/templates";
  const method = isEditing ? "PUT" : "POST";

  try {
    const saved = await requestJson(url, {
      method,
      body: JSON.stringify(payload),
    });

    state.selectedTemplateId = saved.id;
    resetTemplateForm();
    await loadData();
    showToast(isEditing ? "模板已更新" : "模板已保存");
  } catch (error) {
    showToast(error.message, true);
  }
}

async function saveContextCard(event) {
  event.preventDefault();

  const payload = {
    type: elements.contextCardType.value,
    title: elements.contextCardTitle.value,
    tags: parseTags(elements.contextCardTags.value),
    content: elements.contextCardContent.value,
  };

  const isEditing = state.editingContextCardId !== null;
  const url = isEditing ? `/api/context-cards/${state.editingContextCardId}` : "/api/context-cards";
  const method = isEditing ? "PUT" : "POST";

  try {
    const saved = await requestJson(url, {
      method,
      body: JSON.stringify(payload),
    });

    state.selectedContextCardIds.add(saved.id);
    resetContextCardForm();
    await loadData();
    showToast(isEditing ? "上下文卡片已更新" : "上下文卡片已保存");
  } catch (error) {
    showToast(error.message, true);
  }
}

function editTemplate(templateId) {
  const template = state.templates.find((item) => item.id === templateId);
  if (!template) {
    return;
  }

  state.editingTemplateId = templateId;
  elements.templateTitle.value = template.title;
  elements.templateCategory.value = template.category || "";
  elements.templateTags.value = (template.tags || []).join(", ");
  elements.templateDescription.value = template.description || "";
  elements.templateContent.value = template.content;
  elements.templateFormTitle.textContent = "编辑模板";
  elements.saveTemplateButton.textContent = "更新模板";
  elements.cancelTemplateEditButton.classList.remove("is-hidden");
  switchView("templates");
  elements.templateTitle.focus();
}

function editContextCard(contextCardId) {
  const contextCard = state.contextCards.find((item) => item.id === contextCardId);
  if (!contextCard) {
    return;
  }

  state.editingContextCardId = contextCardId;
  elements.contextCardType.value = contextCard.type || "background";
  refreshCustomSelect(elements.contextCardType);
  elements.contextCardTitle.value = contextCard.title;
  elements.contextCardTags.value = (contextCard.tags || []).join(", ");
  elements.contextCardContent.value = contextCard.content;
  elements.contextCardFormTitle.textContent = "编辑上下文卡片";
  elements.saveContextCardButton.textContent = "更新卡片";
  elements.cancelContextCardEditButton.classList.remove("is-hidden");
  switchView("contextCards");
  elements.contextCardTitle.focus();
}

async function deleteItem(url, successMessage, fallbackAction) {
  if (!window.confirm("确定要删除吗？这个操作会立即生效。")) {
    return;
  }

  try {
    await requestJson(url, { method: "DELETE" });
    await loadData();
    showToast(successMessage);
  } catch (error) {
    fallbackAction?.();
    renderAll();
    showToast(error.message, true);
  }
}

async function loadHistoryToPrompt(historyId) {
  const history = state.history.find((item) => item.id === historyId) || await requestJson(`/api/history/${historyId}`);
  elements.finalPrompt.value = history.final_prompt;
  elements.aiPromptInput.value = history.final_prompt;
  elements.promptHint.textContent = `已载入历史 ID：${history.id}`;
  switchView("dashboard");
  showToast("历史 Prompt 已载入");
}

async function askLlm() {
  const prompt = elements.aiPromptInput.value.trim() || elements.finalPrompt.value.trim();
  if (!prompt) {
    showToast("请先生成或填写 Prompt", true);
    return;
  }

  const payload = {
    prompt,
    model: elements.llmModel.value,
    temperature: Number(elements.llmTemperature.value || 0.7),
  };

  try {
    elements.askLlmButton.disabled = true;
    elements.llmAnswer.value = "";
    updateAnswerStats();
    setTerminalStatus("RUN", 18, true);
    elements.llmHint.textContent = `模型：${payload.model}，正在建立流式连接…`;

    const response = await fetch("/api/llm/answer/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    if (!response.body) {
      throw new Error("当前浏览器不支持流式读取响应");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    setTerminalStatus("READ", 62, true);
    elements.llmHint.textContent = `模型：${payload.model}，正在流式输出…`;

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      elements.llmAnswer.value += chunk;
      updateAnswerStats();
      elements.llmAnswer.scrollTop = elements.llmAnswer.scrollHeight;
    }

    const tail = decoder.decode();
    if (tail) {
      elements.llmAnswer.value += tail;
      updateAnswerStats();
    }

    setTerminalStatus("DONE", 100);
    elements.llmHint.textContent = `模型：${payload.model}，输出完成。`;
    showToast("AI 回答已完成");
  } catch (error) {
    setTerminalStatus("ERR", 100, false, true);
    elements.llmHint.textContent = error.message;
    showToast("AI 生成失败，请检查 API Key 或网络", true);
  } finally {
    elements.askLlmButton.disabled = false;
  }
}

async function saveAnswerAsContextCard() {
  const content = elements.llmAnswer.value.trim();
  if (!content) {
    showToast("暂无可保存的回答", true);
    return;
  }

  try {
    await requestJson("/api/context-cards", {
      method: "POST",
      body: JSON.stringify({
        type: "example",
        title: `AI 回答 ${dateTimeFormatter.format(new Date()).replace(/\//g, "-")}`,
        tags: ["AI回答"],
        content,
      }),
    });
    await loadData();
    switchView("contextCards");
    showToast("AI 回答已存为卡片");
  } catch (error) {
    showToast(error.message, true);
  }
}

function bindEvents() {
  initializeCustomSelects();

  elements.mobileMenuButton.addEventListener("click", () => {
    document.body.classList.add("sidebar-open");
  });
  elements.scrim.addEventListener("click", () => {
    document.body.classList.remove("sidebar-open");
  });

  elements.navItems.forEach((item) => {
    item.addEventListener("click", () => switchView(item.dataset.view));
  });

  document.querySelectorAll("[data-jump-view]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.jumpView));
  });

  document.querySelector("[data-focus-builder]").addEventListener("click", () => {
    document.querySelector("#builderArea").scrollIntoView({ behavior: "smooth", block: "start" });
    const firstVariableInput = elements.variableFields.querySelector("[data-variable-name]");
    (firstVariableInput || elements.quickTemplateSelect).focus();
  });

  elements.refreshButton.addEventListener("click", loadData);
  elements.variableFields.addEventListener("input", () => {
    setWorkflowStep("compose");
    updatePromptAssistant();
  });

  elements.quickTemplateSelect.addEventListener("change", () => {
    state.selectedTemplateId = Number(elements.quickTemplateSelect.value);
    refreshCustomSelect(elements.quickTemplateSelect);
    renderVariables();
    renderTemplates();
    hideOptimizeBox();
    setWorkflowStep("compose");
    updatePromptAssistant();
  });

  elements.contextCardChoices.addEventListener("change", (event) => {
    const checkbox = event.target.closest("[data-context-card-choice]");
    if (!checkbox) {
      return;
    }

    const id = Number(checkbox.value);
    if (checkbox.checked) {
      state.selectedContextCardIds.add(id);
    } else {
      state.selectedContextCardIds.delete(id);
    }

    updateSelectedContextCardCount();
    renderContextCards();
    hideOptimizeBox();
    setWorkflowStep("compose");
    updatePromptAssistant();
  });

  elements.previewPromptButton.addEventListener("click", previewPrompt);
  elements.savePromptButton.addEventListener("click", saveCurrentPrompt);
  elements.optimizePromptButton.addEventListener("click", optimizePrompt);
  elements.applyOptimizedButton.addEventListener("click", applyOptimizedPrompt);
  elements.copyOptimizedButton.addEventListener("click", () => copyText(elements.optimizedPrompt.value, "优化稿已复制"));
  elements.copyPromptButton.addEventListener("click", () => copyText(elements.finalPrompt.value, "预生成 Prompt 已复制"));
  elements.pushToAiButton.addEventListener("click", () => {
    elements.aiPromptInput.value = elements.finalPrompt.value;
    setWorkflowStep("save");
    switchView("ai");
    showToast("预生成 Prompt 已同步到 AI 控制台");
  });

  elements.templateForm.addEventListener("submit", saveTemplate);
  elements.cancelTemplateEditButton.addEventListener("click", resetTemplateForm);
  elements.contextCardForm.addEventListener("submit", saveContextCard);
  elements.cancelContextCardEditButton.addEventListener("click", resetContextCardForm);

  elements.templateList.addEventListener("click", (event) => {
    const useButton = event.target.closest("[data-use-template-id]");
    const editButton = event.target.closest("[data-edit-template-id]");
    const deleteButton = event.target.closest("[data-delete-template-id]");
    const card = event.target.closest("[data-template-id]");

    if (useButton) {
      state.selectedTemplateId = Number(useButton.dataset.useTemplateId);
      renderTemplateSelect();
      renderTemplates();
      switchView("dashboard");
      showToast("模板已同步到快速生成区");
      return;
    }

    if (editButton) {
      editTemplate(Number(editButton.dataset.editTemplateId));
      return;
    }

    if (deleteButton) {
      const templateId = Number(deleteButton.dataset.deleteTemplateId);
      deleteItem(`/api/templates/${templateId}`, "模板已删除", () => {
        state.templates = state.templates.filter((item) => item.id !== templateId);
      });
      return;
    }

    if (card) {
      state.selectedTemplateId = Number(card.dataset.templateId);
      renderTemplateSelect();
      renderTemplates();
    }
  });

  elements.contextCardList.addEventListener("click", (event) => {
    const toggleButton = event.target.closest("[data-toggle-context-card-id]");
    const editButton = event.target.closest("[data-edit-context-card-id]");
    const deleteButton = event.target.closest("[data-delete-context-card-id]");

    if (toggleButton) {
      const contextCardId = Number(toggleButton.dataset.toggleContextCardId);
      if (state.selectedContextCardIds.has(contextCardId)) {
        state.selectedContextCardIds.delete(contextCardId);
      } else {
        state.selectedContextCardIds.add(contextCardId);
      }
      renderContextCardChoices();
      renderContextCards();
      return;
    }

    if (editButton) {
      editContextCard(Number(editButton.dataset.editContextCardId));
      return;
    }

    if (deleteButton) {
      const contextCardId = Number(deleteButton.dataset.deleteContextCardId);
      deleteItem(`/api/context-cards/${contextCardId}`, "上下文卡片已删除", () => {
        state.contextCards = state.contextCards.filter((item) => item.id !== contextCardId);
        state.selectedContextCardIds.delete(contextCardId);
      });
    }
  });

  const handleHistoryClick = (event) => {
    const loadButton = event.target.closest("[data-load-history-id]");
    const copyButton = event.target.closest("[data-copy-history-id]");
    const deleteButton = event.target.closest("[data-delete-history-id]");
    const card = event.target.closest("[data-history-id]");

    if (loadButton) {
      loadHistoryToPrompt(Number(loadButton.dataset.loadHistoryId));
      return;
    }

    if (copyButton) {
      const history = state.history.find((item) => item.id === Number(copyButton.dataset.copyHistoryId));
      copyText(history?.final_prompt || "", "历史 Prompt 已复制");
      return;
    }

    if (deleteButton) {
      const historyId = Number(deleteButton.dataset.deleteHistoryId);
      deleteItem(`/api/history/${historyId}`, "历史记录已删除", () => {
        state.history = state.history.filter((item) => item.id !== historyId);
      });
      return;
    }

    if (card) {
      loadHistoryToPrompt(Number(card.dataset.historyId));
    }
  };

  elements.recentHistoryList.addEventListener("click", handleHistoryClick);
  elements.historyList.addEventListener("click", handleHistoryClick);
  elements.reloadHistoryButton.addEventListener("click", loadHistory);

  elements.llmTemperature.addEventListener("input", () => {
    elements.temperatureValue.textContent = elements.llmTemperature.value;
  });
  elements.askLlmButton.addEventListener("click", askLlm);
  elements.copyAnswerButton.addEventListener("click", () => copyText(elements.llmAnswer.value, "AI 回答已复制"));
  elements.saveAnswerContextCardButton.addEventListener("click", saveAnswerAsContextCard);

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".custom-select")) {
      closeCustomSelects();
    }
  });

  document.addEventListener("pointerover", (event) => {
    const target = event.target.closest(".has-hover-tip");
    if (!target) {
      return;
    }
    if (target.closest(".custom-select")) {
      return;
    }
    showHoverTooltip(target, event);
  });

  document.addEventListener("pointermove", (event) => {
    moveHoverTooltip(event);
  });

  document.addEventListener("pointerout", (event) => {
    const target = event.target.closest(".has-hover-tip");
    if (target && !target.contains(event.relatedTarget)) {
      hideHoverTooltip();
    }
  });

  document.addEventListener("focusin", (event) => {
    const target = event.target.closest(".has-hover-tip");
    if (!target) {
      return;
    }
    const rect = target.getBoundingClientRect();
    showHoverTooltip(target, {
      clientX: rect.left + Math.min(rect.width / 2, 220),
      clientY: rect.top + 12,
    });
  });

  document.addEventListener("focusout", (event) => {
    const target = event.target.closest(".has-hover-tip");
    if (target && !target.contains(event.relatedTarget)) {
      hideHoverTooltip();
    }
  });

  document.addEventListener("scroll", (event) => {
    if (event.target.closest && event.target.closest(".custom-select-menu")) {
      return;
    }
    closeCustomSelects();
    hideHoverTooltip();
  }, true);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document.body.classList.remove("sidebar-open");
      closeCustomSelects();
      hideHoverTooltip();
    }
  });
}

bindEvents();
loadData();
