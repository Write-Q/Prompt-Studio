import json
import re
from datetime import datetime

from app.database import get_connection
from app.models.schemas import GenerateRequest, GenerateResponse
from app.services.snippet_service import get_snippet_by_id
from app.services.template_service import get_template_by_id


def extract_variables(template_content: str) -> list[str]:
    """
    从模板正文中提取变量名。

    示例：
    "请用{语气}总结：{输入内容}"
    会提取出：
    ["语气", "输入内容"]

    如果同一个变量重复出现，只保留第一次出现的位置。
    """
    variables: list[str] = []

    # 找出所有 {变量名} 里的变量名，变量名可以是中文
    for variable_name in re.findall(r"\{([^{}\s]+)\}", template_content):
        if variable_name in variables:
            continue

        variables.append(variable_name)

    return variables


def render_template(
    template_content: str,
    variables: dict[str, str],
) -> str:
    """
    根据变量值渲染模板正文。

    当前采用最基础的规则替换：
    - 模板里出现 {变量名}
    - 就用 variables 字典里的对应值替换
    - 如果某个变量没有提供值，就保留原占位符
    """
    final_text = template_content

    for variable_name, variable_value in variables.items():
        placeholder = "{" + variable_name + "}"
        final_text = final_text.replace(placeholder, str(variable_value))

    return final_text


def build_prompt_by_rules(
    template_content: str,
    variables: dict[str, str],
    knowledge_snippets: list[str] | None = None,
) -> str:
    """
    按规则拼接最终 Prompt。

    当前第一版规则很简单：
    1. 先把用户填写的变量替换进模板
    2. 如果选择了知识片段，就追加到最终 Prompt 后面

    这里不调用大模型，只做稳定、可调试的规则拼接。
    """
    rendered_prompt = render_template(template_content, variables)

    if not knowledge_snippets:
        return rendered_prompt

    snippet_text = "\n\n".join(knowledge_snippets)

    return (
        f"{rendered_prompt}\n\n"
        "参考知识片段：\n"
        f"{snippet_text}"
    )


def _get_current_time_text() -> str:
    """
    生成当前时间文本。
    """
    return datetime.now().isoformat(timespec="seconds")


def _find_missing_variables(
    template_content: str,
    variables: dict[str, str],
) -> list[str]:
    """
    找出模板中存在、但用户没有填写的变量。

    当前不阻止生成，只把缺失变量返回给前端，
    方便用户在页面上看到哪里还没填。
    """
    expected_variables = extract_variables(template_content)
    missing_variables: list[str] = []

    for variable_name in expected_variables:
        variable_value = variables.get(variable_name)
        if variable_value is None or str(variable_value).strip() == "":
            missing_variables.append(variable_name)

    return missing_variables


def _save_generation_history(
    template_id: int,
    variables: dict[str, str],
    snippet_ids: list[int],
    final_prompt: str,
) -> int:
    """
    保存生成历史记录。

    历史查看接口后续再单独做，
    当前先把生成结果写入 generation_history 表。
    """
    current_time = _get_current_time_text()

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO generation_history (
                template_id,
                variables_json,
                snippet_ids,
                final_prompt,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                template_id,
                json.dumps(variables, ensure_ascii=False),
                json.dumps(snippet_ids, ensure_ascii=False),
                final_prompt,
                current_time,
            ),
        )
        connection.commit()
        history_id = cursor.lastrowid

    return history_id


def generate_prompt(payload: GenerateRequest) -> GenerateResponse:
    """
    执行一次 Prompt 生成。

    当前流程：
    1. 根据 template_id 查询模板
    2. 根据 snippet_ids 查询知识片段
    3. 使用 rule 模式生成最终 Prompt
    4. 保存生成历史
    5. 返回最终结果
    """
    template = get_template_by_id(payload.template_id)
    snippets = [get_snippet_by_id(snippet_id) for snippet_id in payload.snippet_ids]
    snippet_contents = [snippet.content for snippet in snippets]

    final_prompt = build_prompt_by_rules(
        template_content=template.content,
        variables=payload.variables,
        knowledge_snippets=snippet_contents,
    )
    missing_variables = _find_missing_variables(template.content, payload.variables)
    history_id = _save_generation_history(
        template_id=payload.template_id,
        variables=payload.variables,
        snippet_ids=payload.snippet_ids,
        final_prompt=final_prompt,
    )

    return GenerateResponse(
        template_id=payload.template_id,
        variables=payload.variables,
        snippet_ids=payload.snippet_ids,
        missing_variables=missing_variables,
        final_prompt=final_prompt,
        mode=payload.mode,
        history_id=history_id,
    )
