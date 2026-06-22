import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_PROVIDERS: dict[str, dict[str, str | None]] = {
    "openai": {"base_url": "https://api.openai.com/v1", "api_key": os.getenv("OPENAI_API_KEY")},
    "groq": {"base_url": "https://api.groq.com/openai/v1", "api_key": os.getenv("GROQ_API_KEY")},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "api_key": os.getenv("OPENROUTER_API_KEY")},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "api_key": os.getenv("GEMINI_API_KEY")},
}


def _call_openai_compat(provider: str, model: str, messages: list[dict], **kwargs: Any) -> str:
    config = _PROVIDERS[provider]
    client = OpenAI(base_url=config["base_url"], api_key=config["api_key"])
    res = client.chat.completions.create(model=model, messages=messages, **kwargs)
    return res.choices[0].message.content or ""


def _call_anthropic(model: str, messages: list[dict], **kwargs: Any) -> str:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    system = None
    msgs = messages
    if messages and messages[0]["role"] == "system":
        system = messages[0]["content"]
        msgs = messages[1:]
    kwargs.setdefault("max_tokens", 4096)
    res = client.messages.create(model=model, messages=msgs, system=system, **kwargs)
    return res.content[0].text


_HANDLERS: dict[str, Any] = {
    "openai": lambda m, msg, **kw: _call_openai_compat("openai", m, msg, **kw),
    "groq": lambda m, msg, **kw: _call_openai_compat("groq", m, msg, **kw),
    "openrouter": lambda m, msg, **kw: _call_openai_compat("openrouter", m, msg, **kw),
    "gemini": lambda m, msg, **kw: _call_openai_compat("gemini", m, msg, **kw),
    "anthropic": _call_anthropic,
}


def llm(provider: str, model: str, messages: list[dict], **kwargs: Any) -> str:
    if provider not in _HANDLERS:
        raise ValueError(f"Unsupported provider '{provider}'. Choose from: {list(_HANDLERS)}")
    return _HANDLERS[provider](model, messages, **kwargs)
