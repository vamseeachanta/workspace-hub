# Revision-dispatch prompt: #2206 single-source-of-truth pyramid conformance checks

> **Status:** dispatch-ready
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2206
> **Triggered by:** 2026-04-17 cross-provider adversarial review (14 findings) + 2026-04-19 parent #2205 amendments resolving Patterns 1/2/3
> **Predecessor prompt:** `docs/plans/2026-04-11-claude-agent-team-prompt-2206-conformance-checks.md`

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as a 4-role agent team:
1. Reviser
2. Validation Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

## Mission

Revise `docs/document-intelligence/pyramid-conformance-checks.md` to align with:
1. The 2026-04-19 amendments to the parent operating model (#2205)
2. The 14 findings from the 2026-04-17 cross-provider adversarial review

The deliverable already exists — this is a **revision pass**. Preserve content that doesn't conflict.

## Authoritative inputs

| Input | Path | Role |
|---|---|---|
| Amended parent operating model | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (Sections 2, 3, 8.1 amended 2026-04-19) | Binding parent contract |
| Parent amendment summary | https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277238819 | Decision rationale |
| Claude adversarial review | `scripts/review/results/2026-04-17-plan-2206-claude-adversarial.md` | Findings to address |
| Codex adversarial review | `scripts/review/results/2026-04-17-plan-2206-codex-adversarial.md` | Findings to address |
| Existing deliverable | `docs/document-intelligence/pyramid-conformance-checks.md` | Revision target |
| Sibling — provenance contract (#2207) | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Read-only |
| Sibling — durable/transient boundary (#2209) | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | Read-only |
| Wiki schema authority (engineering) | `knowledge/wikis/engineering/CLAUDE.md` | Authority for L3 frontmatter per Section 8.1 |
| Live writers | `scripts/data/document-index/phase-a-index.py`, `scripts/data/document-index/provenance.py` | Reality check for namespace + status + timestamp |
| Live data sample | `data/document-index/index.jsonl` (read a few lines only — file is large) | Reality check for status enum + identity prefixes |

## Required revisions (driven by amendments)

### A. Remove invented "L3-adjacent" classification (parent Section 2)
- Section 7.3 declares `docs/document-intelligence/ → L3-adjacent normative docs only`. The amended parent declares this an invented layer (forbidden per Section 2 worked examples).
- Per parent: **normative architecture documents (this operating model, child contracts under `docs/document-intelligence/`, conformance designs) are L3.** Reclassify accordingly.
- Update Section 7.3 ownership table to assign `docs/document-intelligence/` to **L3** with the rationale that these are durable architectural-knowledge artifacts.
- The previous self-fail caused by GUARD-1 (your own check would flag your own classification) is resolved.

### B. Strengthen GUARD-1 to detect forbidden inventions (parent Section 2)
- The parent now explicitly forbids: `"between L<n> and L<m>"`, `"L<n>-adjacent"`, `"hybrid layer"` classifications.
- GUARD-1 must detect these patterns in any child doc. Define the regex/string-match patterns.
- Pass signal: zero occurrences of forbidden patterns in `docs/document-intelligence/**` and `docs/governance/**`.

### C. Add new conformance check FRONT-1 — frontmatter baseline floor (parent Section 8.1)
- New check: Every wiki `CLAUDE.md` (`knowledge/wikis/*/CLAUDE.md`) must declare `title`, `last_updated`, and `doc_key` as required for L3 page frontmatter.
- Pass signal: each wiki `CLAUDE.md` lists all three baseline-floor fields in its required-set.
- Fail signal: missing any baseline-floor field, or downgrading any to "optional/recommended."

### D. Update DT-1 frontmatter signal (parent Section 8.1)
- Existing DT-1 pass signal requires `{title, tags, sources, last_updated}` — `sources` REQUIRED.
- Per Section 8.1, the per-wiki `CLAUDE.md` is the binding authority — DT-1 should defer to whatever the wiki `CLAUDE.md` declares as required, not hardcode `sources` as required.
- Reframe DT-1 as: "L3 pages MUST satisfy the required-set declared by the relevant wiki `CLAUDE.md`, which MUST itself satisfy the parent baseline floor."

### E. Update identity-namespace check (parent Section 3)
- Add a check that `doc_key` values match `<algorithm>:<hex>` form.
- Permitted prefixes: `sha256:` (canonical), `md5:` (legacy `og_standards` reads only — flag warning if `md5:` appears in a non-`og_standards` source).
- Bare-hex without prefix is a violation; emit warning.

### F. Update status-vocabulary check (parent Section 3)
- Add a check that `status` values fall within the parent superset: `gap | indexed | summarized | extracted | promoted | superseded | unreachable`.
- Children may use subsets; values outside the superset are violations.

### G. Add `merged_at` / `discovered` migration check (parent Section 3)
- Detect provenance records using legacy `discovered` field; emit informational notice (not a violation — backward compatibility is required).
- Detect new writes (commits after 2026-04-19) using `discovered` instead of `merged_at`; this IS a violation post-rename.

### H. Update cross-references
- All Section refs to point to amended parent.
- Reference parent amendment comment.

## Required revisions (driven by 2026-04-17 findings)

Read both adversarial review files. Address every **MAJOR** finding. Address **MINOR** findings where cost is low. Document deferrals.

For each addressed finding, note in revision notes which finding ID was resolved and how.

## Constraints

### Allowed write paths
- `docs/document-intelligence/pyramid-conformance-checks.md` (primary)
- `scripts/review/results/2026-04-19-revision-2206-claude-review.md`
- `scripts/review/results/2026-04-19-revision-2206-final-review.md`
- `.planning/plan-approved/2206.md` (create marker if missing)

### Read-only paths
- `docs/**`, `knowledge/**`, `scripts/review/results/**`, `scripts/data/document-index/**`, `data/document-index/**`

### Forbidden
- Modifying the parent operating model — already amended
- Modifying #2207 or #2209 deliverables — they have their own dispatches
- Implementing actual conformance check scripts — design only (this is the design doc, not the code)
- Modifying wiki `CLAUDE.md` files — checks design only; the wiki `CLAUDE.md` will be updated separately when conformance is enforced
- Modifying `.claude/**`, `.codex/**`, `config/**`, `tests/**`
- Touching unrelated dirty/untracked files

## Execution steps

**STEP 1 — Ground**
- Read live `#2206` from GitHub.
- Read the amended parent (Sections 2 worked examples + forbidden inventions, 3 namespace/status/`merged_at`, 8.1 schema authority + baseline floor).
- Read both 2026-04-17 adversarial review files. Build a finding-disposition table.
- Read all wiki `CLAUDE.md` files to understand current required-sets.
- Read a sample of `data/document-index/index.jsonl` to confirm namespace + status + timestamp realities.

**STEP 2 — Revise**
- Apply amendments A–H.
- Apply finding-driven revisions.
- Preserve content that doesn't conflict.
- Update the conformance check matrix (Section 5) with FRONT-1, the strengthened GUARD-1, the identity-namespace check, the status-vocabulary check, and the `merged_at` migration check.
- Add a "Revision history" section noting the 2026-04-19 amendment-driven pass.

**STEP 3 — In-run adversarial review**
- Write `scripts/review/results/2026-04-19-revision-2206-claude-review.md`.
- Adversarial stance: assume defects until proven otherwise.
- Verify: `docs/document-intelligence/` is now classified as L3 (not L3-adjacent). GUARD-1 is strong enough to catch the prior `"L3-adjacent"` and `"between L5 and L6"` violations. FRONT-1, namespace, status, and `merged_at` checks are concrete and testable.
- If MAJOR issues remain, revise before finalizing.

**STEP 4 — Integrator pass**
- Write `scripts/review/results/2026-04-19-revision-2206-final-review.md` with verdict.

**STEP 5 — Create marker + commit**
- Verify `.planning/plan-approved/2206.md` exists.
- Stage only allowed-write-path files.
- Commit: `feat(knowledge): revise #2206 conformance checks per 2026-04-19 #2205 amendments`.
- Do NOT push.

**STEP 6 — GitHub update**
- Post a concise summary comment on `#2206`:
  - Document path
  - Amendments applied (A–H)
  - Finding disposition summary
  - New checks added (FRONT-1, strengthened GUARD-1, namespace, status, `merged_at`)
  - Final review verdict
  - Residual risks

## Output contract

1. What changed
2. Final review verdict
3. Findings disposition table
4. New conformance checks added
5. Exact files changed
6. Exact GitHub comment posted
7. Exact commit SHA
8. Residual blockers or risks

## Quality bar

- Zero occurrences of "L3-adjacent" classification anywhere in the doc.
- GUARD-1 must explicitly enumerate the forbidden invention patterns from parent Section 2.
- FRONT-1 must be concrete enough that a future implementer can write the check without re-deriving the schema authority rule.
- Status, namespace, and `merged_at` checks must reference live writers as their reality grounding.
- Every 2026-04-17 finding has explicit disposition.
- Do NOT drift into implementing scripts.
