# Execution-Readiness Audit + Runbook — Issue #2227

> **Audit date:** 2026-04-30
> **Subject issue:** [#2227 — feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis](https://github.com/vamseeachanta/workspace-hub/issues/2227)
> **Subject plan:** `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md`
> **Approval marker:** `.planning/plan-approved/2227.md`
> **Auditor lane:** plan-mode, read-only
> **Verdict:** **DO-NOT-EXECUTE-YET — approval-scope mismatch.** Branch A path is needed but is not the path that was approved. See §Critical Finding.

---

## Context

#2227 carries a `status:plan-approved` label and an approval marker file, so it surfaces as "ready to execute." A read-only audit was run to (a) verify live issue/PR/branch state, (b) extract the exact owned paths, tests, and acceptance criteria, (c) detect any work already shipped, and (d) produce an execution runbook a future isolated-worktree worker can follow without re-deriving context. The audit found one execution-readiness blocker (approval scope) and a clean, narrowly-scoped Branch A implementation path otherwise.

---

## Critical Finding — Approval Scope Mismatch (STOP gate)

The approval marker at `.planning/plan-approved/2227.md` records:

```
Approved revision: plan/issue-2227-ocimf-tandem-csa-z276-wiki-promotion @ b77bdd038f00c045a8816679233a4a6fd8e2de5f
Approved scope:    execute v5 Branch B when OCIMF preview content gate fails;
                   do not write wiki pages under Branch B.
```

**State today contradicts the precondition:**

- The OCIMF Tandem summary artifact at `data/document-index/summaries/sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json` is now content-rich (`summary` ~2 KB describing scope/TOC; `text_preview` quotes title page + Terms of Use). The `acma-wiki-unblock-2245-handoff.yaml` entry has `ready_for_2227: true` for OCIMF Tandem.
- Issue #2521 ("OCIMF-TANDEM-MOORING preview content extraction") closed 2026-04-29T17:30:52Z — that close is what flipped the gate.
- The most recent #2227 comment (2026-04-29T17:30:53Z, by vamseeachanta) acknowledges the unblock and frames Branch A as executable.
- No new approval comment has scoped Branch A. The label is stale relative to the new precondition.

**Worker rule:** the existing marker authorizes Branch B (no wiki writes) under a now-false condition. Writing wiki pages under the existing marker would violate the rule referenced in the project memory ([Issue #2460 approval binding](https://github.com/vamseeachanta/workspace-hub/issues/2460)) — approval is revision-bound, not status-label-bound. Re-approval needed before Branch A execution.

**Required user action before worker proceeds:** vamseeachanta posts a comment on #2227 along the lines of:

```
Branch A approved: OCIMF-TANDEM-MOORING summary content gate now PASS
(via #2521, closed 2026-04-29). Authorize wiki writes per v5 plan
@ <SHA on main with refreshed plan file>. Branch B path (no wiki writes)
is no longer applicable.
```

…and refreshes `.planning/plan-approved/2227.md` to bind to the new SHA + new "Approved scope: Branch A".

---

## Live Repository State (verified)

| Surface | State | SHA / ref | Notes |
|---|---|---|---|
| Issue #2227 | OPEN | n/a | labels: `enhancement`, `priority:medium`, `cat:documentation`, `agent:codex`, `status:plan-approved`; updated 2026-04-29T17:30:55Z |
| Approval marker | exists | binds `b77bdd038` | scope = Branch B only |
| Plan branch | exists | `plan/issue-2227-ocimf-tandem-csa-z276-wiki-promotion` @ `b77bdd038` | v5 plan content lives here |
| On-disk plan file | stale header | `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` | header says "v2"; v5 prose lives on the plan branch (read with `git show b77bdd038:docs/plans/...`) |
| Test file | merged to main | `b7f722569` (2026-04-21) via merge `ad1cbf5ee` (2026-04-28) | `tests/knowledge/test_ocimf_tandem_promotion.py` — 13 tests, Branch A skipped while gate fails |
| Wiki deliverables | NOT shipped | n/a | `ocimf-tandem-mooring.md` does not exist; `ocimf-meg4.md`, `index.md`, `log.md` unchanged |
| Codex execution branch | merged to main | `codex/burn-20260427-issue-2227` @ `b7f722569` | added Branch B guards only |
| Stray local branch | present | `claude/capacity-20260430-1841-issue-2227-wiki-promotion` | likely orphan from earlier capacity sweep; verify before reuse — do not push without checking |
| Content sub-gate | **PASS** today | `ready_for_2227: true`, summary ≠ "" | flipped on 2026-04-29 by #2521 |
| Marine taxonomy sub-gate | **FAIL** | n/a | CSA pages remain deferred to #2522 — out of scope here |
| Parent #2216 | OPEN | `status:plan-review` | child #2227 closure should comment-summary up to parent |

---

## Owned Paths (Branch A)

All paths absolute, repo root `/mnt/local-analysis/workspace-hub/`.

**Net-new file (one):**
- `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`

**Modify (three):**
- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — narrow cross-reference only
- `knowledge/wikis/engineering/wiki/index.md` — bump `## Standards (7 pages)` → `## Standards (8 pages)` and add row
- `knowledge/wikis/engineering/wiki/log.md` — append one promotion entry

**Already on main, do not touch:**
- `tests/knowledge/test_ocimf_tandem_promotion.py` (canonical test contract, see §Test Contract)
- `.planning/plan-approved/2227.md` (will be refreshed by user, not worker)

**Explicitly out of scope (do not create):**
- Any path under `knowledge/wikis/marine-engineering/wiki/standards/` (taxonomy + gitignore blocked; deferred to #2522)
- Any CSA-Z276 page under any wiki (#2522)
- `wiki/sources/` for OCIMF-TANDEM (vendor-derivative deny-list per `.claude/rules/calc-citation-contract.md` §7)

---

## Test Contract (authoritative — supersedes plan v2 prose where they differ)

Source of truth: `tests/knowledge/test_ocimf_tandem_promotion.py` on `main`. Worker must satisfy each test below; failures here are blockers, not warnings.

| ID | Test name | Pre-write requirement | Post-write requirement |
|---|---|---|---|
| T1 | `test_prereq_content_sub_gate_evaluation` | passes today (gate PASS) | continues to pass |
| T2 | `test_branch_b_no_wiki_writes_when_gate_fails` | currently passes vacuously (no writes) | skipped on Branch A; Branch A bypasses by virtue of gate=PASS |
| T3 | `test_ocimf_tandem_page_exists` | n/a | file at owned path must exist |
| T4 | `test_ocimf_tandem_frontmatter_valid` | n/a | frontmatter MUST include all of: `title`, `tags`, `added`, `last_updated`, `sources`, `domain`, `code_id`, `publisher`, `revision` — and `domain == "marine"`, `code_id == "OCIMF-TANDEM-MOORING"` |
| T5 | `test_ocimf_tandem_provenance_fields` | n/a | body must contain `doc_key: sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af`, the literal token `source_ref`, and `promoted_from: 2227` |
| T6 | `test_ocimf_tandem_cross_reference_to_meg4` | n/a | body must contain `[[ocimf-meg4]]` OR the substring `ocimf-meg4.md` |
| T7 | `test_ocimf_meg4_scope_narrow` | n/a | meg4 diff: ≤ 10 added lines, **0 removed lines**, at most one `## Related Standards` heading; every other added line MUST mention `OCIMF-TANDEM-MOORING` or `[[ocimf-tandem-mooring]]` |
| T8 | `test_engineering_index_has_tandem_row` | n/a | section `## Standards (8 pages)` must exist (regex `## Standards \(8 pages\)`) and contain `ocimf-tandem-mooring.md` |
| T9 | `test_engineering_log_has_promotion_entry` | n/a | log must contain regex `## \[\d{4}-\d{2}-\d{2}\] ingest \| OCIMF-TANDEM-MOORING promotion \(#2227\)` |
| T10 | `test_no_out_of_scope_pages` | n/a | the only `wiki/standards/` page added in the diff vs `merge-base origin/main HEAD` is exactly `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` |
| T11 | `test_llm_wiki_lint_engineering_clean` | n/a | `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 |
| T12 | `test_content_has_discriminating_technical_evidence` | n/a | body (excluding frontmatter) > 200 words AND ≥ 2 of: a multi-segment numeric ref like `1.2.3`, a quantity-with-units (`kN`, `t`, `m`, `ft`, `deg`, `kts`, `knots`, `MT`, `bar`, `kPa`, `MPa`), or a named OCIMF artifact (`12-point spread`, `submarine hoses`, `Yokohama fender`, `quick-release hook`, `chafe chain`) |
| T13 | `test_ocimf_tandem_has_inbound_link` | n/a | at least one other engineering wiki .md file (≠ tandem page) must contain `[[ocimf-tandem-mooring]]`, `](standards/ocimf-tandem-mooring.md)`, or `](/knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md)` |

T7 + T13 interact: the meg4 cross-reference satisfies T13 if it uses one of the accepted link patterns. Don't satisfy T13 via index.md alone unless the link there matches one of the three accepted forms; index links typically use shorter relative paths and may not match — meg4 is the safer satisfier.

T12 named-artifacts hint: the source `text_preview` already mentions "submarine hoses" and "chafe chain" — quoting these into the body satisfies category (3). Adding any displacement / hawser-tension figure with units satisfies category (2). One of either is enough alongside one of the others for the count-≥-2 rule.

---

## Verification Commands

### Pre-flight (run from any clean worktree, no writes)

```bash
# 1. Read v5 plan from approved revision (NOT the on-disk file)
git show b77bdd038:docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md

# 2. Confirm content sub-gate
jq '{ready_for_2227, summary_len: (.summary | length), preview_len: (.text_preview | length)}' \
  data/document-index/summaries/sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json

# 3. Confirm tests T1/T2 pass on the worktree as a baseline
uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v

# 4. Confirm meg4, index, log are unchanged from main
git diff origin/main -- knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md \
                       knowledge/wikis/engineering/wiki/index.md \
                       knowledge/wikis/engineering/wiki/log.md

# 5. Confirm parent #2216 is still OPEN and accepting summary comments
gh issue view 2216 --repo vamseeachanta/workspace-hub --json state,labels

# 6. Verify approval has been refreshed for Branch A (REQUIRED — see §Critical Finding)
gh issue view 2227 --repo vamseeachanta/workspace-hub --comments | grep -A3 "Branch A approved"
cat .planning/plan-approved/2227.md  # Approved scope must reference Branch A
```

If step 6 returns nothing, **STOP** — do not write wiki pages.

### Post-implementation (gate to commit / push)

```bash
uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v
# expect all 13 to PASS (T2 may skip on Branch A — that's expected)

uv run scripts/knowledge/llm_wiki.py lint --wiki engineering
# expect exit 0
```

### Verification-close (after Branch A ships, before closing #2227)

```bash
# All deliverables on main?
git -C /mnt/local-analysis/workspace-hub log --all --oneline \
    --grep="2227" --grep="OCIMF-TANDEM" -n 30

# Page exists on main?
git ls-files knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md

# Test suite green on main?
uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v

# Lint clean on main?
uv run scripts/knowledge/llm_wiki.py lint --wiki engineering

# Parent #2216 received summary comment?
gh issue view 2216 --repo vamseeachanta/workspace-hub --comments \
    | grep -i "ocimf-tandem.*#2227"
```

If all five succeed, #2227 is closure-eligible. (The auditor lane must not close issues; flag closure to user.)

---

## Worktree Worker Runbook

Future worker assumed to be running on a separate session in an isolated worktree. Read this section verbatim.

### W0. Refuse-to-execute checks

1. Approval scope: `.planning/plan-approved/2227.md` must mention "Branch A" and bind to a SHA on or after the SHA where the v5 plan file was refreshed on main. If absent, **STOP**, post a comment on #2227 quoting this section, exit.
2. Stray-branch hygiene: if `claude/capacity-20260430-1841-issue-2227-wiki-promotion` still exists locally, do **not** check it out — confirm it is unmerged and stale, then leave it alone (deletion is out of scope for this lane).
3. Confirm `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` shows no Hermes cleanup loop on main; if found, work in a worktree on a feature branch and let Hermes settle (per [hermes-active preflight check](#) memory).

### W1. Worktree setup

```bash
cd /mnt/local-analysis/workspace-hub
git fetch origin
git worktree add .claude/worktrees/issue-2227-branch-a -b feat/issue-2227-branch-a-ocimf-tandem-promotion origin/main
cd .claude/worktrees/issue-2227-branch-a
```

`.claude/worktrees/` is gitignored per [worktree gitlink pollution](#) memory — do not push that path; push only the feature branch.

### W2. Author the OCIMF Tandem page

Write `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`. Frontmatter MUST satisfy T4; body MUST satisfy T5/T6/T12. Skeleton:

```markdown
---
title: OCIMF Tandem Mooring & Offloading Guidelines for Conventional Tankers at F(P)SO Facilities
code_id: OCIMF-TANDEM-MOORING
publisher: Oil Companies International Marine Forum
revision: 1st Edition (2009)
domain: marine
tags: [ocimf, tandem-mooring, fpso, offloading, hawser, chafe-chain]
added: 2026-XX-XX
last_updated: 2026-XX-XX
sources:
  - doc_key: sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af
    source_ref: acma_codes/OCIMF/OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf
cross_links:
  - ocimf-meg4
---

> doc_key: sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af
> source_ref: ledger/acma_codes/OCIMF/OCIMF-TANDEM-MOORING
> promoted_from: 2227

# OCIMF Tandem Mooring & Offloading Guidelines

(>200 words of content grounded ONLY in the summary + text_preview of the source.
Cover: scope, FPSO/FSO offloading philosophy, subsea mooring arrangements,
basis of design, tandem mooring configuration, single/dual hawser systems,
**chafe chain**, fairlead, weak link, hawser handling/storage/retirement,
**submarine hoses**. Include at least one quantity with units (kN/t/m/MT) AND
keep at least two named-artifact terms from the T12 list.)

See also: [[ocimf-meg4]].
```

Notes:
- `added` and `last_updated` use today's date; if execution spans midnight UTC, both should be the day of authorship.
- The `> doc_key:` / `> source_ref:` / `> promoted_from:` block is what T5 regex-matches; keep tokens literal (the test does substring search, not YAML parse).
- Body content must be drawn strictly from the summary artifact (`summary` + `text_preview`); do not invent figures or quote paragraphs not present there. The grounding contract is what makes this defensible to reviewers.

### W3. Modify `ocimf-meg4.md` (≤10 added lines, 0 removed)

Add at the bottom of the existing page exactly one new section, e.g.:

```markdown

## Related Standards
- [[ocimf-tandem-mooring]] — OCIMF-TANDEM-MOORING covers tandem mooring/offloading at F(P)SO facilities (complements MEG4 for conventional tanker tandem operations).
```

That's 4 added lines (counting blank line + heading + bullet + trailing blank). Stay ≤ 10. Every non-heading added line must mention either `OCIMF-TANDEM-MOORING` or `[[ocimf-tandem-mooring]]` per T7.

This step is what satisfies T13 (inbound link via `[[ocimf-tandem-mooring]]` pattern).

### W4. Update `index.md`

Locate `## Standards (7 pages)` and:

1. Bump heading to `## Standards (8 pages)`.
2. Add a row to the Standards table for `ocimf-tandem-mooring.md`. Match the column shape of existing rows (do not invent new columns).

### W5. Append `log.md`

Add at the bottom (or appropriate chronological slot):

```markdown
## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)
- Promoted from acma_codes ledger entry sha256:5e5f61e785... .
- Net-new page at `wiki/standards/ocimf-tandem-mooring.md`.
- Narrow cross-reference appended to `wiki/standards/ocimf-meg4.md`.
- Source: OCIMF *Tandem Mooring & Offloading Guidelines for Conventional Tankers at F(P)SO Facilities*, 1st Ed. 2009.
```

YYYY-MM-DD must match the regex in T9; use today's UTC date.

### W6. Verify locally

```bash
uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v
uv run scripts/knowledge/llm_wiki.py lint --wiki engineering
```

If any test fails, fix the page/index/log/meg4 — do not relax the test. Tests are the contract.

### W7. Commit + push (one commit per logical unit)

```bash
git add knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md
git commit -m "docs(wiki): add OCIMF-TANDEM-MOORING standards page (#2227)"

git add knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md
git commit -m "docs(wiki): cross-reference OCIMF-TANDEM-MOORING from MEG4 (#2227)"

git add knowledge/wikis/engineering/wiki/index.md knowledge/wikis/engineering/wiki/log.md
git commit -m "docs(wiki): index + log entry for OCIMF-TANDEM-MOORING (#2227)"

git push -u origin feat/issue-2227-branch-a-ocimf-tandem-promotion
```

Per [parallel agent write-only pattern](#) memory: if multiple agents touch shared files, serialize commits in the main session — but a single worker in a dedicated worktree may commit directly. Watch for `[rejected]` on push and consult [reflog as ground truth](#) before retrying.

### W8. PR + parent comment

```bash
gh pr create --repo vamseeachanta/workspace-hub \
  --base main \
  --head feat/issue-2227-branch-a-ocimf-tandem-promotion \
  --title "feat(wiki): #2227 OCIMF-TANDEM-MOORING Branch A promotion" \
  --body "$(cat <<'EOF'
Closes #2227 (Branch A path).

Lands the OCIMF Tandem Mooring page in the engineering wiki per the v5 plan,
plus narrow MEG4 cross-reference, index update, and log entry. CSA-Z276
remains deferred to #2522.

Tests: tests/knowledge/test_ocimf_tandem_promotion.py — 13 tests pass.
Lint: scripts/knowledge/llm_wiki.py lint --wiki engineering — exit 0.

Approval: <link to refreshed approval comment>
Plan: docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md
EOF
)"
```

Comment on parent #2216 with implementation summary (per Branch A acceptance):

```bash
gh issue comment 2216 --repo vamseeachanta/workspace-hub --body "$(cat <<'EOF'
#2227 Branch A landed: OCIMF-TANDEM-MOORING promoted to
knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md.
13/13 acceptance tests pass; engineering wiki lint clean. CSA-Z276 split to #2522.
EOF
)"
```

This lane (audit) must NOT post these comments itself — that's the worker's job once approval is refreshed.

### W9. Hand off to user for #2227 close

The auditor and worker lanes do not close issues per the operator constraint at the top of this file. Once W8 lands, the worker posts an implementation summary on #2227 with PR link and yields close to vamseeachanta.

---

## Risks, in priority order

1. **Approval scope mismatch (P0).** Worker must refuse-to-execute until §W0 step 1 succeeds. This is the load-bearing safety property.
2. **Plan file drift on main vs plan branch.** On-disk plan still labeled v2; v5 prose is on `b77bdd038`. Worker must read v5, not the working tree. (`git show b77bdd038:docs/plans/...`)
3. **Test contract exceeds plan v2 prose.** T4 requires `code_id`/`publisher`/`revision`; T8 requires "(8 pages)" heading; T13 requires inbound link. Following plan prose alone fails these. Test file is canonical.
4. **Stray local branch.** `claude/capacity-20260430-1841-issue-2227-wiki-promotion` exists locally only; do not reuse without inspection. Likely orphan from an earlier capacity sweep.
5. **Hermes/auto-sync race.** Per memories, Hermes "remove unrelated files" loops can revert direct-to-main commits. Worker should always operate on a feature branch in a worktree, never push direct to main.
6. **T12 thinness.** With ~2 KB summary + ~1 KB preview as the only grounded source, hitting >200 words *with* technical evidence requires careful quoting. Don't pad with speculation — failing T12 is a worse outcome than a slightly tight body.
7. **CSA scope creep.** CSA pages are explicitly out of scope here. Defer all CSA work to #2522 even if reviewers ask. T10 is the guardrail.
8. **DRM/source-PDF deny-list.** Per `.claude/rules/calc-citation-contract.md` §7, do NOT cite the `wiki/sources/` mirror — cite the `standards/` page (this new one) and let any downstream calc citations point here.

---

## If Implementation Already Exists (verification-close path)

The audit found NO Branch A implementation on main — the wiki page does not exist, meg4/index/log are unchanged from before #2227 work began. So this section is contingent: if a future session lands the work and re-asks "is this done?", run the `Verification-close` block in §Verification Commands. All five checks must succeed; if any fail, the work is not yet shippable and the failing check names the gap (missing page → W2; failing T4 → frontmatter; failing T8 → index heading; failing T11 → lint findings; missing parent comment → W8 comment step).

---

## Out of Scope (do not expand into these)

- CSA-Z276 wiki standards pages → #2522 (and the marine-engineering taxonomy decision underneath it)
- Marine-engineering `wiki/standards/` directory creation or `.gitignore` exemption
- Re-extraction of CSA-Z276 source PDFs (separate issue tree)
- Issue-#2227 close action (auditor lane is read-only; worker hands off to vamseeachanta)
- GitHub label mutations (operator constraint)
- Any change to `tests/knowledge/test_ocimf_tandem_promotion.py` — the test file is the contract; worker satisfies, doesn't relax

---

## Files Critical to This Runbook (paths the worker will need)

| Purpose | Path |
|---|---|
| Approved plan (v5 prose) | `git show b77bdd038:docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` |
| Test contract | `tests/knowledge/test_ocimf_tandem_promotion.py` |
| Lint runner | `scripts/knowledge/llm_wiki.py` (cmd `lint`) |
| Approval marker | `.planning/plan-approved/2227.md` |
| Content gate inputs | `docs/reports/acma-wiki-unblock-2245-handoff.yaml`, `data/document-index/summaries/sha256:5e5f...json` |
| Existing MEG4 page (modify target) | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` |
| Engineering wiki schema | `knowledge/wikis/engineering/CLAUDE.md` |
| Citation-contract rule | `.claude/rules/calc-citation-contract.md` |
| Net-new page (create target) | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` |
| Index (modify target) | `knowledge/wikis/engineering/wiki/index.md` |
| Log (modify target) | `knowledge/wikis/engineering/wiki/log.md` |

---

**End of runbook. The auditor lane stops here. Awaiting the user's decision to refresh approval for Branch A; once refreshed, a worker session can execute §W0–§W9 mechanically.**
