from datetime import date, datetime
from typing import Any

import yaml


def parse_document(content: str) -> tuple[dict[str, Any], str]:
    """Read optional YAML front matter and return serializable tags plus body text."""
    if not content.startswith("---"):
        return {}, content.strip()

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content.strip()
    try:
        closing_index = next(
            index for index in range(1, len(lines)) if lines[index].strip() == "---"
        )
    except StopIteration:
        raise ValueError("YAML front matter is missing its closing '---' delimiter.")

    try:
        parsed = yaml.safe_load("\n".join(lines[1:closing_index])) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML front matter: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("YAML front matter must contain a mapping of metadata fields.")
    metadata = _json_safe(parsed)
    body = "\n".join(lines[closing_index + 1 :]).strip()
    return metadata, body


def _json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value
