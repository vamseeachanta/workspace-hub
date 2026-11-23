# Revision-dispatch prompt: #2207 standards/codes provenance + reuse contract

> **Status:** dispatch-ready
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2207
> **Triggered by:** 2026-04-17 cross-provider adversarial review (11 findings) + 2026-04-19 parent #2205 amendments resolving Patterns 1/2/3
> **Predecessor prompt:** `docs/plans/2026-04-11-claude-agent-team-prompt-2207-provenance-reuse-contract.md`

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as a 4-role agent team:
1. Reviser
2. Validation Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

## Mission

Revise `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` to align with:
1. The 2026-04-19 amendments to the parent operating model (#2205)
2. The 11 findings from the 2026-04-17 cross-provider adversarial review

The deliverable already exists — this is a **revision pass**, not a from-scratch rewrite. Preserve content that does not conflict with the amendments or findings.

## Authoritative inputs

| Input | Path | Role |
|---|---|---|
| Amended parent operating model | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (Sections 2, 3, 8.1 amended 2026-04-19) | Binding parent contract |
| Parent amendment summary | https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277238819 | Decision rationale |
| Claude adversarial review | `scripts/review/results/2026-04-17-plan-2207-claude-adversarial.md` | Findings to address |
| Codex adversarial review | `scripts/review/results/2026-04-17-plan-2207-codex-adversarial.md` | Findings to address |
| Existing deliverable | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Revision target |
| Sibling — durable/transient boundary (#2209) | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | Read-only; adjacent contract |
| Sibling — conformance checks (#2206) | `docs/document-intelligence/pyramid-conformance-checks.md` | Read-only; adjacent contract |
| Wiki schema authority (engineering) | `knowledge/wikis/engineering/CLAUDE.md` | Authority for L3 frontmatter per Section 8.1 |
| Live identity writers | `scripts/data/document-index/phase-a-index.py`, `scripts/data/document-index/provenance.py` | Reality check for namespace + status + `merged_at` |

## Required revisions (driven by amendments)

### A. Adopt `<algorithm>:<hex>` identity form (parent Section 3)
- Rewrite identity references to use `<algorithm>:<hex>` form.
- Add explicit handling for `sha256:` (canonical) and `md5:` (legacy `og_standards` only, no hard sunset).
- Treat bare-hex as `sha256:` for compatibility, emit conformance warning.

### B. Adopt parent status vocabulary (parent Section 3)
- Replace #2207 Section 4.1 status enum (`indexed | summarized | extracted | promoted`) with the parent superset: `gap | indexed | summarized | extracted | promoted | superseded | unreachable`.
- May select a subset relevant to this contract's scope; may not redefine values.

### C. Rename `discovered` → `merged_at` (parent Section 3)
- Update all references in this contract.
- Document semantic: ISO-8601 UTC stamped at provenance-merge time, immutable per record.
- Note backward compatibility: readers accept both fields, prefer `merged_at`.

### D. Reframe frontmatter required-set (parent Section 8.1)
- Section 6.3's required-set (`{title, doc_key, source_ref, domain, promoted_from, last_updated}`) must be reframed as **additional fields layered on top of the baseline floor** (`title`, `last_updated`, `doc_key`).
- Specify which wiki domain(s) this contract requires fields for (engineering wiki is the primary; check if standards-promoted pages land in other wikis).
- Clarify that final binding occurs in the relevant wiki `CLAUDE.md`, not in this contract.

### E. Update cross-references
- Update Section references to point to the amended parent sections.
- Reference parent amendment comment.

## Required revisions (driven by 2026-04-17 findings)

Read both adversarial review files. Address every finding marked **MAJOR** with either a fix or a documented deferral with rationale. Address **MINOR** findings where the cost is low. Document any finding you defer with a sentence on why.

For each addressed finding, note in your revision notes which finding ID was resolved and how.

## Constraints

### Allowed write paths
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (primary)
- `scripts/review/results/2026-04-19-revision-2207-claude-review.md` (in-run adversarial review)
- `scripts/review/results/2026-04-19-revision-2207-final-review.md` (integrator verdict)
- `.planning/plan-approved/2207.md` (create marker if missing — empty file or one-line note is fine)

### Read-only paths
- `docs/**`, `knowledge/**`, `scripts/review/results/**`, `scripts/data/document-index/**`
- GitHub issue threads for related issues

### Forbidden
- Modifying the parent operating model (`llm-wiki-resource-doc-intelligence-operating-model.md`) — already amended; do not re-amend
- Modifying #2206 or #2209 deliverables — they have their own revision dispatches
- Modifying `data/document-index/*` actual data files — schema design only
- Modifying `scripts/data/document-index/*.py` writers — implementation rename of `discovered` → `merged_at` is delegated to a future code-side issue, not this revision
- Modifying `.claude/**`, `.codex/**`, `config/**`, `tests/**`
- Touching unrelated dirty/untracked files in the worktree

## Execution steps

**STEP 1 — Ground**
- Read live `#2207` from GitHub.
- Read the amended parent (Sections 2, 3, 8.1).
- Read both 2026-04-17 adversarial review files. Build a finding-disposition table.
- Read live wiki `knowledge/wikis/engineering/CLAUDE.md` to know its current required-set.
- Read live writers to confirm namespace + status + timestamp behavior.

**STEP 2 — Revise**
- Apply amendments A–E to the deliverable.
- Apply finding-driven revisions.
- Preserve any content that doesn't conflict with amendments or findings.
- Add a "Revision history" section noting the 2026-04-19 amendment-driven pass.

**STEP 3 — In-run adversarial review**
- Write `scripts/review/results/2026-04-19-revision-2207-claude-review.md`.
- Adversarial stance: assume defects until proven otherwise.
- Verify: parent compliance, finding disposition, no scope creep, frontmatter authority correctly delegated.
- If MAJOR issues remain, revise before finalizing.

**STEP 4 — Integrator pass**
- Write `scripts/review/results/2026-04-19-revision-2207-final-review.md` with verdict (APPROVE / MINOR / MAJOR).
- Confirm internal consistency.

**STEP 5 — Create marker + commit**
- Verify `.planning/plan-approved/2207.md` exists (create if not).
- Stage only allowed-write-path files.
- Commit message: `feat(doc-intel): revise #2207 provenance contract per 2026-04-19 #2205 amendments`.
- Do NOT push. User reviews before push.

**STEP 6 — GitHub update**
- Post a concise summary comment on `#2207`:
  - Document path
  - Amendments applied (A–E)
  - Finding disposition summary (count of FIXED / PARTIAL / DEFERRED)
  - Final review verdict
  - Residual risks
- Do not change labels.

## Output contract (return to dispatcher)

1. What changed (file-level summary)
2. Final review verdict
3. Findings disposition table
4. Exact files changed
5. Exact GitHub comment posted
6. Exact commit SHA
7. Residual blockers or risks

## Quality bar

- The revised contract MUST be internally consistent with the amended parent — Section 3 namespace, status, and `merged_at` rules MUST be honored verbatim.
- Section 8.1 authority delegation MUST be respected — this contract specifies fields it WANTS the wiki `CLAUDE.md` to require, but the binding lives in the wiki `CLAUDE.md` itself.
- Every 2026-04-17 finding must have an explicit disposition (FIXED / PARTIAL / DEFERRED with rationale).
- Do NOT drift into implementing the rename in code; document the contract only.
