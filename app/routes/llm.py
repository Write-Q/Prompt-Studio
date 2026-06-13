from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    LlmAnswerRequest,
    PromptOptimizeRequest,
    PromptOptimizeResponse,
)
from app.services.llm_service import optimize_prompt, stream_deepseek_answer


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
