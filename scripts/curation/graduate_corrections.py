#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""graduate_corrections.py — auto-graduate high-confidence correction candidates to
DRAFT skill/memory/rule proposals, parked behind a HUMAN owner-review gate (#3252, epic #3248).

Closes epic gap #1: today every ``.claude/state/candidates/correction-promotions.yaml`` row
carries ``status: identified`` and a human hand-promotes each. This is a GUARDED auto-graduation:
high-confidence + repeated correction patterns become DRAFT proposals under a QUARANTINE tree
(``.claude/state/graduation/``) — never auto-merged into the canonical ``.claude/skills/`` tree
or ``.claude/skills-index.yaml``. Promotion draft → canonical is a separate, explicit human action.

Design (locked by docs/plans/2026-06-27-3252-auto-graduate-correction-candidates.md + r1/r2 review):
  * "Integrate, don't rebuild": reuses ``detect_skill_drift``'s pure-core + injectable-notify +
    last-seen-signature + machine-guard + rc-0-on-success idioms, and ``extract-learnings``'s
    bounded-emission cap. Reads the existing candidate file; it does NOT produce it (that is
    gap #5 / sibling #3254).
  * QUARANTINE is the gate. Drafts live under ``.claude/state/graduation/`` — structurally invisible
    to ``generate_skills_index.py`` (which keys on ``git ls-tree .claude/skills`` filtered to
    ``endswith("/SKILL.md")``). A new-skill scaffold is named ``SKILL.md.draft`` (never ``SKILL.md``)
    as belt-and-suspenders so even an accidental copy into the skills tree can't match the index glob.
  * The classifier treats any non-rules ``<plugin>/<skill>`` namespaced target (e.g.
    ``superpowers/writing-skills``) as an EXISTING-skill addition; ``new_skill`` is reserved ONLY for
    a bare slug absent from the index — so no current live row drafts a SKILL.md.draft (major-1 fix).
  * The OWNER-REVIEW gate stays HUMAN. The script applies NO ``status:`` label, runs NO ``gh``, makes
    NO commit into canonical, runs NO ``propagate-ecosystem.sh``. Terminal state is
    ``draft-parked / owner_review: pending`` in ``queue.yaml``.
  * Exit code is NOT overloaded (Rule 4): ``run_cli`` returns 0 on ANY successful run regardless of
    draft count (and 0 on the off-host guard no-op). New-draft state is signaled via the queue/ledger
    state files + a ``scripts/notify.sh`` ``pass`` event, never a non-zero rc.
  * Machine guard (Rule 6): the nightly wrapper (``comprehensive-learning-nightly.sh``) has NO guard
    of its own and the candidate file is git-committed everywhere, so ``run_cli`` self-guards on
    ``audit_skill_currency.machine_label()`` and no-ops (rc 0) off ``dev-primary``/``ace-linux-1``.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import yaml

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
GRAD_DIR = STATE / "graduation"                      # QUARANTINE — outside .claude/skills/
DRAFTS = GRAD_DIR / "drafts"
QUEUE = GRAD_DIR / "queue.yaml"
LEDGER = GRAD_DIR / "graduated.json"
LASTSEEN = GRAD_DIR / "last-seen.json"
PROMOTIONS_FILE = STATE / "candidates" / "correction-promotions.yaml"
SKILLS_INDEX = REPO / ".claude" / "skills-index.yaml"
NOTIFY_SH = REPO / "scripts" / "notify.sh"

# High-confidence floor + bounded emission. Mirrors extract-learnings.sh's MAX_ISSUES_PER_SESSION
# posture. Sibling #3256 will make GRADUATION_MIN_COUNT ADAPTIVE — keep it a single constant so #3256
# has exactly one change site.
GRADUATION_MIN_COUNT = 50
MAX_GRADUATIONS_PER_RUN = 3
EVIDENCE_PREVIEW_CHARS = 280            # bound rendered rationale; keeps drafts under the size hook
MAX_EVIDENCE_FILES = 8

DEV_HOSTS = {"dev-primary", "ace-linux-1"}

# Import the audit MODULE (not the function) so machine_label() resolves at CALL TIME and stays
# monkeypatchable — same idiom as detect_skill_drift.py. Same-dir module.
_CURATION_DIR = str(Path(__file__).resolve().parent)
if _CURATION_DIR not in sys.path:
    sys.path.insert(0, _CURATION_DIR)
import audit_skill_currency  # noqa: E402  (path set up above)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# PURE CORE — no IO, no clock, no subprocess
# --------------------------------------------------------------------------- #


def _pos_int(v) -> bool:
    """True for a strictly-positive plain int (rejects bool, an int subclass)."""
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def slug_for(theme: str) -> str:
    """Deterministic, stable slug — the dedup key across runs. PURE."""
    return re.sub(r"[^a-z0-9]+", "-", str(theme).lower()).strip("-")


def classify_target(target_skill: str, existing_skill_names) -> str:
    """Route a candidate's target into rule | memory | existing_skill | new_skill. PURE.

    Branch order is load-bearing (major-1): the ``"/" in target_skill`` namespace branch keeps a
    ``<plugin>/<skill>`` target (e.g. ``superpowers/writing-skills``) out of the new_skill path —
    it is a checklist-addition to an existing plugin skill, NOT a brand-new skill. ``new_skill`` is
    reserved ONLY for a bare slug that is absent from the committed index — the sole path that ever
    emits a ``SKILL.md.draft`` scaffold.
    """
    ts = str(target_skill or "")
    if ts.startswith(".claude/rules/"):
        return "rule"
    if ts == "auto memory (system prompt)":
        return "memory"
    if ts in (existing_skill_names or set()):
        return "existing_skill"            # bare slug present in the index
    if "/" in ts:
        return "existing_skill"            # <plugin>/<skill> namespaced add
    return "new_skill"                     # bare slug absent from the index


def select_candidates(promotions, *, min_count, already_graduated, cap) -> list:
    """Filter to high-confidence + repeated + not-already-graduated; highest-count first; cap. PURE."""
    already = already_graduated or set()
    eligible = [
        p for p in (promotions or [])
        if isinstance(p, dict)
        and p.get("status") == "identified"
        and _pos_int(p.get("correction_count"))
        and p.get("correction_count") >= min_count
        and slug_for(p.get("theme", "")) not in already
    ]
    return sorted(eligible, key=lambda p: -int(p["correction_count"]))[:cap]


def graduation_signature(parked_slugs) -> str:
    """Order-independent fingerprint of the parked-draft set (spam-suppression key). PURE.

    Mirrors detect_skill_drift.drift_signature: "CLEAN" when empty, else sorted pipe-join.
    """
    slugs = sorted(set(parked_slugs or []))
    return "CLEAN" if not slugs else "|".join(slugs)


def _existing_queue_slugs(queue) -> list:
    if not isinstance(queue, dict):
        return []
    return [d.get("slug") for d in (queue.get("drafts") or []) if isinstance(d, dict) and d.get("slug")]


def _addition(p: dict, *, now_iso: str, existing_skill_names) -> dict:
    theme = p.get("theme", "")
    return {
        "slug": slug_for(theme),
        "theme": theme,
        "correction_count": int(p["correction_count"]),
        "target_skill": p.get("target_skill"),                 # EXPLICIT field name (never "target")
        "target_kind": classify_target(p.get("target_skill"), existing_skill_names),
        "action": p.get("action"),
        "rationale": p.get("rationale"),
        "files": list(p.get("files") or []),
        "source_rank": p.get("rank"),
        "source_theme": theme,
        "status": "draft-parked",
        "owner_review": "pending",
        "created_at": now_iso,
    }


def evaluate(promotions, already_graduated, queue, last_seen, *, now_iso,
             existing_skill_names, min_count=GRADUATION_MIN_COUNT,
             cap=MAX_GRADUATIONS_PER_RUN) -> dict:
    """Decide what graduates, given the candidate list + ledger + queue + last-seen. PURE.

    ``alerts`` is non-empty (one ``pass`` event) ONLY when NEW slugs are parked AND the parked
    signature changed vs last-seen — an unchanged standing backlog never re-alerts.
    """
    picked = select_candidates(promotions, min_count=min_count,
                               already_graduated=already_graduated or set(), cap=cap)
    additions = [_addition(p, now_iso=now_iso, existing_skill_names=existing_skill_names)
                 for p in picked]
    parked = _existing_queue_slugs(queue) + [a["slug"] for a in additions]
    sig = graduation_signature(parked)
    last_sig = (last_seen or {}).get("signature") if isinstance(last_seen, dict) else None
    changed = sig != last_sig
    alerts = []
    if additions and changed:
        alerts.append({
            "status": "pass",
            "detail": (f"{len(additions)} correction candidate(s) graduated to DRAFT — "
                       f"owner review pending: {QUEUE}"),
        })
    return {
        "new_drafts": additions,
        "queue_additions": additions,
        "ledger_additions": [a["slug"] for a in additions],
        "alerts": alerts,
        "new_state": {"signature": sig, "updated_at": now_iso},
    }


# --------------------------------------------------------------------------- #
# THIN CLI — IO, clock, subprocess live here
# --------------------------------------------------------------------------- #


def _read_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def read_skill_index_names() -> set:
    """Return the set of bare ``name:`` skill slugs from .claude/skills-index.yaml.

    Walks ``categories[].skills[].name`` (skill names — NOT category names). Fail-soft to an empty
    set if the index is absent (it is gitignored / generated per-box) or unparseable. It will NEVER
    contain a ``<plugin>/<skill>`` namespaced string — those are routed by the classifier's
    ``"/"``-namespace branch, not by index membership.
    """
    data = _read_yaml(SKILLS_INDEX)
    names: set = set()
    if isinstance(data, dict):
        for cat in data.get("categories") or []:
            if not isinstance(cat, dict):
                continue
            for sk in cat.get("skills") or []:
                if isinstance(sk, dict) and sk.get("name"):
                    names.add(str(sk["name"]))
    return names


def _evidence_lines(addition: dict) -> list:
    """Basenames + a truncated rationale only — never absolute paths or raw client identifiers.

    The commit-time redact-client-pii.py pass is the load-bearing scrub; this is the belt.
    """
    files = [os.path.basename(str(f)) for f in (addition.get("files") or [])][:MAX_EVIDENCE_FILES]
    lines = []
    if files:
        lines.append("- Files frequently corrected: " + ", ".join(files))
    rationale = (addition.get("rationale") or "").strip().replace("\n", " ")
    if rationale:
        if len(rationale) > EVIDENCE_PREVIEW_CHARS:
            rationale = rationale[:EVIDENCE_PREVIEW_CHARS].rstrip() + "…"
        lines.append("- Rationale (truncated): " + rationale)
    return lines


def _apply_command(addition: dict) -> str:
    kind = addition.get("target_kind")
    target = addition.get("target_skill")
    if kind == "new_skill":
        return f"Run `/write-a-skill` to author a NEW skill for `{target}` (a bare slug not yet in the index)."
    if kind == "existing_skill":
        return f"Hand-edit the EXISTING skill `{target}` (checklist / guidance addition)."
    if kind == "rule":
        return f"Hand-edit the rule file `{target}`."
    if kind == "memory":
        return "Hand-edit the auto-memory (system prompt) guidance."
    return f"Review target `{target}` and apply manually."


def _proposal_md(addition: dict) -> str:
    lines = [
        f"# DRAFT graduation proposal — {addition.get('theme')}",
        "",
        "> **STATUS: draft-parked / owner_review: pending.** This is an automated DRAFT only.",
        "> A HUMAN owner must review and promote it. It is NOT a canonical skill/rule/memory and is",
        "> structurally invisible to `.claude/skills-index.yaml` and `propagate-ecosystem.sh`.",
        "",
        f"- **Source rank:** {addition.get('source_rank')}",
        f"- **Correction count:** {addition.get('correction_count')}",
        f"- **Target:** `{addition.get('target_skill')}`",
        f"- **Target kind:** {addition.get('target_kind')}",
        f"- **Proposed action:** {addition.get('action')}",
        f"- **Created at:** {addition.get('created_at')}",
        "",
        "## Evidence",
    ]
    lines += _evidence_lines(addition) or ["- (no bounded evidence available)"]
    lines += [
        "",
        "## Recommended human apply step",
        f"- {_apply_command(addition)}",
        "- After applying, mark this entry promoted in `queue.yaml` so the ledger never re-graduates it.",
        "",
    ]
    return "\n".join(lines)


def _skill_scaffold(addition: dict) -> str:
    """A non-canonical SKILL.md.draft scaffold (NEVER named SKILL.md). Belt-and-suspenders only."""
    return "\n".join([
        "---",
        f"name: {addition.get('target_skill')}",
        "description: DRAFT — owner must review before this becomes a canonical skill.",
        "---",
        "",
        f"# {addition.get('theme')} (DRAFT skill scaffold)",
        "",
        "<!-- This is a *.draft scaffold parked under .claude/state/graduation/. It does NOT match",
        "     the skills-index glob (endswith('/SKILL.md')) and must NOT be moved into .claude/skills/",
        "     without owner review + /write-a-skill. -->",
        "",
        f"Proposed because of {addition.get('correction_count')} repeated corrections "
        f"(rank {addition.get('source_rank')}).",
        "",
    ])


def render_draft(addition: dict) -> None:
    """Render a DRAFT proposal under the quarantine tree ONLY. Refuses to escape GRAD_DIR."""
    slug = addition["slug"]
    d = DRAFTS / slug
    # Belt-and-suspenders: the draft dir MUST live under the quarantine tree.
    assert _is_within(d, GRAD_DIR), f"refusing to write draft outside quarantine: {d}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "proposal.md").write_text(_proposal_md(addition), encoding="utf-8")
    if addition.get("target_kind") == "new_skill":
        # .draft suffix — NEVER exactly "SKILL.md" (would match the index glob).
        (d / "SKILL.md.draft").write_text(_skill_scaffold(addition), encoding="utf-8")


def _is_within(child: Path, parent: Path) -> bool:
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def _append_queue(additions: list) -> None:
    if not additions:
        return
    queue = _read_yaml(QUEUE)
    if not isinstance(queue, dict):
        queue = {}
    drafts = queue.get("drafts")
    if not isinstance(drafts, list):
        drafts = []
    have = {d.get("slug") for d in drafts if isinstance(d, dict)}
    for a in additions:
        if a["slug"] not in have:
            drafts.append(a)
    queue["drafts"] = drafts
    queue["updated_at"] = additions[0]["created_at"]
    _write_yaml(QUEUE, queue)


def _extend_ledger(slugs: list) -> None:
    if not slugs:
        return
    led = _read_json(LEDGER)
    existing = led.get("graduated") if isinstance(led, dict) else None
    if not isinstance(existing, list):
        existing = []
    merged = sorted(set(existing) | set(slugs))
    _write_json(LEDGER, {"graduated": merged})


def _read_ledger_set() -> set:
    led = _read_json(LEDGER)
    if isinstance(led, dict) and isinstance(led.get("graduated"), list):
        return set(led["graduated"])
    return set()


def _default_notify(alert: dict) -> None:
    """Real notifier: append one JSONL event via scripts/notify.sh (source=cron, job=skill-graduation)."""
    status = alert.get("status", "pass")
    detail = alert.get("detail", "")
    try:
        subprocess.run(
            ["bash", str(NOTIFY_SH), "cron", "skill-graduation", status, detail],
            check=False, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass                                         # a wedged notify.sh must never stall the cron


def run_cli(args: argparse.Namespace, notify_fn: Callable[[dict], None] = _default_notify) -> int:
    """Machine-guard, gather state, decide, render drafts to quarantine, persist, alert. Returns rc.

    Returns 0 on ANY successful run regardless of draft count (and 0 on the off-host guard no-op):
    the notify.sh ``pass`` event + the queue/ledger state files are the signal, NOT the exit code.
    A non-zero exit would abort the Windows cron under $ErrorActionPreference='Stop' — graduation
    deliberately never does that (Rule 4). NO ``gh``, NO canonical commit, NO ``status:`` label,
    NO ``propagate-ecosystem.sh`` — the owner-review gate is a HUMAN step.
    """
    machine = audit_skill_currency.machine_label()
    if machine not in DEV_HOSTS:                      # mirrors comprehensive-learning.sh:26-29
        print(f"graduate_corrections: dev-primary only (machine={machine}); no-op.")
        return 0                                      # Rule 4 + Rule 6: guarded, rc 0

    promotions_doc = _read_yaml(PROMOTIONS_FILE)
    promotions = (promotions_doc or {}).get("promotions", []) if isinstance(promotions_doc, dict) else []
    queue_doc = _read_yaml(QUEUE)
    res = evaluate(
        promotions,
        _read_ledger_set(),
        queue_doc if isinstance(queue_doc, dict) else {},
        _read_json(LASTSEEN),
        now_iso=_now(),
        existing_skill_names=read_skill_index_names(),
    )
    for a in res["queue_additions"]:
        render_draft(a)
    _append_queue(res["queue_additions"])
    _extend_ledger(res["ledger_additions"])
    _write_json(LASTSEEN, res["new_state"])
    for al in res["alerts"]:
        notify_fn(dict(al))

    n = len(res["new_drafts"])
    print(f"graduate_corrections: parked {n} new draft(s) (signature={res['new_state']['signature']})")
    return 0                                          # Rule 4: success rc is ALWAYS 0


def _build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Auto-graduate high-confidence correction candidates to DRAFT proposals "
                    "(owner-review-gated; dev-primary nightly only)."
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
