from fastapi import APIRouter, Query, status

from app.models.schemas import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)
from app.services.template_service import (
    create_template,
    delete_template,
    get_template_by_id,
    list_templates,
    update_template,
)


router = APIRouter(prefix="/api/templates", tags=["Prompt 模板"])


@router.get("", response_model=list[PromptTemplateResponse])
def list_template_items(
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[PromptTemplateResponse]:
    return list_templates(category=category, keyword=keyword, limit=limit, offset=offset)


@router.post("", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template_item(payload: PromptTemplateCreate) -> PromptTemplateResponse:
    return create_template(payload)


@router.get("/{template_id}", response_model=PromptTemplateResponse)
def get_template_item(template_id: int) -> PromptTemplateResponse:
    return get_template_by_id(template_id)


@router.put("/{template_id}", response_model=PromptTemplateResponse)
def update_template_item(
    template_id: int,
    payload: PromptTemplateUpdate,
) -> PromptTemplateResponse:
    return update_template(template_id, payload)


@router.delete("/{template_id}")
def delete_template_item(template_id: int) -> dict:
    delete_template(template_id)
    return {"success": True}
