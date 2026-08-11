"""Every match is counted exactly once, no matter which deny lists supplied it.

WHY
---
`scan_directory` merges a global and a local deny list::

    global_list="$WORKSPACE_ROOT/.legal-deny-list.yaml"
    local_list="$scan_dir/.legal-deny-list.yaml"
    patterns="$(parse_deny_list "$global_list"; parse_deny_list "$local_list")"

For a submodule those are two different files and merging is the documented
intent — "Per-project deny lists in each submodule extend (not replace) this
file". For a scan of the workspace ROOT, `scan_dir` IS `WORKSPACE_ROOT`, so the
two variables name THE SAME FILE. It was parsed twice, every pattern entered the
work list twice, every pattern was searched twice, and every hit was counted
twice.

Measured on origin/main 2026-08-03, scanning the workspace root: 6 block + 108
warn reported against 3 + 54 unique `file:line` hits. Exactly 2x. Every headline
number this gate has ever printed was double the truth — including the "71
unique violations" figure that the severity-tier work was reasoned from, which
the scan itself had been reporting as 142.

A gate whose headline number is wrong by a constant factor is worse than one
that is merely noisy: the noise is visible, the factor is not.

WHY THE COUNT AND NOT JUST THE EXIT CODE
----------------------------------------
The existing tests all assert on presence and return code, which double-counting
cannot disturb — 2 violations fail exactly like 1. That is why the bug survived
every one of them. These tests assert on the COUNT, which is the only thing that
moved.

NOTE ON THIS FILE'S OWN CONTENT
-------------------------------
No deny-listed literal appears here. Every pattern is an invented ZZ...ZZ marker
written into a throwaway deny list, per
`test_public_field_data_exclusion.test_no_legal_test_trips_the_scan_it_guards`.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "scripts" / "legal" / "legal-sanity-scan.sh"

MARK_ROOT = "ZZROOTCOUNTMARKERZZ"
MARK_WARNCOUNT = "ZZWARNCOUNTMARKERZZ"
MARK_GLOBALONLY = "ZZGLOBALONLYMARKERZZ"
MARK_LOCALONLY = "ZZLOCALONLYMARKERZZ"
MARK_DUP = "ZZDUPACROSSLISTSMARKERZZ"
MARK_SEVCONFLICT = "ZZSEVCONFLICTMARKERZZ"


def _deny_list(body: str, default_severity: str = "block") -> str:
    return (
        f"client_references:\n{body}"
        f'exclusions:\n  - ".git/"\n'
        f'default_severity: "{default_severity}"\n'
    )


def _entry(pattern: str, severity: str | None = None) -> str:
    line = f'  - pattern: "{pattern}"\n    case_sensitive: true\n'
    if severity is not None:
        line += f"    severity: {severity}\n"
    return line


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    w = tmp_path / "workspace-hub"
    (w / "scripts" / "legal").mkdir(parents=True)
    shutil.copy(SCANNER, w / "scripts" / "legal" / "legal-sanity-scan.sh")
    subprocess.run(["git", "init", "-q"], cwd=w, check=True)
    return w


def _scan(w: Path, *args: str, env: dict[str, str] | None = None
          ) -> subprocess.CompletedProcess:
    run_env = None
    if env is not None:
        run_env = {**os.environ, **env}
    return subprocess.run(
        ["bash", "scripts/legal/legal-sanity-scan.sh", *args],
        cwd=w, capture_output=True, text=True, timeout=180, env=run_env,
    )


def _scan_subdir(w: Path, sub: Path) -> subprocess.CompletedProcess:
    """Scan `sub` as a separate repo, so global and local deny lists differ.

    Deliberately routed through `--all` + LEGAL_SCAN_REPO_ROOTS rather than the
    more obvious `--repo=<name>`. `--repo` is unusable here: `resolve_repo_path`
    is defined TWICE in the scanner, and the second definition returns its
    result in `RESOLVED_REPO_PATH` while printing nothing — but the call site
    does `repo_path="$(resolve_repo_path ...)"`. So `--repo=<name>` scans the
    empty string, finds nothing, and reports PASS. That is a separate and more
    serious defect (a legal gate passing by scanning nothing), already covered
    by the failing tests in test_repo_resolution.py / test_legal_scan_resolution.py
    and NOT in scope here. `--all` with registered roots calls `scan_directory`
    directly and is unaffected.
    """
    return _scan(w, "--all", env={"LEGAL_SCAN_REPO_ROOTS": str(sub)})


def _blocks(out: str) -> int:
    m = re.search(r"RESULT: FAIL .*?(\d+) block violation", out)
    return int(m.group(1)) if m else 0


def _warns(out: str) -> int:
    m = re.search(r"WARNINGS: (\d+) advisory match", out)
    return int(m.group(1)) if m else 0


def _match_counts(out: str) -> list[int]:
    """The per-pattern `matches=N` figures, in report order."""
    return [int(n) for n in re.findall(r"\bmatches=(\d+)", out)]


# ---------------------------------------------------------------------------
# The bug: root scan parses one file as both global and local
# ---------------------------------------------------------------------------


def test_root_scan_counts_a_single_hit_once(ws: Path) -> None:
    """One occurrence of one pattern is one violation, not two."""
    (ws / ".legal-deny-list.yaml").write_text(_deny_list(_entry(MARK_ROOT, "block")))
    (ws / "sample.md").write_text(f"{MARK_ROOT}\n")

    r = _scan(ws)
    out = r.stdout + r.stderr

    assert MARK_ROOT in out, f"the hit must still be reported:\n{out}"
    assert _match_counts(out) == [1], (
        f"the workspace root's deny list is loaded as BOTH the global and the "
        f"local list, so its patterns are searched twice; expected matches=1, "
        f"got {_match_counts(out)}\n{out}"
    )
    assert _blocks(out) == 1, (
        f"expected 1 block violation, got {_blocks(out)}\n{out}"
    )
    assert r.returncode == 1


def test_root_scan_does_not_double_count_warnings(ws: Path) -> None:
    """The warn tier is counted by the same code path and doubles identically."""
    (ws / ".legal-deny-list.yaml").write_text(
        _deny_list(_entry(MARK_WARNCOUNT, "warn"))
    )
    (ws / "sample.md").write_text(f"{MARK_WARNCOUNT}\n")

    r = _scan(ws)
    out = r.stdout + r.stderr

    assert MARK_WARNCOUNT in out
    assert _warns(out) == 1, f"expected 1 advisory match, got {_warns(out)}\n{out}"
    assert r.returncode == 0


def test_root_scan_json_emits_one_record_per_hit(ws: Path) -> None:
    """JSON consumers see the duplication as two distinct findings."""
    (ws / ".legal-deny-list.yaml").write_text(_deny_list(_entry(MARK_ROOT, "block")))
    (ws / "sample.md").write_text(f"{MARK_ROOT}\n")

    r = _scan(ws, "--json")
    records = [ln for ln in r.stdout.splitlines() if MARK_ROOT in ln]

    assert len(records) == 1, (
        f"one hit must produce exactly one JSON record, got {len(records)}:\n"
        + "\n".join(records)
    )


# ---------------------------------------------------------------------------
# The intent that must survive the fix: local lists EXTEND the global one
# ---------------------------------------------------------------------------


def test_submodule_local_list_still_extends_the_global_list(ws: Path) -> None:
    """Guard against "fix" by dropping the local list.

    The deny list's own header states the contract: "Per-project deny lists in
    each submodule extend (not replace) this file." A submodule scan must still
    see BOTH lists' patterns, each counted once.
    """
    (ws / ".legal-deny-list.yaml").write_text(
        _deny_list(_entry(MARK_GLOBALONLY, "block"))
    )
    sub = ws / "submod"
    sub.mkdir()
    (sub / ".legal-deny-list.yaml").write_text(
        _deny_list(_entry(MARK_LOCALONLY, "block"))
    )
    (sub / "sample.md").write_text(f"{MARK_GLOBALONLY}\n{MARK_LOCALONLY}\n")

    r = _scan_subdir(ws, sub)
    out = r.stdout + r.stderr

    assert MARK_GLOBALONLY in out, f"global pattern must apply to submodules:\n{out}"
    assert MARK_LOCALONLY in out, f"local pattern must be honoured:\n{out}"
    assert _match_counts(out) == [1, 1], (
        f"two distinct patterns, one hit each; got {_match_counts(out)}\n{out}"
    )
    assert _blocks(out) == 2, f"expected 2 block violations, got {_blocks(out)}\n{out}"


def test_pattern_declared_in_both_lists_is_counted_once(ws: Path) -> None:
    """The same doubling, reached the other way.

    "Extend, not replace" invites a submodule author to re-declare a pattern the
    global list already carries — they cannot be expected to have read all 23.
    Searching for the same string twice cannot find anything the first search
    missed, so the second pass contributes only inflation.
    """
    (ws / ".legal-deny-list.yaml").write_text(_deny_list(_entry(MARK_DUP, "block")))
    sub = ws / "submod"
    sub.mkdir()
    (sub / ".legal-deny-list.yaml").write_text(_deny_list(_entry(MARK_DUP, "block")))
    (sub / "sample.md").write_text(f"{MARK_DUP}\n")

    r = _scan_subdir(ws, sub)
    out = r.stdout + r.stderr

    assert MARK_DUP in out
    assert _blocks(out) == 1, (
        f"a pattern declared in both lists describes ONE thing to look for; "
        f"expected 1 block violation, got {_blocks(out)}\n{out}"
    )


def test_duplicate_pattern_keeps_the_blocking_severity(ws: Path) -> None:
    """Collapsing duplicates must fail CLOSED on severity.

    Global says block, the local list re-declares the same pattern as warn. A
    naive last-one-wins collapse would let a submodule silently demote a
    workspace-wide blocking pattern to advisory — turning a counting fix into a
    privilege escalation. Same posture as the unrecognised-severity handling in
    the scanner ("a typo must not silently downgrade a pattern").
    """
    (ws / ".legal-deny-list.yaml").write_text(
        _deny_list(_entry(MARK_SEVCONFLICT, "block"))
    )
    sub = ws / "submod"
    sub.mkdir()
    (sub / ".legal-deny-list.yaml").write_text(
        _deny_list(_entry(MARK_SEVCONFLICT, "warn"))
    )
    (sub / "sample.md").write_text(f"{MARK_SEVCONFLICT}\n")

    r = _scan_subdir(ws, sub)
    out = r.stdout + r.stderr

    assert _blocks(out) == 1, (
        f"the blocking declaration must survive the collapse; got "
        f"{_blocks(out)} block / {_warns(out)} warn\n{out}"
    )
    assert _warns(out) == 0, (
        f"the demoted duplicate must not also be reported as advisory; got "
        f"{_warns(out)} warn\n{out}"
    )
    assert r.returncode == 1, "a block-severity pattern must still fail the scan"


# ---------------------------------------------------------------------------
# Multiplicity that is REAL must survive
# ---------------------------------------------------------------------------


def test_genuinely_repeated_hits_are_all_counted(ws: Path) -> None:
    """Deduplicating PATTERNS must not deduplicate MATCHES.

    Three real occurrences across two files stay three. A fix that collapsed
    identical findings instead of identical patterns would under-report, which
    is the one direction a legal gate must never fail in.
    """
    (ws / ".legal-deny-list.yaml").write_text(_deny_list(_entry(MARK_ROOT, "block")))
    (ws / "a.md").write_text(f"{MARK_ROOT}\nfiller\n{MARK_ROOT}\n")
    (ws / "b.md").write_text(f"{MARK_ROOT}\n")

    r = _scan(ws)
    out = r.stdout + r.stderr

    assert _blocks(out) == 3, (
        f"three genuine occurrences must all count; got {_blocks(out)}\n{out}"
    )
