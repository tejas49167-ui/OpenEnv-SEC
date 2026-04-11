from __future__ import annotations

import sys

import sec_openenv.cli as cli


def test_cli_serve_uses_registry_server_entrypoint(monkeypatch):
    captured: dict[str, object] = {}

    def fake_run(app, host, port, factory):
        captured["app"] = app
        captured["host"] = host
        captured["port"] = port
        captured["factory"] = factory

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        ["sec-openenv", "serve", "--environment", "log-anomaly", "--port", "9001"],
    )

    cli.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 9001
    assert captured["factory"] is False
    assert callable(captured["app"])
