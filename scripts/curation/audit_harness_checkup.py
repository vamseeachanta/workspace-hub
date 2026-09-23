#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""audit_harness_checkup.py — per-machine Claude Code harness-hygiene audit (#3408, epic #3058).

Emits the FACTS for the machine-equality `harness_checkup` line item — the `/doctor` local
diagnostics NOTHING else captures as a comparable per-box cell. The matrix
(build-equality-matrix.py::harness_checkup_verdict) maps these facts → verdict; this module also
carries the self-contained pure verdict (`checkup_category`) so the tier is unit-testable here.

Deliberately NON-duplicative (per the #3408 plan resource-intel):
  * `harness_version` / `harness_install` are ALREADY collected by equivalence-fingerprint.sh
    (#3059). This audit READS them from `.claude/state/equivalence/local-fingerprint.json` — it
    does not re-shell `claude --version`. Version *currency-vs-latest* is the new signal: the
    fingerprint only proves boxes equal EACH OTHER, so uniformly-stale boxes look "equivalent".
  * Per-provider runtime-symlink REPAIR is harness-install-doctor.sh (#3184) — different surface.

Facts graded (all allowlist-safe — counts / booleans / enums / the PUBLIC version strings only;
NEVER tokens, cron lines, env values, absolute paths, skill/plugin names, transcript content, or
denial-command strings — matching the collector serialization allowlist):
  * cc_version / cc_latest / version_current   (currency vs the published latest)
  * install_method                             (npm-global | native | other)
  * duplicate_installs                         (count of extra `claude` on PATH)
  * settings_parse_ok                          (every present settings-cascade file parses)
  * broken_agents                              (bad-frontmatter + same-dir name collisions)
  * unused_skills / unused_plugins             (lifetime-zero usage counters — NOT a transcript scan)
  * default_mode / auto_mode_default           (is auto mode the default here?)

Fail-closed: any collector that cannot prove its fact returns None/False; `checkup_category`
grades MISSING-EVIDENCE when the core evidence (settings parse + install method) is absent, so a
box that could not be audited never grades green. `version_current is None` (no network / essential-
traffic mode) is NOT penalised — unknown currency is not drift.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
HOME = Path.home()

# Reuse machine_label() from the sibling audit rather than re-implementing the host→label table.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Amber past this many lifetime-unused user skills (soft signal — clutter, never red). Tunable here;
# keep in sync with CLUTTER in build-equality-matrix.py::harness_checkup_verdict.
CLUTTER_SKILLS = 15

CHECKUP_OK = "CHECKUP-OK"
CHECKUP_DRIFTED = "CHECKUP-DRIFTED"
CHECKUP_BROKEN = "CHECKUP-BROKEN"
MISSING_EVIDENCE = "MISSING-EVIDENCE"

# Settings-cascade files parse-checked (existence-gated). USER scope + this repo's project scope.
_SETTINGS_FILES = [
    HOME / ".claude" / "settings.json",
    HOME / ".claude.json",
    REPO / ".claude" / "settings.json",
    REPO / ".claude" / "settings.local.json",
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


# ── collectors (each monkeypatchable; each fail-soft to a None/False/0 "no evidence" value) ────────
def _read_claude_json() -> dict | None:
    """Parse ~/.claude.json. None on absent/garbled (⇒ usage-counter facts unknown)."""
    p = HOME / ".claude.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _fingerprint_version_install() -> tuple[str | None, str | None]:
    """(harness_version, harness_install) READ from equivalence-fingerprint.sh's #3059 state —
    NOT re-collected. None,None when the fingerprint is absent/garbled/lacks the fields."""
    fp = REPO / ".claude" / "state" / "equivalence" / "local-fingerprint.json"
    try:
        d = json.loads(fp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return (None, None)
    if not isinstance(d, dict):
        return (None, None)
    v = d.get("harness_version")
    i = d.get("harness_install")
    return (v if isinstance(v, str) and v else None,
            i if isinstance(i, str) and i else None)


def _latest_version(install: str | None) -> str | None:
    """Latest published version for the install channel. None on failure, unknown install, or when
    essential-traffic is disabled (mirrors the built-in updater — the audit must not restore egress).
    Run from $HOME with a pinned registry so a project's committed .npmrc can't redirect the lookup."""
    if os.environ.get("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"):
        return None
    try:
        if install == "npm-global":
            r = subprocess.run(
                ["npm", "view", "@anthropic-ai/claude-code@latest", "version",
                 "--registry", "https://registry.npmjs.org/"],
                capture_output=True, text=True, timeout=25, cwd=str(HOME),
            )
            out = r.stdout.strip()
            return out.split()[0] if (r.returncode == 0 and out) else None
        if install == "native":
            import urllib.request
            with urllib.request.urlopen(
                "https://downloads.claude.ai/claude-code-releases/latest", timeout=25
            ) as resp:
                out = resp.read().decode("utf-8", "replace").strip()
            return out.split()[0] if out else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    return None


def _which_all_claude() -> list[str]:
    """All `claude` executables resolvable on PATH (for the duplicate-install count). Empty on none."""
    seen: list[str] = []
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if not d:
            continue
        cand = Path(d) / "claude"
        try:
            if cand.is_file() and os.access(cand, os.X_OK):
                rp = str(cand.resolve())
                if rp not in seen:
                    seen.append(rp)
        except OSError:
            continue
    return seen


def _duplicate_installs() -> int:
    return max(0, len(_which_all_claude()) - 1)


def _settings_parse_ok() -> bool:
    """True iff every PRESENT settings-cascade file parses as JSON. A single broken file (which the
    harness silently ignores wholesale) ⇒ False. Reads for PARSE ONLY — no values are retained."""
    for f in _SETTINGS_FILES:
        if not f.is_file():
            continue
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
    return True


def _frontmatter(text: str) -> dict:
    """Minimal YAML-frontmatter key extraction (name/description only) from a leading --- block."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def _broken_agents() -> int:
    """Count agent-definition defects: a file with a frontmatter `name` but no `description` never
    loads; two files in the SAME dir sharing a `name` collide (winner is unsorted-readdir order).
    Files with no `name` are co-located docs — skipped."""
    broken = 0
    for adir in (REPO / ".claude" / "agents", HOME / ".claude" / "agents"):
        if not adir.is_dir():
            continue
        names: dict[str, int] = {}
        for md in adir.rglob("*.md"):
            try:
                fm = _frontmatter(md.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            name = fm.get("name")
            if not name:
                continue                       # co-located doc, not an agent
            if not fm.get("description"):
                broken += 1                    # has name, missing description ⇒ won't load
            names[name] = names.get(name, 0) + 1
        broken += sum(c - 1 for c in names.values() if c > 1)   # each extra colliding def
    return broken


def _unused_counts() -> tuple[int | None, int | None]:
    """(unused_skills, unused_plugins) from the LIFETIME usage counters in ~/.claude.json — never a
    transcript scan (r1 perf finding). unused_skills = user-skill dirs whose skillUsage counter is 0
    (bare OR dir-qualified key). unused_plugins = pluginUsage entries with usageCount 0. None,None
    when ~/.claude.json is unreadable (⇒ counts unknown, not silently zero)."""
    cj = _read_claude_json()
    if cj is None:
        return (None, None)
    skill_usage = cj.get("skillUsage", {}) if isinstance(cj.get("skillUsage"), dict) else {}
    used: set[str] = set()
    for k, v in skill_usage.items():
        try:
            if int(v.get("usageCount", 0)) > 0:
                used.add(k.split(":")[-1])
        except (AttributeError, TypeError, ValueError):
            continue
    sk_dir = HOME / ".claude" / "skills"
    unused_skills = 0
    if sk_dir.is_dir():
        for d in sk_dir.iterdir():
            try:
                if d.is_dir() and d.name not in used:
                    unused_skills += 1
            except OSError:
                continue
    plugin_usage = cj.get("pluginUsage", {}) if isinstance(cj.get("pluginUsage"), dict) else {}
    unused_plugins = 0
    for _, v in plugin_usage.items():
        try:
            if int(v.get("usageCount", 0)) == 0:
                unused_plugins += 1
        except (AttributeError, TypeError, ValueError):
            continue
    return (unused_skills, unused_plugins)


def _default_mode() -> str | None:
    """Effective user-scope permissions.defaultMode enum. None when unreadable/unset (⇒ not auto)."""
    p = HOME / ".claude" / "settings.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    mode = d.get("permissions", {}).get("defaultMode") if isinstance(d.get("permissions"), dict) else None
    return mode if isinstance(mode, str) else None


# ── pure verdict ──────────────────────────────────────────────────────────────────────────────────
def checkup_category(facts: dict, clutter: int = CLUTTER_SKILLS) -> str:
    """Pure facts→verdict. MISSING-EVIDENCE when core evidence is absent (settings_parse_ok or
    install_method is None). CHECKUP-BROKEN (red) on a hard defect: broken settings / duplicate
    installs / broken agents. CHECKUP-DRIFTED (amber) on a soft signal: behind latest / non-auto
    default / extension clutter. Else CHECKUP-OK. version_current None (unknown) is NOT drift."""
    if facts.get("settings_parse_ok") is None or facts.get("install_method") is None:
        return MISSING_EVIDENCE
    dup = facts.get("duplicate_installs")
    bad = facts.get("broken_agents")
    if (facts.get("settings_parse_ok") is False
            or (isinstance(dup, int) and dup > 0)
            or (isinstance(bad, int) and bad > 0)):
        return CHECKUP_BROKEN
    us = facts.get("unused_skills")
    up = facts.get("unused_plugins")
    if (facts.get("version_current") is False
            or facts.get("auto_mode_default") is False
            or (isinstance(us, int) and us > clutter)
            or (isinstance(up, int) and up > 0)):
        return CHECKUP_DRIFTED
    return CHECKUP_OK


def audit(machine: str | None = None, now: datetime | None = None) -> dict:
    if now is None:
        now = _now()
    if machine is None:
        import audit_skill_currency            # REUSE machine_label at call time (monkeypatchable)
        machine = audit_skill_currency.machine_label()

    version, install = _fingerprint_version_install()
    latest = _latest_version(install)
    version_current = None
    if version and latest:
        version_current = _semver_ge(version, latest)
    unused_skills, unused_plugins = _unused_counts()
    mode = _default_mode()

    facts = {
        "machine": machine,
        "audited_at": _iso(now),
        "schema_version": 1,
        "cc_version": version,
        "cc_latest": latest,
        "version_current": version_current,
        "install_method": install,
        "duplicate_installs": _duplicate_installs(),
        "settings_parse_ok": _settings_parse_ok(),
        "broken_agents": _broken_agents(),
        "unused_skills": unused_skills,
        "unused_plugins": unused_plugins,
        "default_mode": mode,
        "auto_mode_default": (mode == "auto"),
    }
    facts["checkup"] = checkup_category(facts)
    return facts


def _semver_ge(a: str, b: str) -> bool:
    """True iff version a >= version b, comparing numeric release parts, ignoring +build metadata."""
    def parts(v: str) -> list[int]:
        core = v.split("+", 1)[0].split("-", 1)[0]
        out = []
        for seg in core.split("."):
            try:
                out.append(int(seg))
            except ValueError:
                out.append(0)
        return out
    pa, pb = parts(a), parts(b)
    n = max(len(pa), len(pb))
    pa += [0] * (n - len(pa))
    pb += [0] * (n - len(pb))
    return pa >= pb


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Per-machine harness-checkup (/doctor) audit (#3408)")
    ap.add_argument("--machine", default=None)
    ap.add_argument("--stdout", action="store_true", help="print state JSON, do not write")
    a = ap.parse_args(argv)
    state = audit(a.machine)
    if a.stdout:
        print(json.dumps(state, indent=2))
        return 0
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"harness-checkup-{state['machine']}.json").write_text(json.dumps(state, indent=2) + "\n")
    print(f"audited {state['machine']}: version={state['cc_version']} current={state['version_current']} "
          f"dup={state['duplicate_installs']} settings_ok={state['settings_parse_ok']} "
          f"unused_skills={state['unused_skills']} auto={state['auto_mode_default']} → {state['checkup']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
