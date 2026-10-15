from typing import Any

from litellm import completion

from app.config import get_settings


def complete_chat(messages: list[dict[str, str]], model: str | None = None) -> str:
    settings = get_settings()
    response: Any = completion(
        model=model or settings.llm_model,
        messages=messages,
    )
    content = response.choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("The configured LLM returned an empty or non-text response.")
    return content.strip()
