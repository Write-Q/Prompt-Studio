from fastapi import APIRouter, Query, status

from app.models.schemas import GenerationHistoryCreate, GenerationHistoryResponse
from app.services.history_service import (
    create_history,
    delete_history,
    get_history_by_id,
    list_history,
)


router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[GenerationHistoryResponse])
def get_history_list(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[GenerationHistoryResponse]:
    return list_history(limit=limit)


@router.post("", response_model=GenerationHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_history_item(payload: GenerationHistoryCreate) -> GenerationHistoryResponse:
    return create_history(payload)


@router.post(
    "/",
    response_model=GenerationHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_history_item_with_slash(payload: GenerationHistoryCreate) -> GenerationHistoryResponse:
    return create_history_item(payload)


@router.get("/{history_id}", response_model=GenerationHistoryResponse)
def get_history_detail(history_id: int) -> GenerationHistoryResponse:
    return get_history_by_id(history_id)


@router.delete("/{history_id}")
def delete_history_item(history_id: int) -> dict:
    delete_history(history_id)
    return {"success": True}
