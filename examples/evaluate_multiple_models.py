"""Compare models via ``evaluate_models`` (requires API credentials).

Environment variables (any one auth path):

- ``OPENAI_API_KEY`` or ``HF_TOKEN`` — API key
- ``OPENAI_BASE_URL`` or ``API_BASE_URL`` — optional custom API base (e.g. Hugging Face router)

Install the LLM extra when using OpenAI-compatible APIs: ``pip install 'sec-openenv[llm]'``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sec_openenv import evaluate_models


if __name__ == "__main__":
    results = evaluate_models(
        "cyber-vulnerability-triage",
        ["gpt-4o-mini", "gpt-4.1-mini"],
        task="hard",
        episodes=2,
    )
    print(json.dumps(results, indent=2))
