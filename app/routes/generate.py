from fastapi import APIRouter, HTTPException, status

from app.models.schemas import GenerateRequest, GenerateResponse
from app.services.generate_service import generate_prompt
from app.services.snippet_service import SnippetNotFoundError
from app.services.template_service import TemplateNotFoundError


router = APIRouter(
    prefix="/api",
    tags=["Prompt 生成"],
)


@router.post("/generate", response_model=GenerateResponse)
def generate_prompt_item(payload: GenerateRequest) -> GenerateResponse:
    """
    生成最终 Prompt。

    路由层只接收请求并调用生成服务，
    不直接处理模板替换、知识片段拼接或历史保存。
    """
    try:
        return generate_prompt(payload)
    except TemplateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except SnippetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
