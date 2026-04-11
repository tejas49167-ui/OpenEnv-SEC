from sec_openenv import run_episode
from sec_openenv.framework import get_environment, list_environments
from sec_openenv.framework.registry import create_environment


def test_framework_registry_lists_registered_environments():
    environments = list_environments()
    assert [environment.slug for environment in environments] == [
        "cyber-vulnerability-triage",
        "log-anomaly",
    ]


def test_framework_registry_returns_expected_server_entrypoint():
    descriptor = get_environment("cyber-vulnerability-triage")
    assert (
        descriptor.server_entrypoint
        == "sec_openenv.environments.cyber_vulnerability_triage.server:app"
    )


def test_framework_registry_can_create_log_anomaly_environment():
    environment = create_environment("log-anomaly", task="screen")
    observation = environment.reset(task="screen", seed=1)
    assert observation.event_id.startswith("LOG-")
    assert "submit_triage" in observation.available_action_types


def test_run_episode_supports_new_environment_registry_flow():
    trace = run_episode("log-anomaly", task="screen", seed=0)
    assert trace.environment == "log-anomaly"
    assert trace.steps >= 1
