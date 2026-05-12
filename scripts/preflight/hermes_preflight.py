"""CLI for Hermes workstation preflight readiness checks."""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import socket
import subprocess
import sys
from typing import Any

from .checks import build_report, parse_probe_output
from .render import render_json, render_markdown, write_artifacts


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "config" / "workstations" / "registry.yaml"
DEFAULT_ARTIFACTS = REPO_ROOT / "docs" / "reports" / "preflight"
PROBE_TEMPLATE = Path(__file__).with_name("probe.sh.tmpl")


def _load_registry(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - project dependency
        raise SystemExit("PyYAML is required to parse workstation registry") from exc
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _resolve_target(target: str, registry_path: Path) -> dict[str, Any]:
    registry = _load_registry(registry_path)
    machines = registry.get("machines", {})
    for name, machine in machines.items():
        ids = {name, machine.get("hostname"), *(machine.get("hostname_aliases") or [])}
        if target in ids:
            return {"name": name, **machine}
    return {
        "name": target,
        "hostname": target,
        "role": "secondary-dev",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
        "ssh": target,
        "capabilities": {},
    }


def _quote_probe(workspace_root: str) -> str:
    template = PROBE_TEMPLATE.read_text(encoding="utf-8")
    return f"WORKSPACE_ROOT={shlex.quote(workspace_root)}\n{template}"


def _run_probe(target: dict[str, Any], timeout: int) -> tuple[str, dict[str, Any]]:
    hostname = str(target.get("hostname") or target["name"])
    local_host = socket.gethostname().split(".", 1)[0]
    aliases = {hostname, target.get("name"), *(target.get("hostname_aliases") or [])}
    workspace_root = str(target.get("workspace_root") or "/mnt/local-analysis/workspace-hub")
    script = _quote_probe(workspace_root)

    if local_host in aliases:
        completed = subprocess.run(
            ["bash", "-lc", script],
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        mode = "local"
    else:
        ssh_target = target.get("ssh") or hostname
        completed = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                f"ConnectTimeout={timeout}",
                str(ssh_target),
                f"bash -lc {shlex.quote(script)}",
            ],
            text=True,
            capture_output=True,
            timeout=timeout + 2,
            check=False,
        )
        mode = "remote"

    output = completed.stdout
    if completed.returncode != 0 and not output:
        output = (
            "PREFLIGHT_PROBE_V1\n"
            f"hostname={hostname}\n"
            f"workspace_root={workspace_root}\n"
            "workspace_exists=false\n"
            "disk_free_gb=0\n"
        )
    return output, {
        "mode": mode,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip()[:2000],
    }


def _exit_code(report: dict, strict: bool) -> int:
    summary = report["summary"]
    if summary["block"]:
        return 2
    if strict and summary["warn"]:
        return 1
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a Hermes workstation preflight readiness check."
    )
    parser.add_argument("--target", help="Registry machine, hostname, or SSH target")
    parser.add_argument("--remote", help="Raw SSH target; equivalent to --target with forced remote dispatch")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--fixture", type=Path, help="Parse a saved probe fixture instead of running SSH/local checks")
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--no-artifacts", action="store_true", help="Do not write JSON/Markdown report files")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown instead of JSON")
    parser.add_argument("--json", action="store_true", help="Print JSON (default)")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on warnings and 2 on blockers")
    parser.add_argument("--no-engineering-smoke", action="store_true", help="Reserved compatibility flag; probe only checks tools present on PATH")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    target_name = args.remote or args.target
    if not target_name:
        raise SystemExit("--target or --remote is required")
    target = _resolve_target(target_name, args.registry)
    if args.remote:
        target["ssh"] = args.remote
        target["hostname"] = args.remote
    from_host = socket.gethostname().split(".", 1)[0]

    if args.fixture:
        raw = args.fixture.read_text(encoding="utf-8")
        invocation = {"mode": "fixture", "fixture": str(args.fixture)}
    else:
        raw, invocation = _run_probe(target, args.timeout)

    probe = parse_probe_output(raw)
    report = build_report(probe, target=target, from_host=from_host, invocation=invocation)
    if not args.no_artifacts:
        artifacts = write_artifacts(report, args.artifacts_dir)
        report["artifacts"] = {key: str(path) for key, path in artifacts.items()}

    if args.markdown:
        sys.stdout.write(render_markdown(report))
    else:
        sys.stdout.write(render_json(report))
    return _exit_code(report, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
