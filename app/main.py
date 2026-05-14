from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes.context_cards import router as context_cards_router
from app.routes.generate import router as generate_router
from app.routes.history import router as history_router
from app.routes.llm import router as llm_router
from app.routes.templates import router as templates_router


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title="Prompt Studio API",
    description="Prompt 模板与上下文卡片管理系统后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(templates_router)
app.include_router(context_cards_router)
app.include_router(generate_router)
app.include_router(history_router)
app.include_router(llm_router)
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/")
def read_root() -> dict:
    return {
        "message": "Prompt Studio 后端服务已启动",
        "version": "0.1.0",
        "status": "ok",
    }


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}
