from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    LlmAnswerRequest,
    LlmAnswerResponse,
    PromptOptimizeRequest,
    PromptOptimizeResponse,
)
from app.services.llm_service import (
    LlmConfigError,
    LlmRequestError,
    ask_deepseek,
    optimize_prompt,
    stream_deepseek_answer,
)


router = APIRouter(prefix="/api/llm", tags=["llm"])


def _raise_http_error(error: Exception) -> None:
    status_code = 400 if isinstance(error, LlmConfigError) else 502
    raise HTTPException(status_code=status_code, detail=str(error)) from error


@router.post("/answer", response_model=LlmAnswerResponse)
def create_llm_answer(payload: LlmAnswerRequest) -> LlmAnswerResponse:
    try:
        return ask_deepseek(payload)
    except (LlmConfigError, LlmRequestError) as error:
        _raise_http_error(error)


@router.post("/answer/stream")
def create_llm_answer_stream(payload: LlmAnswerRequest) -> StreamingResponse:
    try:
        answer_stream = stream_deepseek_answer(payload)
    except (LlmConfigError, LlmRequestError) as error:
        _raise_http_error(error)

    return StreamingResponse(answer_stream, media_type="text/plain; charset=utf-8")


@router.post("/optimize-prompt", response_model=PromptOptimizeResponse)
def create_prompt_optimization(payload: PromptOptimizeRequest) -> PromptOptimizeResponse:
    try:
        return optimize_prompt(payload)
    except (LlmConfigError, LlmRequestError) as error:
        _raise_http_error(error)
