# Plan for #2528: Retire 6 Deprecated Email Skills + Update gmail-triage to Queue Model

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-06
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2528
> **Review artifacts:** scripts/review/results/2026-05-06-plan-2528-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.claude/skills/email/` — 15 active skill folders present (not 14 as issue body states); `gmail-operations` is an undocumented extra skill not inventoried in the issue body. The 6 deletion targets (`gmail-touchbase`, `gmail-unsubscribe`, `gmail-data-extraction`, `gmail-extract-and-clean`, `gmail-extract-archive`, `gmail-email-to-repo-extraction`) are all confirmed present as active folders.
- Found: `.claude/skills/email/_archived/` — all 6 deletion targets are confirmed present as archived twins: `gmail-data-extraction`, `gmail-email-to-repo-extraction`, `gmail-extract-and-clean`, `gmail-extract-archive`, `gmail-touchbase`, `gmail-unsubscribe`.
- Found: `knowledge/wikis/engineering/raw/papers/gmail-multi-account.md:15` — `related_skills: [himalaya, google-workspace, gmail-triage, gmail-unsubscribe, gmail-touchbase]` — two deprecated skill references that will break post-deletion.
- Found: `knowledge/wikis/engineering/raw/papers/gmail-triage.md:15` — `related_skills: [gmail-multi-account, himalaya, gmail-unsubscribe, gmail-touchbase]` — two deprecated skill references.
- Found: `knowledge/wikis/engineering/raw/papers/gmail-attachment-to-document.md:15` — `related_skills: [gmail-multi-account, gmail-email-to-repo-extraction, excel-workbook-to-python-cowork]` — one deprecated skill reference.
- Gap: `gmail-operations` skill purpose/disposition — not in issue body's analysis table; decision pending (see Open Questions).
- Conflict: `docs/email/WORKFLOW.md:38` marks `gmail-data-extraction` as "Keep for patterns, not workflow" but issue body marks it DELETE — this contradiction must be resolved before deletion (see Open Questions).

### Standards

Not applicable — this is a harness/skill-curation issue.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/raw/papers/gmail-touchbase.md` — archived-skill paper; confirms original path and umbrella-2026-04-29 archive destination; is NOT a callsite dependency.
- `knowledge/wikis/engineering/raw/papers/gmail-unsubscribe.md` — same pattern as gmail-touchbase.md; archived-skill paper only.
- `knowledge/wikis/engineering/raw/papers/gmail-triage.md:311` — "Old skills (gmail-extract-and-clean, gmail-extract-archive) use the deprecated archive-everything model — use the queue model instead" — confirms deprecation rationale.

### Documents consulted

- `docs/email/WORKFLOW.md` — canonical skills table; lists 8 active + 4 deprecated; marks `gmail-data-extraction` as "Keep for patterns, not workflow" (contradicts issue DELETE disposition); confirms state-label naming convention at line 46 (`wh-email/extracted`, `wh-email/awaiting-reply`, `wh-email/completed`, `wh-email/noise`).
- `docs/plans/2026-04-20-issue-2017-plan.md:253` — "Skill consolidation docs (includes state-label naming for future Gmail-mirror v2) | **#2019** | Downstream documentation; implementation deferred" — confirms state-label doc is a deliverable of this work.
- `docs/plans/2026-04-25-issue-2488-reconcile-untracked-active-skill-files-before-loss.md` — prior reconciliation work; confirmed `_archived/` twins were created by #2488 (closed 2026-04-27).
- `tests/skills/test_weekly_skills_audit.py:211` — uses `"gmail-data-extraction"` as a synthetic fixture name in a test helper; not a dependency on the active skill folder. Post-deletion test still passes.
- Related issue #2019 (open) — superseded by #2528; contains original 12→4 consolidation scope.
- Related issue #2488 (closed 2026-04-27) — created `_archived/` snapshots of the 4 deprecated skills; this plan deletes their active copies.

### Gaps identified

- `gmail-operations` skill disposition: new skill not in issue body; must decide KEEP vs DELETE before implementation.
- `gmail-data-extraction` DELETE vs KEEP conflict between issue body and WORKFLOW.md must be resolved.
- Three wiki raw papers have stale `related_skills` references that the issue body does not address; if not fixed, these become broken references after deletion.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-06 via GitHub MCP):
- `#2528` — OPEN — chore(skills): retire 6 deprecated email skills + update gmail-triage to queue model
- `#2019` — OPEN — skill consolidation (superseded by #2528)
- `#2488` — CLOSED — skill-file reconciliation (created _archived/ twins)
- `#2017` — OPEN — Email-as-Queue workflow (parent)

**File existence** (`ls` 2026-05-06T00:00Z):
- EXISTS: `.claude/skills/email/gmail-touchbase/`
- EXISTS: `.claude/skills/email/gmail-unsubscribe/`
- EXISTS: `.claude/skills/email/gmail-data-extraction/`
- EXISTS: `.claude/skills/email/gmail-extract-and-clean/`
- EXISTS: `.claude/skills/email/gmail-extract-archive/`
- EXISTS: `.claude/skills/email/gmail-email-to-repo-extraction/`
- EXISTS: `.claude/skills/email/_archived/gmail-touchbase/` (twin confirmed)
- EXISTS: `.claude/skills/email/_archived/gmail-unsubscribe/` (twin confirmed)
- EXISTS: `.claude/skills/email/_archived/gmail-data-extraction/` (twin confirmed)
- EXISTS: `.claude/skills/email/_archived/gmail-extract-and-clean/` (twin confirmed)
- EXISTS: `.claude/skills/email/_archived/gmail-extract-archive/` (twin confirmed)
- EXISTS: `.claude/skills/email/_archived/gmail-email-to-repo-extraction/` (twin confirmed)
- EXISTS (undocumented): `.claude/skills/email/gmail-operations/` — not in issue body analysis
- MISSING (new — this plan creates): `docs/security/email-skill-state-labels.md` (state-label naming convention doc)

**Line excerpts** (`grep -n related_skills knowledge/wikis/engineering/raw/papers/gmail-multi-account.md`):
```
15: related_skills: [himalaya, google-workspace, gmail-triage, gmail-unsubscribe, gmail-touchbase]
```

**Gap proofs**:
- `ls .claude/skills/email/ | wc -l` → 16 entries (15 skill folders + `_archived/`) → confirms 15 active skills, not 14 as issue states.
- `grep -rn "gmail-touchbase\|gmail-unsubscribe\|gmail-data-extraction\|gmail-extract-and-clean\|gmail-extract-archive\|gmail-email-to-repo-extraction" . --include="*.md" --include="*.py" --include="*.yaml" | grep -v "_archived/"` → returns only: (1) 2 historical plan-review files, (2) 1 test fixture (non-dependent), (3) 3 wiki raw papers with stale related_skills. No active code/workflow callsites.

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 6 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-06-issue-2528-retire-deprecated-email-skills.md` |
| Skills to delete | `.claude/skills/email/{gmail-touchbase,gmail-unsubscribe,gmail-data-extraction,gmail-extract-and-clean,gmail-extract-archive,gmail-email-to-repo-extraction}/` |
| Skills to update | `.claude/skills/email/gmail-triage/SKILL.md` |
| Docs to update | `docs/email/WORKFLOW.md` |
| Wiki papers to patch | `knowledge/wikis/engineering/raw/papers/gmail-multi-account.md`, `gmail-triage.md`, `gmail-attachment-to-document.md` |
| New doc | `docs/email/email-skill-state-labels.md` |
| Plan review — Claude | `scripts/review/results/2026-05-06-plan-2528-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-06-plan-2528-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-06-plan-2528-gemini.md` |

---

## Deliverable

A clean `.claude/skills/email/` directory with 8 active skills (down from 15), `gmail-triage` SKILL.md updated to the queue model, `docs/email/WORKFLOW.md` Skills table refreshed, three wiki raw papers patched to remove stale `related_skills` references, and `docs/email/email-skill-state-labels.md` created with the durable state-label naming convention.

---

## Pseudocode

Trivial — see Files to Change. No new functions; pure file deletions, content edits, and grep verification.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Delete folder | `.claude/skills/email/gmail-touchbase/` | Superseded by gmail-outreach; _archived/ twin exists |
| Delete folder | `.claude/skills/email/gmail-unsubscribe/` | Superseded by gmail-outreach; _archived/ twin exists |
| Delete folder | `.claude/skills/email/gmail-data-extraction/` | Deprecated archive model; _archived/ twin exists (resolve KEEP/DELETE conflict first — see Open Questions) |
| Delete folder | `.claude/skills/email/gmail-extract-and-clean/` | Deprecated archive model; _archived/ twin exists |
| Delete folder | `.claude/skills/email/gmail-extract-archive/` | Deprecated archive model; _archived/ twin exists |
| Delete folder | `.claude/skills/email/gmail-email-to-repo-extraction/` | Deprecated archive model; _archived/ twin exists |
| Modify | `.claude/skills/email/gmail-triage/SKILL.md` | Update to queue model; cross-link gmail-extract-and-act; remove related_skills references to deleted skills |
| Modify | `.claude/skills/email/gmail-multi-account/SKILL.md` | Remove gmail-unsubscribe and gmail-touchbase from related_skills |
| Modify | `docs/email/WORKFLOW.md` | Refresh Skills table: remove DEPRECATED rows for the 4 archive-model skills; update gmail-data-extraction row per resolved disposition |
| Modify | `knowledge/wikis/engineering/raw/papers/gmail-multi-account.md` | Remove gmail-unsubscribe, gmail-touchbase from related_skills |
| Modify | `knowledge/wikis/engineering/raw/papers/gmail-triage.md` | Remove gmail-unsubscribe, gmail-touchbase from related_skills |
| Modify | `knowledge/wikis/engineering/raw/papers/gmail-attachment-to-document.md` | Remove gmail-email-to-repo-extraction from related_skills |
| Create | `docs/email/email-skill-state-labels.md` | Durable state-label naming convention doc; referenced by #2017 v9 plan line 253 |
| Update | `docs/plans/README.md` | Add this plan to index |

---

## TDD Test List

T1 — tests are grep verifications rather than unit tests.

| Test name | What it verifies | Command | Expected output |
|---|---|---|---|
| `verify_folders_deleted` | 6 skill folders are gone | `ls .claude/skills/email/ \| grep -E "gmail-touchbase\|gmail-unsubscribe\|gmail-data-extraction\|gmail-extract-and-clean\|gmail-extract-archive\|gmail-email-to-repo-extraction"` | empty |
| `verify_archived_intact` | _archived/ twins untouched | `ls .claude/skills/email/_archived/ \| wc -l` | 6 |
| `verify_no_broken_callsites` | No non-archived active references to deleted skill names | `grep -rn "gmail-touchbase\|gmail-unsubscribe\|gmail-data-extraction\|gmail-extract-and-clean\|gmail-extract-archive\|gmail-email-to-repo-extraction" . --include="*.md" --include="*.py" --include="*.yaml" \| grep -v "_archived/"` | only historical plan-review files + test fixture (no active callsites) |
| `verify_gmail_triage_updated` | gmail-triage SKILL.md references queue model and gmail-extract-and-act | `grep -c "gmail-extract-and-act" .claude/skills/email/gmail-triage/SKILL.md` | ≥1 |
| `verify_state_labels_doc` | State-label doc exists with all 4 label names | `grep -c "wh-email/" docs/email/email-skill-state-labels.md` | ≥4 |
| `verify_active_count` | Exactly 8 active skills remain (plus _archived/) | `ls .claude/skills/email/ \| grep -v "_archived" \| wc -l` | 8 (or 9 if gmail-operations is kept; see Open Questions) |

---

## Acceptance Criteria

- [ ] 6 deprecated skill folders deleted: `gmail-touchbase`, `gmail-unsubscribe`, `gmail-data-extraction`, `gmail-extract-and-clean`, `gmail-extract-archive`, `gmail-email-to-repo-extraction`
- [ ] `_archived/` versions retained for all 6 (do not touch `_archived/`)
- [ ] `gmail-triage` SKILL.md updated to queue model; cross-links `gmail-extract-and-act`; no broken `related_skills` references
- [ ] `related_skills` frontmatter in remaining active skills refreshed — no references to deleted skills remain
- [ ] `docs/email/WORKFLOW.md` Skills table refreshed (DEPRECATED rows removed; gmail-data-extraction row updated per resolved disposition)
- [ ] `docs/email/email-skill-state-labels.md` created with all 4 label names (`wh-email/extracted`, `wh-email/awaiting-reply`, `wh-email/completed`, `wh-email/noise`)
- [ ] No callsite breakage: grep for deleted skill names returns only `_archived/` paths and historical plan-review files
- [ ] `gmail-operations` disposition documented (KEEP or DELETE with rationale)
- [ ] All verify_ grep tests pass

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

**Overall result:** Pending

---

## Risks and Open Questions

- **Open (blocker):** `gmail-data-extraction` disposition — WORKFLOW.md says "Keep for patterns, not workflow" (KEEP active) but issue body says DELETE. Recommend DELETE (has _archived/ twin; "patterns" value is preserved in the archived copy), but user must confirm before execution because WORKFLOW.md is a governance document.
- **Open (blocker):** `gmail-operations` skill disposition — undocumented class-level aggregator skill not inventoried in issue body. If KEEP: add to WORKFLOW.md Skills table. If DELETE: verify no callsites and add _archived/ twin. Recommend KEEP (meta-skill describes the overall category; low risk; cost of deletion is less clear than benefit).
- **Risk:** `tests/skills/test_weekly_skills_audit.py:211` uses `"gmail-data-extraction"` as a synthetic fixture string. This is a test helper that creates a fake skill folder in a temp dir; it is NOT a dependency on the active skill. Verify test still passes after deletion with `uv run pytest tests/skills/test_weekly_skills_audit.py -v`.
- **Risk:** Wiki raw papers in `knowledge/wikis/engineering/raw/papers/` have stale `related_skills` frontmatter. These are not validated at skill-load time today, but if a wiki-skills cross-reference tool ships, stale references would surface. Fix proactively as part of this plan.

---

## Complexity: T1

**T1** — pure file deletions and content edits; no new modules, no new tests beyond grep verifications. All target files are identified. Single-session execution is safe.
