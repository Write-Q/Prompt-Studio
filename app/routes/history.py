from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import GenerationHistoryResponse
from app.services.history_service import (
    HistoryNotFoundError,
    delete_history,
    get_history_by_id,
    list_history,
)


router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[GenerationHistoryResponse])
def get_history_list(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[GenerationHistoryResponse]:
    """
    获取生成历史列表。

    路由层只接收参数，并调用 service 层完成真实查询。
    """
    return list_history(limit=limit)


@router.get("/{history_id}", response_model=GenerationHistoryResponse)
def get_history_detail(history_id: int) -> GenerationHistoryResponse:
    """
    获取单条生成历史详情。
    """
    try:
        return get_history_by_id(history_id)
    except HistoryNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/{history_id}")
def delete_history_item(history_id: int) -> dict:
    """
    删除单条生成历史。
    """
    try:
        delete_history(history_id)
        return {"success": True}
    except HistoryNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
