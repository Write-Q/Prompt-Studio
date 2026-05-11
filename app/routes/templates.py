from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)
from app.services.template_service import (
    TemplateNotFoundError,
    create_template,
    delete_template,
    get_template_by_id,
    list_templates,
    update_template,
)


router = APIRouter(
    prefix="/api/templates",
    tags=["Prompt 模板"],
)


def _raise_template_not_found(error: TemplateNotFoundError) -> None:
    """
    把服务层的“模板不存在”异常转换成 HTTP 404。

    服务层不直接处理 HTTP 状态码，
    路由层负责把业务异常转换成接口响应。
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(error),
    ) from error


@router.get("", response_model=list[PromptTemplateResponse])
def list_template_items(
    category: str | None = Query(default=None, description="按模板分类筛选"),
    keyword: str | None = Query(default=None, description="按标题、内容、说明或标签搜索"),
) -> list[PromptTemplateResponse]:
    """
    获取模板列表。

    这里不直接写 SQL，
    只接收查询参数并调用服务层完成实际查询。
    """
    return list_templates(category=category, keyword=keyword)


@router.post(
    "",
    response_model=PromptTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_template_item(payload: PromptTemplateCreate) -> PromptTemplateResponse:
    """
    新增 Prompt 模板。
    """
    return create_template(payload)


@router.get("/{template_id}", response_model=PromptTemplateResponse)
def get_template_item(template_id: int) -> PromptTemplateResponse:
    """
    根据 id 获取模板详情。
    """
    try:
        return get_template_by_id(template_id)
    except TemplateNotFoundError as error:
        _raise_template_not_found(error)


@router.put("/{template_id}", response_model=PromptTemplateResponse)
def update_template_item(
    template_id: int,
    payload: PromptTemplateUpdate,
) -> PromptTemplateResponse:
    """
    更新指定模板。
    """
    try:
        return update_template(template_id, payload)
    except TemplateNotFoundError as error:
        _raise_template_not_found(error)


@router.delete("/{template_id}")
def delete_template_item(template_id: int) -> dict:
    """
    删除指定模板。
    """
    try:
        delete_template(template_id)
    except TemplateNotFoundError as error:
        _raise_template_not_found(error)

    return {"success": True}
