# 知识卡片扑克牌出牌 · 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把仪表盘 `#contextCardChoices` 的勾选列表改造成手牌扇形 + 出牌区的扑克牌交互。

**Architecture:** 纯前端改造（HTML/CSS/JS）。`state.selectedContextCardIds` 仍是唯一真源，所有动作通过修改这个 Set 触发 re-render，与现有 `previewPrompt()` 等流程自动兼容。新增 `state.expandedPileType` 和 `state.pilePageIndex` 控制 UI 状态。后端、数据库、`/api/generate` 调用零改动。

**Tech Stack:** 原生 HTML / CSS / Vanilla JS（无构建步骤）；验证靠 `node --check` 检语法 + 浏览器手测 + 后端 `unittest` 套件保后端无回归。

**前置 spec：** `docs/superpowers/specs/2026-05-23-context-card-poker-design.md`

---

## 文件结构

| 文件 | 责任 | 改动类型 |
|------|------|---------|
| `frontend/index.html` | `#contextCardChoices` 容器内部结构替换 | 修改 1 处 |
| `frontend/style.css` | 新增 `.poker-*` 类与动画 | 追加 ~250 行；不删除旧 `.choice-list` 样式（无害保留） |
| `frontend/script.js` | 新增状态字段、渲染函数、事件处理；删除旧 checkbox 事件 | 多处修改 |

后端、数据库、`docs/`、`tests/` 等其余文件均不动。

---

## 任务清单（共 6 个 Task）

- Task 1：骨架替换 + 5 堆静态呈现（无展开交互）
- Task 2：点击展开 / 收起 + 扇形布局
- Task 3：出牌 / 退牌 + 出牌区
- Task 4：单堆翻页（>10 张）
- Task 5：键盘导航 + ARIA
- Task 6：`prefers-reduced-motion` + 验证三件套

---

## Task 1：骨架替换 + 5 堆静态呈现

**Files:**
- Modify: `frontend/index.html:188`
- Modify: `frontend/style.css`（追加新类，不删原有）
- Modify: `frontend/script.js`（状态、常量、渲染函数、删除旧 change 事件）

### Step 1：先把当前页面截图（基线）

- [ ] 启动后端，浏览器打开 `http://127.0.0.1:8000/app/`，进入"仪表盘"，观察"上下文卡片"区当前是勾选列表的形态。心里记住改造前的样子。

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

预期：当前页面"上下文卡片"区是若干带勾选框的 `.choice-card` 行。

### Step 2：替换 HTML 容器内部

- [ ] 在 `frontend/index.html` 中把第 188 行的容器替换成扑克区骨架。

**Old:**
```html
                <div id="contextCardChoices" class="choice-list"></div>
```

**New:**
```html
                <div id="contextCardChoices" class="poker-zone">
                  <div class="poker-table" data-poker-table aria-label="已挂载卡片"></div>
                  <div class="poker-hand" data-poker-hand role="group" aria-label="知识卡片牌堆"></div>
                </div>
```

### Step 3：CSS 追加扑克区基础样式

- [ ] 在 `frontend/style.css` 末尾追加以下基础样式：

```css
/* ===== 扑克牌交互 · 基础骨架 ===== */
.poker-zone {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.poker-table {
  min-height: 110px;
  padding: 14px;
  border: 2px dashed var(--line-soft);
  border-radius: 12px;
  background: rgba(255, 250, 240, 0.6);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  position: relative;
}

.poker-table:empty::before {
  content: "点击下方卡堆把卡片打过来";
  color: var(--ink-soft);
  font-size: 13px;
  font-weight: 600;
  width: 100%;
  text-align: center;
}

.poker-hand {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 28px;
  padding: 16px 8px 24px;
  min-height: 160px;
  position: relative;
}

.poker-pile {
  position: relative;
  width: 96px;
  height: 128px;
  cursor: pointer;
  background: transparent;
  border: 0;
  padding: 0;
  outline: none;
  font: inherit;
  transition: transform 180ms ease-out, width 220ms ease-out, opacity 180ms ease-out;
}

.poker-pile::before,
.poker-pile::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 8px;
  background: #fffaf0;
  border: 2px solid var(--line);
  box-shadow: 2px 2px 0 rgba(44, 33, 24, 0.18);
  z-index: 0;
}

.poker-pile::before {
  transform: rotate(-2.4deg) translate(-4px, 2px);
}

.poker-pile::after {
  transform: rotate(2.8deg) translate(4px, -1px);
}

.poker-pile:hover,
.poker-pile:focus-visible {
  transform: translateY(-6px);
}

.poker-pile:focus-visible {
  outline: 2px solid var(--accent, #f4c66a);
  outline-offset: 4px;
}

.poker-pile__count {
  position: absolute;
  top: -10px;
  right: -12px;
  min-width: 24px;
  height: 24px;
  padding: 0 7px;
  font-size: 11px;
  font-weight: 800;
  background: var(--ink, #2c2118);
  color: #fff8ea;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  border: 2px solid #fff8ea;
}

.poker-card {
  position: relative;
  width: 96px;
  height: 128px;
  border-radius: 8px;
  border: 2px solid var(--line, #2c2118);
  background: #fff;
  box-shadow: 2px 2px 0 rgba(44, 33, 24, 0.22);
  display: flex;
  flex-direction: column;
  padding: 10px 8px 8px;
  gap: 6px;
  text-align: center;
  z-index: 1;
}

.poker-card__band {
  height: 6px;
  border-radius: 3px;
  background: var(--card-color, #ddd);
  margin-top: 2px;
}

.poker-card__badge {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 10px;
  padding: 1px 6px;
  background: var(--card-color, #ddd);
  color: var(--ink, #2c2118);
  border-radius: 8px;
  font-weight: 700;
  border: 1.5px solid var(--ink, #2c2118);
}

.poker-card__title {
  margin: auto 0;
  font-size: 12.5px;
  font-weight: 800;
  line-height: 1.32;
  color: var(--ink, #2c2118);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 类型配色 */
.poker-card[data-card-type="background"] { --card-color: #f4c66a; }
.poker-card[data-card-type="rule"]       { --card-color: #d96850; }
.poker-card[data-card-type="format"]     { --card-color: #6b8aa8; }
.poker-card[data-card-type="example"]    { --card-color: #7ab85c; }
.poker-card[data-card-type="checklist"]  { --card-color: #8e6bb5; }

.poker-pile[data-poker-pile="background"] .poker-card { background: #fff8e6; }
.poker-pile[data-poker-pile="rule"]       .poker-card { background: #fdeae5; }
.poker-pile[data-poker-pile="format"]     .poker-card { background: #e9eff5; }
.poker-pile[data-poker-pile="example"]    .poker-card { background: #ecf5e6; }
.poker-pile[data-poker-pile="checklist"]  .poker-card { background: #efe9f5; }

/* 堆状态：部分挂载 → 细金边；全部挂载 → 粗金边 + ✓ */
.poker-pile--has-selected::before,
.poker-pile--has-selected::after {
  box-shadow: 0 0 0 2px #f4c66a, 2px 2px 0 rgba(44, 33, 24, 0.18);
}

.poker-pile--all-selected::before,
.poker-pile--all-selected::after {
  box-shadow: 0 0 0 3px #f4c66a, 2px 2px 0 rgba(44, 33, 24, 0.18);
}

.poker-pile--all-selected .poker-pile__count::after {
  content: " ✓";
}
```

### Step 4：JS 状态新增

- [ ] 在 `frontend/script.js` 第 1-10 行的 `state` 对象字面量末尾追加两个字段。

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
};
```

### Step 5：JS 新增常量

- [ ] 在 `frontend/script.js` 中 `contextCardTypeLabels` 常量（第 435 行附近）之后追加扑克牌排序与配色常量：

**Old:**
```js
const contextCardTypeLabels = {
  background: "背景资料",
  rule: "写作规则",
  format: "输出格式",
  example: "参考示例",
  checklist: "检查清单",
};

function contextCardTypeLabel(type) {
  return contextCardTypeLabels[type] || contextCardTypeLabels.background;
}
```

**New:**
```js
const contextCardTypeLabels = {
  background: "背景资料",
  rule: "写作规则",
  format: "输出格式",
  example: "参考示例",
  checklist: "检查清单",
};

const POKER_PILE_ORDER = ["background", "rule", "format", "example", "checklist"];

const pokerTypeBadgeText = {
  background: "背景",
  rule: "规则",
  format: "格式",
  example: "示例",
  checklist: "检查",
};

function contextCardTypeLabel(type) {
  return contextCardTypeLabels[type] || contextCardTypeLabels.background;
}

function pokerBadgeText(type) {
  return pokerTypeBadgeText[type] || pokerTypeBadgeText.background;
}
```

### Step 6：JS 重写 `renderContextCardChoices`

- [ ] 替换 `frontend/script.js` 第 1036-1058 行的 `renderContextCardChoices` 函数为新版（并新增辅助函数）。

**Old:**
```js
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
```

**New:**
```js
function renderContextCardChoices() {
  const zone = elements.contextCardChoices;
  zone.classList.add("poker-zone");
  zone.innerHTML = "";

  const table = document.createElement("div");
  table.className = "poker-table";
  table.dataset.pokerTable = "";
  table.setAttribute("aria-label", "已挂载卡片");
  zone.appendChild(table);

  const hand = document.createElement("div");
  hand.className = "poker-hand";
  hand.dataset.pokerHand = "";
  hand.setAttribute("role", "group");
  hand.setAttribute("aria-label", "知识卡片牌堆");
  zone.appendChild(hand);

  if (!state.contextCards.length) {
    hand.innerHTML = '<div class="empty-state">暂无可选上下文卡片。</div>';
    updateSelectedContextCardCount();
    updateWorkSurface();
    return;
  }

  const grouped = groupContextCardsByType(state.contextCards);
  POKER_PILE_ORDER.forEach((type) => {
    const cards = grouped[type];
    if (!cards.length) {
      return;
    }
    hand.appendChild(renderPokerPile(type, cards));
  });

  renderPokerTable(table);
  updateSelectedContextCardCount();
  updateWorkSurface();
}

function groupContextCardsByType(cards) {
  const buckets = {};
  POKER_PILE_ORDER.forEach((type) => { buckets[type] = []; });
  cards.forEach((card) => {
    const bucket = buckets[card.type] ? card.type : "background";
    buckets[bucket].push(card);
  });
  return buckets;
}

function renderPokerPile(type, cards) {
  const pile = document.createElement("button");
  pile.type = "button";
  pile.className = "poker-pile";
  pile.dataset.pokerPile = type;

  const selectedCount = cards.filter((card) => state.selectedContextCardIds.has(card.id)).length;
  const label = `${contextCardTypeLabel(type)} ${cards.length} 张，${selectedCount} 张已挂载`;
  pile.setAttribute("aria-label", label);
  pile.setAttribute("aria-expanded", "false");

  pile.appendChild(renderPokerCard(cards[0]));

  const count = document.createElement("span");
  count.className = "poker-pile__count";
  count.textContent = selectedCount > 0 ? `${selectedCount}/${cards.length}` : `${cards.length}`;
  pile.appendChild(count);

  return pile;
}

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

function renderPokerTable(table) {
  // Task 3 实现，此处先留空
  table.innerHTML = "";
}
```

### Step 7：JS 删除旧 checkbox 事件监听

- [ ] `frontend/script.js` 第 1704-1722 行的 change 监听已经不再有 checkbox 触发它，删除整段。

**Old:**
```js
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
```

**New:**
```js
  elements.previewPromptButton.addEventListener("click", previewPrompt);
```

### Step 8：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出（成功）。如果报错，根据行号修正语法。

### Step 9：浏览器手测

- [ ] 启动后端，访问仪表盘，确认：
  - "上下文卡片"区下方出现 5 个排排站的卡堆（背景 / 规则 / 格式 / 示例 / 检查），颜色分明
  - 每堆右上角有圆形数字徽章，显示卡片总数（如 `6`）
  - 鼠标 hover 卡堆时整个堆轻轻上浮
  - 上方"出牌区"为虚线框，提示"点击下方卡堆把卡片打过来"
  - 浏览器 DevTools Console 没有报错

### Step 10：Commit

```powershell
git add frontend/index.html frontend/style.css frontend/script.js
git commit -m "feat(poker): 上下文卡片渲染为 5 堆静态扑克牌"
```

---

## Task 2：点击展开 / 收起 + 扇形布局

**Files:**
- Modify: `frontend/style.css`（追加扇形样式）
- Modify: `frontend/script.js`（renderPokerPile 支持展开态、新增 expandPile/collapsePile、绑定堆头点击）

### Step 1：CSS 追加扇形与状态样式

- [ ] 在 `frontend/style.css` 末尾继续追加：

```css
/* ===== 扑克牌交互 · 展开扇形 ===== */
.poker-pile--dimmed {
  width: 56px;
  opacity: 0.45;
  pointer-events: none;
}

.poker-pile--expanded {
  width: 360px;
  height: 160px;
  cursor: default;
  transform: none;
}

.poker-pile--expanded:hover,
.poker-pile--expanded:focus-visible {
  transform: none;
}

.poker-pile--expanded::before,
.poker-pile--expanded::after {
  display: none;
}

.poker-pile--expanded > .poker-pile__count {
  top: -10px;
  right: 8px;
}

.poker-pile__fan {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  pointer-events: none;
}

.poker-pile__fan .poker-card {
  position: absolute;
  bottom: 8px;
  left: 50%;
  margin-left: -48px;
  transform-origin: 50% 110%;
  pointer-events: auto;
  cursor: pointer;
  transition: transform 180ms ease-out, box-shadow 180ms ease-out, z-index 0s 180ms;
  opacity: 0;
  animation: poker-fan-in 280ms ease-out forwards;
}

.poker-pile__fan .poker-card:hover,
.poker-pile__fan .poker-card:focus-visible {
  transform: var(--fan-transform-hover, translate(0, -12px) rotate(0deg));
  z-index: 10;
  box-shadow: 4px 5px 0 rgba(44, 33, 24, 0.28);
  outline: none;
}

@keyframes poker-fan-in {
  from {
    opacity: 0;
    transform: translate(0, 30px) rotate(0deg) scale(0.92);
  }
  to {
    opacity: 1;
    transform: var(--fan-transform, translate(0, 0) rotate(0deg));
  }
}

.poker-card--selected {
  box-shadow: 0 0 0 3px #f4c66a, 4px 5px 0 rgba(44, 33, 24, 0.28);
}
```

### Step 2：JS 改写 `renderPokerPile` 以支持展开态

- [ ] 在 `frontend/script.js` 中替换 Task 1 写入的 `renderPokerPile` 为支持展开渲染的版本：

**Old:**
```js
function renderPokerPile(type, cards) {
  const pile = document.createElement("button");
  pile.type = "button";
  pile.className = "poker-pile";
  pile.dataset.pokerPile = type;

  const selectedCount = cards.filter((card) => state.selectedContextCardIds.has(card.id)).length;
  if (selectedCount > 0 && selectedCount < cards.length) {
    pile.classList.add("poker-pile--has-selected");
  } else if (selectedCount > 0 && selectedCount === cards.length) {
    pile.classList.add("poker-pile--all-selected");
  }

  const label = `${contextCardTypeLabel(type)} ${cards.length} 张，${selectedCount} 张已挂载`;
  pile.setAttribute("aria-label", label);
  pile.setAttribute("aria-expanded", "false");

  pile.appendChild(renderPokerCard(cards[0]));

  const count = document.createElement("span");
  count.className = "poker-pile__count";
  count.textContent = selectedCount > 0 ? `${selectedCount}/${cards.length}` : `${cards.length}`;
  pile.appendChild(count);

  return pile;
}
```

**New:**
```js
function renderPokerPile(type, cards) {
  const isExpanded = state.expandedPileType === type;
  const isDimmed = state.expandedPileType !== null && !isExpanded;

  const pile = document.createElement("button");
  pile.type = "button";
  pile.className = "poker-pile";
  if (isExpanded) pile.classList.add("poker-pile--expanded");
  if (isDimmed) pile.classList.add("poker-pile--dimmed");
  pile.dataset.pokerPile = type;

  const selectedCount = cards.filter((card) => state.selectedContextCardIds.has(card.id)).length;
  if (selectedCount > 0 && selectedCount < cards.length) {
    pile.classList.add("poker-pile--has-selected");
  } else if (selectedCount > 0 && selectedCount === cards.length) {
    pile.classList.add("poker-pile--all-selected");
  }

  pile.setAttribute("aria-label",
    `${contextCardTypeLabel(type)} ${cards.length} 张，${selectedCount} 张已挂载`);
  pile.setAttribute("aria-expanded", isExpanded ? "true" : "false");

  if (!isExpanded) {
    pile.appendChild(renderPokerCard(cards[0]));
  } else {
    pile.appendChild(renderPokerFan(type, cards));
  }

  const count = document.createElement("span");
  count.className = "poker-pile__count";
  count.textContent = selectedCount > 0 ? `${selectedCount}/${cards.length}` : `${cards.length}`;
  pile.appendChild(count);

  return pile;
}

function renderPokerFan(type, cards) {
  const fan = document.createElement("div");
  fan.className = "poker-pile__fan";

  const total = cards.length;
  const arc = 40;
  const halfArc = arc / 2;

  cards.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const offsetX = (ratio - 0.5) * 200;
    const offsetY = Math.abs(ratio - 0.5) * 18;

    const cardEl = renderPokerCard(card);
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

  return fan;
}
```

### Step 3：JS 新增展开 / 收起 action

- [ ] 在 `frontend/script.js` 中 `renderPokerTable` 函数之后追加：

```js
function expandPile(type) {
  if (state.expandedPileType === type) {
    collapsePile();
    return;
  }
  state.expandedPileType = type;
  renderContextCardChoices();
}

function collapsePile() {
  if (state.expandedPileType === null) {
    return;
  }
  state.expandedPileType = null;
  renderContextCardChoices();
}
```

### Step 4：JS 绑定堆头点击 + 全局点击收堆 + Esc 收堆

- [ ] 在 `frontend/script.js` 第 1724 行 `elements.previewPromptButton.addEventListener` 之前插入扑克交互的事件绑定：

```js
  elements.contextCardChoices.addEventListener("click", (event) => {
    if (event.target.closest(".poker-pile__fan")) {
      return;
    }
    const pile = event.target.closest(".poker-pile");
    if (!pile) {
      return;
    }
    expandPile(pile.dataset.pokerPile);
  });

  document.addEventListener("click", (event) => {
    if (state.expandedPileType === null) return;
    if (event.target.closest(".poker-pile")) return;
    if (event.target.closest(".poker-table")) return;
    collapsePile();
  });

```

- [ ] 在 `frontend/script.js` 第 1904 行的全局 keydown 处理里追加 Esc 收堆。

**Old:**
```js
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document.body.classList.remove("sidebar-open");
      closeCustomSelects();
      hideHoverTooltip();
    }
  });
```

**New:**
```js
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document.body.classList.remove("sidebar-open");
      closeCustomSelects();
      hideHoverTooltip();
      collapsePile();
    }
  });
```

### Step 5：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 6：浏览器手测

- [ ] 刷新仪表盘，确认：
  - 点击任意一个堆 → 该堆扇形展开（卡片沿弧形排开，每张依次入场）
  - 其余 4 堆同时变窄、变灰
  - 鼠标 hover 扇内某张卡时该卡上浮
  - 再点同一堆头、点扇形外空白、或按 Esc → 扇形收回，其他堆恢复
  - 同时只能有一个堆展开（点 A 展开，再点 B 时 A 自动收起）

### Step 7：Commit

```powershell
git add frontend/style.css frontend/script.js
git commit -m "feat(poker): 点击牌堆扇形展开 + Esc/空白收堆"
```

---

## Task 3：出牌 / 退牌 + 出牌区

**Files:**
- Modify: `frontend/style.css`（出牌区卡片样式 + ✕ 按钮）
- Modify: `frontend/script.js`（renderPokerTable、playCard、recallCard、事件路由）

### Step 1：CSS 追加出牌区卡片与 ✕ 按钮样式

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌交互 · 出牌区 ===== */
.poker-table .poker-card {
  width: 84px;
  height: 112px;
  padding: 8px 6px 6px;
  flex-shrink: 0;
  position: relative;
  animation: poker-played-in 280ms cubic-bezier(0.34, 1.2, 0.5, 1);
}

.poker-table .poker-card .poker-card__title {
  font-size: 11.5px;
}

.poker-table__remove {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--ink, #2c2118);
  background: #fff;
  color: var(--ink, #2c2118);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  z-index: 4;
  transition: transform 120ms ease-out, background 120ms ease-out;
}

.poker-table__remove:hover,
.poker-table__remove:focus-visible {
  background: #d96850;
  color: #fff;
  transform: scale(1.12);
  outline: none;
}

.poker-table__overflow {
  position: relative;
  display: flex;
  align-items: center;
}

.poker-table__overflow > .poker-card {
  margin-left: -56px;
  transition: margin-left 180ms ease-out;
}

.poker-table__overflow:hover > .poker-card,
.poker-table__overflow:focus-within > .poker-card {
  margin-left: -12px;
}

@keyframes poker-played-in {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.85);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
```

### Step 2：JS 替换 `renderPokerTable` 实现

- [ ] 替换 Task 1 留空的 `renderPokerTable` 函数。

**Old:**
```js
function renderPokerTable(table) {
  // Task 3 实现，此处先留空
  table.innerHTML = "";
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

### Step 3：JS 新增 `playCard` / `recallCard`

- [ ] 在 `frontend/script.js` 中 `collapsePile` 函数之后追加：

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

### Step 4：JS 路由扇内卡片点击 + 出牌区 ✕ 点击

- [ ] 替换 Task 2 Step 4 添加的 `elements.contextCardChoices.addEventListener("click", ...)` 块，把对扇内卡片点击和 ✕ 点击的处理一并加入。

**Old:**
```js
  elements.contextCardChoices.addEventListener("click", (event) => {
    if (event.target.closest(".poker-pile__fan")) {
      return;
    }
    const pile = event.target.closest(".poker-pile");
    if (!pile) {
      return;
    }
    expandPile(pile.dataset.pokerPile);
  });
```

**New:**
```js
  elements.contextCardChoices.addEventListener("click", (event) => {
    const removeButton = event.target.closest(".poker-table__remove");
    if (removeButton) {
      event.stopPropagation();
      recallCard(Number(removeButton.dataset.recallId));
      return;
    }

    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (fanCard) {
      event.stopPropagation();
      playCard(Number(fanCard.dataset.cardId));
      return;
    }

    if (event.target.closest(".poker-pile__fan")) {
      return;
    }

    const pile = event.target.closest(".poker-pile");
    if (pile) {
      expandPile(pile.dataset.pokerPile);
    }
  });
```

### Step 5：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 6：浏览器手测

- [ ] 刷新仪表盘，覆盖以下流程：
  - 展开"背景"堆 → 点击扇内某张卡 → 该卡出现在上方出牌区（带 280ms 飞入动画），扇形收起，堆头徽章变成 `1/6`
  - 再次展开同一堆 → 看到该卡有金色描边（`.poker-card--selected`）
  - 点击出牌区卡片右上角 ✕ → 卡片消失，堆头徽章恢复为 `6`
  - 连续打出 7 张卡片 → 第 7 张起进入 `.poker-table__overflow` 区域，hover overflow 区时层叠卡片散开
  - 点击 "更新预生成" 按钮 → 生成的 Prompt 文本里能看到被打出卡片的内容（验证后端接收正常）

### Step 7：Commit

```powershell
git add frontend/style.css frontend/script.js
git commit -m "feat(poker): 点击扇内卡片出牌，✕ 按钮退牌"
```

---

## Task 4：单堆翻页（>10 张）

**Files:**
- Modify: `frontend/style.css`（追加翻页指示器样式）
- Modify: `frontend/script.js`（renderPokerFan 分页、pagePile、renderPokerPager）

### Step 1：CSS 追加翻页指示器样式

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌交互 · 翻页 ===== */
.poker-pile__pager {
  position: absolute;
  bottom: -22px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: auto;
}

.poker-pile__pager-button {
  width: 22px;
  height: 22px;
  border: 2px solid var(--line, #2c2118);
  background: #fffaf0;
  border-radius: 50%;
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: var(--ink, #2c2118);
}

.poker-pile__pager-button:hover:not(:disabled),
.poker-pile__pager-button:focus-visible {
  background: var(--accent, #f4c66a);
  outline: none;
}

.poker-pile__pager-button:disabled {
  opacity: 0.35;
  cursor: default;
}

.poker-pile__pager-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(44, 33, 24, 0.25);
}

.poker-pile__pager-dot.is-active {
  background: var(--ink, #2c2118);
}
```

### Step 2：JS 改写 `renderPokerFan` 支持分页 + 新增辅助函数

- [ ] 替换 Task 2 写入的 `renderPokerFan` 函数。

**Old:**
```js
function renderPokerFan(type, cards) {
  const fan = document.createElement("div");
  fan.className = "poker-pile__fan";

  const total = cards.length;
  const arc = 40;
  const halfArc = arc / 2;

  cards.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const offsetX = (ratio - 0.5) * 200;
    const offsetY = Math.abs(ratio - 0.5) * 18;

    const cardEl = renderPokerCard(card);
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

  return fan;
}
```

**New:**
```js
const POKER_PAGE_SIZE = 10;

function renderPokerFan(type, allCards) {
  const fan = document.createElement("div");
  fan.className = "poker-pile__fan";

  const totalPages = Math.max(1, Math.ceil(allCards.length / POKER_PAGE_SIZE));
  const pageIndex = Math.min(state.pilePageIndex[type] || 0, totalPages - 1);
  state.pilePageIndex[type] = pageIndex;

  const start = pageIndex * POKER_PAGE_SIZE;
  const cards = allCards.slice(start, start + POKER_PAGE_SIZE);

  const total = cards.length;
  const arc = 40;
  const halfArc = arc / 2;

  cards.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const offsetX = (ratio - 0.5) * 200;
    const offsetY = Math.abs(ratio - 0.5) * 18;

    const cardEl = renderPokerCard(card);
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

  if (totalPages > 1) {
    fan.appendChild(renderPokerPager(type, pageIndex, totalPages));
  }

  return fan;
}

function renderPokerPager(type, pageIndex, totalPages) {
  const pager = document.createElement("div");
  pager.className = "poker-pile__pager";
  pager.dataset.pokerPager = type;

  const prev = document.createElement("button");
  prev.type = "button";
  prev.className = "poker-pile__pager-button";
  prev.textContent = "‹";
  prev.dataset.pokerPagerDir = "-1";
  prev.disabled = pageIndex === 0;
  prev.setAttribute("aria-label", "上一页");
  pager.appendChild(prev);

  for (let i = 0; i < totalPages; i++) {
    const dot = document.createElement("span");
    dot.className = "poker-pile__pager-dot";
    if (i === pageIndex) dot.classList.add("is-active");
    pager.appendChild(dot);
  }

  const next = document.createElement("button");
  next.type = "button";
  next.className = "poker-pile__pager-button";
  next.textContent = "›";
  next.dataset.pokerPagerDir = "1";
  next.disabled = pageIndex === totalPages - 1;
  next.setAttribute("aria-label", "下一页");
  pager.appendChild(next);

  return pager;
}

function pagePile(type, delta) {
  const grouped = groupContextCardsByType(state.contextCards);
  const cards = grouped[type] || [];
  const totalPages = Math.max(1, Math.ceil(cards.length / POKER_PAGE_SIZE));
  const current = state.pilePageIndex[type] || 0;
  const next = Math.max(0, Math.min(totalPages - 1, current + delta));
  if (next === current) return;
  state.pilePageIndex[type] = next;
  renderContextCardChoices();
}
```

### Step 3：JS 在点击路由中添加翻页按钮处理

- [ ] 替换 Task 3 写入的 `elements.contextCardChoices.addEventListener("click", ...)` 块。

**Old:**
```js
  elements.contextCardChoices.addEventListener("click", (event) => {
    const removeButton = event.target.closest(".poker-table__remove");
    if (removeButton) {
      event.stopPropagation();
      recallCard(Number(removeButton.dataset.recallId));
      return;
    }

    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (fanCard) {
      event.stopPropagation();
      playCard(Number(fanCard.dataset.cardId));
      return;
    }

    if (event.target.closest(".poker-pile__fan")) {
      return;
    }

    const pile = event.target.closest(".poker-pile");
    if (pile) {
      expandPile(pile.dataset.pokerPile);
    }
  });
```

**New:**
```js
  elements.contextCardChoices.addEventListener("click", (event) => {
    const removeButton = event.target.closest(".poker-table__remove");
    if (removeButton) {
      event.stopPropagation();
      recallCard(Number(removeButton.dataset.recallId));
      return;
    }

    const pagerButton = event.target.closest(".poker-pile__pager-button");
    if (pagerButton) {
      event.stopPropagation();
      const pager = pagerButton.closest("[data-poker-pager]");
      const dir = Number(pagerButton.dataset.pokerPagerDir);
      if (pager && dir) {
        pagePile(pager.dataset.pokerPager, dir);
      }
      return;
    }

    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (fanCard) {
      event.stopPropagation();
      playCard(Number(fanCard.dataset.cardId));
      return;
    }

    if (event.target.closest(".poker-pile__fan")) {
      return;
    }

    const pile = event.target.closest(".poker-pile");
    if (pile) {
      expandPile(pile.dataset.pokerPile);
    }
  });
```

### Step 4：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 5：手测翻页（手动注入 >10 张卡片）

- [ ] 在浏览器 DevTools Console 临时塞入 12 张 background 类型卡片，触发翻页 UI：

```js
const fakeCards = Array.from({ length: 12 }, (_, i) => ({
  id: 9000 + i,
  type: "background",
  title: `测试卡片 ${i + 1}`,
  tags: ["test"],
  content: "翻页测试用",
}));
state.contextCards = [...fakeCards, ...state.contextCards.filter(c => c.type !== "background")];
renderContextCardChoices();
```

- [ ] 然后点击 "背景" 堆展开，确认：
  - 扇形下方出现 `‹ ● ○ ›` 翻页指示器
  - 第一页 ‹ 禁用（灰）
  - 点 › 切到第二页，活动点变化、‹ 启用、› 禁用
  - 点 ‹ 回到第一页

- [ ] 验证完后刷新页面恢复正常数据。

### Step 6：Commit

```powershell
git add frontend/style.css frontend/script.js
git commit -m "feat(poker): 单堆超 10 张时启用翻页"
```

---

## Task 5：键盘导航 + ARIA

**Files:**
- Modify: `frontend/script.js`（键盘事件分发、role/aria 属性）
- Modify: `frontend/style.css`（扇内卡片 focus-visible 样式）

### Step 1：JS 扇内卡片加 role / tabindex

- [ ] 替换 Task 2 写入的 `renderPokerFan` 中 `cards.forEach` 块（在创建 cardEl 之后增加 role、tabindex、aria-selected）。

**Old:**
```js
  cards.forEach((card, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = -halfArc + ratio * arc;
    const offsetX = (ratio - 0.5) * 200;
    const offsetY = Math.abs(ratio - 0.5) * 18;

    const cardEl = renderPokerCard(card);
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
    fan.appendChild(cardEl);
  });
```

### Step 2：JS 在容器 keydown 上加键盘导航

- [ ] 在 `frontend/script.js` 中 Task 4 写入的 `elements.contextCardChoices.addEventListener("click", ...)` 块**之后**追加 keydown 处理：

```js
  elements.contextCardChoices.addEventListener("keydown", (event) => {
    const pile = event.target.closest(".poker-pile");
    if (!pile) return;
    const type = pile.dataset.pokerPile;

    if (event.target.matches(".poker-pile") && !pile.classList.contains("poker-pile--expanded")) {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        const piles = [...elements.contextCardChoices.querySelectorAll(".poker-pile")];
        const idx = piles.indexOf(pile);
        const nextIdx = (idx + (event.key === "ArrowRight" ? 1 : -1) + piles.length) % piles.length;
        piles[nextIdx].focus();
      }
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        expandPile(type);
        requestAnimationFrame(() => {
          const firstCard = elements.contextCardChoices.querySelector(
            `.poker-pile[data-poker-pile="${type}"] .poker-pile__fan .poker-card`);
          firstCard?.focus();
        });
      }
      return;
    }

    const fanCard = event.target.closest(".poker-pile__fan .poker-card");
    if (fanCard) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        playCard(Number(fanCard.dataset.cardId));
      }
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        const cards = [...pile.querySelectorAll(".poker-pile__fan .poker-card")];
        const idx = cards.indexOf(fanCard);
        const nextIdx = (idx + (event.key === "ArrowRight" ? 1 : -1) + cards.length) % cards.length;
        cards[nextIdx].focus();
      }
    }
  });

```

### Step 3：CSS 追加扇内卡片 focus-visible 样式

- [ ] 在 `frontend/style.css` 末尾追加：

```css
.poker-pile__fan .poker-card:focus-visible {
  outline: 3px solid var(--accent, #f4c66a);
  outline-offset: 2px;
}
```

### Step 4：语法检查

- [ ] 运行：

```powershell
node --check frontend\script.js
```

预期：无输出。

### Step 5：纯键盘手测

- [ ] 在浏览器仪表盘里，从 "更新预生成" 按钮后用 Tab 走到第一个堆，确认：
  - Tab 走进第一个堆 → 焦点环可见
  - ← / → 在 5 堆之间切换焦点
  - Enter / Space → 展开当前堆，焦点自动跳到扇内第一张卡
  - ← / → 在扇内卡片间循环切换
  - Enter / Space → 出牌（卡飞到上方），自动收堆
  - Esc → 收堆
  - 出牌区的 ✕ 按钮也可用 Tab 走到并 Enter 触发

### Step 6：Commit

```powershell
git add frontend/style.css frontend/script.js
git commit -m "feat(poker): 键盘导航支持（方向键 + Enter/Esc）"
```

---

## Task 6：`prefers-reduced-motion` + 验证三件套

**Files:**
- Modify: `frontend/style.css`（追加媒体查询降级）

### Step 1：CSS 追加 reduced-motion 降级

- [ ] 在 `frontend/style.css` 末尾追加：

```css
/* ===== 扑克牌交互 · 动效降级 ===== */
@media (prefers-reduced-motion: reduce) {
  .poker-pile,
  .poker-pile::before,
  .poker-pile::after,
  .poker-card,
  .poker-table__overflow > .poker-card,
  .poker-table__remove {
    transition: opacity 100ms linear !important;
    animation: none !important;
  }

  .poker-pile__fan .poker-card {
    animation: poker-fan-fade 100ms linear forwards !important;
  }

  .poker-pile:hover,
  .poker-pile:focus-visible {
    transform: none;
  }

  .poker-pile__fan .poker-card:hover,
  .poker-pile__fan .poker-card:focus-visible {
    transform: var(--fan-transform, none);
  }
}

@keyframes poker-fan-fade {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### Step 2：手测降级

- [ ] 在浏览器 DevTools 里启用 reduced motion 模拟：
  - Chrome / Edge：DevTools → 三点菜单 → More tools → Rendering → 找到 "Emulate CSS media feature prefers-reduced-motion" → 选 "reduce"

- [ ] 然后在仪表盘点击堆头展开 / 收起 / 出牌 / 退牌，确认所有动作只有简单 fade，无横向飞行 / 弹性回弹 / 上浮。

### Step 3：运行后端 unittest 套件

- [ ] 跑后端测试确保未受影响（即便本次没改后端，做一次完整体检）：

```powershell
D:\VScode\Python\PromptStudio\.venv\Scripts\python.exe -m unittest discover -s tests
```

预期：所有用例通过（OK）。

### Step 4：编译检查

- [ ] 跑 compileall 与 node --check：

```powershell
D:\VScode\Python\PromptStudio\.venv\Scripts\python.exe -m compileall app seed_test_data.py
node --check frontend\script.js
```

预期：无错误。

### Step 5：端到端流程验证

- [ ] 启动应用，覆盖一次完整流程：
  1. 选择模板
  2. 在 5 堆中分别出 2-3 张卡（不同类型）
  3. 点 "更新预生成" → 生成的 Prompt 应包含所有已挂载卡片的内容，且按 `background → rule → format → example → checklist` 顺序拼接
  4. 在出牌区 ✕ 退一张卡 → 再次更新预生成 → 该卡内容应已消失
  5. 浏览器 DevTools Console 无红色报错

### Step 6：Commit

```powershell
git add frontend/style.css
git commit -m "feat(poker): 适配 prefers-reduced-motion"
```

---

## 收尾

完成 6 个 Task 后，本次改造结束。后端、数据库、`/api/generate` 调用路径完全未动。

如需后续扩展，可在新分支独立开展：
- 拖拽出牌（替代或补充点击出牌）
- 卡片背面像素图案精细化
- 搜索 / 标签筛选
- 移动端响应式适配

用户验收后即可合并主分支。
