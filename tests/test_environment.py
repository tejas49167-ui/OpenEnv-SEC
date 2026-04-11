from sec_openenv.environments.cyber_vulnerability_triage.environment import (
    CyberVulnerabilityTriageEnvironment,
)
from sec_openenv.environments.cyber_vulnerability_triage.models import Action
from sec_openenv.environments.log_anomaly.environment import LogAnomalyEnvironment
from sec_openenv.environments.log_anomaly.models import Action as LogAction


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


def test_repeated_investigation_action_adds_penalty_feedback():
    env = CyberVulnerabilityTriageEnvironment(task="easy")
    env.reset(task="easy", seed=0)
    env.step(Action(action_type="inspect_payload"))
    repeated = env.step(Action(action_type="inspect_payload"))
    assert repeated.done is False
    assert "already reviewed" in repeated.metadata["reward"]["feedback"]


def test_log_anomaly_environment_submit_verdict_ends_episode():
    env = LogAnomalyEnvironment(task="medium")
    observation = env.reset(task="medium", seed=0)
    assert observation.done is False

    env.step(LogAction(action_type="inspect_log"))
    final = env.step(
        LogAction(
            action_type="submit_triage",
            label="bruteforce",
            severity="medium",
            response_action="monitor",
            explanation="Repeated failed logins from one source look like brute force activity.",
        )
    )
    assert final.done is True
    assert final.metadata["reward"]["score"] > 0
