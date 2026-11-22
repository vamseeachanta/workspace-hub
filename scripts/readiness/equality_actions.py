"""Pure rollup and remediation policy for the equality matrix.

Policy and thresholds are preserved from build-equality-matrix.py at the
parent revision; this extraction changes no verdict or emitted action.
"""

from __future__ import annotations

# Worst-of severity for the collapsed group rollup. Higher = more operator attention.
# A group's rollup cell shows the worst verdict among its dims for that machine; an
# all-good group collapses to a single green "OK" so a clean box reads at a glance.
ROLLUP_SEVERITY = {
    "BELOW-BASELINE": 6, "DIVERGES": 6, "CURATED-EXPIRED": 6, "SKILLS-DRIFTED": 6, "MEMORY-EXPIRED": 6,
    "CHECKUP-BROKEN": 6, "PUBLISH-GATED": 6,
    "MISSING-BASELINE": 5, "NO-MAJORITY": 5, "CURATED-STALE": 5, "SKILLS-INDEX-STALE": 5, "MEMORY-STALE": 5,
    "SKILL-LINKS-DRIFTED": 5, "CHECKUP-DRIFTED": 5, "PUBLISH-STALE": 5,
    "MISSING-EVIDENCE": 4, "PENDING": 4,
    "STALE-CHECKOUT": 3,
    "EXPECTED-DIFF": 1, "EXPECTED-DIVERGENCE": 1, "UNREACHABLE": 1, "ABSENT": 1,
    "CONFORMS": 0, "EQUAL": 0, "PARITY": 0, "CURATED-FRESH": 0, "SKILLS-CURRENT": 0, "MEMORY-FRESH": 0,
    "SKILL-LINKS-OK": 0, "CHECKUP-OK": 0, "PUBLISH-OK": 0,
}


def rollup_verdict(verdicts: list[str]) -> tuple[str, str]:
    """(label, css_class) for a group's per-machine rollup cell. Unknown verdicts grade
    at MISSING-EVIDENCE severity (fail-soft, never silently 'OK')."""
    if not verdicts:
        return ("n/a", "na")
    worst = max(verdicts, key=lambda v: ROLLUP_SEVERITY.get(v, 4))
    if ROLLUP_SEVERITY.get(worst, 4) == 0:
        return ("OK", "ok")
    return (worst, worst.lower())


# ── remediation playbook (verdict → action) — keep in sync with the verdict→fix table in
#    .claude/skills/workspace-hub/ecosystem-equivalence-reconcile/SKILL.md + reconcile-ecosystem.sh
OK_VERDICTS = {"CONFORMS", "EQUAL", "PARITY", "EXPECTED-DIFF", "EXPECTED-DIVERGENCE",
               "UNREACHABLE", "ABSENT", "CURATED-FRESH", "SKILLS-CURRENT", "MEMORY-FRESH",
               "SKILL-LINKS-OK", "CHECKUP-OK", "PUBLISH-OK"}


def remediate(dim: str, verdict: str) -> tuple[str, str, bool] | None:
    """(action, assignee, by_design) for a non-OK cell; None if the cell needs no action.
    by_design=True means the cell can't/shouldn't reach green — it's expected, not a defect."""
    if verdict in OK_VERDICTS:
        return None
    is_provider = dim.startswith("harness:")
    if verdict == "MISSING-EVIDENCE":
        if is_provider:
            return (("capability not detected — or no Claude baseline on this host "
                    "(a Hermes-only box grades provider rows MISSING-EVIDENCE by design)"),
                    "by-design / operator", True)
        return (("no fresh report on this box — run the collector "
                "(equality-matrix-cron.sh; equality-report.ps1 on Windows)"), "this box", False)
    if verdict == "STALE-CHECKOUT":
        return ("checkout dirty / behind / stale ref — clean the tree, git fetch origin main, re-collect",
                "this box", False)
    if verdict == "BELOW-BASELINE":
        if dim == "solvers":
            return (("solver licence probe emits 'present', baseline wants 'licensed' — "
                    "Windows licence-probe follow-up"), "operator (Windows)", True)
        if dim == "data_access":
            return ("a required tier-1 repo isn't cloned here — clone the missing sibling", "this box", False)
        if dim == "compute":
            return ("under the declared cores/ram/gpu floor — upgrade box or retune harness-config floor",
                    "operator", False)
        return ("below the declared baseline — inspect this box's equality report", "operator", False)
    if verdict in ("DIVERGES", "NO-MAJORITY"):
        if is_provider:
            return (("capability diverges from the Claude baseline — refresh the report; "
                    "if persistent, install/repair that provider on this box"), "this box", False)
        if dim == "skills":
            return (("skills count differs — usually a tracked symlink materialized as a text file; "
                    "git config core.symlinks true, then rm + git checkout the symlink paths"), "this box", False)
        if dim in ("harness", "behavior"):
            return ("runtime/config drift — rebuild + install the soul runtime, then re-collect", "this box", False)
        if dim == "scheduler":
            return ("cron jobs differ — reconcile via setup-cron.sh --check, then re-collect", "this box", False)
        return (("differs from peers — OFTEN a stale-peer artifact; refresh ALL machines' reports first, "
                "then reconcile any genuine config drift"), "all boxes", False)
    if verdict == "MISSING-BASELINE":
        return ("no declared baseline for this dim — add one in harness-config.yaml", "operator", False)
    if verdict in ("CURATED-STALE", "CURATED-EXPIRED"):
        return (("session analysis + memory curation is stale (>12h orange / >24h red) — run "
                "the collector (bash scripts/curation/curate-session-memory.sh; "
                "curate-session-memory.ps1 on Windows) or repair the every-6h cron"), "this box", False)
    if verdict == "SKILLS-DRIFTED":
        return (("a provider's skill families UNEXPECTEDLY differ from canonical — reconcile via "
                "scripts/propagate-ecosystem.sh, or if the difference is intended, allowlist it in "
                "harness-config.yaml expected_skill_divergence"), "this box", False)
    if verdict == "SKILLS-INDEX-STALE":
        return (("the skills index has dangling entries (paths no longer in the tree) — regenerate "
                ".claude/skills-index.yaml (skills-curation cron / generator)"), "this box", False)
    if verdict in ("MEMORY-STALE", "MEMORY-EXPIRED"):
        return (("memory surfaces are stale (>36h orange / >72h red) — run the memory bridge "
                "(scripts/memory/bridge-hermes-claude.sh) or repair its cron"), "this box", False)
    if verdict == "SKILL-LINKS-DRIFTED":
        return (("shared-skill links are missing/broken on ecosystem repos (froze at link time) — "
                "re-sync via scripts/skills/resync-skill-links.sh --apply (or propagate-ecosystem.sh "
                "--skills-only)"), "this box", False)
    if verdict == "CHECKUP-BROKEN":
        return (("harness hygiene is broken — a settings file fails to parse, there are duplicate "
                "claude installs, or an agent def is broken/colliding; run /doctor on this box and "
                "apply its fixes"), "this box", False)
    if verdict == "CHECKUP-DRIFTED":
        return (("harness hygiene drift — behind the latest release, auto mode isn't the default, or "
                "unused skills/plugins have accumulated; run /doctor (claude update; set auto default; "
                "prune unused extensions)"), "this box", False)
    if verdict == "PUBLISH-GATED":
        return (("last equivalence publish failed or took gate-length time (>60s) — the #3500 "
                "pre-push RUN_ALL deadlock signature; check the pre-push hook and publish bypass"),
                "this box", False)
    if verdict == "PUBLISH-STALE":
        return ("no equivalence publish in >26h — run equivalence-sentinel.sh and inspect its cron logs",
                "this box", False)
    return ("investigate this cell's report", "operator", False)


