from fastapi import APIRouter

from app.models.schemas import GenerateRequest, GenerateResponse
from app.services.generate_service import generate_prompt


router = APIRouter(prefix="/api", tags=["Prompt 生成"])


@router.post("/generate", response_model=GenerateResponse)
def generate_prompt_item(payload: GenerateRequest) -> GenerateResponse:
    return generate_prompt(payload)
