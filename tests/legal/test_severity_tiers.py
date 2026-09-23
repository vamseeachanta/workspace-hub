"""Per-pattern severity: `warn` reports without failing, `block` fails.

WHY
---
`.legal-deny-list.yaml` has documented two severity levels since v2.0 —
"block — fail the scan, PR cannot proceed" / "warn — flag but allow to
proceed" — and carries a `default_severity` key. None of it was implemented:
the scanner counted every match toward the exit code and hardcoded
`"severity":"block"` in its JSON output. The documentation described a feature
that did not exist.

That gap is why the deny list is one flat block tier, and why it conflates two
different things under one severity:

  * The vendor company and named author recorded under #1773 — copyright
    holders of code that must be clean-roomed. A genuine constraint, and
    genuinely blocking. (Named here only by reference: writing the literals
    would trip the very scan this file tests.)
  * Public Gulf of Mexico field names — which are ALSO the names of client
    engagements, but appear overwhelmingly in public-data analysis, GTM
    competitor research, and auto-generated reports.

Measured on origin/main 2026-08-03: 71 unique violations, and NOT ONE was a
leak. 60 of them were public field names. A gate that is ~85% noise stops being
read, which is the actual risk to the material the gate exists to protect.

Owner decision 2026-08-03: implement the documented tiers. Vendor/author
patterns stay `block`; public field/project names become `warn` — still
surfaced, no longer failing.

BACK-COMPAT IS PART OF THE CONTRACT
-----------------------------------
An entry with no `severity:` must keep its current blocking behaviour via
`default_severity`. Silently downgrading unmarked patterns would turn a
documentation fix into a security regression.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "scripts" / "legal" / "legal-sanity-scan.sh"

MARK_WARN = "ZZWARNMARKERZZ"
MARK_BLOCK = "ZZBLOCKMARKERZZ"
MARK_PLAIN = "ZZPLAINMARKERZZ"
MARK_NOCASE = "ZZNOCASEKEYMARKERZZ"


def _deny_list(body: str, default_severity: str = "block") -> str:
    return f"client_references:\n{body}\nexclusions:\n  - \".git/\"\ndefault_severity: \"{default_severity}\"\n"


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    w = tmp_path / "workspace-hub"
    (w / "scripts" / "legal").mkdir(parents=True)
    shutil.copy(SCANNER, w / "scripts" / "legal" / "legal-sanity-scan.sh")
    subprocess.run(["git", "init", "-q"], cwd=w, check=True)
    return w


def _run(w: Path, deny_body: str, content: str, default_severity: str = "block"):
    (w / ".legal-deny-list.yaml").write_text(_deny_list(deny_body, default_severity))
    (w / "sample.md").write_text(content)
    return subprocess.run(
        ["bash", "scripts/legal/legal-sanity-scan.sh"],
        cwd=w, capture_output=True, text=True, timeout=180,
    )


def test_warn_severity_reports_but_does_not_fail(ws: Path) -> None:
    r = _run(
        ws,
        f'  - pattern: "{MARK_WARN}"\n    case_sensitive: true\n    severity: warn\n',
        f"{MARK_WARN}\n",
    )
    out = r.stdout + r.stderr
    assert MARK_WARN in out, f"a warn-severity match must still be REPORTED:\n{out}"
    assert r.returncode == 0, (
        f"warn must not fail the scan (that is the whole point of the tier); "
        f"rc={r.returncode}\n{out}"
    )


def test_block_severity_still_fails(ws: Path) -> None:
    r = _run(
        ws,
        f'  - pattern: "{MARK_BLOCK}"\n    case_sensitive: true\n    severity: block\n',
        f"{MARK_BLOCK}\n",
    )
    out = r.stdout + r.stderr
    assert MARK_BLOCK in out
    assert r.returncode == 1, f"block severity must fail the scan; rc={r.returncode}\n{out}"


def test_unmarked_pattern_keeps_blocking_via_default(ws: Path) -> None:
    """Back-compat: no `severity:` means `default_severity`, which is block.

    Guards the regression that would matter most — a parser change that
    silently downgrades every existing unmarked pattern to warn.
    """
    r = _run(
        ws,
        f'  - pattern: "{MARK_PLAIN}"\n    case_sensitive: true\n',
        f"{MARK_PLAIN}\n",
    )
    out = r.stdout + r.stderr
    assert MARK_PLAIN in out
    assert r.returncode == 1, (
        f"an unmarked pattern must keep blocking via default_severity; "
        f"rc={r.returncode}\n{out}"
    )


def test_warn_and_block_together_fail_but_both_report(ws: Path) -> None:
    """A warn hit must not mask a block hit, and must not be lost either."""
    r = _run(
        ws,
        f'  - pattern: "{MARK_WARN}"\n    case_sensitive: true\n    severity: warn\n'
        f'  - pattern: "{MARK_BLOCK}"\n    case_sensitive: true\n    severity: block\n',
        f"{MARK_WARN}\n{MARK_BLOCK}\n",
    )
    out = r.stdout + r.stderr
    assert MARK_BLOCK in out and MARK_WARN in out, f"both tiers must report:\n{out}"
    assert r.returncode == 1, "a block hit must still fail even alongside warns"


def test_pattern_without_case_sensitive_key_is_still_scanned(ws: Path) -> None:
    """Latent silent-drop bug in the parser.

    The parser emitted a pattern only when a `case_sensitive:` line followed it,
    so an entry lacking that key was never scanned at all — invisible, since a
    pattern that is never searched simply reports nothing. Adding a `severity:`
    key makes entry shapes more varied, so this has to hold.
    """
    r = _run(
        ws,
        f'  - pattern: "{MARK_NOCASE}"\n    description: "no case_sensitive key"\n',
        f"{MARK_NOCASE}\n",
    )
    out = r.stdout + r.stderr
    assert MARK_NOCASE in out, (
        f"a pattern without case_sensitive: must still be scanned, not silently "
        f"dropped:\n{out}"
    )


def test_json_output_reports_the_real_severity(ws: Path) -> None:
    """JSON hardcoded severity":"block" for every hit, warn included."""
    (ws / ".legal-deny-list.yaml").write_text(
        _deny_list(f'  - pattern: "{MARK_WARN}"\n    case_sensitive: true\n    severity: warn\n')
    )
    (ws / "sample.md").write_text(f"{MARK_WARN}\n")
    r = subprocess.run(
        ["bash", "scripts/legal/legal-sanity-scan.sh", "--json"],
        cwd=ws, capture_output=True, text=True, timeout=180,
    )
    out = r.stdout + r.stderr
    assert MARK_WARN in out, f"warn hit missing from JSON output:\n{out}"
    assert '"severity":"warn"' in out.replace(" ", ""), (
        f"JSON must carry the real severity, not a hardcoded block:\n{out}"
    )
