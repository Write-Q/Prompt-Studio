# 扑克牌交互 Polish v2 · 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 v1 扑克牌交互（5 堆 + 点击展开 + 出牌）基础上，补全出牌/退牌飞行动画、加双轨拖拽、把 hover 浮层改成卡片自展开、出牌区升级为弧形、扇形角度规整化，并保留全部 v1 行为与 reduced-motion 兜底。

**Architecture:** 纯前端 vanilla JS 改造。新增三类基础设施：(1) FLIP 飞行工具 `flipAnimate`，统一所有"飞行"类动画；(2) pointer 事件拖拽控制器 `dragController`，同时处理桌面与触屏；(3) 卡内详情态切换工具 `renderPokerCardInternals`。状态新增三字段（`draggingCardId` / `draggingFromZone` / `hoveredCardId`），后端/DB/`index.html`/`tests/` 完全不动。

**Tech Stack:** 原生 HTML/CSS/JS（无构建步骤）。FLIP 模式（First/Last/Invert/Play）+ pointer events + CSS transitions + `prefers-reduced-motion`。验证靠 `node --check` + 浏览器手测 + 后端 `unittest` 兜底。

**前置 spec：** `docs/superpowers/specs/2026-05-23-context-card-poker-polish-design.md`
**前置实现：** v1 已合入 `context-card-v1` 分支（commits `9b44f03..01bbe67`）。

---

## 文件结构

| 文件 | 责任 | 改动 |
|---|---|---|
| `frontend/script.js` | 状态、渲染、事件、FLIP 工具、拖拽控制器、详情态工具 | 新增 ~250 行，修改 ~50 行 |
| `frontend/style.css` | 出牌区弧形、详情卡放大、FLIP 过渡、拖拽幻影/高亮、reduced-motion 增量 | 追加 ~200 行 |
| `frontend/index.html` | 不动 |
| 后端 / DB / `tests/` | 不动 |

---

## 任务清单（共 6 个 Task）

- Task 1：FLIP 飞行框架 + 出牌/退牌飞行动画
- Task 2：hover 卡片自展开（去扇内浮层）
- Task 3：桌面拖拽出牌（pointer 事件）
- Task 4：出牌区升级成小弧形
- Task 5：触屏长按拖拽 + 拖回退牌
- Task 6：扇形角度规整 + 收堆反向飞 + reduced-motion 兜底

---

## Task 1：FLIP 飞行框架 + 出牌/退牌飞行动画

**Files:**
- Modify: `frontend/script.js`（新增 `flipAnimate` 工具；改 `playCard`、`recallCard`）
- Modify: `frontend/style.css`（追加 FLIP 配套样式）

### Step 1：在 script.js 末尾追加 flipAnimate 工具

- [ ] 在 `frontend/script.js` 文件末尾追加：

```js
/* ===== FLIP 飞行框架 ===== */
const FLIP_DEFAULTS = {
  duration: 320,
  easing: "cubic-bezier(0.34, 1.2, 0.5, 1)",
};

function flipAnimate(fromRect, toEl, options = {}) {
  if (!toEl || !fromRect) return null;
  const opts = { ...FLIP_DEFAULTS, ...options };
  const toRect = toEl.getBoundingClientRect();
  const dx = fromRect.left - toRect.left;
  const dy = fromRect.top - toRect.top;
  const sx = fromRect.width === 0 ? 1 : fromRect.width / toRect.width;
  const sy = fromRect.height === 0 ? 1 : fromRect.height / toRect.height;

  if (toEl._flipAnim) {
    toEl._flipAnim.cancel();
  }

  const anim = toEl.animate(
    [
      { transform: `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})`, zIndex: 200 },
      { transform: "translate(0, 0) scale(1, 1)", zIndex: 200 },
    ],
    { duration: opts.duration, easing: opts.easing, fill: "both" },
  );
  toEl._flipAnim = anim;
  anim.addEventListener("finish", () => {
    if (toEl._flipAnim === anim) {
      toEl._flipAnim = null;
    }
    if (typeof opts.onFinish === "function") opts.onFinish();
  });
  return anim;
}

function captureCardRect(cardId, zone = "any") {
  const root = elements.contextCardChoices;
  let selector;
  if (zone === "hand") {
    selector = `.poker-pile__fan .poker-card[data-card-id="${cardId}"]`;
  } else if (zone === "table") {
    selector = `.poker-table .poker-card[data-card-id="${cardId}"]`;
  } else {
    selector = `.poker-card[data-card-id="${cardId}"]`;
  }
  const el = root?.querySelector(selector);
  return el ? el.getBoundingClientRect() : null;
}
```

### Step 2：改 playCard 走 FLIP

- [ ] 替换 `frontend/script.js:1310` 处的 `playCard` 函数。

**Old:**
```js
function playCard(cardId) {
  if (state.selectedContextCardIds.has(cardId)) {
    return;
  }
  state.selectedContextCardIds.add(cardId);
  renderContextCardChoices();
  renderContextCards();
  hideOptimizeBox();
  setWorkflowStep("compose");
  updatePromptAssistant();
}
```

**New:**
```js
function playCard(cardId) {
  if (state.selectedContextCardIds.has(cardId)) {
    return;
  }
  const fromRect = captureCardRect(cardId, "hand");
  state.selectedContextCardIds.add(cardId);
  renderContextCardChoices();
  renderContextCards();
  hideOptimizeBox();
  setWorkflowStep("compose");
  updatePromptAssistant();
  if (fromRect) {
    const toEl = elements.contextCardChoices.querySelector(
      `.poker-table .poker-card[data-card-id="${cardId}"]`);
    if (toEl) flipAnimate(fromRect, toEl);
  }
}
```

### Step 3：改 recallCard 走 FLIP

- [ ] 替换 `frontend/script.js:1322` 处的 `recallCard` 函数。

**Old:**
```js
function recallCard(cardId) {
  if (!state.selectedContextCardIds.has(cardId)) {
    return;
  }
  state.selectedContextCardIds.delete(cardId);
  renderContextCardChoices();
  renderContextCards();
  hideOptimizeBox();
  setWorkflowStep("compose");
  updatePromptAssistant();
}
```

**New:**
```js
function recallCard(cardId) {
  if (!state.selectedContextCardIds.has(cardId)) {
    return;
  }
  const fromRect = captureCardRect(cardId, "table");
  const card = state.contextCards.find((c) => c.id === cardId);
  state.selectedContextCardIds.delete(cardId);
  renderContextCardChoices();
  renderContextCards();
  hideOptimizeBox();
  setWorkflowStep("compose");
  updatePromptAssistant();
  if (fromRect && card) {
    const pileEl = elements.contextCardChoices.querySelector(
      `.poker-pile[data-poker-pile="${card.type}"]`);
    if (pileEl) flipAnimate(fromRect, pileEl);
  }
}
```

### Step 4：style.css 追加 FLIP 配套样式

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌 polish v2 · FLIP 飞行 ===== */
.poker-card[data-flip-active="true"] {
  z-index: 200;
}
```

### Step 5：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 6：浏览器手测

- [ ] 启动后端，访问仪表盘：

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

- [ ] 在 `http://127.0.0.1:8000/app/` 仪表盘里点开一个堆 → 点扇内某张卡。预期：卡从扇位飞到上方出牌区落位（带轻回弹），不再瞬间消失。
- [ ] 点出牌区某卡的 ✕。预期：卡飞回该堆头位置，不再瞬间消失。
- [ ] DevTools Console 应无报错。

### Step 7：Commit

```powershell
git add frontend/script.js frontend/style.css
git commit -m "feat(poker): FLIP 飞行框架 + 出牌/退牌飞行动画"
```

---

## Task 2：hover 卡片自展开（去扇内浮层）

**Files:**
- Modify: `frontend/script.js`（新增 `renderPokerCardInternals`；改 `renderPokerCard` / `buildPlayedCard` / `renderPokerFan`；state 新增 `hoveredCardId`）
- Modify: `frontend/style.css`（追加 `.poker-card--detail` 等样式）

### Step 1：state 新增 hoveredCardId

- [ ] 替换 `frontend/script.js` 第 1-12 行的 `state` 对象。

**Old:**
```js
const state = {
  templates: [],
  contextCards: [],
  history: [],
  activeView: "dashboard",
  selectedTemplateId: null,
  selectedContextCardIds: new Set(),
  editingTemplateId: null,
  editingContextCardId: null,
  expandedPileType: null,
  pilePageIndex: {},
};
```

**New:**
```js
const state = {
  templates: [],
  contextCards: [],
  history: [],
  activeView: "dashboard",
  selectedTemplateId: null,
  selectedContextCardIds: new Set(),
  editingTemplateId: null,
  editingContextCardId: null,
  expandedPileType: null,
  pilePageIndex: {},
  hoveredCardId: null,
  draggingCardId: null,
  draggingFromZone: null,
};
```

（`draggingCardId` / `draggingFromZone` 是 Task 3 用的，一并加上避免后续再改这段。）

### Step 2：新增 renderPokerCardInternals 工具

- [ ] 在 `frontend/script.js` 中 `renderPokerCard` 函数（第 1227 行）**之前**追加：

```js
function renderPokerCardInternals(wrapper, card, isDetail) {
  wrapper.innerHTML = "";

  const band = document.createElement("div");
  band.className = "poker-card__band";
  wrapper.appendChild(band);

  const badge = document.createElement("span");
  badge.className = "poker-card__badge";
  badge.textContent = pokerBadgeText(card.type);
  wrapper.appendChild(badge);

  const title = document.createElement("div");
  title.className = "poker-card__title";
  title.textContent = card.title;
  wrapper.appendChild(title);

  if (!isDetail) return;

  const tags = Array.isArray(card.tags) ? card.tags.slice(0, 3) : [];
  if (tags.length) {
    const tagBox = document.createElement("div");
    tagBox.className = "poker-card__tags";
    tags.forEach((tag) => {
      const pill = document.createElement("span");
      pill.className = "poker-card__tag";
      pill.textContent = tag;
      tagBox.appendChild(pill);
    });
    wrapper.appendChild(tagBox);
  }

  const body = document.createElement("div");
  body.className = "poker-card__body";
  const text = (card.content || "").trim();
  body.textContent = text.length > 80 ? `${text.slice(0, 80)}…` : text;
  wrapper.appendChild(body);
}
```

### Step 3：改 renderPokerCard 调用新工具 + 去掉扇内浮层依赖

- [ ] 替换 `frontend/script.js:1227` 处的 `renderPokerCard` 函数。

**Old:**
```js
function renderPokerCard(card) {
  const wrapper = document.createElement("div");
  wrapper.className = "poker-card has-hover-tip";
  wrapper.dataset.cardId = String(card.id);
  wrapper.dataset.cardType = card.type;
  wrapper.dataset.tooltip = contextCardHoverText(card);

  const band = document.createElement("div");
  band.className = "poker-card__band";
  wrapper.appendChild(band);

  const badge = document.createElement("span");
  badge.className = "poker-card__badge";
  badge.textContent = pokerBadgeText(card.type);
  wrapper.appendChild(badge);

  const title = document.createElement("div");
  title.className = "poker-card__title";
  title.textContent = card.title;
  wrapper.appendChild(title);

  return wrapper;
}
```

**New:**
```js
function renderPokerCard(card) {
  const wrapper = document.createElement("div");
  wrapper.className = "poker-card";
  wrapper.dataset.cardId = String(card.id);
  wrapper.dataset.cardType = card.type;
  renderPokerCardInternals(wrapper, card, false);
  return wrapper;
}
```

### Step 4：buildPlayedCard 保留 tooltip（出牌区不变）

- [ ] 替换 `frontend/script.js:1278` 处的 `buildPlayedCard` 函数。

**Old:**
```js
function buildPlayedCard(card) {
  const wrapper = renderPokerCard(card);
  wrapper.classList.add("poker-card--played");

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "poker-table__remove";
  remove.dataset.recallId = String(card.id);
  remove.setAttribute("aria-label", `退回 ${contextCardTypeLabel(card.type)}：${card.title}`);
  remove.textContent = "×";
  wrapper.appendChild(remove);

  return wrapper;
}
```

**New:**
```js
function buildPlayedCard(card) {
  const wrapper = renderPokerCard(card);
  wrapper.classList.add("poker-card--played", "has-hover-tip");
  wrapper.dataset.tooltip = contextCardHoverText(card);

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "poker-table__remove";
  remove.dataset.recallId = String(card.id);
  remove.setAttribute("aria-label", `退回 ${contextCardTypeLabel(card.type)}：${card.title}`);
  remove.textContent = "×";
  wrapper.appendChild(remove);

  return wrapper;
}
```

### Step 5：renderPokerFan 给扇内卡 hydrate hover 详情态

- [ ] 在 `frontend/script.js:1154` 处 `cards.forEach((card, index) => {` 内，替换创建卡 + 设置属性的整段。

**Old:**
```js
  cards.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const offsetX = (ratio - 0.5) * 200;
    const offsetY = Math.abs(ratio - 0.5) * 18;

    const cardEl = renderPokerCard(card);
    cardEl.setAttribute("role", "option");
    cardEl.setAttribute("tabindex", "0");
    cardEl.setAttribute("aria-selected",
      state.selectedContextCardIds.has(card.id) ? "true" : "false");
    cardEl.style.setProperty("--fan-transform",
      `translate(${offsetX}px, ${-offsetY}px) rotate(${angle}deg)`);
    cardEl.style.setProperty("--fan-transform-hover",
      `translate(${offsetX}px, ${-offsetY - 14}px) rotate(${angle}deg) scale(1.06)`);
    cardEl.style.animationDelay = `${index * 30}ms`;
    if (state.selectedContextCardIds.has(card.id)) {
      cardEl.classList.add("poker-card--selected");
    }
    fan.appendChild(cardEl);
  });
```

**New:**
```js
  cards.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const offsetX = (ratio - 0.5) * 200;
    const offsetY = Math.abs(ratio - 0.5) * 18;

    const cardEl = renderPokerCard(card);
    cardEl.setAttribute("role", "option");
    cardEl.setAttribute("tabindex", "0");
    cardEl.setAttribute("aria-selected",
      state.selectedContextCardIds.has(card.id) ? "true" : "false");
    cardEl.style.setProperty("--fan-transform",
      `translate(${offsetX}px, ${-offsetY}px) rotate(${angle}deg)`);
    cardEl.style.setProperty("--fan-transform-hover",
      `translate(${offsetX}px, ${-offsetY - 14}px) rotate(${angle}deg) scale(1.06)`);
    cardEl.style.animationDelay = `${index * 30}ms`;
    if (state.selectedContextCardIds.has(card.id)) {
      cardEl.classList.add("poker-card--selected");
    }
    if (state.hoveredCardId === card.id && state.draggingCardId === null) {
      cardEl.classList.add("poker-card--detail");
      renderPokerCardInternals(cardEl, card, true);
    }
    fan.appendChild(cardEl);
  });
```

### Step 6：绑定 hover 事件（mouseenter/leave/focus）

- [ ] 在 `frontend/script.js` 中找 Task 4 写入的 `elements.contextCardChoices.addEventListener("click", ...)` 块（位于 `elements.previewPromptButton.addEventListener("click", previewPrompt);` 前），在它**之后、`elements.previewPromptButton` 之前**插入：

```js
  elements.contextCardChoices.addEventListener("mouseover", (event) => {
    if (state.draggingCardId !== null) return;
    const cardEl = event.target.closest(".poker-pile__fan .poker-card");
    if (!cardEl) return;
    const id = Number(cardEl.dataset.cardId);
    if (state.hoveredCardId === id) return;
    enterCardDetail(id, cardEl);
  });

  elements.contextCardChoices.addEventListener("mouseout", (event) => {
    const cardEl = event.target.closest(".poker-pile__fan .poker-card");
    if (!cardEl) return;
    const related = event.relatedTarget;
    if (related && cardEl.contains(related)) return;
    const id = Number(cardEl.dataset.cardId);
    if (state.hoveredCardId !== id) return;
    leaveCardDetail(id, cardEl);
  });

  elements.contextCardChoices.addEventListener("focusin", (event) => {
    if (state.draggingCardId !== null) return;
    const cardEl = event.target.closest(".poker-pile__fan .poker-card");
    if (!cardEl) return;
    enterCardDetail(Number(cardEl.dataset.cardId), cardEl);
  });

  elements.contextCardChoices.addEventListener("focusout", (event) => {
    const cardEl = event.target.closest(".poker-pile__fan .poker-card");
    if (!cardEl) return;
    leaveCardDetail(Number(cardEl.dataset.cardId), cardEl);
  });

```

### Step 7：新增 enterCardDetail / leaveCardDetail 工具

- [ ] 在 `frontend/script.js` 中 `collapsePile` 函数（第 1302 行附近）**之后**追加：

```js
function enterCardDetail(cardId, cardEl) {
  const card = state.contextCards.find((c) => c.id === cardId);
  if (!card || !cardEl) return;
  state.hoveredCardId = cardId;
  cardEl.classList.add("poker-card--detail");
  renderPokerCardInternals(cardEl, card, true);
}

function leaveCardDetail(cardId, cardEl) {
  const card = state.contextCards.find((c) => c.id === cardId);
  if (!card || !cardEl) return;
  if (state.hoveredCardId === cardId) {
    state.hoveredCardId = null;
  }
  cardEl.classList.remove("poker-card--detail");
  renderPokerCardInternals(cardEl, card, false);
}
```

### Step 8：style.css 追加详情卡样式

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌 polish v2 · hover 详情态 ===== */
.poker-pile__fan .poker-card {
  transition:
    transform 180ms ease-out,
    box-shadow 180ms ease-out,
    z-index 0s 180ms,
    width 220ms ease-out,
    height 220ms ease-out;
}

.poker-pile__fan .poker-card.poker-card--detail {
  width: 134px;
  height: 178px;
  margin-left: -67px;
  transform: var(--fan-transform-hover, translate(0, -14px) rotate(0deg) scale(1.4));
  z-index: 999;
  box-shadow: 4px 5px 0 rgba(44, 33, 24, 0.28);
}

.poker-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.poker-card__tag {
  font-size: 9.5px;
  padding: 1px 6px;
  border: 1.2px solid var(--ink, #2c2118);
  border-radius: 8px;
  background: rgba(255, 250, 240, 0.85);
  color: var(--ink, #2c2118);
  font-weight: 600;
  line-height: 1.3;
}

.poker-card__body {
  font-size: 10.5px;
  line-height: 1.45;
  color: var(--ink, #2c2118);
  margin-top: 4px;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  position: relative;
  -webkit-mask-image: linear-gradient(180deg, #000 70%, transparent 100%);
          mask-image: linear-gradient(180deg, #000 70%, transparent 100%);
}
```

### Step 9：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 10：浏览器手测

- [ ] 在仪表盘里展开任一堆，鼠标 hover 扇内某张卡。预期：该卡放大约 1.4 倍，显示色条 + 标题（2 行）+ 标签云（最多 3 个）+ 内容前 80 字（底部渐变截断），原 hover 浮层不再出现。
- [ ] 鼠标离开 → 卡恢复默认大小和布局。
- [ ] 出牌区的卡 hover 时，仍出现原有的 `.hover-tooltip` 浮层（保留行为）。
- [ ] Tab 键移到扇内某张卡 → 也进入详情态（focusin 路径）。

### Step 11：Commit

```powershell
git add frontend/script.js frontend/style.css
git commit -m "feat(poker): hover 时卡片自展开显示详情，去扇内浮层"
```

---

## Task 3：桌面拖拽出牌（pointer 事件）

**Files:**
- Modify: `frontend/script.js`（新增 `dragController`；绑定 pointerdown）
- Modify: `frontend/style.css`（追加拖拽幻影、克隆样式、出牌区高亮）

### Step 1：style.css 追加拖拽样式

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌 polish v2 · 拖拽 ===== */
.poker-card--ghost {
  opacity: 0.32;
  filter: blur(0.5px);
  pointer-events: none;
}

.poker-drag-clone {
  position: fixed;
  z-index: 2000;
  pointer-events: none;
  margin: 0;
  box-shadow: 6px 8px 0 rgba(44, 33, 24, 0.3);
  transition: none;
  will-change: transform;
}

.poker-drag-clone.is-returning {
  transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
              opacity 300ms cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
}

.poker-table.poker-table--drop-target {
  border-color: #f4c66a;
  background: rgba(244, 198, 106, 0.18);
  border-style: dashed;
}

body.poker-is-dragging,
body.poker-is-dragging * {
  cursor: grabbing !important;
  user-select: none;
}
```

### Step 2：新增 dragController 框架

- [ ] 在 `frontend/script.js` 文件末尾（FLIP 工具之后）追加：

```js
/* ===== 拖拽控制器 ===== */
const DRAG_THRESHOLD_PX = 6;
const DRAG_THRESHOLD_MS = 100;
const DRAG_MIN_MOVE_PX = 2;

const dragController = {
  pointerId: null,
  startX: 0,
  startY: 0,
  startTime: 0,
  cardId: null,
  fromZone: null,
  sourceEl: null,
  cloneEl: null,
  cloneOffsetX: 0,
  cloneOffsetY: 0,
  active: false,
};

function dragReset() {
  if (dragController.cloneEl && dragController.cloneEl.parentNode) {
    dragController.cloneEl.parentNode.removeChild(dragController.cloneEl);
  }
  if (dragController.sourceEl) {
    dragController.sourceEl.classList.remove("poker-card--ghost");
  }
  document.body.classList.remove("poker-is-dragging");
  const table = elements.contextCardChoices?.querySelector(".poker-table");
  if (table) table.classList.remove("poker-table--drop-target");
  dragController.pointerId = null;
  dragController.cardId = null;
  dragController.fromZone = null;
  dragController.sourceEl = null;
  dragController.cloneEl = null;
  dragController.active = false;
  state.draggingCardId = null;
  state.draggingFromZone = null;
}

function dragBegin(event, cardEl, fromZone) {
  const rect = cardEl.getBoundingClientRect();
  dragController.pointerId = event.pointerId;
  dragController.startX = event.clientX;
  dragController.startY = event.clientY;
  dragController.startTime = performance.now();
  dragController.cardId = Number(cardEl.dataset.cardId);
  dragController.fromZone = fromZone;
  dragController.sourceEl = cardEl;
  dragController.cloneOffsetX = event.clientX - rect.left;
  dragController.cloneOffsetY = event.clientY - rect.top;
  dragController.active = false;
}

function dragActivate(event) {
  const cardEl = dragController.sourceEl;
  if (!cardEl) return;
  const rect = cardEl.getBoundingClientRect();
  const clone = cardEl.cloneNode(true);
  clone.classList.add("poker-drag-clone");
  clone.classList.remove("poker-card--detail", "poker-card--ghost");
  clone.style.width = `${rect.width}px`;
  clone.style.height = `${rect.height}px`;
  clone.style.left = "0px";
  clone.style.top = "0px";
  clone.style.transform = `translate(${event.clientX - dragController.cloneOffsetX}px, ${event.clientY - dragController.cloneOffsetY}px) rotate(0deg) scale(1)`;
  document.body.appendChild(clone);
  cardEl.classList.add("poker-card--ghost");
  document.body.classList.add("poker-is-dragging");
  const table = elements.contextCardChoices.querySelector(".poker-table");
  if (table) table.classList.add("poker-table--drop-target");
  dragController.cloneEl = clone;
  dragController.active = true;
  state.draggingCardId = dragController.cardId;
  state.draggingFromZone = dragController.fromZone;
  if (state.hoveredCardId !== null) {
    state.hoveredCardId = null;
    cardEl.classList.remove("poker-card--detail");
    const card = state.contextCards.find((c) => c.id === dragController.cardId);
    if (card) renderPokerCardInternals(cardEl, card, false);
  }
}

function dragMove(event) {
  if (!dragController.cloneEl) return;
  dragController.cloneEl.style.transform =
    `translate(${event.clientX - dragController.cloneOffsetX}px, ${event.clientY - dragController.cloneOffsetY}px) rotate(0deg) scale(1)`;
}

function dragEnd(event) {
  if (!dragController.active) {
    dragReset();
    return;
  }
  const table = elements.contextCardChoices.querySelector(".poker-table");
  const tableRect = table?.getBoundingClientRect();
  const inTable =
    tableRect &&
    event.clientX >= tableRect.left && event.clientX <= tableRect.right &&
    event.clientY >= tableRect.top && event.clientY <= tableRect.bottom;

  if (dragController.fromZone === "hand" && inTable) {
    const cardId = dragController.cardId;
    dragReset();
    playCard(cardId);
    return;
  }

  dragReturnHome();
}

function dragReturnHome() {
  const clone = dragController.cloneEl;
  const source = dragController.sourceEl;
  if (!clone) {
    dragReset();
    return;
  }
  const targetRect = source?.getBoundingClientRect();
  if (targetRect) {
    clone.classList.add("is-returning");
    clone.style.transform = `translate(${targetRect.left}px, ${targetRect.top}px) rotate(0deg) scale(1)`;
  } else {
    clone.classList.add("is-returning");
  }
  setTimeout(() => {
    dragReset();
  }, 320);
}
```

### Step 3：绑定 pointerdown / pointermove / pointerup / pointercancel

- [ ] 在 `frontend/script.js` 中 Task 2 Step 6 写入的 hover 事件块**之后**插入：

```js
  elements.contextCardChoices.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 && event.pointerType === "mouse") return;
    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (!fanCard) return;
    dragBegin(event, fanCard, "hand");
  });

  document.addEventListener("pointermove", (event) => {
    if (dragController.pointerId === null) return;
    if (event.pointerId !== dragController.pointerId) return;
    if (!dragController.active) {
      const dx = event.clientX - dragController.startX;
      const dy = event.clientY - dragController.startY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const elapsed = performance.now() - dragController.startTime;
      const trigger =
        dist >= DRAG_THRESHOLD_PX ||
        (elapsed >= DRAG_THRESHOLD_MS && dist >= DRAG_MIN_MOVE_PX);
      if (!trigger) return;
      dragActivate(event);
    }
    dragMove(event);
  });

  document.addEventListener("pointerup", (event) => {
    if (dragController.pointerId === null) return;
    if (event.pointerId !== dragController.pointerId) return;
    dragEnd(event);
  });

  document.addEventListener("pointercancel", (event) => {
    if (dragController.pointerId === null) return;
    if (event.pointerId !== dragController.pointerId) return;
    dragReturnHome();
  });

  window.addEventListener("blur", () => {
    if (dragController.pointerId !== null) dragReturnHome();
  });

```

### Step 4：避免拖拽触发原点击 playCard

- [ ] 替换 `frontend/script.js` Task 3 写入的 `elements.contextCardChoices.addEventListener("click", ...)` 中处理"扇内卡点击 → playCard"那一段（在第 1286-1320 附近，找以 `const fanCard = event.target.closest(".poker-pile__fan .poker-card")` 开头的分支）。

**Old:**
```js
    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (fanCard) {
      event.stopPropagation();
      playCard(Number(fanCard.dataset.cardId));
      return;
    }
```

**New:**
```js
    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (fanCard) {
      event.stopPropagation();
      if (dragController.active) return;
      playCard(Number(fanCard.dataset.cardId));
      return;
    }
```

### Step 5：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 6：浏览器手测

- [ ] 展开任一堆，按住扇内某张卡缓慢拖动鼠标。预期：移动 6px 以上后克隆卡跟手，原卡变虚化幻影，出牌区出现金色虚线高亮。
- [ ] 拖到出牌区松开。预期：该卡被加入出牌区，幻影消失，伴随 FLIP 飞行落到目标位。
- [ ] 再拖一张到出牌区外松开。预期：克隆卡 300ms 内回弹到原位并消失，原卡恢复正常。
- [ ] 短点击扇内卡（不拖动）。预期：仍触发出牌（向后兼容点击）。
- [ ] 拖拽中按 Esc → 应该没影响（Esc 收堆走另一路径），按 Alt+Tab 切走窗口 → 拖拽自动取消、原卡恢复。

### Step 7：Commit

```powershell
git add frontend/script.js frontend/style.css
git commit -m "feat(poker): 桌面双轨拖拽出牌（保留点击与键盘）"
```

---

## Task 4：出牌区升级成小弧形

**Files:**
- Modify: `frontend/script.js`（重写 `renderPokerTable` 的定位算法）
- Modify: `frontend/style.css`（出牌区改 relative + 子卡 absolute + 高度）

### Step 1：style.css 调整出牌区容器

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌 polish v2 · 出牌区弧形 ===== */
.poker-table {
  position: relative;
  min-height: 140px;
  padding: 18px 14px 14px;
}

.poker-table > .poker-card {
  position: absolute;
  top: 14px;
  left: 50%;
  margin-left: -42px;
  transform-origin: 50% 110%;
}

.poker-table > .poker-table__overflow {
  position: absolute;
  top: 14px;
  right: 14px;
}
```

### Step 2：重写 renderPokerTable 弧形算法

- [ ] 替换 `frontend/script.js:1251` 处的 `renderPokerTable` 函数。

**Old:**
```js
function renderPokerTable(table) {
  table.innerHTML = "";

  const selected = state.contextCards.filter(
    (card) => state.selectedContextCardIds.has(card.id));

  if (!selected.length) {
    return;
  }

  const visibleLimit = 6;
  const visible = selected.slice(0, visibleLimit);
  const overflow = selected.slice(visibleLimit);

  visible.forEach((card) => {
    table.appendChild(buildPlayedCard(card));
  });

  if (overflow.length) {
    const stack = document.createElement("div");
    stack.className = "poker-table__overflow";
    stack.setAttribute("aria-label", `还有 ${overflow.length} 张已挂载卡片`);
    overflow.forEach((card) => stack.appendChild(buildPlayedCard(card)));
    table.appendChild(stack);
  }
}
```

**New:**
```js
function renderPokerTable(table) {
  table.innerHTML = "";

  const selected = state.contextCards.filter(
    (card) => state.selectedContextCardIds.has(card.id));

  if (!selected.length) {
    return;
  }

  const visibleLimit = 6;
  const visible = selected.slice(0, visibleLimit);
  const overflow = selected.slice(visibleLimit);

  const total = visible.length;
  const arc = 60;
  const halfArc = arc / 2;
  const radius = 180;

  visible.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const rad = (angle * Math.PI) / 180;
    const offsetX = Math.sin(rad) * radius;
    const offsetY = (1 - Math.cos(rad)) * radius * 0.18;
    const cardEl = buildPlayedCard(card);
    cardEl.style.transform =
      `translate(${offsetX}px, ${offsetY}px) rotate(${angle * 0.6}deg)`;
    table.appendChild(cardEl);
  });

  if (overflow.length) {
    const stack = document.createElement("div");
    stack.className = "poker-table__overflow";
    stack.setAttribute("aria-label", `还有 ${overflow.length} 张已挂载卡片`);
    overflow.forEach((card) => stack.appendChild(buildPlayedCard(card)));
    table.appendChild(stack);
  }
}
```

### Step 3：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 4：浏览器手测

- [ ] 出 1 张卡。预期：卡居中显示在出牌区。
- [ ] 出 3 张卡（不同类型）。预期：3 张以弧形对称排开（中间高、两侧略低、稍微旋转）。
- [ ] 出 6 张卡。预期：6 张铺成完整弧形，无重叠。
- [ ] 出 7 张以上。预期：前 6 张走弧形，剩余进入右上角 overflow 堆叠（hover 时展开）。
- [ ] 出牌 FLIP 飞行仍然顺畅（每次卡都落到弧上的目标位）。

### Step 5：Commit

```powershell
git add frontend/script.js frontend/style.css
git commit -m "feat(poker): 出牌区升级成小弧形布局"
```

---

## Task 5：触屏长按拖拽 + 拖回退牌

**Files:**
- Modify: `frontend/script.js`（dragController 支持触屏、出牌区卡也可拖、堆头作落点）
- Modify: `frontend/style.css`（追加 `.poker-pile--drop-target` 与 `touch-action`）

### Step 1：style.css 追加触屏与堆头高亮

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌 polish v2 · 触屏 + 拖回退牌 ===== */
.poker-pile__fan .poker-card,
.poker-table .poker-card {
  touch-action: none;
}

.poker-pile.poker-pile--drop-target::before,
.poker-pile.poker-pile--drop-target::after {
  box-shadow: 0 0 0 3px #f4c66a, 2px 2px 0 rgba(44, 33, 24, 0.18);
}
```

### Step 2：dragBegin 区分触屏长按 vs 鼠标即时

- [ ] 替换 `frontend/script.js` 中 `dragController` 框架附近的 `DRAG_THRESHOLD_MS` 常量定义（Step 2 of Task 3 写入），改为按指针类型区分阈值。

**Old:**
```js
const DRAG_THRESHOLD_PX = 6;
const DRAG_THRESHOLD_MS = 100;
const DRAG_MIN_MOVE_PX = 2;
```

**New:**
```js
const DRAG_THRESHOLD_PX = 6;
const DRAG_THRESHOLD_MS_MOUSE = 100;
const DRAG_THRESHOLD_MS_TOUCH = 200;
const DRAG_MIN_MOVE_PX = 2;
```

### Step 3：pointermove handler 用触屏阈值

- [ ] 替换 Task 3 Step 3 写入的 `document.addEventListener("pointermove", ...)` 整段。

**Old:**
```js
  document.addEventListener("pointermove", (event) => {
    if (dragController.pointerId === null) return;
    if (event.pointerId !== dragController.pointerId) return;
    if (!dragController.active) {
      const dx = event.clientX - dragController.startX;
      const dy = event.clientY - dragController.startY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const elapsed = performance.now() - dragController.startTime;
      const trigger =
        dist >= DRAG_THRESHOLD_PX ||
        (elapsed >= DRAG_THRESHOLD_MS && dist >= DRAG_MIN_MOVE_PX);
      if (!trigger) return;
      dragActivate(event);
    }
    dragMove(event);
  });
```

**New:**
```js
  document.addEventListener("pointermove", (event) => {
    if (dragController.pointerId === null) return;
    if (event.pointerId !== dragController.pointerId) return;
    if (!dragController.active) {
      const dx = event.clientX - dragController.startX;
      const dy = event.clientY - dragController.startY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const elapsed = performance.now() - dragController.startTime;
      const isTouch = event.pointerType === "touch";
      const minMs = isTouch ? DRAG_THRESHOLD_MS_TOUCH : DRAG_THRESHOLD_MS_MOUSE;
      const trigger =
        (!isTouch && dist >= DRAG_THRESHOLD_PX) ||
        (elapsed >= minMs && dist >= DRAG_MIN_MOVE_PX);
      if (!trigger) return;
      dragActivate(event);
    }
    dragMove(event);
  });
```

### Step 4：pointerdown 也覆盖出牌区卡（fromZone="table"）

- [ ] 替换 Task 3 Step 3 写入的 `elements.contextCardChoices.addEventListener("pointerdown", ...)` 整段。

**Old:**
```js
  elements.contextCardChoices.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 && event.pointerType === "mouse") return;
    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (!fanCard) return;
    dragBegin(event, fanCard, "hand");
  });
```

**New:**
```js
  elements.contextCardChoices.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 && event.pointerType === "mouse") return;
    if (event.target.closest(".poker-table__remove")) return;
    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (fanCard) {
      dragBegin(event, fanCard, "hand");
      return;
    }
    const tableCard = event.target.closest(".poker-table .poker-card");
    if (tableCard) {
      dragBegin(event, tableCard, "table");
    }
  });
```

### Step 5：dragActivate 在拖出牌区卡时高亮所有堆头

- [ ] 替换 Task 3 Step 2 写入的 `dragActivate` 函数末尾几行（从 `document.body.appendChild(clone);` 开始的整段）。

**Old:**
```js
  document.body.appendChild(clone);
  cardEl.classList.add("poker-card--ghost");
  document.body.classList.add("poker-is-dragging");
  const table = elements.contextCardChoices.querySelector(".poker-table");
  if (table) table.classList.add("poker-table--drop-target");
  dragController.cloneEl = clone;
  dragController.active = true;
  state.draggingCardId = dragController.cardId;
  state.draggingFromZone = dragController.fromZone;
  if (state.hoveredCardId !== null) {
    state.hoveredCardId = null;
    cardEl.classList.remove("poker-card--detail");
    const card = state.contextCards.find((c) => c.id === dragController.cardId);
    if (card) renderPokerCardInternals(cardEl, card, false);
  }
}
```

**New:**
```js
  document.body.appendChild(clone);
  cardEl.classList.add("poker-card--ghost");
  document.body.classList.add("poker-is-dragging");
  if (dragController.fromZone === "hand") {
    const table = elements.contextCardChoices.querySelector(".poker-table");
    if (table) table.classList.add("poker-table--drop-target");
  } else {
    elements.contextCardChoices
      .querySelectorAll(".poker-pile")
      .forEach((p) => p.classList.add("poker-pile--drop-target"));
  }
  dragController.cloneEl = clone;
  dragController.active = true;
  state.draggingCardId = dragController.cardId;
  state.draggingFromZone = dragController.fromZone;
  if (state.hoveredCardId !== null) {
    state.hoveredCardId = null;
    cardEl.classList.remove("poker-card--detail");
    const card = state.contextCards.find((c) => c.id === dragController.cardId);
    if (card) renderPokerCardInternals(cardEl, card, false);
  }
}
```

### Step 6：dragReset 同步清理堆头高亮

- [ ] 替换 Task 3 Step 2 写入的 `dragReset` 函数。

**Old:**
```js
function dragReset() {
  if (dragController.cloneEl && dragController.cloneEl.parentNode) {
    dragController.cloneEl.parentNode.removeChild(dragController.cloneEl);
  }
  if (dragController.sourceEl) {
    dragController.sourceEl.classList.remove("poker-card--ghost");
  }
  document.body.classList.remove("poker-is-dragging");
  const table = elements.contextCardChoices?.querySelector(".poker-table");
  if (table) table.classList.remove("poker-table--drop-target");
  dragController.pointerId = null;
  dragController.cardId = null;
  dragController.fromZone = null;
  dragController.sourceEl = null;
  dragController.cloneEl = null;
  dragController.active = false;
  state.draggingCardId = null;
  state.draggingFromZone = null;
}
```

**New:**
```js
function dragReset() {
  if (dragController.cloneEl && dragController.cloneEl.parentNode) {
    dragController.cloneEl.parentNode.removeChild(dragController.cloneEl);
  }
  if (dragController.sourceEl) {
    dragController.sourceEl.classList.remove("poker-card--ghost");
  }
  document.body.classList.remove("poker-is-dragging");
  const root = elements.contextCardChoices;
  const table = root?.querySelector(".poker-table");
  if (table) table.classList.remove("poker-table--drop-target");
  root?.querySelectorAll(".poker-pile--drop-target")
    .forEach((p) => p.classList.remove("poker-pile--drop-target"));
  dragController.pointerId = null;
  dragController.cardId = null;
  dragController.fromZone = null;
  dragController.sourceEl = null;
  dragController.cloneEl = null;
  dragController.active = false;
  state.draggingCardId = null;
  state.draggingFromZone = null;
}
```

### Step 7：dragEnd 增加 fromZone="table" 拖回退牌分支

- [ ] 替换 Task 3 Step 2 写入的 `dragEnd` 函数。

**Old:**
```js
function dragEnd(event) {
  if (!dragController.active) {
    dragReset();
    return;
  }
  const table = elements.contextCardChoices.querySelector(".poker-table");
  const tableRect = table?.getBoundingClientRect();
  const inTable =
    tableRect &&
    event.clientX >= tableRect.left && event.clientX <= tableRect.right &&
    event.clientY >= tableRect.top && event.clientY <= tableRect.bottom;

  if (dragController.fromZone === "hand" && inTable) {
    const cardId = dragController.cardId;
    dragReset();
    playCard(cardId);
    return;
  }

  dragReturnHome();
}
```

**New:**
```js
function dragEnd(event) {
  if (!dragController.active) {
    dragReset();
    return;
  }
  const root = elements.contextCardChoices;
  const table = root.querySelector(".poker-table");
  const tableRect = table?.getBoundingClientRect();
  const inTable =
    tableRect &&
    event.clientX >= tableRect.left && event.clientX <= tableRect.right &&
    event.clientY >= tableRect.top && event.clientY <= tableRect.bottom;

  if (dragController.fromZone === "hand" && inTable) {
    const cardId = dragController.cardId;
    dragReset();
    playCard(cardId);
    return;
  }

  if (dragController.fromZone === "table") {
    const piles = root.querySelectorAll(".poker-pile");
    for (const pile of piles) {
      const r = pile.getBoundingClientRect();
      if (event.clientX >= r.left && event.clientX <= r.right &&
          event.clientY >= r.top && event.clientY <= r.bottom) {
        const cardId = dragController.cardId;
        dragReset();
        recallCard(cardId);
        return;
      }
    }
  }

  dragReturnHome();
}
```

### Step 8：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 9：浏览器手测

- [ ] 桌面手测（鼠标）：从出牌区某卡按住拖到任一堆头释放。预期：堆头在拖拽中加金色边，松开时该卡退回扇内，伴随 FLIP 飞回。
- [ ] 桌面手测：从出牌区拖到非堆头非出牌区松开。预期：克隆回弹消失。
- [ ] 触屏手测（DevTools → Toggle device toolbar 切到 iPhone 12 或真机）：扇内卡短点 → 出牌（不应触发拖拽）；扇内卡长按 200ms+ → 进入拖拽态，拖到出牌区松开 → 出牌。
- [ ] 触屏长按拖拽时页面不应跟随手指滚动。

### Step 10：Commit

```powershell
git add frontend/script.js frontend/style.css
git commit -m "feat(poker): 触屏长按拖拽 + 出牌区拖回退牌"
```

---

## Task 6：扇形角度规整 + 收堆反向飞 + reduced-motion 兜底

**Files:**
- Modify: `frontend/script.js`（renderPokerFan 角度算法；collapsePile 异步动画）
- Modify: `frontend/style.css`（5 堆 transition 曲线；reduced-motion 增量）

### Step 1：renderPokerFan 角度算法重写

- [ ] 替换 `frontend/script.js:1150` 起的 `const total = cards.length; const arc = 40; const halfArc = arc / 2;` 一直到 `cards.forEach((card, index) => {` 这一行**之前**。

**Old:**
```js
  const total = cards.length;
  const arc = 40;
  const halfArc = arc / 2;
```

**New:**
```js
  const total = cards.length;
  const step = Math.min(12, total <= 1 ? 0 : 84 / (total - 1));
  const startAngle = -((total - 1) / 2) * step;
```

- [ ] 然后在同函数内（`cards.forEach((card, index) => {` 内部）替换 angle / offset 计算的前三行。

**Old:**
```js
  cards.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const offsetX = (ratio - 0.5) * 200;
    const offsetY = Math.abs(ratio - 0.5) * 18;
```

**New:**
```js
  cards.forEach((card, index) => {
    const angle = startAngle + index * step;
    const rad = (angle * Math.PI) / 180;
    const offsetX = Math.sin(rad) * 150;
    const offsetY = (1 - Math.cos(rad)) * 150;
```

### Step 2：collapsePile 改异步反向飞 + expandPile 尊重锁

- [ ] 替换 `frontend/script.js:1302` 处的 `collapsePile`。

**Old:**
```js
function collapsePile() {
  if (state.expandedPileType === null) {
    return;
  }
  state.expandedPileType = null;
  renderContextCardChoices();
}
```

**New:**
```js
let pokerCollapsing = false;

function collapsePile() {
  if (state.expandedPileType === null) {
    return;
  }
  if (pokerCollapsing) {
    return;
  }
  const root = elements.contextCardChoices;
  const fan = root?.querySelector(".poker-pile--expanded .poker-pile__fan");
  const pile = root?.querySelector(".poker-pile--expanded");
  if (!fan || !pile) {
    state.expandedPileType = null;
    renderContextCardChoices();
    return;
  }

  const fanCards = [...fan.querySelectorAll(".poker-card")];
  const pileRect = pile.getBoundingClientRect();
  const stagger = 20;
  pokerCollapsing = true;

  fanCards.forEach((cardEl, index) => {
    const rect = cardEl.getBoundingClientRect();
    const dx = pileRect.left + pileRect.width / 2 - (rect.left + rect.width / 2);
    const dy = pileRect.top + pileRect.height / 2 - (rect.top + rect.height / 2);
    cardEl.animate(
      { transform: `translate(${dx}px, ${dy}px) scale(0.6) rotate(0deg)`, opacity: 0 },
      {
        duration: 260,
        delay: index * stagger,
        easing: "cubic-bezier(0.4, 0, 0.2, 1)",
        fill: "forwards",
      },
    );
  });

  const totalMs = 260 + Math.max(0, fanCards.length - 1) * stagger;
  setTimeout(() => {
    pokerCollapsing = false;
    state.expandedPileType = null;
    renderContextCardChoices();
  }, totalMs);
}
```

> `pokerCollapsing` 锁防止收堆动画期间再次点击堆头触发新展开/收堆。

- [ ] 同步替换 `frontend/script.js:1293` 处的 `expandPile`，让它也尊重锁。

**Old:**
```js
function expandPile(type) {
  if (state.expandedPileType === type) {
    collapsePile();
    return;
  }
  state.expandedPileType = type;
  renderContextCardChoices();
}
```

**New:**
```js
function expandPile(type) {
  if (pokerCollapsing) return;
  if (state.expandedPileType === type) {
    collapsePile();
    return;
  }
  state.expandedPileType = type;
  renderContextCardChoices();
}
```

### Step 3：style.css 调整 5 堆变窄/变灰曲线

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌 polish v2 · 收堆 + 5 堆联动曲线 ===== */
.poker-pile {
  transition:
    transform 220ms cubic-bezier(0.4, 0, 0.2, 1),
    width 260ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 220ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

（覆盖 v1 中 `.poker-pile` 较早的 ease-out 过渡——CSS 后定义优先级生效。）

### Step 4：style.css reduced-motion 增量兜底

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌 polish v2 · reduced-motion 兜底 ===== */
@media (prefers-reduced-motion: reduce) {
  .poker-card[data-flip-active="true"] {
    transition: opacity 100ms linear !important;
    animation: none !important;
  }

  .poker-pile__fan .poker-card.poker-card--detail {
    transition: none !important;
    transform: none !important;
  }

  .poker-drag-clone {
    transition: none !important;
  }

  .poker-drag-clone.is-returning {
    transition: opacity 100ms linear !important;
  }

  .poker-pile {
    transition: opacity 100ms linear !important;
  }
}
```

### Step 5：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 6：后端体检（确认无回归）

- [ ] 运行：

```powershell
D:\VScode\Python\PromptStudio\.venv\Scripts\python.exe -m unittest discover -s tests
D:\VScode\Python\PromptStudio\.venv\Scripts\python.exe -m compileall app seed_test_data.py
```

预期：unittest 全绿；compileall 无错误。

### Step 7：浏览器手测（端到端 acceptance）

- [ ] **扇形规整**：展开一个有 5 张卡的堆。预期：5 张卡严格对称（中间 0°，两侧 ±12°、±24°），无偏移。
- [ ] **多卡兜底**：用 DevTools Console 注入 12 张 background 卡触发分页：
  ```js
  const fakeCards = Array.from({ length: 12 }, (_, i) => ({
    id: 9000 + i, type: "background", title: `测试 ${i + 1}`,
    tags: ["test"], content: "测试内容",
  }));
  state.contextCards = [...fakeCards, ...state.contextCards.filter(c => c.type !== "background")];
  renderContextCardChoices();
  ```
  展开"背景"堆。预期：单页 10 张卡仍铺满 ≤84° 弧，规则、对称。
- [ ] **收堆反向飞**：展开一堆，按 Esc。预期：扇内每张卡逐张飞向堆头中心（stagger 20ms），全部消失后堆头恢复。
- [ ] **reduced-motion**：DevTools → Rendering → Emulate CSS media feature `prefers-reduced-motion: reduce`。重新测试以下动作，应全部变成简单 fade，无 transform 动画：
  - 出牌 / 退牌 FLIP 飞行 → 淡入淡出
  - hover 扇内卡 → 文字直切，不放大
  - 拖拽克隆 → 跟手时不带 transition；松开回弹只是淡出
  - 收堆 → 扇内卡淡出，不向中心飞
- [ ] **后端拼接**：刷新页面（恢复正常数据），打 3 张不同类型的卡 → 点"更新预生成"。预期：生成的 Prompt 按 `background → rule → format → example → checklist` 顺序拼接卡片内容。

### Step 8：Commit

```powershell
git add frontend/script.js frontend/style.css
git commit -m "feat(poker): 扇形角度规整 + 收堆反向飞 + reduced-motion 兜底"
```

---

## 收尾

完成 6 个 Task 后：

1. 全部 v1 行为保留（5 堆分类、点击展开、键盘导航、单堆分页、ARIA、reduced-motion）
2. 新增能力：出牌/退牌 FLIP 飞行、hover 卡自展开、桌面+触屏拖拽双轨、出牌区弧形、扇形角度规整、收堆反向飞
3. 后端、DB、`/api/*`、`tests/` 全程未动

如需推送或开 PR，提交本地 8 个累计 commit（v1 6 个 + v2 2 个未必，按实际 Task 数计），与用户确认后再执行。
