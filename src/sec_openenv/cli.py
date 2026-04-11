from __future__ import annotations

import argparse
import json
from typing import Any

import uvicorn

from sec_openenv.framework import get_environment, list_environments


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sec-openenv",
        description="CLI for the Sec-OpenEnv security environment framework.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List bundled environments.")

    info_parser = subparsers.add_parser("info", help="Show framework metadata for one environment.")
    info_parser.add_argument(
        "--environment",
        default="cyber-vulnerability-triage",
        help="Environment slug to inspect.",
    )

    serve_parser = subparsers.add_parser("serve", help="Run the bundled FastAPI server.")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)

    return parser


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    args = _build_parser().parse_args()

    if args.command == "list":
        _print_json([descriptor.__dict__ for descriptor in list_environments()])
        return

    if args.command == "info":
        _print_json(get_environment(args.environment).__dict__)
        return

    if args.command == "serve":
        uvicorn.run("server.app:app", host=args.host, port=args.port, factory=False)
        return

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
