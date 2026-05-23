# 知识卡片扑克牌交互 Polish v2 · 设计稿

**日期：** 2026-05-23
**前置实现：** `docs/superpowers/specs/2026-05-23-context-card-poker-design.md`（v1 已落地，commits `9b44f03..01bbe67`）
**对应 plan：** `docs/superpowers/plans/2026-05-23-context-card-poker-polish.md`（由 writing-plans 生成）

---

## 1. 背景与动机

v1 把仪表盘上下文卡片改造成 5 堆扑克牌 + 扇形展开 + 点击出牌，已上线。用户体验后提出三条反馈：

1. **切换不流畅**：出牌瞬间没飞行动画（卡突然消失、出牌区凭空出现）；收堆没有反向动画
2. **想要拖拽出牌的"手感"**：纯点击交互缺少物理感
3. **hover 看卡片信息不流畅**：现有 `.hover-tooltip` 跟鼠标飘、跨卡切换闪烁、和扇内卡上浮动画叠加显得乱

经 brainstorming 确认：
- 结构保留（5 堆默认收叠、点击散成扇形），不推翻
- 拖拽走"双轨并存"（点击 + 拖拽 + 键盘三套都保留）
- hover 改成卡片自展开（去掉全局浮层）
- 出牌区升级成小弧形（"已出手牌"观感）

## 2. 目标

| 维度 | v1 现状 | v2 目标 |
|---|---|---|
| 出牌反馈 | 卡瞬间消失，出牌区凭空出现 | 卡从原位飞到出牌区目标位（FLIP，带回弹） |
| 退牌反馈 | 出牌区卡瞬间消失 | 卡从出牌区飞回该堆头 |
| 收堆 | 扇内卡 fade-out | 每张卡反向飞回堆头（stagger） |
| hover | 全局浮层跟鼠标 | 该卡放大 1.4x + 卡内展开"详情" |
| 出牌操作 | 仅点击 | 点击 / 拖拽 / 键盘 三轨并存 |
| 出牌区形态 | 横向 flex 排列 | 向上微凹的小弧形 |
| 扇形角度 | 每张 4°、上限 40° | 固定 12°/张严格对称 |
| 动效降级 | 已支持 prefers-reduced-motion | 新增动画也要支持 |

## 3. 边界

- **后端 / 数据库 / `/api/*` 路径完全不改**
- **`frontend/index.html` 不改**（v1 已建好 `.poker-zone` 骨架）
- **`tests/` 不改**（项目无前端测试套件；前端验证靠 `node --check` + 手测；后端 `unittest` 跑一次确认无回归）
- v1 已有的"5 堆 + 点击展开 + 单堆 >10 张分页 + 键盘导航 + ARIA"全部保留并向后兼容

## 4. 状态新增

`frontend/script.js` 中 `state` 对象追加三个字段：

```js
state.draggingCardId    // number | null —— 当前拖拽中的卡 id
state.draggingFromZone  // "hand" | "table" | null —— 拖拽起点区域
state.hoveredCardId     // number | null —— 强制进入"详情视图"的卡 id
```

不新增后端字段、不新增 localStorage 持久化字段。

## 5. 改动点详述

### 5.1 FLIP 飞行框架

新增工具函数 `flipAnimate(fromRect, toEl, options)`：

- 输入：起点 `DOMRect`、终点元素、可选项 `{duration, easing, onFinish}`
- 行为：在终点元素上算出当前 rect，反算 transform = `translate(dx, dy) scale(sx, sy)`，先 apply 让它"看起来在起点"，然后 `requestAnimationFrame` 内播 `transform → none`
- 默认参数：`duration = 320ms`，`easing = cubic-bezier(0.34, 1.2, 0.5, 1)`（带轻回弹）
- 中断保护：若该元素已有进行中的 FLIP animation，先 `cancel()` 再起新动画

所有"飞行"类动画统一走这个函数：出牌、退牌、出牌区内的弧位重排。

### 5.2 出牌飞行动画（解决痛点 C）

`playCard(cardId)` 改造：

1. 找到当前 DOM 里该卡的源元素（扇内卡），`rect0 = el.getBoundingClientRect()`
2. `state.selectedContextCardIds.add(cardId)`
3. `renderContextCardChoices()`（同步重渲染让出牌区生成新位）
4. 在新 DOM 里找到该卡的目标元素（出牌区里那张），调 `flipAnimate(rect0, targetEl)`
5. 同时触发其他流程：`renderContextCards()` / `hideOptimizeBox()` / `setWorkflowStep("compose")` / `updatePromptAssistant()`

### 5.3 退牌飞回动画

`recallCard(cardId)` 镜像处理：

1. 记录出牌区源元素 rect
2. 从 state 删除
3. 重渲染
4. FLIP 目标元素 = 该卡所属类的堆头（`.poker-pile[data-poker-pile="${type}"]`）

### 5.4 hover 卡片自展开（解决痛点 hover）

去除：扇内卡 `renderPokerCard()` 不再附加 `.has-hover-tip` 与 `data-tooltip`（堆头、出牌区卡可保留浮层使用，不本次范围）

新增：
- CSS 类 `.poker-card--detail`：放大 1.4x、上浮 14px、`z-index: 999`、`box-shadow` 加强
- 工具函数 `renderPokerCardInternals(cardEl, card, isDetail)`：清空卡内 children 后按状态重建
  - 默认：色条 + 标题（line-clamp 3）
  - 详情：色条 + 标题（line-clamp 2）+ 标签云（小胶囊，最多 3 个）+ 内容前 80 字（line-clamp + 底部渐变截断）
- `renderPokerCard()` 内部改为调 `renderPokerCardInternals(wrapper, card, false)`，保证默认路径不变

事件：
- 扇内卡 `mouseenter` / `focusin` → 设 `state.hoveredCardId = id`，对该卡加 class 并调 `renderPokerCardInternals(cardEl, card, true)`（局部 DOM 切换，不全量 re-render）
- `mouseleave` / `focusout` → 清 `state.hoveredCardId`，移除 class，调 `renderPokerCardInternals(cardEl, card, false)` 切回默认布局
- 拖拽态下（`state.draggingCardId != null`）不进入详情视图（避免视觉冲突）；进入拖拽时若当前有 hover 详情，先强制退出
- 全量 re-render（如出牌后）：保留 `state.hoveredCardId`，新 DOM 里对该 id 的卡 hydrate 时即附加详情布局

### 5.5 桌面拖拽（pointer 事件）

不使用 HTML5 DnD（无法控制样式），自研 pointer 事件控制器。

**触发条件**（避免点击误判为拖）：
- `pointerdown` 在扇内卡或出牌区卡上 → 记录起点 `{x, y, time, cardId, fromZone}`
- `pointermove` 满足以下任一 → 进入拖拽态：
  - 位移 ≥ 6px
  - 按住时间 ≥ 100ms 且位移 ≥ 2px

**拖拽态视觉**：
- 克隆源卡到 `<body>` 末尾，`position: fixed`、`pointer-events: none`、`z-index: 2000`、跟随光标偏移
- 源卡原位保留，加 `.poker-card--ghost` 类（opacity 0.3、虚化）
- 出牌区加 `.poker-table--drop-target` 类（金色虚线边框 + 背景微亮）
- 若 `fromZone === "table"`（拖回退牌），所有堆头加 `.poker-pile--drop-target` 类（金色边）

**落点判定**（`pointerup`）：
- 命中出牌区 rect 且 `fromZone === "hand"` → `playCard(cardId)`，移除克隆，FLIP 收尾飞到目标位
- 命中堆头 rect 且 `fromZone === "table"` → `recallCard(cardId)`，FLIP 飞回堆头
- 命中出牌区 rect 且 `fromZone === "table"` → 不动（无意义）
- 其他情况 → 克隆 300ms 回弹消失（`cubic-bezier(0.4, 0, 0.2, 1)`），state 清零

**异常**：
- `pointercancel` / window `blur` → 强制走"回弹消失 + 清零"分支

### 5.6 出牌区升级成弧形（方案 3 增量）

`renderPokerTable(table)` 改造：

- 容器仍是 `.poker-table`，但改用 `position: relative`，子卡 `position: absolute`
- 已挂载卡按 `selectedContextCardIds` 插入顺序均匀分布在向上凹的小弧上
  - 半径 R ≈ 180px（比扇内 150px 大）
  - 弧度跨 60°（比扇内 40° 大）
  - 卡片 `transform-origin: 50% 110%`（沿圆心方向）
  - 角度间隔 = 60° / max(1, count - 1)
- 超过 6 张走原有 `.poker-table__overflow` 堆叠（保留 v1 行为）
- 出牌区高度调整：从 110px → 130px（留弧形空间）

### 5.7 触屏拖拽 + 拖回退牌

- 触屏：`touchstart` 长按 200ms（或位移 ≥ 8px）触发拖拽，避免和页面滚动冲突
- 扇内卡和出牌区卡设 `touch-action: none`，body 仍可滚
- 拖回退牌：复用 5.5 中 `fromZone === "table"` 分支

### 5.8 扇形角度规整 + 收堆反向飞 + reduced-motion

**扇形角度算法**（重写 v1 的 `renderPokerFan`）：
- 期望：每张卡固定 12° 间距，从中心严格对称
- 但 v1 容器 `.poker-pile--expanded` 宽 360px 限制了总弧度，所以分段处理：
  - n ≤ 7 张：12°/张严格对称（总弧度 ≤ 72°，容器够宽）
  - n > 7 张：总弧度封顶 84°，等分到 (n-1) 份（每张 ≤ 12°，最坏 12° 比 v1 的 ~4.4° 仍宽得多）
- 公式：`step = min(12, 84 / max(1, n-1))`，`angle_i = (i - (n-1)/2) * step`
- 半径 R = 150px（保持不变）
- offsetX = `R * sin(angle)`，offsetY = `R * (1 - cos(angle))`（沿弧线分布）
- 超过 10 张走 v1 已有的分页（保留），分页后单页最多 10 张，落入 "n > 7" 分支

**收堆动画**：
- `collapsePile()` 不再瞬间 re-render，先对当前扇内每张卡播一遍反向 FLIP（终点 = 堆头 rect），stagger 20ms
- 全部动画结束后才 `state.expandedPileType = null` + re-render

**5 堆变窄/变灰过渡曲线**：`ease-out` → `cubic-bezier(0.4, 0, 0.2, 1)`（v1 的 transition 在 `.poker-pile` 选择器上）

**prefers-reduced-motion**：v1 已有的媒体查询块追加新规则：
- FLIP 动画 → 简化为 100ms opacity 淡入
- 拖拽克隆 → 直接跟手不带 transform transition
- hover 详情切换 → 100ms 直切，不放大

## 6. 错误与边界

| 场景 | 处理 |
|---|---|
| 拖拽中 `pointercancel` / window blur | 克隆 300ms 回弹消失，state 三个字段清零 |
| FLIP 动画期间再次触发同卡 FLIP | `Animation.cancel()` 旧动画，从当前 transform 起新动画 |
| 触屏长按和滚动冲突 | `touch-action: none` 仅扇内卡/出牌区卡 |
| 拖出后松开在非出牌区非堆头 | 回弹，不变更 state |
| 拖出牌区卡时落回出牌区 | 不变更 state（无意义） |
| hover 详情态下被拖拽触发 | 强制退出详情态，进入拖拽态 |
| reduced-motion 用户 | FLIP / 拖拽 / 详情切换全部简化为 fade，无 transform 动画 |
| 出牌区从 0 → 1 张 / 1 → 0 张 | 弧度计算用 `max(1, count-1)` 避免除零 |

## 7. 验证

项目无前端单元测试。验证三件套：

1. **语法**：`node --check frontend\script.js`
2. **后端体检**：`D:\VScode\Python\PromptStudio\.venv\Scripts\python.exe -m unittest discover -s tests` —— 应全绿（本次不改后端）
3. **手测 acceptance**（浏览器 `http://127.0.0.1:8000/app/`）：
   - [ ] hover 任一扇内卡 → 卡放大显示色条/标题/标签/内容前 80 字；移开恢复
   - [ ] 点击扇内卡 → 看到卡从扇位飞到出牌区弧上目标位（FLIP，带轻回弹）
   - [ ] 按住扇内卡拖出 → 跟随鼠标，原位留虚化幻影；松开在出牌区命中 → 出牌；松开在外 → 回弹复位
   - [ ] 点击出牌区 ✕ → 卡飞回该堆头
   - [ ] 拖出牌区卡到任意堆头 → 退牌（堆头在拖拽态下有金色边反馈）
   - [ ] 按 Esc / 点空白 → 扇内卡逐张反向飞回堆头收堆
   - [ ] 触屏长按扇内卡 → 触发拖拽（手机模拟器或真机）
   - [ ] DevTools 启用 prefers-reduced-motion: reduce → 所有飞行 / 拖拽 / 放大变成简单淡入，无 transform 动画

## 8. Task 拆分（预估）

由 writing-plans 定稿，预计 6 个 Task：

1. **FLIP 框架 + 出牌飞行 + 退牌飞回**（5.1 + 5.2 + 5.3）
2. **hover 卡片自展开**（5.4，含去掉扇内卡浮层）
3. **桌面拖拽出牌**（5.5）
4. **出牌区弧形布局**（5.6）
5. **触屏长按拖拽 + 拖回退牌**（5.7）
6. **扇形角度规整 + 收堆反向飞 + reduced-motion 兜底**（5.8）

每个 Task 都要求语法检查 + 手测对应 acceptance + commit。

## 9. 文件改动估算

| 文件 | 估算 |
|---|---|
| `frontend/script.js` | 新增 ~250 行（FLIP 工具、pointer 控制器、详情态切换、出牌区弧形算法），修改 ~50 行（renderPokerFan、renderPokerTable、事件路由、playCard/recallCard） |
| `frontend/style.css` | 追加 ~200 行（出牌区弧形、详情卡放大、FLIP 过渡、拖拽幻影、出牌区/堆头拖拽高亮、reduced-motion 增量） |
| `frontend/index.html` | 不动 |
| 后端 / DB / tests | 不动 |

## 10. 后续（不在本次范围）

- 拖拽出牌时的"抛掷"物理感（速度 → 角动量 → 落地反弹）
- 出牌区已挂载卡的拖拽重排序
- 移动端响应式布局（屏宽 <600px 时的弧度收紧）
- 卡片背面像素图案
- 搜索 / 标签筛选
