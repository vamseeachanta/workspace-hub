# Plan for #2324: Curate MEMORY.md index — consolidate stale project_* and feedback_*

> **Status:** implemented 2026-04-17 (direct on main — T1 editorial; see `docs/reports/memory-curation-2026-04.md`)
> **Complexity:** T1
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2324
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2324-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 37 lines. Sections: Feedback (5 entries), Project (14 entries), Tips (1 entry), References (2 entries).
- Found: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/` directory — 45 `.md` memory files; several are referenced from MEMORY.md, many are group headers (prefixed `>`).
- Found: `scripts/memory/` — exists at workspace-hub root; has bootstrap script (per `~/.claude/CLAUDE.md`). No curation tool exists today.
- Gap: no script validates index entries against underlying files or against closed/open issue status.

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — governance/hygiene work | n/a | — |

### LLM Wiki pages consulted
- Not applicable.

### Documents consulted
- Issue #1977 — remaining memory ecosystem work (backup/rollback, Windows sync) — sibling scope, not blocker.
- Issue #1782 — zero-loss agent learnings epic — parent; confirms MEMORY.md curation is within scope but narrow.
- Issue #2231 — memory regression coverage — test-side complement.
- `~/.claude/CLAUDE.md` — confirms MEMORY.md is the index loaded into context.
- Recon finding (corrected via GH comment on #2324): current file is **37 lines**, well below the 200-line truncation limit. The primary remediation value is staleness detection, not line-budget pressure.

### Gaps identified
- No mapping from each index entry to the open/closed status of the issues it references (e.g., `[Field-dev econ] DONE; follow-ups #2076,#2079,#2081`).
- No routine that cross-checks entry claims against current repo state (e.g., `[Tier-1 refactor] Ph1 DONE; Ph2A/2B ready` — is Ph2A still pending?).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2324-memory-md-curation.md` |
| Curation report | `docs/reports/memory-curation-2026-04.md` |
| MEMORY.md (updated) | `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` |
| Archived memory files (if any dropped) | `~/.claude/projects/.../memory/_archive/` |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2324-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2324-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-17-plan-2324-gemini.md` |

---

## Deliverable

A one-shot curation pass producing `docs/reports/memory-curation-2026-04.md` (disposition per entry with one-line reason) and an updated `MEMORY.md` where every entry has been verified against its underlying file and against current repo/issue state; obsolete entries archived.

---

## Pseudocode

```
for each entry in MEMORY.md:
    linked_file = parse_link(entry)
    if linked_file not exists: flag "broken link"
    
    # Cross-check Why-still-applies
    if entry mentions issue numbers:
        for each issue:
            gh issue view <number> --json state
            record open/closed
    
    # Heuristic disposition
    if all referenced issues closed AND entry body describes shipped work:
        disposition = "archive — all follow-ups closed"
    elif linked_file missing:
        disposition = "broken — investigate"
    elif siblings share theme (e.g., two field-dev entries):
        disposition = "consolidate candidate"
    else:
        disposition = "keep"
    
    record in report

apply dispositions:
    move archived files to _archive/
    rewrite MEMORY.md with kept + consolidated rollups
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/memory-curation-2026-04.md` | disposition + reasoning log |
| Modify | `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` | rewrite with curated index |
| Move (if any) | individual `*.md` memory files to `_archive/` | per-entry archival |
| Update | `docs/plans/README.md` | add row for this plan |

Note: the memory dir is under `~/.claude/`, not the workspace-hub repo. It may not be git-tracked. If not git-tracked, archival is local-disk only and the report is the durable record.

---

## TDD Test List

<!-- T1 governance/hygiene task — "tests" here are verification checks. -->

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_every_entry_has_linked_file | every `[name](file.md)` resolves | post-curation MEMORY.md | all files exist |
| verify_no_stale_issue_references | issues named in entries are open or explicitly marked closed | grep + `gh issue view` | each issue status recorded |
| verify_report_covers_all_entries | report has one row per pre-curation entry | diff entry counts | counts match |
| verify_line_count_reasonable | file remains well under 200-line truncation | wc -l | <150 |

---

## Acceptance Criteria

- [ ] `docs/reports/memory-curation-2026-04.md` lists every pre-curation entry with disposition (keep / consolidate / archive / broken) and one-line reason.
- [ ] Every entry in the post-curation `MEMORY.md` has a linked file that exists.
- [ ] Issues referenced in kept entries are cross-checked (open/closed status recorded in the report).
- [ ] No entry archived without the underlying file also moved to `_archive/` (if git-tracked) or clearly noted in the report (if local-only).
- [ ] Post-curation line count recorded in the report (before/after).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
**Wave v2 (2026-04-17, stance-contract applied):**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Memory-system conflation confirmed (target dir is NOT git-tracked; plan proposes `git mv` on a non-git dir); open question unresolved in plan body despite answer available; cross-machine-sync claim is a false premise inherited from wrong memory system; CI-checkable acceptance criteria target paths outside the repo |
| Codex | MAJOR | (see scripts/review/results/2026-04-17-plan-2324-codex.md) |
| Gemini | MAJOR | (see scripts/review/results/2026-04-17-plan-2324-gemini.md) |

**Overall result:** FAIL — MAJOR from all three providers. Plan requires re-scope before user approval.

**Blockers to resolve before approval:**
- Resolve memory-system ambiguity (target auto-memory per-machine OR repo `.claude/memory/` OR both, in explicit separate deliverables).
- All `git mv` references and CI-checkable acceptance criteria must be consistent with the chosen memory system's tracking status.
- See `scripts/review/results/2026-04-17-plan-2324-claude.md` for re-scope options.

---

## Risks and Open Questions

- **Risk:** Archiving an entry whose underlying work is still active. Mitigation: require explicit open-issue cross-check before archive.
- **Risk:** Memory dir may not be git-tracked — archival is local-only and loses disaster-recovery guarantee. Mitigation: the report IS the durable record; capture pre-state file listing in the report.
- **Risk:** Memory dir is shared across machines via sync (per `user/CLAUDE.md` "git-tracked, same on every machine"). If curated on one machine, changes need to propagate. Mitigation: run on the designated canonical machine (ace-linux-1 or dev-secondary per sync policy).
- **Open:** Is the memory dir at `~/.claude/projects/.../memory/` actually git-tracked? The bootstrap script header says "git-tracked" but this needs verification as part of Step 1.
- **Open:** Should consolidation merge two entries into one or keep both and just rewrite descriptions? Recommend: rewrite where rollup is clearly more informative; otherwise keep.

---

## Complexity: T1

**T1** — editorial/governance work, no new code, single output report + file rewrite. Upgraded from trivial because of the cross-machine sync wrinkle and the cross-check-with-GH-issues requirement.
