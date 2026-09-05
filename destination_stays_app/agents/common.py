from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL")


def agent_model_kwargs() -> dict[str, str]:
    # If OPENAI_MODEL is omitted, let the Agents SDK use its configured default.
    return {"model": MODEL} if MODEL else {}
