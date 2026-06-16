#!/usr/bin/env python3
"""Repo-level statusline provider coverage evidence for #2893."""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATED_BY = "scripts/readiness/statusline_provider_coverage.py"
ISSUE_2894 = "https://github.com/vamseeachanta/workspace-hub/issues/2894"

MEASURED_PATHS = [
    ".claude/statusline-command.sh",
    ".claude/statusline-combined.sh",
    "tests/statusline/",
    "scripts/ai/assessment/query-quota.sh",
    "scripts/ai/assessment/lib/providers.sh",
    "scripts/ai/assessment/gemini-usage.py",
    "config/ai-tools/agent-quota-latest.json",
    "scripts/readiness/build-equality-matrix.py",
    "scripts/readiness/statusline_provider_coverage.py",
    "tests/readiness/test_build_equality_matrix.py",
    "tests/readiness/test_statusline_provider_coverage.py",
    "docs/standards/statusline-provider-coverage.md",
    "docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.md",
    "docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.html",
    "docs/plans/README.md",
]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
SEGMENT_RE = {
    "claude": re.compile(r"(?:^|\|)C:(?P<pct>-|\d+)%?(?P<mark>\?)?"),
    "codex": re.compile(r"(?:^|\|)O:(?P<pct>-|\d+)%?(?P<mark>\?)?(?P<suffix>[^|]*)"),
    "gemini": re.compile(r"(?:^|\|)G:(?P<pct>-|\d+)%?(?P<mark>\?)?(?P<suffix>[^|]*)"),
}


def _run(cmd: list[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=repo_root, text=True, capture_output=True, check=False)


def checkout_sha(repo_root: Path) -> str:
    proc = _run(["git", "rev-parse", "--short", "HEAD"], repo_root)
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def inspect_measured_paths(repo_root: Path, measured_paths: list[str] | None = None) -> dict:
    paths = measured_paths or MEASURED_PATHS
    missing: list[str] = []
    dirty_paths: list[str] = []
    dirty_entries: list[dict[str, str]] = []
    for rel in paths:
        path = repo_root / rel
        if not path.exists():
            missing.append(rel.rstrip("/"))
            continue
        if rel.endswith("/") or path.is_dir():
            tracked = _run(["git", "ls-files", "--", rel], repo_root)
            if not tracked.stdout.strip():
                missing.append(rel.rstrip("/"))
        else:
            tracked = _run(["git", "ls-files", "--error-unmatch", "--", rel], repo_root)
            if tracked.returncode != 0:
                missing.append(rel)
    status = _run(["git", "status", "--porcelain", "--untracked-files=all", "--", *paths], repo_root)
    if status.stdout.strip():
        for line in status.stdout.splitlines():
            if not line.strip():
                continue
            dirty_entries.append({"status": line[:2].strip(), "path": line[3:].strip()})
        dirty_paths = [entry["path"] for entry in dirty_entries]
    return {
        "dirty": bool(dirty_paths),
        "dirty_paths": dirty_paths,
        "dirty_entries": dirty_entries,
        "missing_paths": sorted(set(missing)),
    }


def _pct_value(raw: str) -> int | None:
    return None if raw == "-" else int(raw)


def _state(raw: str, mark: str | None, provider: str) -> str:
    if raw == "-":
        return "missing"
    if mark == "?":
        return "estimate" if provider == "claude" else "stale_or_estimate"
    return "fresh"


def parse_statusline_output(output: str) -> dict:
    clean = strip_ansi(output)
    providers = {
        "claude": {"state": "missing", "weekly_remaining_pct": None},
        "codex": {"state": "missing", "weekly_remaining_pct": None, "five_hour_remaining_pct": None},
        "gemini": {"state": "missing", "remaining_pct": None},
        "hermes": {"state": "missing", "alias": None},
    }
    for provider, regex in SEGMENT_RE.items():
        match = regex.search(clean)
        if not match:
            continue
        raw = match.group("pct")
        state = _state(raw, match.group("mark"), provider)
        if provider == "codex":
            suffix = match.group("suffix") or ""
            five = re.search(r"5h(?P<pct>\d+)%?(?P<mark>\?)?", suffix)
            providers[provider].update(
                state=state,
                weekly_remaining_pct=_pct_value(raw),
                five_hour_remaining_pct=(int(five.group("pct")) if five else None),
                five_hour_state=(
                    "missing" if five is None
                    else "stale_or_estimate" if five.group("mark")
                    else "fresh"
                ),
            )
        elif provider == "gemini":
            providers[provider].update(state=state, remaining_pct=_pct_value(raw))
        else:
            providers[provider].update(state=state, weekly_remaining_pct=_pct_value(raw))
    alias = re.search(r"(?:^|\|)H=O(?P<mark>\?)?", clean)
    if alias:
        providers["hermes"] = {
            "state": "alias",
            "stale_marker": bool(alias.group("mark")),
            "alias": "codex",
        }
    return providers


def contract_verdict(providers: dict) -> str:
    if providers["claude"]["state"] == "missing":
        return "PARTIAL"
    if providers["codex"]["state"] == "missing":
        return "PARTIAL"
    if providers["codex"].get("five_hour_remaining_pct") is None:
        return "PARTIAL"
    if providers["gemini"]["state"] == "missing":
        return "PARTIAL"
    if providers["hermes"]["state"] != "alias":
        return "PARTIAL"
    return "COMPLETE"


def issue_2894_state() -> dict:
    env_state = os.environ.get("STATUSLINE_R6_BLOCKER_STATE")
    if env_state in {"open", "closed", "unknown"}:
        return {"issue": ISSUE_2894, "state": env_state, "source": "env"}
    cache = os.environ.get("STATUSLINE_R6_BLOCKER_CACHE")
    if cache:
        try:
            raw = Path(cache).read_text().strip()
            data = json.loads(raw) if raw.startswith("{") else {"state": raw}
            state = data.get("state", "unknown")
            if state not in {"open", "closed", "unknown"}:
                state = "unknown"
            return {"issue": ISSUE_2894, "state": state, "source": cache}
        except (OSError, ValueError, TypeError):
            pass
    return {"issue": ISSUE_2894, "state": "unknown", "source": "absent"}


def final_verdict(providers: dict, blocker: dict, dirty: bool, missing_paths: list[str]) -> str:
    if dirty or missing_paths:
        return "PARTIAL"
    if blocker.get("state") != "closed":
        return "PARTIAL"
    return contract_verdict(providers)


def _write_fixture_files(tmp: Path) -> dict[str, str]:
    now = datetime.now(timezone.utc).isoformat()
    quota = tmp / "agent-quota.json"
    quota.write_text(json.dumps({
        "timestamp": now,
        "agents": [
            {"provider": "claude", "week_pct": None, "pct_remaining": None, "source": "unavailable"},
            {"provider": "codex", "week_pct": 65, "pct_remaining": 35, "five_hour_pct": 1,
             "hours_to_reset": 60, "resets_at": "", "source": "app-server-live"},
        ],
    }))
    gemini = tmp / "agy-usage-snapshot.json"
    gemini.write_text(json.dumps({
        "captured_at": now,
        "gemini": {
            "weekly": {"pct_remaining": 100, "reset_hours": 159.5},
            "five_hour": {"pct_remaining": 100, "reset_hours": 3.2},
        },
    }))
    creds = tmp / ".credentials.json"
    creds.write_text(json.dumps({"claudeAiOauth": {"subscriptionType": "pro", "rateLimitTier": "pro"}}))
    stats = tmp / "stats-cache.json"
    stats.write_text(json.dumps({
        "dailyActivity": [
            {"date": datetime.now(timezone.utc).date().isoformat(), "messageCount": 1500,
             "sessionCount": 3, "toolCallCount": 9}
        ],
    }))
    return {
        "STATUSLINE_QUOTA_PRIMARY": str(quota),
        "STATUSLINE_QUOTA_CACHE": str(quota),
        "STATUSLINE_GEMINI_SNAPSHOT": str(gemini),
        "GEMINI_ERROR_DIR": str(tmp),
        "STATUSLINE_CLAUDE_CREDS": str(creds),
        "STATUSLINE_CLAUDE_STATS_CACHE": str(stats),
    }


def run_statusline_fixture(repo_root: Path) -> tuple[str, str | None]:
    script = repo_root / ".claude" / "statusline-command.sh"
    if not script.exists():
        return "", "missing statusline-command.sh"
    with tempfile.TemporaryDirectory(prefix="statusline-coverage-") as raw_tmp:
        tmp = Path(raw_tmp)
        env = dict(os.environ)
        env.update(_write_fixture_files(tmp))
        payload = json.dumps({
            "model": {"display_name": "Opus"},
            "workspace": {"current_dir": str(repo_root)},
            "cost": {"total_cost_usd": 0},
            "context_window": {"used_percentage": 10},
        })
        proc = subprocess.run(
            ["bash", str(script), "--usage-tail"],
            input=payload,
            cwd=repo_root,
            text=True,
            capture_output=True,
            env=env,
            timeout=10,
            check=False,
        )
    if proc.returncode != 0:
        return proc.stdout, (proc.stderr or f"statusline exited {proc.returncode}").strip()
    return proc.stdout, None


def collect_statusline_provider_coverage(repo_root: Path = REPO) -> dict:
    path_status = inspect_measured_paths(repo_root)
    sample, error = run_statusline_fixture(repo_root)
    providers = parse_statusline_output(sample)
    blocker = issue_2894_state()
    renderer_verdict = contract_verdict(providers)
    verdict = final_verdict(providers, blocker, path_status["dirty"], path_status["missing_paths"])
    return {
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "checkout_sha": checkout_sha(repo_root),
        "dirty": path_status["dirty"],
        "dirty_paths": path_status["dirty_paths"],
        "dirty_entries": path_status["dirty_entries"],
        "missing_paths": path_status["missing_paths"],
        "r6_closeout_blocker": blocker,
        "issue_state_evidence": blocker,
        "renderer_contract_verdict": renderer_verdict,
        "contract_verdict": verdict,
        "output_sample": strip_ansi(sample),
        "error": error,
        "providers": providers,
    }


def main() -> int:
    print(json.dumps(collect_statusline_provider_coverage(REPO), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
