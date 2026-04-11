from __future__ import annotations

import asyncio

from client import CyberVulnerabilityTriageEnv


async def main() -> None:
    async with CyberVulnerabilityTriageEnv(base_url="http://localhost:8000") as env:
        result = await env.reset(task="hard")
        observation = result.observation
        print(f"request_id={observation.request_id} task={observation.task}")

        for action_name, action in [
            ("inspect_payload", env.inspect_payload),
            ("review_history", env.review_history),
            ("consult_playbook", env.consult_playbook),
        ]:
            result = await action()
            print(
                f"{action_name}: reward={result.reward} "
                f"evidence_items={len(result.observation.evidence_log)}"
            )


if __name__ == "__main__":
    asyncio.run(main())
