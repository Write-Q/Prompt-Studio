const state = {
  templates: [],
  snippets: [],
  history: [],
  selectedTemplateId: null,
};

const elements = {
  statusText: document.querySelector("#statusText"),
  refreshButton: document.querySelector("#refreshButton"),
  templateForm: document.querySelector("#templateForm"),
  snippetForm: document.querySelector("#snippetForm"),
  templateList: document.querySelector("#templateList"),
  snippetList: document.querySelector("#snippetList"),
  templateCount: document.querySelector("#templateCount"),
  snippetCount: document.querySelector("#snippetCount"),
  historyCount: document.querySelector("#historyCount"),
  templateSearch: document.querySelector("#templateSearch"),
  snippetSearch: document.querySelector("#snippetSearch"),
  templateSelect: document.querySelector("#templateSelect"),
  templatePreview: document.querySelector("#templatePreview"),
  variableFields: document.querySelector("#variableFields"),
  variableCount: document.querySelector("#variableCount"),
  snippetChoices: document.querySelector("#snippetChoices"),
  selectedSnippetCount: document.querySelector("#selectedSnippetCount"),
  generateButton: document.querySelector("#generateButton"),
  finalPrompt: document.querySelector("#finalPrompt"),
  copyButton: document.querySelector("#copyButton"),
  missingVariables: document.querySelector("#missingVariables"),
  reloadHistoryButton: document.querySelector("#reloadHistoryButton"),
  historyList: document.querySelector("#historyList"),
  askLlmButton: document.querySelector("#askLlmButton"),
  llmModel: document.querySelector("#llmModel"),
  llmTemperature: document.querySelector("#llmTemperature"),
  llmAnswer: document.querySelector("#llmAnswer"),
  llmHint: document.querySelector("#llmHint"),
  copyAnswerButton: document.querySelector("#copyAnswerButton"),
};

function setStatus(message, isError = false) {
  elements.statusText.textContent = message;
  elements.statusText.classList.toggle("error", isError);
}

function parseTags(text) {
  return text
    .replaceAll("，", ",")
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function extractVariables(content) {
  const matches = content.matchAll(/\{([^{}\s]+)\}/g);
  const variables = [];

  for (const match of matches) {
    const variableName = match[1];
    if (!variables.includes(variableName)) {
      variables.push(variableName);
    }
  }

  return variables;
}

function filterItems(items, keyword, fields) {
  const text = keyword.trim().toLowerCase();
  if (!text) {
    return items;
  }

  return items.filter((item) =>
    fields.some((field) => String(field(item) ?? "").toLowerCase().includes(text))
  );
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

async function loadTemplates() {
  state.templates = await requestJson("/api/templates");

  if (!state.templates.some((item) => item.id === state.selectedTemplateId)) {
    state.selectedTemplateId = state.templates[0]?.id ?? null;
  }

  renderTemplates();
  renderTemplateSelect();
}

async function loadSnippets() {
  state.snippets = await requestJson("/api/snippets");
  renderSnippets();
  renderSnippetChoices();
}

async function loadHistory() {
  state.history = await requestJson("/api/history?limit=20");
  renderHistory();
}

async function reloadAll() {
  try {
    await Promise.all([loadTemplates(), loadSnippets(), loadHistory()]);
    setStatus("后端连接正常");
  } catch (error) {
    setStatus(error.message, true);
  }
}

function getSelectedTemplate() {
  return state.templates.find((item) => item.id === state.selectedTemplateId) ?? null;
}

function renderTags(tags) {
  if (!tags?.length) {
    return "<span class=\"tag\">无标签</span>";
  }

  return tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
}

function renderTemplates() {
  const keyword = elements.templateSearch.value;
  const items = filterItems(state.templates, keyword, [
    (item) => item.title,
    (item) => item.category,
    (item) => item.tags?.join(" "),
    (item) => item.content,
  ]);

  elements.templateCount.textContent = state.templates.length;

  if (items.length === 0) {
    elements.templateList.innerHTML = "<div class=\"empty-state\">暂无模板</div>";
    return;
  }

  elements.templateList.innerHTML = items
    .map((item) => `
      <article class="resource-card ${item.id === state.selectedTemplateId ? "is-active" : ""}" data-template-id="${item.id}">
        <div class="resource-title-row">
          <div>
            <div class="resource-title">${escapeHtml(item.title)}</div>
            <div class="resource-meta">${escapeHtml(item.category || "未分类")}</div>
          </div>
          <button class="delete-button" type="button" data-delete-template-id="${item.id}">删除</button>
        </div>
        <div class="tag-row">${renderTags(item.tags)}</div>
      </article>
    `)
    .join("");
}

function renderSnippets() {
  const keyword = elements.snippetSearch.value;
  const items = filterItems(state.snippets, keyword, [
    (item) => item.title,
    (item) => item.tags?.join(" "),
    (item) => item.content,
    (item) => item.source,
  ]);

  elements.snippetCount.textContent = state.snippets.length;

  if (items.length === 0) {
    elements.snippetList.innerHTML = "<div class=\"empty-state\">暂无知识片段</div>";
    return;
  }

  elements.snippetList.innerHTML = items
    .map((item) => `
      <article class="resource-card">
        <div class="resource-title-row">
          <div>
            <div class="resource-title">${escapeHtml(item.title)}</div>
            <div class="resource-meta">${escapeHtml(item.source || "无来源")}</div>
          </div>
          <button class="delete-button" type="button" data-delete-snippet-id="${item.id}">删除</button>
        </div>
        <div class="tag-row">${renderTags(item.tags)}</div>
      </article>
    `)
    .join("");
}

function renderTemplateSelect() {
  if (state.templates.length === 0) {
    elements.templateSelect.innerHTML = "<option value=\"\">暂无模板</option>";
    renderBuilder();
    return;
  }

  elements.templateSelect.innerHTML = state.templates
    .map((item) => `<option value="${item.id}">${escapeHtml(item.title)}</option>`)
    .join("");
  elements.templateSelect.value = String(state.selectedTemplateId);
  renderBuilder();
}

function renderBuilder() {
  const template = getSelectedTemplate();

  if (!template) {
    elements.templatePreview.textContent = "暂无模板";
    elements.variableFields.innerHTML = "<div class=\"empty-state\">暂无变量</div>";
    elements.variableCount.textContent = "0 个变量";
    return;
  }

  const variables = extractVariables(template.content);
  elements.templatePreview.textContent = template.content;
  elements.variableCount.textContent = `${variables.length} 个变量`;

  if (variables.length === 0) {
    elements.variableFields.innerHTML = "<div class=\"empty-state\">当前模板没有变量</div>";
    return;
  }

  elements.variableFields.innerHTML = variables
    .map((variableName) => `
      <label>
        ${escapeHtml(variableName)}
        <input data-variable-name="${escapeHtml(variableName)}" type="text" placeholder="填写 ${escapeHtml(variableName)}">
      </label>
    `)
    .join("");
}

function renderSnippetChoices() {
  if (state.snippets.length === 0) {
    elements.snippetChoices.innerHTML = "<div class=\"empty-state\">暂无知识片段</div>";
    elements.selectedSnippetCount.textContent = "已选 0 个";
    return;
  }

  elements.snippetChoices.innerHTML = state.snippets
    .map((item) => `
      <label class="choice-card">
        <input type="checkbox" value="${item.id}" data-snippet-choice>
        <span>
          <strong>${escapeHtml(item.title)}</strong><br>
          <span class="resource-meta">${escapeHtml((item.tags || []).join(" / ") || "无标签")}</span>
        </span>
      </label>
    `)
    .join("");

  updateSelectedSnippetCount();
}

function renderHistory() {
  elements.historyCount.textContent = state.history.length;

  if (state.history.length === 0) {
    elements.historyList.innerHTML = "<div class=\"empty-state\">暂无生成历史</div>";
    return;
  }

  elements.historyList.innerHTML = state.history
    .map((item) => {
      const preview = item.final_prompt.length > 110
        ? `${item.final_prompt.slice(0, 110)}...`
        : item.final_prompt;

      return `
        <article class="history-card" data-history-id="${item.id}">
          <div class="resource-title-row">
            <div>
              <div class="resource-title">历史 #${item.id}</div>
              <div class="resource-meta">${escapeHtml(item.created_at)}</div>
            </div>
            <button class="delete-button" type="button" data-delete-history-id="${item.id}">删除</button>
          </div>
          <div class="tag-row">
            <span class="tag">模板 ${item.template_id}</span>
          </div>
          <div class="resource-meta">${escapeHtml(preview)}</div>
        </article>
      `;
    })
    .join("");
}

function collectVariables() {
  const inputs = elements.variableFields.querySelectorAll("[data-variable-name]");
  const variables = {};

  inputs.forEach((input) => {
    variables[input.dataset.variableName] = input.value;
  });

  return variables;
}

function collectSnippetIds() {
  const checkedItems = elements.snippetChoices.querySelectorAll("[data-snippet-choice]:checked");
  return Array.from(checkedItems).map((item) => Number(item.value));
}

function updateSelectedSnippetCount() {
  elements.selectedSnippetCount.textContent = `已选 ${collectSnippetIds().length} 个`;
}

async function createTemplate(event) {
  event.preventDefault();

  const payload = {
    title: document.querySelector("#templateTitle").value,
    category: document.querySelector("#templateCategory").value || null,
    tags: parseTags(document.querySelector("#templateTags").value),
    content: document.querySelector("#templateContent").value,
    description: document.querySelector("#templateDescription").value || null,
  };

  try {
    const created = await requestJson("/api/templates", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.selectedTemplateId = created.id;
    elements.templateForm.reset();
    await loadTemplates();
    setStatus("模板已新增");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function createSnippet(event) {
  event.preventDefault();

  const payload = {
    title: document.querySelector("#snippetTitle").value,
    tags: parseTags(document.querySelector("#snippetTags").value),
    content: document.querySelector("#snippetContent").value,
    source: document.querySelector("#snippetSource").value || null,
  };

  try {
    await requestJson("/api/snippets", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    elements.snippetForm.reset();
    await loadSnippets();
    setStatus("知识片段已新增");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteTemplate(templateId) {
  try {
    await requestJson(`/api/templates/${templateId}`, { method: "DELETE" });
    if (state.selectedTemplateId === templateId) {
      state.selectedTemplateId = null;
    }
    await loadTemplates();
    setStatus("模板已删除");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteSnippet(snippetId) {
  try {
    await requestJson(`/api/snippets/${snippetId}`, { method: "DELETE" });
    await loadSnippets();
    setStatus("知识片段已删除");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function generatePrompt() {
  const template = getSelectedTemplate();

  if (!template) {
    setStatus("请先选择模板", true);
    return;
  }

  const payload = {
    template_id: template.id,
    variables: collectVariables(),
    snippet_ids: collectSnippetIds(),
    mode: "rule",
  };

  try {
    elements.generateButton.disabled = true;
    const result = await requestJson("/api/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    elements.finalPrompt.value = result.final_prompt;
    elements.missingVariables.textContent = result.missing_variables.length
      ? `未填写变量：${result.missing_variables.join("、")}`
      : `生成成功，历史 ID：${result.history_id}`;
    await loadHistory();
    setStatus("生成成功");
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    elements.generateButton.disabled = false;
  }
}

async function copyText(text, successMessage) {
  if (!text) {
    setStatus("暂无可复制内容", true);
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    setStatus(successMessage);
  } catch {
    const helper = document.createElement("textarea");
    helper.value = text;
    document.body.appendChild(helper);
    helper.select();
    document.execCommand("copy");
    helper.remove();
    setStatus(successMessage);
  }
}

function copyPrompt() {
  copyText(elements.finalPrompt.value, "已复制最终 Prompt");
}

function copyAnswer() {
  copyText(elements.llmAnswer.value, "已复制模型回答");
}

async function loadHistoryToPrompt(historyId) {
  try {
    const history = await requestJson(`/api/history/${historyId}`);
    elements.finalPrompt.value = history.final_prompt;
    elements.missingVariables.textContent = `已载入历史 ID：${history.id}`;
    setStatus("历史 Prompt 已载入");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteHistory(historyId) {
  try {
    await requestJson(`/api/history/${historyId}`, { method: "DELETE" });
    await loadHistory();
    setStatus("历史记录已删除");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function askLlm() {
  if (!elements.finalPrompt.value.trim()) {
    setStatus("请先生成或载入最终 Prompt", true);
    return;
  }

  const payload = {
    prompt: elements.finalPrompt.value,
    model: elements.llmModel.value.trim() || "deepseek-v4-flash",
    temperature: Number(elements.llmTemperature.value || 0.7),
  };

  try {
    elements.askLlmButton.disabled = true;
    elements.llmAnswer.value = "";
    elements.llmHint.textContent = "正在连接 DeepSeek 流式接口...";

    const response = await fetch("/api/llm/answer/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `请求失败：${response.status}`);
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

      const textChunk = decoder.decode(value, { stream: true });
      elements.llmAnswer.value += textChunk;
      answerLength += textChunk.length;
      elements.llmAnswer.scrollTop = elements.llmAnswer.scrollHeight;
    }

    const lastText = decoder.decode();
    if (lastText) {
      elements.llmAnswer.value += lastText;
      answerLength += lastText.length;
    }

    elements.llmHint.textContent = `模型：${payload.model}，流式输出完成，共 ${answerLength} 个字符`;
    setStatus("DeepSeek 流式回答完成");
  } catch (error) {
    elements.llmHint.textContent = error.message;
    setStatus(error.message, true);
  } finally {
    elements.askLlmButton.disabled = false;
  }
}

elements.templateForm.addEventListener("submit", createTemplate);
elements.snippetForm.addEventListener("submit", createSnippet);
elements.refreshButton.addEventListener("click", reloadAll);
elements.reloadHistoryButton.addEventListener("click", loadHistory);
elements.generateButton.addEventListener("click", generatePrompt);
elements.copyButton.addEventListener("click", copyPrompt);
elements.copyAnswerButton.addEventListener("click", copyAnswer);
elements.askLlmButton.addEventListener("click", askLlm);
elements.templateSearch.addEventListener("input", renderTemplates);
elements.snippetSearch.addEventListener("input", renderSnippets);

elements.templateSelect.addEventListener("change", () => {
  state.selectedTemplateId = Number(elements.templateSelect.value);
  renderTemplates();
  renderBuilder();
});

elements.templateList.addEventListener("click", (event) => {
  const deleteButton = event.target.closest("[data-delete-template-id]");
  if (deleteButton) {
    deleteTemplate(Number(deleteButton.dataset.deleteTemplateId));
    return;
  }

  const card = event.target.closest("[data-template-id]");
  if (!card) {
    return;
  }

  state.selectedTemplateId = Number(card.dataset.templateId);
  renderTemplates();
  renderTemplateSelect();
});

elements.snippetList.addEventListener("click", (event) => {
  const deleteButton = event.target.closest("[data-delete-snippet-id]");
  if (!deleteButton) {
    return;
  }

  deleteSnippet(Number(deleteButton.dataset.deleteSnippetId));
});

elements.snippetChoices.addEventListener("change", updateSelectedSnippetCount);

elements.historyList.addEventListener("click", (event) => {
  const deleteButton = event.target.closest("[data-delete-history-id]");
  if (deleteButton) {
    deleteHistory(Number(deleteButton.dataset.deleteHistoryId));
    return;
  }

  const card = event.target.closest("[data-history-id]");
  if (!card) {
    return;
  }

  loadHistoryToPrompt(Number(card.dataset.historyId));
});

reloadAll();
