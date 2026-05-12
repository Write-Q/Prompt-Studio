# Prompt Studio

Prompt Studio 是一个用于管理 Prompt 模板、知识片段和生成历史的轻量级 Web 应用。后端基于 FastAPI，前端使用原生 HTML、CSS 和 JavaScript，数据默认保存在本地 SQLite 数据库中。

## 功能

- 管理 Prompt 模板
- 管理知识片段
- 根据模板和变量生成最终 Prompt
- 保存并查看生成历史
- 调用 DeepSeek 接口生成大模型回答
- 提供简单的前端页面用于日常操作

## 项目结构

```text
PromptStudio/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── database.py          # SQLite 连接和初始化
│   ├── models/              # Pydantic 数据模型
│   ├── routes/              # API 路由
│   └── services/            # 业务逻辑
├── frontend/
│   ├── index.html           # 前端页面
│   ├── css/
│   └── js/
├── data/                    # 本地数据库目录，不上传到 GitHub
├── requirements.txt         # Python 依赖
└── README.md
```

## 环境要求

- Python 3.10 或更高版本
- Git

## 安装依赖

建议先创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

## 配置环境变量

如果需要使用大模型回答功能，需要配置 DeepSeek API Key：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

如果只是管理模板、知识片段和生成 Prompt，可以先不配置这个环境变量。

## 运行项目

在项目根目录执行：

```powershell
uvicorn app.main:app --reload
```

启动后访问：

```text
http://127.0.0.1:8000/app/
```

后端健康检查接口：

```text
http://127.0.0.1:8000/health
```

## 常用 API

- `GET /health`：健康检查
- `GET /api/templates`：获取 Prompt 模板列表
- `POST /api/templates`：创建 Prompt 模板
- `GET /api/snippets`：获取知识片段列表
- `POST /api/snippets`：创建知识片段
- `POST /api/generate`：生成最终 Prompt
- `GET /api/history`：获取生成历史
- `POST /api/llm/answer`：获取大模型回答
- `POST /api/llm/answer/stream`：流式获取大模型回答

## 数据库说明

项目启动时会自动初始化 SQLite 数据库。数据库文件默认位于：

```text
data/app.db
```

数据库文件属于本地运行数据，已经通过 `.gitignore` 排除，不会上传到 GitHub。

## 推送到 GitHub

如果是第一次上传项目：

```powershell
git init -b main
git remote add origin https://github.com/Write-Q/Prompt-Studio.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

如果项目已经绑定过 GitHub，以后每次改完代码只需要：

```powershell
git status
git add .
git commit -m "Update project"
git push
```

如果推送时遇到代理导致的连接问题，可以临时清理当前 PowerShell 窗口里的代理变量后再推送：

```powershell
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
$env:ALL_PROXY=""
$env:GIT_HTTP_PROXY=""
$env:GIT_HTTPS_PROXY=""
git push
```
