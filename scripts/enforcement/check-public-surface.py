#!/usr/bin/env python3
"""Scan PR added lines for public-surface IP, secret, hostname, and identifier leaks."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALLOWLIST = REPO_ROOT / "config" / "public-surface-allowlist.yml"
DEFAULT_HOST_DENYLIST = REPO_ROOT / "config" / "public-surface-host-denylist.txt"
DEFAULT_CLIENT_REGISTRY = REPO_ROOT / "config" / "client-wikis.yml"

BLOCKED_NETWORKS = [
    ("host-ip", ipaddress.ip_network("100.64.0.0/10")),
    ("host-ip", ipaddress.ip_network("10.0.0.0/8")),
    ("host-ip", ipaddress.ip_network("172.16.0.0/12")),
    ("host-ip", ipaddress.ip_network("192.168.0.0/16")),
]
DOCUMENTATION_NETWORKS = [
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
]
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

SECRET_PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai-key", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("aws-access-key", re.compile(r"\b(?:A3T[A-Z0-9]|AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
]


@dataclass(frozen=True)
class AddedLine:
    path: str
    line: int
    text: str


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    masked: str
    codename: str | None = None


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def load_allowlist(path: Path) -> dict[str, set[str]]:
    data = load_yaml(path)
    return {
        key: {str(value) for value in data.get(key, []) or []}
        for key in ("host_ips", "hostnames", "secrets", "identifiers")
    }


def load_host_patterns(path: Path) -> list[re.Pattern[str]]:
    if not path.exists():
        return []
    patterns: list[re.Pattern[str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(re.compile(rf"\b(?:{line})\b"))
    return patterns


def mask_value(value: str) -> str:
    if IP_RE.fullmatch(value):
        parts = value.split(".")
        return f"{parts[0]}.***.***.{parts[-1]}"
    if len(value) <= 4:
        return "*" * len(value)
    if len(value) <= 8:
        return f"{value[:2]}***{value[-2:]}"
    prefix_len = 4 if value.startswith(("gh", "sk-", "AKIA", "ASIA", "A3T", "xox", "AIza")) else 2
    return f"{value[:prefix_len]}****{value[-4:]}"


def diff_text(args: argparse.Namespace) -> str:
    if args.diff_file:
        return Path(args.diff_file).read_text(encoding="utf-8")
    cmd = [
        "git",
        "diff",
        "--unified=0",
        "--no-ext-diff",
        f"{args.base_ref}...{args.head_ref}",
    ]
    return subprocess.check_output(cmd, cwd=Path.cwd(), text=True)


def parse_added_lines(diff: str) -> list[AddedLine]:
    lines: list[AddedLine] = []
    current_path: str | None = None
    new_line: int | None = None
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            name = raw[4:].strip()
            current_path = name[2:] if name.startswith("b/") else name
            continue
        if raw.startswith("@@ "):
            match = re.search(r"\+(\d+)(?:,(\d+))?", raw)
            new_line = int(match.group(1)) if match else None
            continue
        if current_path is None or new_line is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            lines.append(AddedLine(current_path, new_line, raw[1:]))
            new_line += 1
        elif raw.startswith(" "):
            new_line += 1
        elif raw.startswith("-"):
            continue
    return lines


def ip_findings(line: AddedLine, allowlist: dict[str, set[str]]) -> Iterable[Finding]:
    for match in IP_RE.finditer(line.text):
        value = match.group(0)
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        if value in allowlist["host_ips"]:
            continue
        if any(address in network for network in DOCUMENTATION_NETWORKS):
            continue
        if any(address in network for _, network in BLOCKED_NETWORKS):
            yield Finding(line.path, line.line, "host-ip", mask_value(value))


def hostname_findings(
    line: AddedLine,
    patterns: list[re.Pattern[str]],
    allowlist: dict[str, set[str]],
) -> Iterable[Finding]:
    for pattern in patterns:
        for match in pattern.finditer(line.text):
            value = match.group(0)
            if value in allowlist["hostnames"]:
                continue
            yield Finding(line.path, line.line, "physical-hostname", mask_value(value))


def secret_findings(line: AddedLine, allowlist: dict[str, set[str]]) -> Iterable[Finding]:
    for kind, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(line.text):
            value = match.group(0)
            if value in allowlist["secrets"]:
                continue
            yield Finding(line.path, line.line, kind, mask_value(value))


def blocking_findings(
    lines: Iterable[AddedLine],
    allowlist: dict[str, set[str]],
    host_patterns: list[re.Pattern[str]],
) -> list[Finding]:
    findings: list[Finding] = []
    for line in lines:
        findings.extend(ip_findings(line, allowlist))
        findings.extend(hostname_findings(line, host_patterns, allowlist))
        findings.extend(secret_findings(line, allowlist))
    return findings


def identifier_entries(registry_path: Path) -> list[tuple[str, str]]:
    data = load_yaml(registry_path)
    entries: list[tuple[str, str]] = []
    for wiki in data.get("wikis", []) or []:
        if not isinstance(wiki, dict):
            continue
        codename = str(wiki.get("codename") or wiki.get("short") or "").strip()
        if not codename:
            continue
        raw_identifiers = []
        for key in ("identifiers", "client_identifiers", "legal_names", "project_ids"):
            value = wiki.get(key, [])
            if isinstance(value, str):
                raw_identifiers.append(value)
            elif isinstance(value, list):
                raw_identifiers.extend(str(item) for item in value)
        for value in raw_identifiers:
            ident = value.strip()
            if len(ident) >= 3:
                entries.append((ident, codename))
    return entries


def identifier_findings(
    lines: Iterable[AddedLine],
    registry_path: Path,
    allowlist: dict[str, set[str]],
) -> list[Finding]:
    entries = identifier_entries(registry_path)
    findings: list[Finding] = []
    for line in lines:
        lower = line.text.casefold()
        for ident, codename in entries:
            if ident in allowlist["identifiers"]:
                continue
            if ident.casefold() in lower:
                findings.append(
                    Finding(line.path, line.line, "client-identifier", mask_value(ident), codename)
                )
    return findings


def write_markdown(path: Path, findings: list[Finding]) -> None:
    if not findings:
        path.write_text("", encoding="utf-8")
        return
    rows = [
        "| Location | Probable identifier | Suggested codename |",
        "|---|---:|---|",
    ]
    for finding in findings:
        rows.append(
            f"| `{finding.path}:{finding.line}` | `{finding.masked}` | `{finding.codename or ''}` |"
        )
    path.write_text(
        "\n".join(
            [
                "### Public surface identifier warning",
                "",
                "O13 warn-only client-identifier check found probable client identifiers in added lines.",
                "The identifier is masked here; review the PR diff and replace it with the suggested codename when publication authority is not established.",
                "",
                *rows,
                "",
            ]
        ),
        encoding="utf-8",
    )


def emit(findings: list[Finding], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps({"findings": [asdict(finding) for finding in findings]}, indent=2))
        return
    for finding in findings:
        suffix = f" codename={finding.codename}" if finding.codename else ""
        print(f"{finding.path}:{finding.line}: {finding.kind}: {finding.masked}{suffix}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("blocking", "identifiers"), default="blocking")
    parser.add_argument("--base-ref", default=os.environ.get("PUBLIC_SURFACE_BASE_REF", "origin/main"))
    parser.add_argument("--head-ref", default=os.environ.get("PUBLIC_SURFACE_HEAD_REF", "HEAD"))
    parser.add_argument("--diff-file")
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST)
    parser.add_argument("--host-denylist", type=Path, default=DEFAULT_HOST_DENYLIST)
    parser.add_argument("--client-registry", type=Path, default=DEFAULT_CLIENT_REGISTRY)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    lines = parse_added_lines(diff_text(args))
    allowlist = load_allowlist(args.allowlist)
    if args.mode == "identifiers":
        findings = identifier_findings(lines, args.client_registry, allowlist)
        if args.markdown_output:
            write_markdown(args.markdown_output, findings)
        if findings and not args.markdown_output:
            emit(findings, args.format)
        return 0

    findings = blocking_findings(lines, allowlist, load_host_patterns(args.host_denylist))
    if findings:
        emit(findings, args.format)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
