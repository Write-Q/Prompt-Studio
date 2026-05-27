# PromptStudio 后端答辩讲解稿

## 一句话介绍

PromptStudio 的后端是一个本地单机 Prompt 管理服务，主要负责三件事：保存 Prompt 模板、保存上下文卡片、根据模板和卡片组装最终 Prompt。系统使用 FastAPI 提供接口，使用 SQLite 保存数据，使用 Pydantic 做请求校验。

## 后端整体结构

答辩时可以按这个顺序讲：

```text
app/
├── main.py                  应用入口，注册路由，挂载前端
├── database.py              SQLite 连接、建表、索引
├── models/schemas.py        请求和响应的数据模型
├── routes/                  接口层，处理 HTTP 请求和异常转换
└── services/                业务层，执行数据库操作和 Prompt 组装
```

后端保持了比较清楚的三层结构：

```text
浏览器页面
  ↓
routes 路由层
  ↓
services 业务层
  ↓
database SQLite 数据库
```

可以这样解释：

> 路由层只负责接收请求和返回 HTTP 响应；服务层负责真正的业务逻辑；数据库层统一提供 SQLite 连接和建表逻辑。这样每一层职责比较明确，代码也方便答辩时逐层讲解。

## 每个核心文件怎么讲

### 1. main.py

作用：创建 FastAPI 应用，启动时初始化数据库，并挂载前端页面。

讲法：

> `main.py` 是后端入口。项目启动时会执行 `init_db()`，确保 SQLite 表存在。之后注册模板、上下文卡片、历史记录、Prompt 生成和 AI 调用相关路由。前端页面通过 `/app/` 访问。

重点代码：

```python
app.include_router(templates_router)
app.include_router(context_cards_router)
app.include_router(generate_router)
app.include_router(history_router)
app.include_router(llm_router)
```

### 2. database.py

作用：连接 SQLite，并创建当前版本需要的三张表。

三张表：

```text
prompt_templates     Prompt 模板
context_cards        上下文卡片
generation_history   生成历史
```

讲法：

> 因为项目定位是本地单机工具，所以我没有引入 MySQL 或 ORM，而是使用 Python 标准库 sqlite3。启动时会自动创建表，页面新增的数据会写入 `data/app.db`，关闭页面或重启后端后数据仍然保留。

可以强调：

> 为了方便答辩演示，我删除了历史版本迁移和复杂种子同步逻辑，只保留当前版本表结构。这样代码更短，也更容易说明。

### 3. schemas.py

作用：定义接口输入和输出的数据结构。

讲法：

> `schemas.py` 使用 Pydantic 定义请求和响应模型。比如模板标题不能为空，标签可以传列表，也可以传逗号分隔字符串，后端会统一整理成 `list[str]`。

例子：

```text
PromptTemplateCreate     新建模板请求
PromptTemplateResponse   模板响应
ContextCardCreate        新建上下文卡片请求
GenerateRequest          生成 Prompt 请求
GenerateResponse         生成 Prompt 响应
```

### 4. routes/

作用：定义 API 地址。

主要接口：

```text
GET /api/templates              获取模板列表
POST /api/templates             新建模板
PUT /api/templates/{id}         修改模板
DELETE /api/templates/{id}      删除模板

GET /api/context-cards          获取上下文卡片列表
POST /api/context-cards         新建上下文卡片

POST /api/generate              组装最终 Prompt
GET /api/history                查看生成历史
POST /api/history               保存生成历史
```

讲法：

> routes 层基本不写复杂业务，只负责把浏览器请求转发给 services。如果数据不存在，service 抛出业务异常，route 转成 404。

### 5. services/

作用：执行真正的业务逻辑。

可以分成四类讲：

```text
template_service.py       模板增删改查
context_card_service.py   上下文卡片增删改查
history_service.py        生成历史保存和读取
generate_service.py       Prompt 组装核心逻辑
```

讲法：

> 大部分 service 都是标准 CRUD，也就是对 SQLite 执行 INSERT、SELECT、UPDATE、DELETE。比较核心的是 `generate_service.py`，它负责把模板变量和上下文卡片拼成最终 Prompt。

## 核心业务流程

### 新建模板流程

```text
页面填写模板
  ↓
POST /api/templates
  ↓
routes/templates.py
  ↓
template_service.create_template()
  ↓
INSERT INTO prompt_templates
  ↓
返回新模板数据
```

答辩讲法：

> 用户在页面新增模板后，前端会调用后端接口，后端通过 service 写入 SQLite。因为数据写入的是本地数据库文件，所以刷新或重启后仍然存在。

### 生成 Prompt 流程

```text
选择模板
  ↓
填写变量
  ↓
选择上下文卡片
  ↓
POST /api/generate
  ↓
读取模板和卡片
  ↓
替换 {变量}
  ↓
按卡片类型拼接
  ↓
返回 final_prompt
```

这是最适合重点讲的业务逻辑。

可以这样说：

> Prompt 生成不是调用大模型，而是先做规则拼接。系统读取模板内容，把 `{变量名}` 替换成用户输入，再把选中的上下文卡片按固定顺序追加到模板后面，最后得到一个完整 Prompt。

卡片顺序：

```text
background 背景资料
rule       写作规则
format     输出格式
example    参考示例
checklist  检查清单
```

## 关于 DeepSeek 调用

讲法建议简短：

> DeepSeek 是可选能力。项目的本地模板管理、上下文卡片管理、Prompt 组装都不依赖大模型。只有配置 `DEEPSEEK_API_KEY` 后，才会调用 DeepSeek 进行回答或 Prompt 优化。

如果老师追问：

> 我使用 OpenAI SDK 的兼容接口调用 DeepSeek，统一处理配置错误和请求错误。流式接口会把模型输出按文本片段返回给前端。

## 关于种子数据

讲法：

> `seed_test_data.py` 用于答辩前重建演示数据库，插入固定的模板和上下文卡片。它不是业务运行必须步骤，而是为了让演示环境可复现。

注意事项：

```text
python seed_test_data.py
```

这条命令会重建 `data/app.db`，所以会清空页面里手动新增的数据。平时使用时不运行它，页面新增的数据会保留。

## 代码简化说明

答辩时可以自然解释：

> 为了方便答辩展示，我保留了项目结构，但简化了后端内部逻辑。比如删除了历史版本数据库迁移、seed_key 幂等导入、旧数据兼容清理等代码，只保留当前系统需要的核心功能。

当前代码量：

```text
app/ 后端代码：约 876 行
原先 app/ 后端代码：约 1073 行
减少约 197 行
```

如果把演示数据脚本也算上：

```text
原先 app + seed_test_data.py：约 1781 行
现在 app + seed_test_data.py：约 1337 行
减少约 444 行
```

## 答辩时重点说什么

推荐主线：

```text
1. 项目是本地 Prompt 工作台
2. 后端用 FastAPI + SQLite
3. 数据分为模板、上下文卡片、生成历史三类
4. routes 负责接口，services 负责业务，database 负责数据库
5. 核心业务是把模板、变量和上下文卡片组装成最终 Prompt
6. DeepSeek 是可选扩展，不影响本地核心功能
```

## 老师可能问的问题

### Q1：新增模板后数据会不会保存？

会。新增模板会写入 SQLite 的 `data/app.db`。刷新页面、关闭页面、重启后端后数据仍然存在。

### Q2：为什么不用 MySQL？

因为项目定位是本地单机工具，SQLite 不需要单独安装数据库服务，更适合课程设计和本地演示。

### Q3：为什么不用 ORM？

项目规模较小，使用原生 sqlite3 可以减少依赖，也能更直观地展示 SQL 增删改查逻辑。

### Q4：Prompt 是怎么生成的？

先读取模板，用用户输入替换 `{变量}`，再按固定顺序追加上下文卡片，最后返回完整 Prompt。

### Q5：DeepSeek 是必须的吗？

不是。模板管理、卡片管理和 Prompt 组装都可以离线使用。DeepSeek 只是可选的 AI 回答和优化能力。

### Q6：为什么删除复杂迁移逻辑？

因为答辩展示使用当前版本数据库，不需要兼容历史旧表结构。删除迁移逻辑后，代码更短，讲解也更清楚。

## 最短口述版

如果时间很紧，可以直接这样讲：

> 我的后端使用 FastAPI 和 SQLite。FastAPI 提供接口，SQLite 保存模板、上下文卡片和生成历史。代码分为 routes、services、models 和 database 四部分。routes 负责 HTTP 请求，services 负责业务逻辑，models 负责数据校验，database 负责建表和连接。核心功能是根据用户选择的模板和上下文卡片，把 `{变量}` 替换成用户输入，再按背景、规则、格式、示例、检查清单的顺序拼接成最终 Prompt。DeepSeek 调用是可选扩展，不影响本地核心功能。
