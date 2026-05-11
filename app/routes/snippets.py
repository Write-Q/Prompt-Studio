from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import (
    KnowledgeSnippetCreate,
    KnowledgeSnippetResponse,
    KnowledgeSnippetUpdate,
)
from app.services.snippet_service import (
    SnippetNotFoundError,
    create_snippet,
    delete_snippet,
    get_snippet_by_id,
    list_snippets,
    update_snippet,
)


router = APIRouter(
    prefix="/api/snippets",
    tags=["知识片段"],
)


def _raise_snippet_not_found(error: SnippetNotFoundError) -> None:
    """
    把服务层的“知识片段不存在”异常转换成 HTTP 404。
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(error),
    ) from error


@router.get("", response_model=list[KnowledgeSnippetResponse])
def list_snippet_items(
    tag: str | None = Query(default=None, description="按标签筛选"),
    keyword: str | None = Query(default=None, description="按标题、内容、来源或标签搜索"),
) -> list[KnowledgeSnippetResponse]:
    """
    获取知识片段列表。

    路由层只接收查询参数，实际查询交给服务层完成。
    """
    return list_snippets(tag=tag, keyword=keyword)


@router.post(
    "",
    response_model=KnowledgeSnippetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_snippet_item(payload: KnowledgeSnippetCreate) -> KnowledgeSnippetResponse:
    """
    新增知识片段。
    """
    return create_snippet(payload)


@router.get("/{snippet_id}", response_model=KnowledgeSnippetResponse)
def get_snippet_item(snippet_id: int) -> KnowledgeSnippetResponse:
    """
    根据 id 获取知识片段详情。
    """
    try:
        return get_snippet_by_id(snippet_id)
    except SnippetNotFoundError as error:
        _raise_snippet_not_found(error)


@router.put("/{snippet_id}", response_model=KnowledgeSnippetResponse)
def update_snippet_item(
    snippet_id: int,
    payload: KnowledgeSnippetUpdate,
) -> KnowledgeSnippetResponse:
    """
    更新指定知识片段。
    """
    try:
        return update_snippet(snippet_id, payload)
    except SnippetNotFoundError as error:
        _raise_snippet_not_found(error)


@router.delete("/{snippet_id}")
def delete_snippet_item(snippet_id: int) -> dict:
    """
    删除指定知识片段。
    """
    try:
        delete_snippet(snippet_id)
    except SnippetNotFoundError as error:
        _raise_snippet_not_found(error)

    return {"success": True}
