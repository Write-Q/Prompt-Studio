from fastapi import APIRouter, Query, status

from app.models.schemas import (
    ContextCardCreate,
    ContextCardRecommendRequest,
    ContextCardResponse,
    ContextCardType,
    ContextCardUpdate,
)
from app.services.context_card_service import (
    create_context_card,
    delete_context_card,
    get_context_card_by_id,
    list_context_cards,
    recommend_context_cards,
    update_context_card,
)


router = APIRouter(prefix="/api/context-cards", tags=["上下文卡片"])


@router.get("", response_model=list[ContextCardResponse])
def list_context_card_items(
    type: ContextCardType | None = Query(default=None),
    tag: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[ContextCardResponse]:
    return list_context_cards(type=type, tag=tag, keyword=keyword, limit=limit, offset=offset)


@router.post("", response_model=ContextCardResponse, status_code=status.HTTP_201_CREATED)
def create_context_card_item(payload: ContextCardCreate) -> ContextCardResponse:
    return create_context_card(payload)


@router.post("/recommend", response_model=list[ContextCardResponse])
def recommend_context_card_items(
    payload: ContextCardRecommendRequest,
) -> list[ContextCardResponse]:
    return recommend_context_cards(payload)


@router.get("/{card_id}", response_model=ContextCardResponse)
def get_context_card_item(card_id: int) -> ContextCardResponse:
    return get_context_card_by_id(card_id)


@router.put("/{card_id}", response_model=ContextCardResponse)
def update_context_card_item(card_id: int, payload: ContextCardUpdate) -> ContextCardResponse:
    return update_context_card(card_id, payload)


@router.delete("/{card_id}")
def delete_context_card_item(card_id: int) -> dict:
    delete_context_card(card_id)
    return {"success": True}
