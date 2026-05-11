from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes.generate import router as generate_router
from app.routes.history import router as history_router
from app.routes.llm import router as llm_router
from app.routes.snippets import router as snippets_router
from app.routes.templates import router as templates_router


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    应用生命周期管理。

    服务启动时先初始化数据库表结构，
    后续如果有更多启动前准备工作，也可以继续放在这里。
    """
    init_db()
    yield


# 创建 FastAPI 应用实例
# 这是整个后端服务的入口，后续数据库初始化、路由注册都会挂载到这里
app = FastAPI(
    title="Prompt Studio API",
    description="Prompt 模板与知识片段管理系统后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

# 注册 Prompt 模板相关接口
app.include_router(templates_router)

# 注册知识片段相关接口
app.include_router(snippets_router)

# 注册 Prompt 生成相关接口
app.include_router(generate_router)

# 注册生成历史相关接口
app.include_router(history_router)

# 注册大模型回答相关接口
app.include_router(llm_router)

# 托管前端页面，访问地址：http://127.0.0.1:8000/app/
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/")
def read_root() -> dict:
    """
    根路径接口。
    现在先用于确认服务是否成功启动，后续也可以扩展成系统首页说明接口。
    """
    return {
        "message": "Prompt Studio 后端服务已启动",
        "version": "0.1.0",
        "status": "ok",
    }


@app.get("/health")
def health_check() -> dict:
    """
    健康检查接口。
    这个接口通常用于最简单地确认服务进程是否可用。
    """
    return {"status": "healthy"}
