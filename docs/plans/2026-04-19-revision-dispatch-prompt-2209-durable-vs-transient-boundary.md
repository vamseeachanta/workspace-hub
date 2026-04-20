# Revision-dispatch prompt: #2209 durable-vs-transient knowledge boundary

> **Status:** dispatch-ready
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2209
> **Triggered by:** 2026-04-17 cross-provider adversarial review (13 findings) + 2026-04-19 parent #2205 amendments resolving Patterns 1/2/3
> **Predecessor prompt:** `docs/plans/2026-04-11-claude-agent-team-prompt-2209-durable-vs-transient-boundary.md`

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as a 4-role agent team:
1. Reviser
2. Validation Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

## Mission

Revise `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` to align with:
1. The 2026-04-19 amendments to the parent operating model (#2205)
2. The 13 findings from the 2026-04-17 cross-provider adversarial review

The deliverable already exists — this is a **revision pass**. Preserve content that doesn't conflict with amendments or findings.

## Authoritative inputs

| Input | Path | Role |
|---|---|---|
| Amended parent operating model | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (Sections 2, 3, 8.1 amended 2026-04-19) | Binding parent contract |
| Parent amendment summary | https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277238819 | Decision rationale |
| Claude adversarial review | `scripts/review/results/2026-04-17-plan-2209-claude-adversarial.md` | Findings to address |
| Codex adversarial review | `scripts/review/results/2026-04-17-plan-2209-codex-adversarial.md` | Findings to address |
| Existing deliverable | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | Revision target |
| Sibling — provenance contract (#2207) | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Read-only; adjacent contract |
| Sibling — conformance checks (#2206) | `docs/document-intelligence/pyramid-conformance-checks.md` | Read-only; adjacent contract |
| Wiki schema authority (engineering) | `knowledge/wikis/engineering/CLAUDE.md` | Authority for L3 frontmatter per Section 8.1 |

## Required revisions (driven by amendments)

### A. Remove invented "between L5 and L6" classification (parent Section 2)
- Section 4.4 classifies weekly-review artifacts as "Between L5 and L6 — Recurring operational evidence." The amended parent (Section 2 worked examples) declares this invention forbidden.
- Per parent guidance: **each individual recurring-operational run is L5** (execution-state evidence); synthesized findings across runs flow to L3 via the standard L5→L3 promotion path.
- Remove the "Recurring-operational artifact" class from the glossary. Update Sections 4.4, 5.1, 6.1 accordingly.
- Section 11 item 6 self-acknowledged this as "a pragmatic classification, not a formal new layer" — that acknowledgment is now incorrect; it was a violation. Replace with the corrected layer assignment.

### B. Reframe frontmatter required-set (parent Section 8.1)
- Section 10.1 prescribes `{title, tags, sources, added, last_updated}` with optional `promoted_from`.
- Reframe as **additional fields on top of the baseline floor** (`title`, `last_updated`, `doc_key`) rather than as a required-set.
- `doc_key` is NEW in the baseline floor — specify how durable pages should populate it.
- Specify which wiki domain(s) this boundary applies to; final binding lives in the relevant wiki `CLAUDE.md`, not in this doc.

### C. Adopt `<algorithm>:<hex>` identity form (parent Section 3)
- Any `doc_key` references in this document must use the namespaced form.

### D. Adopt `merged_at` terminology (parent Section 3)
- If this document references the `discovered` timestamp field anywhere (even implicitly when describing provenance records), use `merged_at`.

### E. Update cross-references
- Update Section references to point to the amended parent sections.
- Reference parent amendment comment.

## Required revisions (driven by 2026-04-17 findings)

Read both adversarial review files. Address every **MAJOR** finding with a fix or documented deferral. Address **MINOR** findings where cost is low. Document deferrals with rationale.

For each addressed finding, note in revision notes which finding ID was resolved and how.

## Constraints

### Allowed write paths
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (primary)
- `scripts/review/results/2026-04-19-revision-2209-claude-review.md`
- `scripts/review/results/2026-04-19-revision-2209-final-review.md`
- `.planning/plan-approved/2209.md` (create marker if missing)

### Read-only paths
- `docs/**`, `knowledge/**`, `scripts/review/results/**`

### Forbidden
- Modifying the parent operating model — already amended
- Modifying #2207 or #2206 deliverables — they have their own revision dispatches
- Modifying `data/**`, `scripts/data/**`, `scripts/knowledge/**` actual code or data
- Modifying `.claude/**`, `.codex/**`, `config/**`, `tests/**`
- Touching unrelated dirty/untracked files

## Execution steps

**STEP 1 — Ground**
- Read live `#2209` from GitHub.
- Read the amended parent (Sections 2 worked examples, 3, 8.1).
- Read both 2026-04-17 adversarial review files. Build a finding-disposition table.
- Read live wiki `knowledge/wikis/engineering/CLAUDE.md` for its required-set.

**STEP 2 — Revise**
- Apply amendments A–E.
- Apply finding-driven revisions.
- Preserve content that doesn't conflict.
- Add a "Revision history" section noting the 2026-04-19 amendment-driven pass.

**STEP 3 — In-run adversarial review**
- Write `scripts/review/results/2026-04-19-revision-2209-claude-review.md`.
- Adversarial stance: assume defects until proven otherwise.
- Verify the "Between L5 and L6" and "Recurring-operational artifact" terms have been fully purged and replaced with the parent's L5-with-L5→L3-promotion model.
- If MAJOR issues remain, revise before finalizing.

**STEP 4 — Integrator pass**
- Write `scripts/review/results/2026-04-19-revision-2209-final-review.md` with verdict.

**STEP 5 — Create marker + commit**
- Verify `.planning/plan-approved/2209.md` exists.
- Stage only allowed-write-path files.
- Commit: `chore(knowledge): revise #2209 durable/transient boundary per 2026-04-19 #2205 amendments`.
- Do NOT push.

**STEP 6 — GitHub update**
- Post a concise summary comment on `#2209`:
  - Document path
  - Amendments applied (A–E)
  - Finding disposition summary
  - Final review verdict
  - Residual risks

## Output contract

1. What changed
2. Final review verdict
3. Findings disposition table
4. Exact files changed
5. Exact GitHub comment posted
6. Exact commit SHA
7. Residual blockers or risks

## Quality bar

- Zero occurrences of "Between L5 and L6", "Recurring-operational artifact" as a layer class, or any other invented layer terminology.
- Frontmatter required-set reframed per Section 8.1.
- Every 2026-04-17 finding has explicit disposition.
