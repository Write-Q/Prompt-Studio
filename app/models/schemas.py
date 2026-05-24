from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ContextCardType = Literal["background", "rule", "format", "example", "checklist"]

CONTEXT_CARD_LABELS: dict[str, str] = {
    "background": "背景资料",
    "rule": "写作规则",
    "format": "输出格式",
    "example": "参考示例",
    "checklist": "检查清单",
}


def clean_required(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("字段内容不能为空")
    return cleaned


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


def normalize_tags(value: list[str] | str | None) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        value = value.replace("，", ",").replace("、", ",").split(",")
    return [tag.strip() for tag in value if tag.strip()]


class PromptTemplateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list)
    content: str = Field(..., min_length=1)
    description: str | None = None

    @field_validator("title", "content")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return clean_required(value)

    @field_validator("category", "description")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        return clean_optional(value)

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: list[str] | str | None) -> list[str]:
        return normalize_tags(value)


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(PromptTemplateBase):
    pass


class PromptTemplateResponse(PromptTemplateBase):
    id: int
    seed_key: str | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ContextCardBase(BaseModel):
    type: ContextCardType = Field(default="background")
    title: str = Field(..., min_length=1, max_length=100)
    tags: list[str] = Field(default_factory=list)
    content: str = Field(..., min_length=1)

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        return str(value).strip()

    @field_validator("title", "content")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return clean_required(value)

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: list[str] | str | None) -> list[str]:
        return normalize_tags(value)


class ContextCardCreate(ContextCardBase):
    pass


class ContextCardUpdate(ContextCardBase):
    pass


class ContextCardResponse(ContextCardBase):
    id: int
    seed_key: str | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class GenerateRequest(BaseModel):
    template_id: int
    variables: dict[str, str] = Field(default_factory=dict)
    context_card_ids: list[int] = Field(default_factory=list)
    mode: str = "rule"

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        if value != "rule":
            raise ValueError("当前阶段只支持 rule 规则拼接模式")
        return value


class GenerateResponse(BaseModel):
    template_id: int
    variables: dict[str, str]
    context_card_ids: list[int]
    missing_variables: list[str]
    final_prompt: str
    mode: str = "rule"
    history_id: int | None = None


class GenerationHistoryCreate(BaseModel):
    template_id: int
    variables: dict[str, str] = Field(default_factory=dict)
    context_card_ids: list[int] = Field(default_factory=list)
    final_prompt: str = Field(..., min_length=1)

    @field_validator("final_prompt")
    @classmethod
    def validate_final_prompt(cls, value: str) -> str:
        return clean_required(value)


class GenerationHistoryResponse(BaseModel):
    id: int
    template_id: int
    variables: dict[str, str]
    context_card_ids: list[int]
    final_prompt: str
    created_at: str


class LlmAnswerRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str = "deepseek-v4-flash"
    temperature: float = Field(default=0.7, ge=0, le=2)

    @field_validator("prompt", "model")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return clean_required(value)


class LlmAnswerResponse(BaseModel):
    model: str
    answer: str


class PromptOptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str = "deepseek-v4-flash"
    temperature: float = Field(default=0.2, ge=0, le=2)

    @field_validator("prompt", "model")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return clean_required(value)


class PromptOptimizeResponse(BaseModel):
    model: str
    optimized_prompt: str
