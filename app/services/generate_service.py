import json
import re

from app.database import get_connection
from app.models.schemas import GenerateRequest, GenerateResponse, KnowledgeSnippetResponse
from app.services.common import now_text
from app.services.snippet_service import get_snippet_by_id
from app.services.template_service import get_template_by_id


def extract_variables(template_content: str) -> list[str]:
    variables: list[str] = []
    for name in re.findall(r"\{([^{}\s]+)\}", template_content):
        if name not in variables:
            variables.append(name)
    return variables


def render_template(template_content: str, variables: dict[str, str]) -> str:
    final_text = template_content
    for name, value in variables.items():
        final_text = final_text.replace("{" + name + "}", str(value))
    return final_text


def format_snippet(snippet: KnowledgeSnippetResponse) -> str:
    return f"- {snippet.title}\n{snippet.content}"


def build_prompt_by_rules(
    template_content: str,
    variables: dict[str, str],
    knowledge_snippets: list[str] | None = None,
) -> str:
    prompt = render_template(template_content, variables)
    if not knowledge_snippets:
        return prompt

    snippet_text = "\n\n".join(knowledge_snippets)
    return f"{prompt}\n\n参考知识片段：\n{snippet_text}"


def _find_missing_variables(
    template_content: str,
    variables: dict[str, str],
) -> list[str]:
    return [
        name
        for name in extract_variables(template_content)
        if not str(variables.get(name, "")).strip()
    ]


def _save_generation_history(
    template_id: int,
    variables: dict[str, str],
    snippet_ids: list[int],
    final_prompt: str,
) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO generation_history (
                template_id, variables_json, snippet_ids, final_prompt, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                template_id,
                json.dumps(variables, ensure_ascii=False),
                json.dumps(snippet_ids, ensure_ascii=False),
                final_prompt,
                now_text(),
            ),
        )
        connection.commit()
        return cursor.lastrowid


def generate_prompt(payload: GenerateRequest) -> GenerateResponse:
    template = get_template_by_id(payload.template_id)
    snippets = [get_snippet_by_id(snippet_id) for snippet_id in payload.snippet_ids]
    snippet_blocks = [format_snippet(snippet) for snippet in snippets]

    final_prompt = build_prompt_by_rules(
        template_content=template.content,
        variables=payload.variables,
        knowledge_snippets=snippet_blocks,
    )
    missing_variables = _find_missing_variables(template.content, payload.variables)
    history_id = None

    if not missing_variables:
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
