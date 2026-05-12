import json
from datetime import datetime


def now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def serialize_tags(tags: list[str]) -> str:
    return json.dumps(tags, ensure_ascii=False)


def deserialize_tags(tags_text: str | None) -> list[str]:
    if not tags_text:
        return []

    try:
        parsed = json.loads(tags_text)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, list):
        return [str(tag).strip() for tag in parsed if str(tag).strip()]

    return [tag.strip() for tag in tags_text.replace("，", ",").split(",") if tag.strip()]
