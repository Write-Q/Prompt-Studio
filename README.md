# Prompt Studio

Prompt Studio 是一个轻量级 Prompt 工作台，用于管理 Prompt 模板、上下文卡片和生成历史。后端基于 FastAPI + 原生 sqlite3（无 ORM），前端使用原生 HTML / CSS / JavaScript（无构建步骤），数据默认保存在本地 SQLite。

## 功能

- 管理 Prompt 模板与上下文卡片
- 按模板、变量和上下文卡片预生成 Prompt（规则层组装）
- 手动保存并查看生成历史
- 调用 DeepSeek 生成回答（支持流式）或优化 Prompt
- 上下文卡片以「像素扑克牌」形式展示：5 堆分类、扇形展开、拖拽 / 点击出牌、键盘可导航
- 像素工作室风格 UI：花体英文 pill、宋体大字标题 + CRT 色差、像素小猫插画与水印装饰

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

## 浏览器要求

前端使用了 `:has()`、`display: contents`、`mix-blend-mode`、`aspect-ratio` 等现代 CSS 特性。最低要求：

- Chrome / Edge 105+
- Safari 15.4+
- Firefox 121+

字体通过 [fonts.loli.net](https://fonts.loli.net) 国内镜像加载 Inter 与思源宋体 SC，网络不可达时自动 fallback 到系统字体（PingFang SC / Microsoft YaHei UI / SimSun）。

## DeepSeek 配置

需要使用 AI 回答或 Prompt 优化时，配置环境变量：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

只管理模板、上下文卡片和预生成 Prompt 时，可以不配置。

## 常用 API

| 路径 | 方法 | 说明 |
|---|---|---|
| `/health` | GET | 健康检查 |
| `/api/templates` | GET / POST | 模板列表（支持 `category`、`keyword`、`limit`、`offset`）/ 新建 |
| `/api/templates/{id}` | GET / PUT / DELETE | 单条详情 / 更新 / 删除 |
| `/api/context-cards` | GET / POST | 上下文卡片列表（支持 `type`、`tag`、`keyword`、`limit`、`offset`）/ 新建 |
| `/api/context-cards/recommend` | POST | 根据输入文本推荐相关上下文卡片 |
| `/api/context-cards/{id}` | GET / PUT / DELETE | 单条详情 / 更新 / 删除 |
| `/api/generate` | POST | 预生成 Prompt（规则组装，不写历史） |
| `/api/history` | GET / POST | 历史列表（支持 `limit`）/ 手动保存 |
| `/api/history/{id}` | GET / DELETE | 单条详情 / 删除 |
| `/api/llm/answer/stream` | POST | 流式获取大模型回答 |
| `/api/llm/optimize-prompt` | POST | 优化 Prompt |
| `/api/llm/chat` | POST | 带工具调用（Tool Use）的对话，模型可自动检索模板 / 上下文卡片 |

## 上下文卡片类型

| 类型 | 中文标签 |
|---|---|
| `background` | 背景资料 |
| `rule` | 写作规则 |
| `format` | 输出格式 |
| `example` | 参考示例 |
| `checklist` | 检查清单 |

## 目录结构

```text
app/
├── main.py                 # FastAPI 应用 + 路由挂载 + lifespan
├── database.py             # sqlite3 连接 + 建表 + 索引
├── models/schemas.py       # Pydantic 请求/响应模型
├── routes/                 # 路由层（参数解析 + HTTPException 映射）
└── services/               # 服务层（业务逻辑 + 自定义异常）

frontend/
├── index.html
├── script.js
├── style.css
└── assets/illustrations/   # 像素插画 PNG（8 张）

seed_test_data.py           # 重建演示数据库并写入固定示例数据
requirements.txt
```

## 验证

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m compileall app seed_test_data.py verify_tool_use.py
node --check frontend\script.js
```

Tool Use（函数调用）联网验证（需配置 `DEEPSEEK_API_KEY`，建议先跑 `seed_test_data.py` 准备数据）：

```powershell
.\.venv\Scripts\python.exe verify_tool_use.py
```

> `tests/` 目录已被 `.gitignore` 忽略，不随仓库分发。本地保留即可跑测试；如需获取测试套件可从历史 commit `86b6d13` 之前的版本中提取。

## 数据库初始化与示例数据

```powershell
# 创建当前表结构（启动时自动执行，也可手动跑）
.\.venv\Scripts\python.exe -m app.database

# 重建演示数据库并写入示例模板与上下文卡片
.\.venv\Scripts\python.exe seed_test_data.py
```

数据库默认位置：`data/app.db`（首次启动自动创建）。

## 可分发的种子数据（开箱即用）

为了让别人本地部署时直接获得数据，种子数据以 JSON 文本存放在 `seed/` 目录（进 git、可无限扩充），数据库本身（`data/*.db`）不入库。

- **首次启动自动灌入**：`app.main` 启动时调用 `seed_if_empty()`，若库为空则从 `seed/*.json` 灌入；库里已有数据则跳过，不会覆盖用户后续添加的内容。
- **维护数据的两个方向**：

```powershell
# 把当前数据库导出成 seed/*.json（在 UI 里编辑数据后，导出成可分发的种子）
.\.venv\Scripts\python.exe -m app.seed --export

# 手动灌入（库为空时生效，等同于首次启动的行为）
.\.venv\Scripts\python.exe -m app.seed
```

别人拿到项目后：`uvicorn app.main:app` 一跑，空库会自动从 `seed/` 灌好数据，开箱即用。

> 数据量很大时，再决定 `seed/` 的分发方式：几十 MB 内可直接进 git；几百 MB 用 Git LFS 或挂 GitHub Release；GB 级则考虑首次运行下载或只发子集。机制本身不变。
