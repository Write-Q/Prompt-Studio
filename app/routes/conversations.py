from fastapi import APIRouter

from app.models.schemas import ConversationMessage, ConversationSummary
from app.services.conversation_service import (
    delete_conversation,
    get_history,
    list_conversations,
)


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
def get_conversations() -> list[ConversationSummary]:
    return list_conversations()


@router.get("/{conversation_id}", response_model=list[ConversationMessage])
def get_conversation(conversation_id: str) -> list[ConversationMessage]:
    return get_history(conversation_id)


@router.delete("/{conversation_id}")
def remove_conversation(conversation_id: str) -> dict:
    return {"deleted": delete_conversation(conversation_id)}
