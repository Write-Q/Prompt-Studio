from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromptTemplateBase(BaseModel):
    """
    Prompt 模板公共字段。

    当前阶段先只放模板管理相关的 schema，
    后续再逐步补充知识片段、生成历史等数据结构。
    """

    title: str = Field(..., min_length=1, max_length=100, description="模板标题")
    category: str | None = Field(default=None, max_length=50, description="模板分类")
    tags: list[str] = Field(default_factory=list, description="模板标签列表")
    content: str = Field(..., min_length=1, description="模板正文内容")
    description: str | None = Field(default=None, description="模板说明")

    @field_validator("title", "content")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """
        清理必填文本字段。

        这里会去掉首尾空格，并阻止只输入空白字符的情况。
        """
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("字段内容不能为空")
        return cleaned_value

    @field_validator("category", "description")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        """
        清理可选文本字段。

        如果用户只输入空格，就统一转成 None，
        这样数据库层和接口层更容易保持一致。
        """
        if value is None:
            return None

        cleaned_value = value.strip()
        return cleaned_value or None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: list[str] | str | None) -> list[str]:
        """
        统一标签输入格式。

        当前先兼容两种输入：
        1. ["写作", "总结"]
        2. "写作, 总结"
        """
        if value is None or value == "":
            return []

        if isinstance(value, str):
            # 同时兼容英文逗号和中文逗号
            raw_tags = value.replace("，", ",").split(",")
            return [tag.strip() for tag in raw_tags if tag.strip()]

        return [tag.strip() for tag in value if tag.strip()]


class PromptTemplateCreate(PromptTemplateBase):
    """
    新增模板请求体。

    现在先直接复用公共字段，后续如果创建逻辑有额外字段，
    再单独在这里扩展。
    """


class PromptTemplateUpdate(PromptTemplateBase):
    """
    编辑模板请求体。

    当前项目的更新接口准备按“整条更新”的思路处理，
    所以这里先与创建结构保持一致。
    """


class PromptTemplateResponse(PromptTemplateBase):
    """
    模板响应体。

    相比请求体，响应体会多出数据库生成的 id 和时间字段。
    """

    id: int
    created_at: str
    updated_at: str

    # 允许后续直接从对象或字典转换成响应模型
    model_config = ConfigDict(from_attributes=True)


class KnowledgeSnippetBase(BaseModel):
    """
    知识片段公共字段。

    知识片段用于保存可复用的背景资料、写作规范、项目说明等内容。
    """

    title: str = Field(..., min_length=1, max_length=100, description="片段标题")
    tags: list[str] = Field(default_factory=list, description="片段标签列表")
    content: str = Field(..., min_length=1, description="片段正文内容")
    source: str | None = Field(default=None, description="片段来源")

    @field_validator("title", "content")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """
        清理必填文本字段。

        标题和正文不允许只输入空格。
        """
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("字段内容不能为空")
        return cleaned_value

    @field_validator("source")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        """
        清理可选文本字段。

        如果来源只输入空格，就统一转成 None。
        """
        if value is None:
            return None

        cleaned_value = value.strip()
        return cleaned_value or None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: list[str] | str | None) -> list[str]:
        """
        统一标签输入格式。

        兼容数组输入和逗号分隔字符串输入。
        """
        if value is None or value == "":
            return []

        if isinstance(value, str):
            raw_tags = value.replace("，", ",").split(",")
            return [tag.strip() for tag in raw_tags if tag.strip()]

        return [tag.strip() for tag in value if tag.strip()]


class KnowledgeSnippetCreate(KnowledgeSnippetBase):
    """
    新增知识片段请求体。
    """


class KnowledgeSnippetUpdate(KnowledgeSnippetBase):
    """
    编辑知识片段请求体。

    当前也采用整条更新方式，要求提交完整字段。
    """


class KnowledgeSnippetResponse(KnowledgeSnippetBase):
    """
    知识片段响应体。

    相比请求体，多出数据库生成的 id 和时间字段。
    """

    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class GenerateRequest(BaseModel):
    """
    生成 Prompt 的请求体。

    当前只支持 rule 规则拼接模式，
    后续如果要扩展 llm 模式，可以继续复用 mode 字段。
    """

    template_id: int = Field(..., description="要使用的模板 ID")
    variables: dict[str, str] = Field(default_factory=dict, description="模板变量值")
    snippet_ids: list[int] = Field(default_factory=list, description="参与拼接的知识片段 ID 列表")
    mode: str = Field(default="rule", description="生成模式，当前只支持 rule")

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        """
        当前阶段只允许规则拼接。
        """
        if value != "rule":
            raise ValueError("当前阶段只支持 rule 规则拼接模式")
        return value


class GenerateResponse(BaseModel):
    """
    生成 Prompt 的响应体。
    """

    template_id: int
    variables: dict[str, str]
    snippet_ids: list[int]
    missing_variables: list[str]
    final_prompt: str
    mode: str = "rule"
    history_id: int | None = None


class GenerationHistoryResponse(BaseModel):
    """
    生成历史响应体。

    历史记录是系统复盘和再次使用 Prompt 的入口，
    所以这里把保存时的变量、知识片段 ID 和最终 Prompt 都返回给前端。
    """

    id: int
    template_id: int
    variables: dict[str, str]
    snippet_ids: list[int]
    final_prompt: str
    created_at: str


class LlmAnswerRequest(BaseModel):
    """
    大模型回答请求体。

    当前只负责把最终 Prompt 发给 DeepSeek，
    API Key 从后端环境变量读取，不从前端传入，避免泄露。
    """

    prompt: str = Field(..., min_length=1, description="要发送给大模型的最终 Prompt")
    model: str = Field(default="deepseek-v4-flash", description="DeepSeek 模型名称")
    temperature: float = Field(default=0.7, ge=0, le=2, description="生成随机性")

    @field_validator("prompt", "model")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """
        清理必填文本字段，避免提交空字符串。
        """
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("字段内容不能为空")
        return cleaned_value


class LlmAnswerResponse(BaseModel):
    """
    大模型回答响应体。
    """

    model: str
    answer: str


class PromptOptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str = Field(default="deepseek-v4-flash")
    temperature: float = Field(default=0.2, ge=0, le=2)

    @field_validator("prompt", "model")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("字段内容不能为空")
        return cleaned_value


class PromptOptimizeResponse(BaseModel):
    model: str
    optimized_prompt: str
