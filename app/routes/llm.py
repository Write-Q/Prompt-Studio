from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    LlmAnswerRequest,
    LlmChatRequest,
    LlmChatResponse,
    PromptOptimizeRequest,
    PromptOptimizeResponse,
)
from app.services.llm_service import (
    chat_with_tools,
    optimize_prompt,
    stream_chat_with_tools,
    stream_deepseek_answer,
)


router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.post("/answer/stream")
def create_llm_answer_stream(payload: LlmAnswerRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_deepseek_answer(payload),
        media_type="text/plain; charset=utf-8",
    )


@router.post("/optimize-prompt", response_model=PromptOptimizeResponse)
def create_prompt_optimization(payload: PromptOptimizeRequest) -> PromptOptimizeResponse:
    return optimize_prompt(payload)


@router.post("/chat", response_model=LlmChatResponse)
def create_llm_chat(payload: LlmChatRequest) -> LlmChatResponse:
    return chat_with_tools(payload)


@router.post("/chat/stream")
def create_llm_chat_stream(payload: LlmChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_chat_with_tools(payload),
        media_type="application/x-ndjson; charset=utf-8",
    )
