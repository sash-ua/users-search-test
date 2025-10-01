import os
from typing import Tuple


def load_env() -> Tuple[str, str | None]:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY in environment. Create a .env with OPENAI_API_KEY=..."
        )
    return api_key, base_url
