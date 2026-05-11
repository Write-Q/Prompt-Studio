from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import LlmAnswerRequest, LlmAnswerResponse
from app.services.llm_service import (
    LlmConfigError,
    LlmRequestError,
    ask_deepseek,
    stream_deepseek_answer,
)


router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.post("/answer", response_model=LlmAnswerResponse)
def create_llm_answer(payload: LlmAnswerRequest) -> LlmAnswerResponse:
    """
    根据最终 Prompt 调用 DeepSeek 生成回答。

    路由层不直接拼接口参数，只把请求交给 llm_service。
    """
    try:
        return ask_deepseek(payload)
    except LlmConfigError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except LlmRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.post("/answer/stream")
def create_llm_answer_stream(payload: LlmAnswerRequest) -> StreamingResponse:
    """
    根据最终 Prompt 调用 DeepSeek，并流式返回回答文本。

    前端会一边接收一边写入文本框，用户能看到回答逐步出现。
    """
    try:
        answer_stream = stream_deepseek_answer(payload)
    except LlmConfigError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except LlmRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return StreamingResponse(
        answer_stream,
        media_type="text/plain; charset=utf-8",
    )
