"""Tests for nightly-readiness.sh R-HOOK-STATIC + R-TELEGRAM-HERMES host-awareness.

Covers three behaviours added to scripts/readiness/nightly-readiness.sh:

1. R-HOOK-STATIC blocking-pattern scan excludes lines carrying a
   ``hook-static-allow`` sentinel (mirrors the R-MODEL ``r-model-allow``
   precedent so pattern-detector hooks don't trip on the strings they scan for).
2. R-HOOK-STATIC line-count check honours a config-driven
   ``hook_static_line_exempt`` list of basenames, and falls back to *no*
   exemptions when the key is absent.
3. R-TELEGRAM-HERMES is host-aware: it runs the real readiness probe only when
   THIS host is the Telegram coordinator in config/workstations/registry.yaml;
   every other host passes with the "not on this host" reason.

Each test drives the real shell script against an isolated temp WORKSPACE_HUB so
we exercise the production code path, not a reimplementation.
"""

from __future__ import annotations

import socket
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "readiness" / "nightly-readiness.sh"
REAL_CONFIG = REPO_ROOT / "scripts" / "readiness" / "harness-config.yaml"


def _run(ws: Path, config: Path) -> str:
    """Run nightly-readiness.sh against an isolated workspace; return stdout."""
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "HOME": str(ws / "home"),
        "WORKSPACE_HUB": str(ws),
        "HARNESS_CONFIG": str(config),
    }
    proc = subprocess.run(
        ["bash", str(SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
        timeout=120,
    )
    return proc.stdout


def _line(output: str, check_id: str) -> str:
    for raw in output.splitlines():
        if check_id in raw and ("OK" in raw or "FAIL" in raw):
            return raw.strip()
    raise AssertionError(f"{check_id} line not found in:\n{output}")


def _mk_ws(tmp_path: Path, *, config_body: str | None = None) -> tuple[Path, Path]:
    """Build a minimal isolated workspace; return (ws_root, config_path)."""
    ws = tmp_path / "ws"
    (ws / ".claude" / "hooks").mkdir(parents=True)
    (ws / ".claude" / "state").mkdir(parents=True)
    (ws / "home").mkdir(parents=True)
    cfg_dir = ws / "scripts" / "readiness"
    cfg_dir.mkdir(parents=True)
    config = cfg_dir / "harness-config.yaml"
    config.write_text(config_body if config_body is not None else REAL_CONFIG.read_text())
    return ws, config


# ── R-HOOK-STATIC: sentinel exclusion ────────────────────────────────────────


def test_hook_static_blocking_pattern_without_sentinel_fails(tmp_path: Path) -> None:
    ws, config = _mk_ws(tmp_path)
    hook = ws / ".claude" / "hooks" / "detector.sh"
    hook.write_text("#!/usr/bin/env bash\nPATTERN='curl http://evil'\n")
    out = _run(ws, config)
    line = _line(out, "R-HOOK-STATIC")
    assert line.startswith("FAIL"), line
    assert "blocking-pattern" in line


def test_hook_static_sentinel_excludes_pattern_line(tmp_path: Path) -> None:
    ws, config = _mk_ws(tmp_path)
    hook = ws / ".claude" / "hooks" / "detector.sh"
    # Same offending content, but tagged as a detector definition — must pass.
    hook.write_text(
        "#!/usr/bin/env bash\nPATTERN='curl http://evil'  # hook-static-allow\n"
    )
    out = _run(ws, config)
    line = _line(out, "R-HOOK-STATIC")
    assert line.startswith("OK"), line


def test_hook_static_real_hooks_pass(tmp_path: Path) -> None:
    """The real .claude/hooks tree (with its tagged detectors) must pass."""
    out = _run(REPO_ROOT, REAL_CONFIG)
    line = _line(out, "R-HOOK-STATIC")
    assert line.startswith("OK"), line


# ── R-HOOK-STATIC: line-count exemption ──────────────────────────────────────

_BIG_HOOK = "#!/usr/bin/env bash\n" + "".join(f"echo line {i}\n" for i in range(250))


def test_hook_static_exempt_basename_skips_line_check(tmp_path: Path) -> None:
    body = (
        "schema_version: 1\n"
        "hook_static_max_lines: 200\n"
        "hook_static_line_exempt:\n"
        "  - big-validator.sh   # big intrinsic validator\n"
        "hook_blocking_patterns:\n"
        "  - 'git commit'\n"
    )
    ws, config = _mk_ws(tmp_path, config_body=body)
    (ws / ".claude" / "hooks" / "big-validator.sh").write_text(_BIG_HOOK)
    out = _run(ws, config)
    assert _line(out, "R-HOOK-STATIC").startswith("OK")


def test_hook_static_non_exempt_oversize_still_fails(tmp_path: Path) -> None:
    body = (
        "schema_version: 1\n"
        "hook_static_max_lines: 200\n"
        "hook_static_line_exempt:\n"
        "  - some-other.sh\n"
        "hook_blocking_patterns:\n"
        "  - 'git commit'\n"
    )
    ws, config = _mk_ws(tmp_path, config_body=body)
    (ws / ".claude" / "hooks" / "big-validator.sh").write_text(_BIG_HOOK)
    out = _run(ws, config)
    line = _line(out, "R-HOOK-STATIC")
    assert line.startswith("FAIL"), line
    assert "big-validator.sh:" in line and ">max200" in line


def test_hook_static_missing_exempt_key_means_no_exemptions(tmp_path: Path) -> None:
    body = (
        "schema_version: 1\n"
        "hook_static_max_lines: 200\n"
        "hook_blocking_patterns:\n"
        "  - 'git commit'\n"
    )
    ws, config = _mk_ws(tmp_path, config_body=body)
    (ws / ".claude" / "hooks" / "big-validator.sh").write_text(_BIG_HOOK)
    out = _run(ws, config)
    line = _line(out, "R-HOOK-STATIC")
    assert line.startswith("FAIL"), line
    assert ">max200" in line


# ── R-TELEGRAM-HERMES: host-awareness ────────────────────────────────────────


def _write_registry(ws: Path, *, this_host_mode: str) -> None:
    """Write a registry marking THIS host with the given telegram_mode."""
    reg_dir = ws / "config" / "workstations"
    reg_dir.mkdir(parents=True)
    local = socket.gethostname()
    reg_dir.joinpath("registry.yaml").write_text(
        "machines:\n"
        "  this-host:\n"
        f"    hostname: {local}\n"
        "    hostname_aliases: []\n"
        f"    telegram_mode: {this_host_mode}\n"
        "  other-host:\n"
        "    hostname: some-other-box\n"
        "    telegram_mode: coordinator\n"
    )


def test_telegram_passes_when_local_host_is_not_coordinator(tmp_path: Path) -> None:
    ws, config = _mk_ws(tmp_path)
    _write_registry(ws, this_host_mode="worker")
    # Provide the readiness sub-script so the check reaches the host gate.
    tg = ws / "scripts" / "readiness" / "telegram-hermes-readiness.sh"
    tg.write_text("#!/usr/bin/env bash\necho '{\"overall_status\":\"fail\"}'\n")
    tg.chmod(0o755)
    out = _run(ws, config)
    line = _line(out, "R-TELEGRAM-HERMES")
    assert line.startswith("OK"), line
    assert "not on this host" in line


def test_telegram_runs_probe_when_local_host_is_coordinator(tmp_path: Path) -> None:
    ws, config = _mk_ws(tmp_path)
    _write_registry(ws, this_host_mode="coordinator")
    # A failing probe must surface as a real R-TELEGRAM-HERMES FAIL on the
    # coordinator (proves the gate still runs and can fail on the Hermes host).
    tg = ws / "scripts" / "readiness" / "telegram-hermes-readiness.sh"
    tg.write_text("#!/usr/bin/env bash\necho '{\"overall_status\":\"fail\"}'\n")
    tg.chmod(0o755)
    out = _run(ws, config)
    line = _line(out, "R-TELEGRAM-HERMES")
    assert line.startswith("FAIL"), line


def test_telegram_passes_when_registry_absent(tmp_path: Path) -> None:
    """No registry → can't prove coordinator → fall back to pass (no hard-fail)."""
    ws, config = _mk_ws(tmp_path)
    tg = ws / "scripts" / "readiness" / "telegram-hermes-readiness.sh"
    tg.write_text("#!/usr/bin/env bash\necho '{\"overall_status\":\"fail\"}'\n")
    tg.chmod(0o755)
    out = _run(ws, config)
    assert _line(out, "R-TELEGRAM-HERMES").startswith("OK")


# ── R-AI-CLI: absent CLIs / cross-host rows don't fail ───────────────────────


def test_ai_cli_passes_when_clis_absent(tmp_path: Path) -> None:
    """The harness is provider-neutral: a host that doesn't run a given CLI emits
    a "CLI not found in PATH" row (empty version), which must NOT fail R-AI-CLI.

    The minimal test PATH (/usr/bin:/bin:/usr/local/bin) has none of
    claude/codex/gemini, so ai-agent-readiness.sh writes three empty-version warn
    rows for this host. Before the host/version-aware fix a blind tail counted
    them as 3 warnings → FAIL; now they're skipped → OK. Also implicitly checks
    the per-host filter (only this host's latest status per agent is counted).
    """
    ws, config = _mk_ws(tmp_path)
    out = _run(ws, config)
    line = _line(out, "R-AI-CLI")
    assert line.startswith("OK"), line


# ── R1: auto-generated memory artifacts are exempt from the 200-line budget ──


def test_r1_skips_managed_oversized_memory_file(tmp_path: Path) -> None:
    """A >200-line memory file that declares itself managed/auto-generated must
    NOT fail R1 — the budget targets hand-authored memory, not generated mirrors."""
    ws, config = _mk_ws(tmp_path)
    mem = ws / ".claude" / "memory"
    mem.mkdir(parents=True)
    body = "<!-- MANAGED by build_topics_index.py — do not hand-edit -->\n" + \
        "".join(f"- entry {i}\n" for i in range(250))
    (mem / "INDEX.md").write_text(body)
    line = _line(_run(ws, config), "R1")
    assert line.startswith("OK"), line


def test_r1_still_fails_handauthored_oversized_memory_file(tmp_path: Path) -> None:
    """A hand-authored (unmarked) >200-line memory file must still fail R1."""
    ws, config = _mk_ws(tmp_path)
    mem = ws / ".claude" / "memory"
    mem.mkdir(parents=True)
    (mem / "notes.md").write_text("# Notes\n" + "".join(f"- point {i}\n" for i in range(250)))
    line = _line(_run(ws, config), "R1")
    assert line.startswith("FAIL"), line
    assert "notes.md" in line


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
