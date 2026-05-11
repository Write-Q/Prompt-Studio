const state = {
  templates: [],
  snippets: [],
  history: [],
  activeView: "dashboard",
  selectedTemplateId: null,
};

const mockTemplates = [
  {
    id: 1001,
    title: "学习笔记整理",
    category: "学习",
    tags: ["学习", "总结"],
    content: "请用{语气}的方式，将以下内容整理成{长度}学习笔记：\n{输入内容}",
    description: "适合课堂笔记和阅读笔记整理。",
    updated_at: "本地示例",
  },
  {
    id: 1002,
    title: "工作周报生成",
    category: "办公",
    tags: ["周报", "汇报"],
    content: "请根据以下工作内容，生成一份{周期}工作周报：\n{输入内容}",
    description: "适合办公汇报。",
    updated_at: "本地示例",
  },
];

const mockSnippets = [
  {
    id: 2001,
    title: "结构化输出原则",
    tags: ["结构化", "输出"],
    content: "回答时优先使用标题、要点和行动建议，让结果便于阅读和复用。",
    source: "本地示例",
  },
];

const elements = {
  pageTitle: document.querySelector("#pageTitle"),
  navItems: document.querySelectorAll(".nav-item"),
  viewSections: document.querySelectorAll(".view-section"),
  globalSearch: document.querySelector("#globalSearch"),
  refreshButton: document.querySelector("#refreshButton"),
  toast: document.querySelector("#toast"),

  snippetCount: document.querySelector("#snippetCount"),
  templateCount: document.querySelector("#templateCount"),
  historyCount: document.querySelector("#historyCount"),
  latestUpdate: document.querySelector("#latestUpdate"),

  quickTemplateSelect: document.querySelector("#quickTemplateSelect"),
  quickKeyword: document.querySelector("#quickKeyword"),
  variableFields: document.querySelector("#variableFields"),
  variableCount: document.querySelector("#variableCount"),
  snippetChoices: document.querySelector("#snippetChoices"),
  selectedSnippetCount: document.querySelector("#selectedSnippetCount"),
  generatePromptButton: document.querySelector("#generatePromptButton"),
  finalPrompt: document.querySelector("#finalPrompt"),
  promptHint: document.querySelector("#promptHint"),
  copyPromptButton: document.querySelector("#copyPromptButton"),
  aiPromptInput: document.querySelector("#aiPromptInput"),

  recentHistoryList: document.querySelector("#recentHistoryList"),
  historyList: document.querySelector("#historyList"),
  reloadHistoryButton: document.querySelector("#reloadHistoryButton"),

  snippetForm: document.querySelector("#snippetForm"),
  snippetList: document.querySelector("#snippetList"),
  templateForm: document.querySelector("#templateForm"),
  templateList: document.querySelector("#templateList"),

  askLlmButton: document.querySelector("#askLlmButton"),
  llmModel: document.querySelector("#llmModel"),
  llmTemperature: document.querySelector("#llmTemperature"),
  llmHint: document.querySelector("#llmHint"),
  llmAnswer: document.querySelector("#llmAnswer"),
  copyAnswerButton: document.querySelector("#copyAnswerButton"),
};

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.style.background = isError
    ? "rgba(194, 59, 46, 0.94)"
    : "rgba(11, 22, 36, 0.92)";
  elements.toast.classList.add("show");

  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2400);
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
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function extractVariables(content) {
  const variables = [];
  const matches = content.matchAll(/\{([^{}\s]+)\}/g);

  for (const match of matches) {
    if (!variables.includes(match[1])) {
      variables.push(match[1]);
    }
  }

  return variables;
}

function getSelectedTemplate() {
  return state.templates.find((item) => item.id === state.selectedTemplateId) ?? null;
}

function renderTags(tags = []) {
  if (!tags.length) {
    return "<span class=\"tag\">无标签</span>";
  }

  return tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
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
    const errorText = await response.text();
    throw new Error(errorText || `请求失败：${response.status}`);
  }

  return response.json();
}

function switchView(viewName) {
  state.activeView = viewName;
  const titleMap = {
    dashboard: "仪表盘",
    snippets: "知识片段",
    templates: "提示词模板",
    history: "生成记录",
    ai: "AI 生成",
  };

  elements.pageTitle.textContent = titleMap[viewName] || "仪表盘";
  elements.navItems.forEach((item) => {
    item.classList.toggle("active", item.dataset.view === viewName);
  });
  elements.viewSections.forEach((section) => {
    section.classList.toggle("active", section.id === `${viewName}View`);
  });
}

function getKeyword() {
  return elements.globalSearch.value.trim().toLowerCase();
}

function matchesKeyword(item) {
  const keyword = getKeyword();
  if (!keyword) {
    return true;
  }

  return [
    item.title,
    item.category,
    item.source,
    item.description,
    item.content,
    item.final_prompt,
    (item.tags || []).join(" "),
  ]
    .join(" ")
    .toLowerCase()
    .includes(keyword);
}

function renderStats() {
  elements.snippetCount.textContent = state.snippets.length;
  elements.templateCount.textContent = state.templates.length;
  elements.historyCount.textContent = state.history.length;
  elements.latestUpdate.textContent = state.history[0]?.created_at?.slice(5, 16) || "--";
}

function renderTemplateSelect() {
  if (!state.templates.length) {
    elements.quickTemplateSelect.innerHTML = "<option value=\"\">暂无模板</option>";
    renderVariables();
    return;
  }

  if (!state.templates.some((item) => item.id === state.selectedTemplateId)) {
    state.selectedTemplateId = state.templates[0].id;
  }

  elements.quickTemplateSelect.innerHTML = state.templates
    .map((item) => `<option value="${item.id}">${escapeHtml(item.title)}</option>`)
    .join("");
  elements.quickTemplateSelect.value = String(state.selectedTemplateId);
  renderVariables();
}

function renderVariables() {
  const template = getSelectedTemplate();
  if (!template) {
    elements.variableFields.innerHTML = "<div class=\"empty-state\">暂无模板变量</div>";
    elements.variableCount.textContent = "0 个变量";
    return;
  }

  const variables = extractVariables(template.content);
  elements.variableCount.textContent = `${variables.length} 个变量`;

  if (!variables.length) {
    elements.variableFields.innerHTML = "<div class=\"empty-state\">当前模板没有变量，生成时会直接使用模板内容。</div>";
    return;
  }

  elements.variableFields.innerHTML = variables
    .map((name) => `
      <label>
        ${escapeHtml(name)}
        <input data-variable-name="${escapeHtml(name)}" type="text" placeholder="填写 ${escapeHtml(name)}">
      </label>
    `)
    .join("");
}

function renderSnippetChoices() {
  const snippets = state.snippets.filter(matchesKeyword);

  if (!snippets.length) {
    elements.snippetChoices.innerHTML = "<div class=\"empty-state\">暂无可选知识片段</div>";
    elements.selectedSnippetCount.textContent = "已选 0 个";
    return;
  }

  elements.snippetChoices.innerHTML = snippets
    .map((item) => `
      <label class="choice-card">
        <input type="checkbox" value="${item.id}" data-snippet-choice>
        <span>
          <strong>${escapeHtml(item.title)}</strong><br>
          <small>${escapeHtml((item.tags || []).join(" / ") || "无标签")}</small>
        </span>
      </label>
    `)
    .join("");
  updateSelectedSnippetCount();
}

function renderTemplates() {
  const templates = state.templates.filter(matchesKeyword);

  if (!templates.length) {
    elements.templateList.innerHTML = "<div class=\"empty-state\">暂无模板</div>";
    return;
  }

  elements.templateList.innerHTML = templates
    .map((item) => `
      <article class="resource-card ${item.id === state.selectedTemplateId ? "active" : ""}" data-template-id="${item.id}">
        <div class="resource-row">
          <div>
            <div class="resource-title">${escapeHtml(item.title)}</div>
            <div class="resource-meta">${escapeHtml(item.category || "未分类")}</div>
          </div>
          <button class="delete-button" type="button" data-delete-template-id="${item.id}">删除</button>
        </div>
        <p class="resource-meta">${escapeHtml(item.description || item.content.slice(0, 90))}</p>
        <div class="tag-row">${renderTags(item.tags)}</div>
      </article>
    `)
    .join("");
}

function renderSnippets() {
  const snippets = state.snippets.filter(matchesKeyword);

  if (!snippets.length) {
    elements.snippetList.innerHTML = "<div class=\"empty-state\">暂无知识片段</div>";
    return;
  }

  elements.snippetList.innerHTML = snippets
    .map((item) => `
      <article class="resource-card">
        <div class="resource-row">
          <div>
            <div class="resource-title">${escapeHtml(item.title)}</div>
            <div class="resource-meta">${escapeHtml(item.source || "无来源")}</div>
          </div>
          <button class="delete-button" type="button" data-delete-snippet-id="${item.id}">删除</button>
        </div>
        <p class="resource-meta">${escapeHtml(item.content.slice(0, 130))}</p>
        <div class="tag-row">${renderTags(item.tags)}</div>
      </article>
    `)
    .join("");
}

function historyCard(item) {
  const preview = item.final_prompt.length > 150
    ? `${item.final_prompt.slice(0, 150)}...`
    : item.final_prompt;

  return `
    <article class="record-card" data-history-id="${item.id}">
      <div class="record-row">
        <div>
          <div class="record-title">生成记录 #${item.id}</div>
          <div class="record-meta">${escapeHtml(item.created_at)} · 模板 ${item.template_id}</div>
        </div>
        <button class="delete-button" type="button" data-delete-history-id="${item.id}">删除</button>
      </div>
      <p class="record-meta">${escapeHtml(preview)}</p>
    </article>
  `;
}

function renderHistory() {
  const history = state.history.filter(matchesKeyword);
  const recent = history.slice(0, 5);

  elements.recentHistoryList.innerHTML = recent.length
    ? recent.map(historyCard).join("")
    : "<div class=\"empty-state\">暂无最近生成记录</div>";

  elements.historyList.innerHTML = history.length
    ? history.map(historyCard).join("")
    : "<div class=\"empty-state\">暂无生成记录</div>";
}

function renderAll() {
  renderStats();
  renderTemplateSelect();
  renderSnippetChoices();
  renderTemplates();
  renderSnippets();
  renderHistory();
}

async function loadData() {
  try {
    const [templates, snippets, history] = await Promise.all([
      requestJson("/api/templates"),
      requestJson("/api/snippets"),
      requestJson("/api/history?limit=50"),
    ]);

    state.templates = templates;
    state.snippets = snippets;
    state.history = history;
    showToast("已连接 FastAPI 后端");
  } catch {
    state.templates = mockTemplates;
    state.snippets = mockSnippets;
    state.history = [];
    showToast("后端未连接，已加载本地展示数据", true);
  }

  renderAll();
}

function collectVariables() {
  const variables = {};
  const inputs = elements.variableFields.querySelectorAll("[data-variable-name]");

  inputs.forEach((input) => {
    const name = input.dataset.variableName;
    const isMainInput = name.includes("输入") || name.includes("内容") || name.includes("关键词");
    variables[name] = input.value.trim() || (isMainInput ? elements.quickKeyword.value.trim() : "");
  });

  return variables;
}

function collectSnippetIds() {
  return Array.from(elements.snippetChoices.querySelectorAll("[data-snippet-choice]:checked"))
    .map((item) => Number(item.value));
}

function updateSelectedSnippetCount() {
  elements.selectedSnippetCount.textContent = `已选 ${collectSnippetIds().length} 个`;
}

function buildLocalPrompt(template, variables, snippetIds) {
  let prompt = template.content;
  Object.entries(variables).forEach(([name, value]) => {
    prompt = prompt.replaceAll(`{${name}}`, value || elements.quickKeyword.value.trim() || `{${name}}`);
  });

  const selectedSnippets = state.snippets.filter((item) => snippetIds.includes(item.id));
  if (!selectedSnippets.length) {
    return prompt;
  }

  return `${prompt}\n\n参考知识片段：\n${selectedSnippets.map((item) => item.content).join("\n\n")}`;
}

async function generatePrompt() {
  const template = getSelectedTemplate();
  if (!template) {
    showToast("请先选择模板", true);
    return;
  }

  const payload = {
    template_id: template.id,
    variables: collectVariables(),
    snippet_ids: collectSnippetIds(),
    mode: "rule",
  };

  try {
    elements.generatePromptButton.disabled = true;
    const result = await requestJson("/api/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    elements.finalPrompt.value = result.final_prompt;
    elements.aiPromptInput.value = result.final_prompt;
    elements.promptHint.textContent = result.missing_variables.length
      ? `未填写变量：${result.missing_variables.join("、")}`
      : `生成成功，历史 ID：${result.history_id}`;
    await loadData();
    showToast("Prompt 已生成");
  } catch {
    const localPrompt = buildLocalPrompt(template, payload.variables, payload.snippet_ids);
    elements.finalPrompt.value = localPrompt;
    elements.aiPromptInput.value = localPrompt;
    elements.promptHint.textContent = "当前使用本地模拟生成结果。";
    showToast("后端生成失败，已显示模拟结果", true);
  } finally {
    elements.generatePromptButton.disabled = false;
  }
}

async function copyText(text, message) {
  if (!text.trim()) {
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

async function createTemplate(event) {
  event.preventDefault();
  const payload = {
    title: document.querySelector("#templateTitle").value,
    category: document.querySelector("#templateCategory").value || null,
    tags: parseTags(document.querySelector("#templateTags").value),
    description: document.querySelector("#templateDescription").value || null,
    content: document.querySelector("#templateContent").value,
  };

  try {
    const created = await requestJson("/api/templates", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.selectedTemplateId = created.id;
    elements.templateForm.reset();
    await loadData();
    showToast("模板已保存");
  } catch (error) {
    showToast(error.message, true);
  }
}

async function createSnippet(event) {
  event.preventDefault();
  const payload = {
    title: document.querySelector("#snippetTitle").value,
    tags: parseTags(document.querySelector("#snippetTags").value),
    source: document.querySelector("#snippetSource").value || null,
    content: document.querySelector("#snippetContent").value,
  };

  try {
    await requestJson("/api/snippets", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    elements.snippetForm.reset();
    await loadData();
    showToast("知识片段已保存");
  } catch (error) {
    showToast(error.message, true);
  }
}

async function deleteItem(url, successMessage) {
  try {
    await requestJson(url, { method: "DELETE" });
    await loadData();
    showToast(successMessage);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function loadHistoryToPrompt(historyId) {
  try {
    const history = await requestJson(`/api/history/${historyId}`);
    elements.finalPrompt.value = history.final_prompt;
    elements.aiPromptInput.value = history.final_prompt;
    elements.promptHint.textContent = `已载入历史 ID：${history.id}`;
    switchView("dashboard");
    showToast("历史记录已载入");
  } catch (error) {
    showToast(error.message, true);
  }
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
    elements.llmHint.textContent = `模型：${payload.model}，正在流式输出...`;

    const response = await fetch("/api/llm/answer/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      elements.llmAnswer.value += decoder.decode(value, { stream: true });
      elements.llmAnswer.scrollTop = elements.llmAnswer.scrollHeight;
    }

    elements.llmAnswer.value += decoder.decode();
    elements.llmHint.textContent = `模型：${payload.model}，生成完成`;
    showToast("AI 回答完成");
  } catch (error) {
    elements.llmHint.textContent = error.message;
    showToast("AI 生成失败，请检查 API Key 或网络", true);
  } finally {
    elements.askLlmButton.disabled = false;
  }
}

elements.navItems.forEach((item) => {
  item.addEventListener("click", () => switchView(item.dataset.view));
});

document.querySelectorAll("[data-jump-view]").forEach((button) => {
  button.addEventListener("click", () => switchView(button.dataset.jumpView));
});

elements.refreshButton.addEventListener("click", loadData);
elements.globalSearch.addEventListener("input", renderAll);
elements.quickTemplateSelect.addEventListener("change", () => {
  state.selectedTemplateId = Number(elements.quickTemplateSelect.value);
  renderVariables();
  renderTemplates();
});
elements.snippetChoices.addEventListener("change", updateSelectedSnippetCount);
elements.generatePromptButton.addEventListener("click", generatePrompt);
elements.copyPromptButton.addEventListener("click", () => copyText(elements.finalPrompt.value, "Prompt 已复制"));
elements.copyAnswerButton.addEventListener("click", () => copyText(elements.llmAnswer.value, "AI 回答已复制"));
elements.templateForm.addEventListener("submit", createTemplate);
elements.snippetForm.addEventListener("submit", createSnippet);
elements.reloadHistoryButton.addEventListener("click", loadData);
elements.askLlmButton.addEventListener("click", askLlm);

elements.templateList.addEventListener("click", (event) => {
  const deleteButton = event.target.closest("[data-delete-template-id]");
  if (deleteButton) {
    deleteItem(`/api/templates/${deleteButton.dataset.deleteTemplateId}`, "模板已删除");
    return;
  }

  const card = event.target.closest("[data-template-id]");
  if (card) {
    state.selectedTemplateId = Number(card.dataset.templateId);
    renderTemplateSelect();
    renderTemplates();
    switchView("dashboard");
  }
});

elements.snippetList.addEventListener("click", (event) => {
  const deleteButton = event.target.closest("[data-delete-snippet-id]");
  if (deleteButton) {
    deleteItem(`/api/snippets/${deleteButton.dataset.deleteSnippetId}`, "知识片段已删除");
  }
});

document.addEventListener("click", (event) => {
  const historyDelete = event.target.closest("[data-delete-history-id]");
  if (historyDelete) {
    deleteItem(`/api/history/${historyDelete.dataset.deleteHistoryId}`, "历史记录已删除");
    return;
  }

  const historyCardElement = event.target.closest("[data-history-id]");
  if (historyCardElement) {
    loadHistoryToPrompt(Number(historyCardElement.dataset.historyId));
  }
});

loadData();
