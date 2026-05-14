import re

from app.models.schemas import CONTEXT_CARD_LABELS, ContextCardResponse, GenerateRequest, GenerateResponse
from app.services.context_card_service import get_context_card_by_id
from app.services.template_service import get_template_by_id


CARD_TYPE_ORDER = ["background", "rule", "format", "example", "checklist"]


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


def format_context_card(card: ContextCardResponse) -> str:
    return f"- {card.title}\n{card.content}"


def format_context_card_sections(cards: list[ContextCardResponse]) -> list[str]:
    sections: list[str] = []
    for card_type in CARD_TYPE_ORDER:
        blocks = [format_context_card(card) for card in cards if card.type == card_type]
        if blocks:
            sections.append(f"【{CONTEXT_CARD_LABELS[card_type]}】\n" + "\n\n".join(blocks))
    return sections


def build_prompt_by_rules(
    template_content: str,
    variables: dict[str, str],
    context_cards: list[ContextCardResponse] | None = None,
) -> str:
    prompt = render_template(template_content, variables)
    sections = format_context_card_sections(context_cards or [])
    return prompt if not sections else f"{prompt}\n\n" + "\n\n".join(sections)


def _find_missing_variables(template_content: str, variables: dict[str, str]) -> list[str]:
    return [
        name
        for name in extract_variables(template_content)
        if not str(variables.get(name, "")).strip()
    ]


def generate_prompt(payload: GenerateRequest) -> GenerateResponse:
    template = get_template_by_id(payload.template_id)
    cards = [get_context_card_by_id(card_id) for card_id in payload.context_card_ids]
    final_prompt = build_prompt_by_rules(template.content, payload.variables, cards)

    return GenerateResponse(
        template_id=payload.template_id,
        variables=payload.variables,
        context_card_ids=payload.context_card_ids,
        missing_variables=_find_missing_variables(template.content, payload.variables),
        final_prompt=final_prompt,
        mode=payload.mode,
        history_id=None,
    )
