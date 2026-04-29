# Cross-Review Readiness Package — #2374 Transient-Promotion Candidate Queue

> **Feed:** 21
> **Machine:** ace-linux-1
> **Provider:** Claude Opus 4.6
> **Date:** 2026-04-29
> **Feed chain:** feed16 (patch) → feed17 (review) → feed18 (patch) → feed19 (re-review) → feed20 (micro-patch) → **feed21 (cross-review readiness)**

---

## 1. Current Plan Status

| Field | Value |
|-------|-------|
| **Plan path** | `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md` |
| **Status header** | `draft` (line 3) |
| **Complexity** | T2 |
| **Issue** | [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) |
| **Plan length** | 459 lines (post-feed20 state) |
| **Adversarial review rows** | Claude MINOR (feed17, resolved in feed18); Codex PENDING; Gemini PENDING |

---

## 2. Feed19 / Feed20 Provenance Summary

### Feed19 — Cold-Context Re-Review (APPROVE_FOR_CROSS_REVIEW)

- Verified all 7 feed17 findings (3 MINOR, 4 LOW) resolved by feed18 patches
- Fresh adversarial pass found 3 LOW (N1–N3) and 3 INFO (N4–N6) — no MAJOR or MINOR
- Verdict: `APPROVE_FOR_CROSS_REVIEW` — plan structurally sound, evidence-rich, well-bounded vs siblings
- Result file: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-rereview-2374-feed19.md`

### Feed20 — Bounded Micro-Patch (COMPLETED_WITH_RESULT)

Applied exactly 3 optional edits from Feed19:

| Edit | Feed19 ID | What changed |
|------|-----------|-------------|
| Dedup key alignment | N2 | TDD test renamed from `dedupes_by_source_path_plus_summary` → `dedupes_by_normalized_summary_plus_issue_ref` (line 388) |
| Wiki lookup default | N3 | Pseudocode `existing_wiki_page_for(c)` ternary replaced with `"create"` default + comment (line 188) |
| Score threshold caveat | N6 | Added threshold divergence sentence to merge-contract paragraph (line 35) |

- Result file: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-micropatch-2374-feed20.md`

---

## 3. Feed21 Patch Verification (Read-Only)

All three Feed20 patches independently verified still present in the live plan file:

| Patch | Verification | Result |
|-------|-------------|--------|
| N2 (dedup key) | `grep 'dedupes_by' plan` → line 388 shows `dedupes_by_normalized_summary_plus_issue_ref` | **PRESENT** |
| N3 (wiki lookup) | `grep 'existing_wiki_page_for' plan` → only line 449 (Open Questions prose); absent from pseudocode line 188 which now reads `"create"  # v1: default` | **PRESENT** (old pseudocode correctly absent) |
| N6 (score threshold) | `grep 'Score threshold also diverges' plan` → line 35 | **PRESENT** |
| Old pseudocode absent | `grep '"extend" if existing_wiki_page_for' plan` → no matches | **CONFIRMED ABSENT** |

---

## 4. Readiness Verdict

### **READY_FOR_CROSS_REVIEW**

**Rationale:**
- All MINOR findings (feed17 F1–F3) resolved and verified across two independent passes (feed18 patch, feed19 re-review)
- All LOW findings (feed19 N1–N3) patched in feed20 and verified in this feed21 check
- Remaining INFO observations (N4, N5) are implementer-awareness items, not plan defects
- Feed19 verdict was explicit `APPROVE_FOR_CROSS_REVIEW`
- Plan has 459 lines, 12 distinct sources cited, 26 TDD tests, 12 testable acceptance criteria
- No outstanding MAJOR or MINOR findings
- Plan status correctly remains `draft` — no premature label advancement

---

## 5. Cross-Review Dispatch — Operator Manual Command Pack

### Why manual dispatch (not automated)

The `scripts/review/plan-review-fanout.sh` script has **no dry-run mode**. It directly invokes `claude`, `codex`, and `gemini` CLIs with real provider calls (10-minute timeout per provider). Since this lane is bounded to non-destructive artifact writing, the commands below are drafted for human-controlled execution.

### Pre-execution preflight (no-mutation, safe to run)

```bash
# 1. Verify plan file exists and is the expected size
wc -l docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md
# Expected: ~459 lines

# 2. Verify plan status is still 'draft'
head -5 docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md | grep 'Status:'
# Expected: > **Status:** draft

# 3. Verify no cross-review artifacts already exist for today
ls scripts/review/results/2026-04-29-plan-2374-*.md 2>/dev/null
# Expected: only this readiness file; no claude/codex/gemini verdict files

# 4. Verify issue is still OPEN and no parallel session has posted
gh issue view 2374 --json state,labels,updatedAt | jq -c '{s:.state,u:.updatedAt,l:[.labels[].name]}'
# Expected: state=OPEN

# 5. Verify no Hermes or parallel git operations in flight
pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)' || echo "No git operations in flight"

# 6. Verify the review prompt template exists
test -f scripts/review/plan-review-prompt.md && echo "Prompt template found" || echo "MISSING"

# 7. Verify provider CLIs are available
which claude codex gemini 2>/dev/null || echo "Some CLIs missing — check PATH"
```

### Cross-review dispatch command

```bash
# Full 3-provider fanout (Claude + Codex + Gemini in parallel)
# Expected output: scripts/review/results/2026-04-29-plan-2374-{claude,codex,gemini}.md
# Timeout: 600s per provider (configurable via PLAN_REVIEW_PROVIDER_TIMEOUT_SEC)
bash scripts/review/plan-review-fanout.sh \
  docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md
```

### Alternative: single-provider test run

```bash
# Run only Claude first to verify the pipeline works
bash scripts/review/plan-review-fanout.sh \
  docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md \
  --providers=claude
# Then inspect: cat scripts/review/results/2026-04-29-plan-2374-claude.md
```

### Post-dispatch verification

```bash
# 1. Confirm all three artifacts exist
ls -la scripts/review/results/2026-04-29-plan-2374-{claude,codex,gemini}.md

# 2. Check verdicts (each should be APPROVE/MINOR/MAJOR, not UNAVAILABLE)
for p in claude codex gemini; do
  echo "=== $p ==="
  grep -A1 '^## Verdict' scripts/review/results/2026-04-29-plan-2374-$p.md
done

# 3. Check disagreement report if generated
cat scripts/review/results/2026-04-29-plan-2374-disagreement.md 2>/dev/null || echo "No disagreement file"

# 4. Update plan's Adversarial Review Summary table with actual verdicts
# (manual edit to lines 425-431 of the plan)
```

---

## 6. Boundary Reminders

1. **Cross-review does NOT equal approval.** After cross-review:
   - Verdicts are recorded in the plan's Adversarial Review Summary table
   - Plan status moves to `status:plan-review` (label change = user-gated)
   - Implementation remains BLOCKED until user moves label to `status:plan-approved`
   - Per `feedback_never_offer_to_self_label_plan_approved.md`: no agent may self-approve

2. **No implementation until:**
   - All three provider verdicts are in (or UNAVAILABLE with documented reason)
   - Plan's Adversarial Review Summary table is updated
   - GitHub label is moved to `status:plan-review` by authorized operator
   - User reviews and moves to `status:plan-approved`
   - Approval marker is revision-bound per [#2460](https://github.com/vamseeachanta/workspace-hub/issues/2460)

3. **Known Codex sandbox constraints** (from memory):
   - `codex exec` may hang on stdin if not redirected (the fanout script uses `</dev/null`)
   - codex-cli 0.124.0 had upstream stdin-hang regression; verify installed version
   - Codex sandbox blocks filesystem writes; MAJOR verdicts lacking fallback-read citation may be weakly grounded
   - Verify Codex findings locally before accepting MAJOR (per `feedback_cross_provider_review_payoff.md`)

4. **Known Gemini constraints** (from memory):
   - Gemini CLI exits 55 without `GEMINI_CLI_TRUST_WORKSPACE=true` (the fanout script sets this)
   - Gemini sandbox can't see sparse-checkout overlay; verify file-missing claims with `git ls-files` before accepting MAJOR (per `feedback_gemini_sandbox_overlay_blindness.md`)

---

## 7. Artifacts Written by This Lane

| # | Path | Purpose |
|---|------|---------|
| 1 | `scripts/review/results/2026-04-29-plan-2374-crossreview-readiness-feed21.md` | This readiness package |
| 2 | `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-crossreview-readiness-2374-feed21.md` | Lane result artifact |

---

## Boundary Compliance Statement

- Did NOT commit, push, or mutate git state
- Did NOT execute `plan-review-fanout.sh` or any provider CLI
- Did NOT mutate GitHub (no `gh issue comment`, labels, PRs, closes, merges)
- Did NOT create or edit `.planning/plan-approved/*` markers
- Did NOT implement code or launch tests
- Did NOT overwrite other lanes' result files
- Plan status remains `draft` — not marked approved
- All operations were read-only verification (grep, read)
