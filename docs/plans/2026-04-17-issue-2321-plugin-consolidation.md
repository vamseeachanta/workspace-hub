# Plan for #2321: Fix or remove failing semantic-scholar-mcp + consolidate gsd/sparc/workflows overlap

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2321
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2321-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/_archive/` pattern already established (referenced in #2290 and skills tooling) — used for deprecating skills without deleting.
- Found: `.claude/plugins.json` (and/or settings plugin entries) — plugin registry.
- Found: `scripts/skills/skill-usage-report.py` cross-reference graph — can identify overlapping skill families mechanically.
- Gap: no documented overlap map between `gsd:*`, `sparc:*`, `workflows:*`, `agents:*` families.
- Gap: no current-state document for MCP server health (#1804 evaluation was one-shot, not a live status).

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — harness hygiene | n/a | — |

### LLM Wiki pages consulted
- Not applicable.

### Documents consulted
- Issue #1804 — MCP server evaluation (evalview, insaits, token-optimizer, omega-memory).
- Issue #2316 — quarterly MCP server re-evaluation cadence (sibling: recurring cadence; this plan: one-shot cleanup).
- Issue #2258 — track Claude plugin inventory in ai-tools-status reports (inventory source).
- Issue #2290 — deduplicate 7 exact-copy skills (completed); pattern for archive-with-stub.
- Session `/plugin` log showing `Failed to reconnect to semantic-scholar-mcp` (primary acute signal).
- `docs/plans/2026-04-15-issue-2290-*.md` — precedent for archive mechanics.

### Gaps identified
- `semantic-scholar-mcp` configuration source is unknown — needs discovery (plugin manifest, ~/.claude/settings.json, or project settings).
- Overlap decisions between `gsd:orchestrator` ↔ `sparc:orchestrator` ↔ `workflows:workflow-execute` have never been written down.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2321-plugin-consolidation.md` |
| Overlap map | `docs/reports/plugin-consolidation-2026-04.md` |
| Archive moves (tracked) | `.claude/skills/_archive/<family>/<skill>/` |
| Archive READMEs | `.claude/skills/_archive/<family>/README.md` |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2321-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2321-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-17-plan-2321-gemini.md` |

---

## Deliverable

Two artifacts: (1) `semantic-scholar-mcp` either connects cleanly or is removed from plugin configuration with a cleanup note, and (2) `docs/reports/plugin-consolidation-2026-04.md` containing an overlap map with ≥5 canonical-vs-archive decisions, each implemented by moving archived skills under `.claude/skills/_archive/`.

---

## Pseudocode

```
# Phase 1 — acute: semantic-scholar-mcp
locate_plugin_config():
    check ~/.claude/settings.json
    check <repo>/.claude/settings.json, settings.local.json
    check any installed plugin manifests
    return config_paths_containing_semantic_scholar

diagnose_reconnect_failure():
    read error logs from session transcripts
    test: curl the API endpoint (if documented)
    test: verify token/env var presence

decide:
    if fixable: apply fix, verify /plugin reload succeeds
    else: remove config entry, document removal reason

# Phase 2 — overlap map
scan_skill_families():
    for family in [gsd, sparc, workflows, agents]:
        list all skill names under family
    identify orchestrator/reviewer/researcher/tester/coordinator clusters

for each overlap cluster:
    pick canonical (prefer gsd if all families have one, else prefer most-invoked per #2320 data if available)
    list siblings to archive
    draft one-line justification

# Phase 3 — execute archival
for each decision (canonical, [siblings]):
    git mv .claude/skills/<sibling>/ .claude/skills/_archive/<family>/<sibling>/
    write .claude/skills/_archive/<family>/README.md pointing to canonical
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | plugin config (tbd — one of `.claude/settings.json` / `settings.local.json` / `~/.claude/settings.json`) | fix or remove `semantic-scholar-mcp` |
| Create | `docs/reports/plugin-consolidation-2026-04.md` | overlap map, decisions, justifications |
| Move (git mv) | `.claude/skills/<family>/<sibling>/` → `.claude/skills/_archive/<family>/<sibling>/` | archival per decision |
| Create | `.claude/skills/_archive/<family>/README.md` (per family) | forward-pointer to canonical |
| Update | `docs/plans/README.md` | add row for this plan |

---

## TDD Test List

<!-- This is governance/cleanup work — "tests" here mean verification checks, not unit tests. -->

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_semantic_scholar_state | plugin either connects or is absent | fresh `/plugin` session | no "Failed to reconnect" for semantic-scholar-mcp |
| verify_archive_has_readme | every archived family has README pointer | walk `.claude/skills/_archive/<family>/` | README present per family moved-from |
| verify_canonical_still_present | canonical skills remain in original location | check each decision row | canonical path exists |
| verify_no_broken_skill_refs | `scripts/skills/skill-usage-report.py` runs clean | execute the script | exit 0, no MISSING_SKILL warnings for canonicals |
| regression_plugin_health | `/plugin` listing shows no half-installed state | fresh Claude Code session | success |

---

## Acceptance Criteria

- [ ] `semantic-scholar-mcp` either: (a) reconnects cleanly in a fresh `/plugin` session, OR (b) is fully removed from plugin config with removal noted in the consolidation report.
- [ ] `docs/reports/plugin-consolidation-2026-04.md` lists ≥5 canonical-vs-archive decisions with one-line justifications per row.
- [ ] Archived skills moved (git-tracked) under `.claude/skills/_archive/<family>/<skill>/`; each archived family has a README pointer to canonical.
- [ ] `scripts/skills/skill-usage-report.py` runs without MISSING_SKILL warnings for any canonical.
- [ ] Fresh session `/plugin` shows no failed reconnects.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Plugin config location TBD; no rollback plan; "≥5 decisions" gameable; archive may depend on #2320 data |
| Codex | MAJOR | (see scripts/review/results/2026-04-17-plan-2321-codex.md — correctness + scope issues) |
| Gemini | MAJOR | (see scripts/review/results/2026-04-17-plan-2321-gemini.md — correctness + scope issues) |

**Overall result:** FAIL — MAJOR from Codex+Gemini. Plan requires revision before user approval.

**Blockers to resolve before approval:** see per-provider review artifacts under `scripts/review/results/2026-04-17-plan-2321-*.md`.

---

## Risks and Open Questions

- **Risk:** Archiving a skill the user actively invokes. Mitigation: cross-check with #2320 invocation data (once available) or require explicit user confirmation in plan-approval step for each skill archived.
- **Risk:** `semantic-scholar-mcp` may be a third-party plugin the user wants to keep — removal should be last resort.
- **Risk:** Multiple settings locations may contain the plugin entry; partial cleanup leaves ghost state.
- **Open:** Which 5+ canonical-vs-archive decisions get surfaced in the report? Recommend these starting clusters: orchestrator (gsd vs sparc), reviewer (gsd vs sparc vs code-review), tester (gsd vs sparc), swarm (github:github-swarm vs agents:agent-spawning), researcher (gsd vs sparc).
- **Open:** Should `_archive` be git-tracked or gitignored? Current pattern (per #2290) is tracked for discoverability.

---

## Complexity: T2

**T2** — mixes config edit with structural repo moves; acceptance depends on runtime verification in a fresh plugin session.
