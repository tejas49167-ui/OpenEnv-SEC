from sec_openenv.framework import get_environment, list_environments


def test_framework_registry_lists_bundled_environment():
    environments = list_environments()
    assert len(environments) == 1
    assert environments[0].slug == "cyber-vulnerability-triage"


def test_framework_registry_returns_expected_entrypoint():
    descriptor = get_environment("cyber-vulnerability-triage")
    assert descriptor.server_entrypoint == "server.app:app"
