from fastapi import APIRouter, HTTPException, status

from app.models.schemas import GenerateRequest, GenerateResponse
from app.services.context_card_service import ContextCardNotFoundError
from app.services.generate_service import generate_prompt
from app.services.template_service import TemplateNotFoundError


router = APIRouter(prefix="/api", tags=["Prompt 生成"])


@router.post("/generate", response_model=GenerateResponse)
def generate_prompt_item(payload: GenerateRequest) -> GenerateResponse:
    try:
        return generate_prompt(payload)
    except TemplateNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ContextCardNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
