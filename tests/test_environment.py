from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import Action


def test_reset_with_seed_is_reproducible():
    env = CyberVulnerabilityTriageEnvironment(task="easy")
    first = env.reset(task="easy", seed=7)
    second = env.reset(task="easy", seed=7)
    assert first.request_id == second.request_id
    assert first.service == second.service
    assert first.triage_priority == second.triage_priority


def test_step_populates_reward_metadata():
    env = CyberVulnerabilityTriageEnvironment(task="medium")
    env.reset(task="medium", seed=1)
    observation = env.step(Action(action_type="inspect_payload"))
    assert observation.done is False
    assert observation.reward is not None
    assert "reward" in observation.metadata
    assert "info" in observation.metadata


def test_submit_triage_ends_episode():
    env = CyberVulnerabilityTriageEnvironment(task="easy")
    env.reset(task="easy", seed=0)
    observation = env.step(
        Action(
            action_type="submit_triage",
            vulnerability_type="xss",
            severity="medium",
            response_action="block",
            explanation="Detected reflected script injection in request payload.",
        )
    )
    assert observation.done is True
    assert observation.metadata["reward"]["score"] > 0
