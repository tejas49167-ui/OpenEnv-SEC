from __future__ import annotations

import argparse
import json
from typing import Any

import uvicorn

from sec_openenv.framework import create_environment, get_environment, list_environments


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sec-openenv",
        description="CLI for the Sec-OpenEnv security environment framework.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List bundled environments.")
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a table.",
    )

    info_parser = subparsers.add_parser("info", help="Show framework metadata for one environment.")
    info_parser.add_argument("--environment", default="cyber-vulnerability-triage")

    serve_parser = subparsers.add_parser("serve", help="Run the bundled FastAPI server.")
    serve_parser.add_argument(
        "--environment",
        default="cyber-vulnerability-triage",
        help="Environment slug to serve.",
    )
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)

    return parser


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _print_environment_table() -> None:
    descriptors = list_environments()
    headers = ("slug", "maturity", "domain", "server", "description")
    rows = [
        (
            descriptor.slug,
            descriptor.maturity,
            descriptor.domain,
            descriptor.server_entrypoint,
            descriptor.description,
        )
        for descriptor in descriptors
    ]
    widths = [
        max(len(header), *(len(str(row[index])) for row in rows))
        for index, header in enumerate(headers)
    ]

    def format_row(values: tuple[str, ...]) -> str:
        return "  ".join(str(value).ljust(widths[index]) for index, value in enumerate(values))

    print(format_row(headers))
    print(format_row(tuple("-" * width for width in widths)))
    for row in rows:
        print(format_row(row))


def main() -> None:
    args = _build_parser().parse_args()

    if args.command == "list":
        if args.json:
            _print_json([descriptor.to_dict() for descriptor in list_environments()])
        else:
            _print_environment_table()
        return

    if args.command == "info":
        descriptor = get_environment(args.environment)
        metadata = create_environment(args.environment).get_metadata()
        payload = descriptor.to_dict()
        payload["metadata"] = metadata.model_dump() if hasattr(metadata, "model_dump") else metadata
        _print_json(payload)
        return

    if args.command == "serve":
        descriptor = get_environment(args.environment)
        uvicorn.run(descriptor.load_server(), host=args.host, port=args.port, factory=False)
        return

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
