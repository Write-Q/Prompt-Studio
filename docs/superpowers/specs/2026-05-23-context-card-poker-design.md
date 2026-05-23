# 知识卡片 · 扑克牌出牌交互设计

- 创建日期：2026-05-23
- 改造对象：PromptStudio 仪表盘的"上下文卡片选择区"
- 改造范围：纯前端（HTML / CSS / JS），后端与数据模型不动

## 1. 背景与目标

仪表盘 `#contextCardChoices` 当前是勾选式 `<label class="choice-card"><input type="checkbox">` 列表（`frontend/script.js:1036-1058`），交互平淡、缺乏仪式感。希望改造成**像打扑克牌出牌**的视觉：手牌在底部按类型分堆排列，点击卡片"飞"到上方出牌区表示挂载进 Prompt。

设计需要在保持现有数据模型与拼装流程（5 种 `ContextCardType`、`CARD_TYPE_ORDER`、`state.selectedContextCardIds`、`/api/generate`）零改动的前提下完成。

## 2. 不改什么

- 后端路由、服务、数据库：完全不动
- `state.selectedContextCardIds` 这个 `Set<id>` 仍然是唯一真源
- `/api/generate` 调用 payload 不变
- 上下文卡片库视图（`#contextCardList`）不动，仍是 CRUD 列表
- result-panel（预生成 Prompt 区）不动

## 3. 布局结构

`builder-panel` 内"上下文卡片"段落整体替换为三层结构：

```
builder-panel 内：
┌────────────────────────────────────────┐
│ 选择模板 + 模板变量（不动）             │
├────────────────────────────────────────┤
│ ▒ 出牌区（已挂载卡片）▒                 │
│   ┌──┐ ┌──┐                            │
│   │背│ │规│  ← 已出的牌横排             │
│   └──┘ └──┘                            │
├────────────────────────────────────────┤
│ ▒ 手牌堆区 ▒                            │
│   ┌─┐⁶ ┌─┐⁶ ┌─┐⁶ ┌─┐⁶ ┌─┐⁶            │
│   │背│ │规│ │格│ │示│ │检│             │
│   └─┘ └─┘ └─┘ └─┘ └─┘                 │
└────────────────────────────────────────┘
```

result-panel（预生成 Prompt 区）保持原位，整体仍是 `dashboard-grid` 左右双栏。

## 4. 手牌堆（防乱三层）

### 4.1 默认形态

底部 5 堆并排，按 `CARD_TYPE_ORDER` 顺序：background → rule → format → example → checklist。

每堆只露顶上一张卡 + 右上角圆形数字徽章。徽章显示**该类型已挂载/总数**（如 `2/6`）；当已挂载为 0 时只显示总数（如 `6`）。堆侧边带 1-2° 旋转偏移，制造"一摞纸牌"的层叠错位感。

堆的整体状态用三种视觉表达：

- 全未挂载：默认外观
- 部分挂载：堆边缘呈现细金边
- 全部挂载：金边变粗，并叠加 ✓ 角标

### 4.2 点击展开

被点击的堆扇形展开：

- 圆弧覆盖 ±20°（共 40°）
- 相邻卡片以 60% 卡宽交叠
- 沿扇心向外 translateY 升起 ~30px
- 进入动画 250ms ease-out，每张卡 stagger 30ms

其余 4 堆同时缩到旁边，宽度变为正常的 50%，进入"待选"灰度状态。

再次点击堆头、Esc 键或点击扇形外的空白区：当前展开堆以 180ms ease-in 退回（exit 时长约为 enter 的 70%）。

同一时刻最多一堆处于展开状态。

### 4.3 单堆翻页（卡片 >10 张时启用）

某一类型卡片超过 10 张时，扇形分页显示，下方出现页码指示器 `● ○ ○`。点击指示器或在扇内向左右拖动切换页面。

## 5. 出牌区（已挂载卡片显示）

位于变量区与手牌堆之间，高度按已选卡数动态：

- **0 张**：极扁占位条（高度 ~36px），显示提示文字"点击下方卡堆把卡片打过来"
- **1-6 张**：横排展开，每张卡完整可见，右上角小 ✕ 按钮，点击退回手牌
- **>6 张**：从第 7 张起层叠收边（卡片以 -20px margin-left 互相重叠），hover 该层叠区时轻微扇开方便查看

出牌区的卡片就是手牌堆里被点击的卡片的"副本展示" —— 数据上仍只有 `state.selectedContextCardIds` 一处真源，出牌区只是这个集合的可视化。

## 6. 卡片正面（信息密度：中）

```
┌────────────┐
│ ▓▓▓ 背景 ▓▓│  ← 类型色带 + 中文徽章
│            │
│   日常使用  │  ← 标题（最多 8 字两行，超出截断+省略号）
│   方式      │
│            │
│  ╭───╮     │
│  │ ◐ │     │  ← 小像素装饰
│  ╰───╯     │
└────────────┘
```

完整内容、tags、类型完整名称通过 hover tooltip 显示（复用 `frontend/script.js:584-597` 现有 `.hover-tooltip` 机制 + `contextCardHoverText()`）。

### 6.1 类型配色

| 类型 | 主色 | 中文徽章 |
|------|------|---------|
| background | `#f4c66a` 米黄 | 背景 |
| rule | `#d96850` 砖红 | 规则 |
| format | `#6b8aa8` 灰蓝 | 格式 |
| example | `#7ab85c` 草绿 | 示例 |
| checklist | `#8e6bb5` 紫灰 | 检查 |

色带与中文徽章**双重表达**，不靠颜色独占语义（WCAG 兼容）。

### 6.2 卡片背面

复用 brand 区的 `pixel-cat` SVG 作为图案，搭配 ▒▓▒ 棋盘纹背景。背面在以下场景使用：

- 翻页过渡的中间帧
- 拖动/出牌动画的初始帧（增强"翻牌"感）

## 7. 动效

| 动作 | 时长 | 曲线 | 备注 |
|------|------|------|------|
| 收→扇形展开 | 250ms | ease-out | stagger 30ms/张 |
| 扇形→收 | 180ms | ease-in | exit < enter |
| 出牌（手牌→出牌区） | 280ms | `cubic-bezier(0.34, 1.2, 0.5, 1)` | 带轻微回弹 |
| 退牌（出牌区→手牌） | 240ms | ease-in-out | |
| hover 卡片 | 120ms | ease-out | `translateY(-8px) scale(1.04)` |
| 翻页 | 200ms | ease-in-out | 水平 fade + slide |

约束：

- 全部动效仅用 `transform` 和 `opacity`（避免 layout reflow）
- 出牌动画用 FLIP 技巧（First-Last-Invert-Play）：先在出牌区占位、计算起止位置差、用 transform 从手牌位置过渡到 0
- 全局尊重 `prefers-reduced-motion: reduce` —— 启用时所有动效统一降级为 100ms 的 `opacity` fade

## 8. 无障碍

- 每堆是 `<button>` 元素，`aria-label="背景资料 6 张，3 张已挂载"`
- 扇形展开后每张卡是 `<button role="option" aria-selected="true|false">`，selected 状态反映"是否已出"
- 出牌区每张卡的 ✕ 按钮：`aria-label="退回背景资料：日常使用方式"`
- 键盘流程：
  - Tab 在 5 堆之间循环
  - Enter / Space 在堆上展开/收起
  - 展开后方向键在扇形内移动焦点
  - Enter / Space 出牌或退牌
  - Esc 收回当前展开的堆
- 焦点可见：每个交互元素有 2px 描边焦点环（不依赖默认浏览器样式）

## 9. 实现拆解

### 9.1 HTML（`frontend/index.html`）

将 `#contextCardChoices` 容器内部替换为：

```html
<div id="contextCardChoices" class="poker-zone">
  <div class="poker-table" data-poker-table>
    <!-- 已出的卡片：动态渲染 -->
  </div>
  <div class="poker-hand" data-poker-hand>
    <!-- 5 个 .poker-pile，动态渲染 -->
  </div>
</div>
```

原 `.choice-list` 类（`frontend/style.css:695, 1021`）只在该容器使用，新结构不再需要它的网格样式，可直接换掉。计数显示元素 `#selectedContextCardCount` 是独立节点，由 `updateSelectedContextCardCount()` 维护，与本次结构改造无耦合，保持原样。

### 9.2 JS（`frontend/script.js`）

**状态新增**：

```js
state.expandedPileType = null;  // 当前展开的堆类型，null 表示都收起
state.pilePageIndex = {};       // 每个堆当前页码，键为类型，默认 0
```

**新增/重写函数**：

- `renderContextCardChoices()` — 重写：分组渲染 5 堆 + 出牌区
- `renderPokerPile(type, cards)` — 渲染单个堆（收/展形态）
- `renderPokerTable()` — 渲染出牌区
- `expandPile(type)` — 切换展开（含自动收起其他堆）
- `collapsePile()` — 收回当前展开
- `playCard(cardId)` — 把卡加入 `selectedContextCardIds`，触发出牌动画
- `recallCard(cardId)` — 反向操作
- `pagePile(type, delta)` — 翻页

**事件**：

- 堆头点击 → `expandPile`
- 扇形里卡片点击 → `playCard`
- 出牌区卡片 ✕ 点击 → `recallCard`
- Esc / 全局 click outside → `collapsePile`
- 键盘导航绑定

**数据集成**：以上所有操作都通过修改 `state.selectedContextCardIds` 这个唯一真源驱动 re-render，与现有 `previewPrompt()`、`saveCurrentPrompt()` 等流程自动兼容。

### 9.3 CSS（`frontend/style.css`）

新增类：

- `.poker-zone` — 容器
- `.poker-table` — 出牌区
- `.poker-table--empty` / `.poker-table--full` — 空/超 6 张时的样式变体
- `.poker-hand` — 手牌堆区
- `.poker-pile` — 单个堆
- `.poker-pile--expanded` / `.poker-pile--dimmed` — 展开/灰化状态
- `.poker-card` — 单张卡
- `.poker-card--type-{background|rule|format|example|checklist}` — 类型变体
- `.poker-card--face-down` — 背面
- `.poker-card--selected` — 已挂载金边
- `.poker-pager` — 翻页指示器

动画用 CSS `transition` + 必要的 `@keyframes`（如 stagger 入场用 nth-child 延迟）。

## 10. 验收标准

实现完成后必须满足：

1. 选择模板后，下方 5 堆按 `CARD_TYPE_ORDER` 顺序渲染，每堆显示数字徽章
2. 点击堆头能展开扇形，其余 4 堆自动缩窄
3. 点击扇内卡片飞到上方出牌区，手牌中对应卡片显示金边"已挂载"
4. 出牌区卡片点击 ✕ 能退回手牌
5. 同时只有一个堆展开
6. 单堆 >10 张时出现翻页指示器
7. 出牌后调用 `previewPrompt()`，生成的 Prompt 应包含被选卡片的内容（与改造前行为一致）
8. 键盘 Tab / 方向键 / Enter / Esc 全部可用
9. `prefers-reduced-motion: reduce` 时无大幅度动画
10. 浏览器控制台无报错，`node --check frontend\script.js` 通过

## 11. 不在本次范围

- 上下文卡片库视图（`#contextCardsView`）的样式
- 模板/历史/AI 三个视图
- 拖拽出牌（仅支持点击）
- 搜索/标签筛选（当前数据规模不需要）
- 移动端响应式适配（保留为后续工作）
- 卡片背面图案的精细化设计（先用现有 pixel-cat SVG）
