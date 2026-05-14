from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import ContextCardCreate, ContextCardResponse, ContextCardType, ContextCardUpdate
from app.services.context_card_service import (
    ContextCardNotFoundError,
    create_context_card,
    delete_context_card,
    get_context_card_by_id,
    list_context_cards,
    update_context_card,
)


router = APIRouter(prefix="/api/context-cards", tags=["上下文卡片"])


def _raise_card_not_found(error: ContextCardNotFoundError) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get("", response_model=list[ContextCardResponse])
def list_context_card_items(
    type: ContextCardType | None = Query(default=None),
    tag: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
) -> list[ContextCardResponse]:
    return list_context_cards(type=type, tag=tag, keyword=keyword)


@router.post("", response_model=ContextCardResponse, status_code=status.HTTP_201_CREATED)
def create_context_card_item(payload: ContextCardCreate) -> ContextCardResponse:
    return create_context_card(payload)


@router.get("/{card_id}", response_model=ContextCardResponse)
def get_context_card_item(card_id: int) -> ContextCardResponse:
    try:
        return get_context_card_by_id(card_id)
    except ContextCardNotFoundError as error:
        _raise_card_not_found(error)


@router.put("/{card_id}", response_model=ContextCardResponse)
def update_context_card_item(card_id: int, payload: ContextCardUpdate) -> ContextCardResponse:
    try:
        return update_context_card(card_id, payload)
    except ContextCardNotFoundError as error:
        _raise_card_not_found(error)


@router.delete("/{card_id}")
def delete_context_card_item(card_id: int) -> dict:
    try:
        delete_context_card(card_id)
    except ContextCardNotFoundError as error:
        _raise_card_not_found(error)

    return {"success": True}
