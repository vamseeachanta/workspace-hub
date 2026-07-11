"""Fail-closed GitHub remote-state classification."""
from __future__ import annotations
import json
import re
import subprocess
from .bootstrap_git import isolated_env, trusted_executable
_OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")


def _run(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command, check=False, capture_output=True, env=isolated_env(), timeout=15,
    )


def github_api(endpoint: str) -> tuple[int, dict]:
    command = [trusted_executable("gh"), "api", "--hostname", "github.com", "--include", endpoint]
    try:
        result = _run(command)
    except BaseException:
        return 0, {}
    match = re.search(rb"(?:HTTP/\S+ )([0-9]{3})[^\n]*\n", result.stdout)
    separator = b"\r\n\r\n" if b"\r\n\r\n" in result.stdout else b"\n\n"
    body = result.stdout.split(separator, 1)[-1]
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeError):
        payload = {}
    status = int(match.group(1)) if match else (200 if result.returncode == 0 else 0)
    return status, payload if isinstance(payload, dict) else {}


def remote_state(repo: str, expected: str | None) -> tuple[str, str | None]:
    status, payload = github_api(f"repos/{repo}")
    owner, name = repo.split("/", 1)
    valid = payload.get("name") == name and payload.get("owner", {}).get("login") == owner
    if status != 200 or not valid or payload.get("private") is not True:
        return "unknown", None
    if payload.get("archived") is not False:
        return "unknown", None
    status, branch = github_api(f"repos/{repo}/git/ref/heads/main")
    if status == 404:
        return "absent", None
    oid = branch.get("object", {}).get("sha") if status == 200 else None
    if not isinstance(oid, str) or _OID.fullmatch(oid) is None:
        return "unknown", None
    return ("equal" if oid == expected else "different"), oid
