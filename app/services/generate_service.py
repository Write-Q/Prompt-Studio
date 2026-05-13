import re

from app.models.schemas import GenerateRequest, GenerateResponse, KnowledgeSnippetResponse
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

    return GenerateResponse(
        template_id=payload.template_id,
        variables=payload.variables,
        snippet_ids=payload.snippet_ids,
        missing_variables=missing_variables,
        final_prompt=final_prompt,
        mode=payload.mode,
        history_id=None,
    )
