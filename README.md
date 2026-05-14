# Prompt Studio

Prompt Studio 是一个轻量级 Prompt 工作台，用于管理 Prompt 模板、上下文卡片和生成历史。后端基于 FastAPI，前端使用原生 HTML、CSS 和 JavaScript，数据默认保存在本地 SQLite。

## 功能

- 管理 Prompt 模板
- 管理上下文卡片
- 按模板、变量和上下文卡片预生成 Prompt
- 手动保存并查看生成历史
- 调用 DeepSeek 生成回答或优化 Prompt

## 运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端入口：

```text
http://127.0.0.1:8000/app/
```

健康检查：

```text
http://127.0.0.1:8000/health
```

## DeepSeek 配置

需要使用 AI 回答或 Prompt 优化时，配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

只管理模板、上下文卡片和预生成 Prompt 时，可以不配置。

## 常用 API

- `GET /health`：健康检查
- `GET /api/templates`：获取 Prompt 模板列表
- `POST /api/templates`：创建 Prompt 模板
- `GET /api/context-cards`：获取上下文卡片列表
- `POST /api/context-cards`：创建上下文卡片
- `POST /api/generate`：预生成 Prompt
- `GET /api/history`：获取生成历史
- `POST /api/history`：手动保存生成历史
- `POST /api/llm/answer`：获取大模型回答
- `POST /api/llm/answer/stream`：流式获取大模型回答
- `POST /api/llm/optimize-prompt`：优化 Prompt

## 上下文卡片类型

- `background`：背景资料
- `rule`：写作规则
- `format`：输出格式
- `example`：参考示例
- `checklist`：检查清单

## 验证

```powershell
D:\VScode\Python\PromptStudio\.venv\Scripts\python.exe -m unittest discover -s tests
D:\VScode\Python\PromptStudio\.venv\Scripts\python.exe -m compileall app seed_test_data.py
node --check frontend\script.js
```
