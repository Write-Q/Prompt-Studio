const state = {
  templates: [],
  snippets: [],
  history: [],
  activeView: "dashboard",
  selectedTemplateId: null,
  selectedSnippetIds: new Set(),
  editingTemplateId: null,
  editingSnippetId: null,
};

const fallbackTemplates = [
  {
    id: 1001,
    title: "学习笔记整理",
    category: "学习",
    tags: ["学习", "总结"],
    content: "请用{语气}的方式，将以下内容整理成{长度}学习笔记：\n{输入内容}",
    description: "适合课堂笔记、阅读笔记和复习资料整理。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 1002,
    title: "工作周报生成",
    category: "办公",
    tags: ["周报", "汇报"],
    content: "请根据以下工作内容，生成一份{周期}工作周报，语气要求{语气}：\n{输入内容}",
    description: "适合日常工作复盘和团队汇报。",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
];

const fallbackSnippets = [
  {
    id: 2001,
    title: "结构化输出原则",
    tags: ["结构化", "输出"],
    content: "回答时优先使用标题、要点和行动建议，让结果便于阅读、复制和继续迭代。",
    source: "本地示例",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
  {
    id: 2002,
    title: "友好但高效的语气",
    tags: ["语气", "写作"],
    content: "表达要清楚、自然、有一点温度。少用空泛赞美，多给可执行的下一步。",
    source: "本地示例",
    created_at: "本地示例",
    updated_at: "本地示例",
  },
];

const pageMeta = {
  dashboard: ["仪表盘", "把模板、知识和灵感收进一个可复用的 AI 工作台。"],
  templates: ["提示词模板", "沉淀高频任务的结构，让好 Prompt 可以复用。"],
  snippets: ["知识片段", "保存背景资料、写作规范和项目上下文。"],
  history: ["生成记录", "回收每次试验，不让好结果只出现一次。"],
  ai: ["AI 生成", "把最终 Prompt 交给 DeepSeek，并查看流式回答。"],
};

const elements = {
  mobileMenuButton: document.querySelector("#mobileMenuButton"),
  scrim: document.querySelector("#scrim"),
  pageTitle: document.querySelector("#pageTitle"),
  pageSubtitle: document.querySelector("#pageSubtitle"),
  navItems: document.querySelectorAll(".nav-item"),
  viewSections: document.querySelectorAll(".view-section"),
  globalSearch: document.querySelector("#globalSearch"),
  refreshButton: document.querySelector("#refreshButton"),
  toast: document.querySelector("#toast"),
  apiStatus: document.querySelector("#apiStatus"),

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
  templateList: document.querySelector("#templateList"),

  snippetForm: document.querySelector("#snippetForm"),
  snippetFormTitle: document.querySelector("#snippetFormTitle"),
  snippetTitle: document.querySelector("#snippetTitle"),
  snippetTags: document.querySelector("#snippetTags"),
  snippetSource: document.querySelector("#snippetSource"),
  snippetContent: document.querySelector("#snippetContent"),
  saveSnippetButton: document.querySelector("#saveSnippetButton"),
  cancelSnippetEditButton: document.querySelector("#cancelSnippetEditButton"),
  snippetList: document.querySelector("#snippetList"),

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
};

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.classList.toggle("error", isError);
  elements.toast.classList.add("show");

  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2600);
}

function setApiStatus(message, mode = "pending") {
  elements.apiStatus.textContent = message;
  elements.apiStatus.classList.toggle("ok", mode === "ok");
  elements.apiStatus.classList.toggle("error", mode === "error");
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
    item.created_at,
    (item.tags || []).join(" "),
  ]
    .join(" ")
    .toLowerCase()
    .includes(keyword);
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

  return String(value).replace("T", " ").slice(0, 16);
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
  elements.snippetCount.textContent = state.snippets.length;
  elements.templateCount.textContent = state.templates.length;
  elements.historyCount.textContent = state.history.length;
  elements.latestUpdate.textContent = formatDate(state.history[0]?.created_at)?.slice(5) || "--";
}

function renderTemplateSelect() {
  syncSelectedTemplate();

  if (!state.templates.length) {
    elements.quickTemplateSelect.innerHTML = '<option value="">暂无模板</option>';
    renderVariables();
    return;
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
        <input data-variable-name="${escapeHtml(name)}" type="text" placeholder="填写 ${escapeHtml(name)}">
      </label>
    `)
    .join("");
}

function renderSnippetChoices() {
  const snippets = state.snippets.filter(matchesKeyword);

  if (!snippets.length) {
    elements.snippetChoices.innerHTML = '<div class="empty-state">暂无可选知识片段。</div>';
    elements.selectedSnippetCount.textContent = `已选 ${state.selectedSnippetIds.size} 个`;
    return;
  }

  elements.snippetChoices.innerHTML = snippets
    .map((item) => `
      <label class="choice-card">
        <input type="checkbox" value="${item.id}" data-snippet-choice ${state.selectedSnippetIds.has(item.id) ? "checked" : ""}>
        <span>
          <strong>${escapeHtml(item.title)}</strong>
          <small>${escapeHtml((item.tags || []).join(" / ") || item.source || "无标签")}</small>
        </span>
      </label>
    `)
    .join("");
  updateSelectedSnippetCount();
}

function renderTemplates() {
  const templates = state.templates.filter(matchesKeyword);

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

function renderSnippets() {
  const snippets = state.snippets.filter(matchesKeyword);

  if (!snippets.length) {
    elements.snippetList.innerHTML = '<div class="empty-state">暂无知识片段。可以先保存一条写作规范或项目背景。</div>';
    return;
  }

  elements.snippetList.innerHTML = snippets
    .map((item) => `
      <article class="resource-card">
        <div class="resource-row">
          <div>
            <div class="resource-title">${escapeHtml(item.title)}</div>
            <div class="resource-meta">${escapeHtml(item.source || "无来源")} · ${escapeHtml(item.content.slice(0, 94))}</div>
          </div>
          <div class="resource-actions">
            <button class="tiny-button secondary-button" type="button" data-toggle-snippet-id="${item.id}">
              ${state.selectedSnippetIds.has(item.id) ? "取消选择" : "加入生成"}
            </button>
            <button class="tiny-button secondary-button" type="button" data-edit-snippet-id="${item.id}">编辑</button>
            <button class="delete-button" type="button" data-delete-snippet-id="${item.id}">删除</button>
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
    ? `${item.final_prompt.slice(0, 170)}...`
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
  const history = state.history.filter(matchesKeyword);
  const recent = history.slice(0, 5);

  elements.recentHistoryList.innerHTML = recent.length
    ? recent.map(historyCard).join("")
    : '<div class="empty-state">暂无最近生成记录。</div>';

  elements.historyList.innerHTML = history.length
    ? history.map(historyCard).join("")
    : '<div class="empty-state">暂无历史记录。生成 Prompt 后会自动保存到这里。</div>';
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
  setApiStatus("连接中", "pending");

  try {
    const [templates, snippets, history] = await Promise.all([
      requestJson("/api/templates"),
      requestJson("/api/snippets"),
      requestJson("/api/history?limit=50"),
    ]);

    state.templates = templates;
    state.snippets = snippets;
    state.history = history;
    syncSelectedTemplate();
    renderAll();
    setApiStatus("已连接", "ok");
    showToast("已连接 FastAPI 后端");
  } catch (error) {
    if (!state.templates.length) {
      state.templates = fallbackTemplates;
      state.snippets = fallbackSnippets;
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
    const shouldUseMainInput = /输入|内容|主题|关键词|问题|任务/.test(name);
    variables[name] = input.value.trim() || (shouldUseMainInput ? elements.quickKeyword.value.trim() : "");
  });

  return variables;
}

function collectSnippetIds() {
  return Array.from(state.selectedSnippetIds);
}

function updateSelectedSnippetCount() {
  elements.selectedSnippetCount.textContent = `已选 ${state.selectedSnippetIds.size} 个`;
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

  return `${prompt}\n\n参考知识片段：\n${selectedSnippets.map((item) => `- ${item.title}\n${item.content}`).join("\n\n")}`;
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
    elements.promptHint.textContent = "正在生成 Prompt...";

    const result = await requestJson("/api/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    elements.finalPrompt.value = result.final_prompt;
    elements.aiPromptInput.value = result.final_prompt;
    elements.promptHint.textContent = result.missing_variables.length
      ? `未填写变量：${result.missing_variables.join("、")}`
      : `生成成功，历史 ID：${result.history_id}`;
    await loadHistory();
    showToast("Prompt 已生成");
  } catch (error) {
    const localPrompt = buildLocalPrompt(template, payload.variables, payload.snippet_ids);
    elements.finalPrompt.value = localPrompt;
    elements.aiPromptInput.value = localPrompt;
    elements.promptHint.textContent = "后端生成失败，当前显示本地拼接结果。";
    showToast(error.message, true);
  } finally {
    elements.generatePromptButton.disabled = false;
  }
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

function resetSnippetForm() {
  state.editingSnippetId = null;
  elements.snippetForm.reset();
  elements.snippetFormTitle.textContent = "新增知识片段";
  elements.saveSnippetButton.textContent = "保存片段";
  elements.cancelSnippetEditButton.classList.add("is-hidden");
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

async function saveSnippet(event) {
  event.preventDefault();

  const payload = {
    title: elements.snippetTitle.value,
    tags: parseTags(elements.snippetTags.value),
    source: elements.snippetSource.value || null,
    content: elements.snippetContent.value,
  };

  const isEditing = state.editingSnippetId !== null;
  const url = isEditing ? `/api/snippets/${state.editingSnippetId}` : "/api/snippets";
  const method = isEditing ? "PUT" : "POST";

  try {
    const saved = await requestJson(url, {
      method,
      body: JSON.stringify(payload),
    });

    state.selectedSnippetIds.add(saved.id);
    resetSnippetForm();
    await loadData();
    showToast(isEditing ? "知识片段已更新" : "知识片段已保存");
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

function editSnippet(snippetId) {
  const snippet = state.snippets.find((item) => item.id === snippetId);
  if (!snippet) {
    return;
  }

  state.editingSnippetId = snippetId;
  elements.snippetTitle.value = snippet.title;
  elements.snippetTags.value = (snippet.tags || []).join(", ");
  elements.snippetSource.value = snippet.source || "";
  elements.snippetContent.value = snippet.content;
  elements.snippetFormTitle.textContent = "编辑知识片段";
  elements.saveSnippetButton.textContent = "更新片段";
  elements.cancelSnippetEditButton.classList.remove("is-hidden");
  switchView("snippets");
  elements.snippetTitle.focus();
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
    elements.llmHint.textContent = `模型：${payload.model}，正在建立流式连接...`;

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
    let answerLength = 0;
    elements.llmHint.textContent = `模型：${payload.model}，正在流式输出...`;

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      elements.llmAnswer.value += chunk;
      answerLength += chunk.length;
      elements.llmAnswer.scrollTop = elements.llmAnswer.scrollHeight;
    }

    const tail = decoder.decode();
    if (tail) {
      elements.llmAnswer.value += tail;
      answerLength += tail.length;
    }

    elements.llmHint.textContent = `模型：${payload.model}，输出完成，共 ${answerLength} 个字符`;
    showToast("AI 回答已完成");
  } catch (error) {
    elements.llmHint.textContent = error.message;
    showToast("AI 生成失败，请检查 API Key 或网络", true);
  } finally {
    elements.askLlmButton.disabled = false;
  }
}

function bindEvents() {
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
    elements.quickKeyword.focus();
  });

  elements.refreshButton.addEventListener("click", loadData);
  elements.globalSearch.addEventListener("input", renderAll);
  elements.quickKeyword.addEventListener("input", () => {
    if (!elements.finalPrompt.value) {
      elements.promptHint.textContent = "填写核心输入后即可生成 Prompt。";
    }
  });

  elements.quickTemplateSelect.addEventListener("change", () => {
    state.selectedTemplateId = Number(elements.quickTemplateSelect.value);
    renderVariables();
    renderTemplates();
  });

  elements.snippetChoices.addEventListener("change", (event) => {
    const checkbox = event.target.closest("[data-snippet-choice]");
    if (!checkbox) {
      return;
    }

    const id = Number(checkbox.value);
    if (checkbox.checked) {
      state.selectedSnippetIds.add(id);
    } else {
      state.selectedSnippetIds.delete(id);
    }

    updateSelectedSnippetCount();
    renderSnippets();
  });

  elements.generatePromptButton.addEventListener("click", generatePrompt);
  elements.copyPromptButton.addEventListener("click", () => copyText(elements.finalPrompt.value, "Prompt 已复制"));
  elements.pushToAiButton.addEventListener("click", () => {
    elements.aiPromptInput.value = elements.finalPrompt.value;
    switchView("ai");
    showToast("Prompt 已同步到 AI 控制台");
  });

  elements.templateForm.addEventListener("submit", saveTemplate);
  elements.cancelTemplateEditButton.addEventListener("click", resetTemplateForm);
  elements.snippetForm.addEventListener("submit", saveSnippet);
  elements.cancelSnippetEditButton.addEventListener("click", resetSnippetForm);

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

  elements.snippetList.addEventListener("click", (event) => {
    const toggleButton = event.target.closest("[data-toggle-snippet-id]");
    const editButton = event.target.closest("[data-edit-snippet-id]");
    const deleteButton = event.target.closest("[data-delete-snippet-id]");

    if (toggleButton) {
      const snippetId = Number(toggleButton.dataset.toggleSnippetId);
      if (state.selectedSnippetIds.has(snippetId)) {
        state.selectedSnippetIds.delete(snippetId);
      } else {
        state.selectedSnippetIds.add(snippetId);
      }
      renderSnippetChoices();
      renderSnippets();
      return;
    }

    if (editButton) {
      editSnippet(Number(editButton.dataset.editSnippetId));
      return;
    }

    if (deleteButton) {
      const snippetId = Number(deleteButton.dataset.deleteSnippetId);
      deleteItem(`/api/snippets/${snippetId}`, "知识片段已删除", () => {
        state.snippets = state.snippets.filter((item) => item.id !== snippetId);
        state.selectedSnippetIds.delete(snippetId);
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

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document.body.classList.remove("sidebar-open");
    }
  });
}

bindEvents();
loadData();
