# Plan for #2697: chore(ai-tools): refresh subscriptions.yaml with current Codex paid plan + bump declared totals

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2697
> **Review artifacts:** scripts/review/results/2026-05-20-plan-2697-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- `config/ai-tools/subscriptions.yaml` — current state: `last_updated: 2025-12-23`, `totals.monthly_subscriptions: 156.75`, 4 active subscriptions: `claude` ($106.60/mo), `openai` plus ($21.28/mo), `google_ai` ($19.99/mo), `github_copilot` ($8.88/mo via `monthly_equivalent` from annual $106.60). No `codex` block. Sum verified: $106.60 + $21.28 + $19.99 + $8.88 = $156.75 ✓. Note: `github_copilot` uses `annual_cost` + `monthly_equivalent` instead of `monthly_cost` — implementer must handle both field names in the arithmetic test.
- `config/ai-tools/pricing.yaml` — records per-model token rates (out of scope: per-API-call pricing, not subscription cost).
- `docs/BUSINESS_BRAIN.md` lines 58–63 — subscription table lists Codex as "Variable by authenticated account" with explicit caution: "verify Codex/OpenAI account availability from live machine/auth evidence before promising parallel lanes." Does NOT record Codex at $200/mo. Requires a reconciling update once the cost is confirmed.

### Standards

Not applicable.

### LLM Wiki pages consulted

Not applicable.

### Documents consulted

- Issue #2697 body — defines 5 changes: add codex block ($200/mo per issue body), update totals, update `last_updated`, reconcile `docs/BUSINESS_BRAIN.md`, add maintenance-contract comment per `feedback_doc_counter_rule_writetime`.
- `docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md` line 20 — prior plan explicitly flagged: "Stale: missing the Codex paid plan ($200/mo per `project_hermes_codex_quota` memory)." Confirms $200/mo figure originates from auto-memory (`project_hermes_codex_quota`), not from a live account screenshot — **implementer must verify the exact cost before committing the value**.
- `config/ai-tools/agent-capability-scores.yaml` — tags Codex as "HARD GATE" with the cross-review role; confirms Codex is an active system component warranting subscription tracking.

### Gaps identified

- `config/ai-tools/subscriptions.yaml` missing `codex` block and carrying stale totals (confirmed via file read).
- `project_hermes_codex_quota` memory node (the authoritative source) is in `~/.claude/projects/` auto-memory, not accessible via repo-tracked paths. The $200/mo figure is known from prior plan context but needs live-account confirmation before landing.
- `docs/BUSINESS_BRAIN.md` Codex row uses "Variable" placeholder — needs update to confirmed amount or a per-usage clarification.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-20 via GitHub MCP `issue_read`):
- `#2697` — OPEN — "chore(ai-tools): refresh subscriptions.yaml with current Codex paid plan + bump declared totals"
- `#2675` — referenced parent plan (closed) — AI ecosystem design

**File existence** (`ls config/ai-tools/` 2026-05-20):
- EXISTS: `config/ai-tools/subscriptions.yaml`
- EXISTS: `config/ai-tools/pricing.yaml`
- EXISTS: `config/ai-tools/agent-capability-scores.yaml`
- MISSING (this plan creates): `tests/config/test_subscriptions_yaml.py`

**Line excerpts** — current `subscriptions.yaml` totals block:
```yaml
totals:
  monthly_subscriptions: 156.75
  annual_projection: 1881.04
  currency: "USD"
  last_updated: "2025-12-23"
```

**Line excerpts** — `BUSINESS_BRAIN.md` subscription table rows (lines 58–63):
```
| Claude (Anthropic) | Claude Max | $200 max | Primary planning/orchestration subscription |
| Codex / OpenAI | Confirm active account before allocating load | Variable by authenticated account |
"treat Claude Max ($200) and Gemini ($20) as the baseline confirmed subscriptions for planning;
 verify Codex/OpenAI account availability from live machine/auth evidence"
```

**Gap proof** (`grep codex config/ai-tools/subscriptions.yaml` 2026-05-20):
```
(no output)
```
→ No codex block exists.

**Arithmetic** — new totals (pending live-account cost verification):
- Current declared: $106.60 + $21.28 + $19.99 + $8.88 = $156.75
- Codex at $200/mo (pending verification): $156.75 + $200.00 = $356.75
- New annual projection at $356.75/mo: $356.75 × 12 = $4,281.00

**Reproduction proof:**
N/A — config staleness issue, no runtime failure. Gap confirmed by visual inspection: `last_updated: "2025-12-23"` and absent `codex:` block. Skip intentional.

<!-- Verification: distinct sources: (1) issue body, (2) subscriptions.yaml current state,
     (3) BUSINESS_BRAIN.md lines 58–63, (4) prior plan #2675 line 20, (5) agent-capability-scores.yaml.
     Count: 5 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-2697-subscriptions-codex-refresh.md` |
| Modified config | `config/ai-tools/subscriptions.yaml` |
| Modified doc | `docs/BUSINESS_BRAIN.md` |
| Tests | `tests/config/test_subscriptions_yaml.py` |
| Plan review — Claude | `scripts/review/results/2026-05-20-plan-2697-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-20-plan-2697-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-20-plan-2697-gemini.md` |

---

## Deliverable

An updated `config/ai-tools/subscriptions.yaml` with a verified `codex` subscription block, corrected `totals.monthly_subscriptions` and `annual_projection`, refreshed `last_updated`, a maintenance-contract comment in the YAML preamble, and a reconciling update to `docs/BUSINESS_BRAIN.md` replacing the "Variable" Codex placeholder with the confirmed cost.

---

## Pseudocode

Trivial — see Files to Change. YAML edit is additive; math is `sum(monthly_costs) + sum(monthly_equivalents)`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/ai-tools/subscriptions.yaml` | Add `codex` block; update `totals.monthly_subscriptions`, `annual_projection`, `last_updated`; add maintenance-contract comment to preamble |
| Modify | `docs/BUSINESS_BRAIN.md` | Update Codex row from "Variable" to confirmed cost (or add note if cost is usage-metered, not flat) |
| Create | `tests/config/test_subscriptions_yaml.py` | TDD: validate YAML completeness and arithmetic correctness |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_subscriptions_has_codex_block` | `codex` key added | YAML load | `yaml['subscriptions']['codex']` exists |
| `test_codex_block_required_fields` | Block is complete | codex dict keys | `provider`, `plan`, `monthly_cost`, `currency`, `billing_cycle`, `status` all present |
| `test_totals_sum_matches_subscriptions` | Arithmetic correctness | sum of `monthly_cost` + `monthly_equivalent` values | equals `totals['monthly_subscriptions']` ± 0.01 |
| `test_last_updated_not_stale` | Date was refreshed | `last_updated` string | != `"2025-12-23"` |
| `test_annual_projection_consistent` | Annual math correct | `monthly_subscriptions × 12` | equals `annual_projection` ± 0.01 |

---

## Acceptance Criteria

- [ ] `config/ai-tools/subscriptions.yaml` includes a `codex` subscription block with `provider`, `plan`, `monthly_cost`, `currency`, `billing_cycle`, `features`, `primary_uses`, `status`
- [ ] `totals.monthly_subscriptions` matches the sum of all subscription monthly costs ± $0.01
- [ ] `totals.annual_projection` is updated to `monthly_subscriptions × 12` ± $0.01
- [ ] `totals.last_updated` reflects the implementation date (not `"2025-12-23"`)
- [ ] YAML preamble contains maintenance-contract comment per `feedback_doc_counter_rule_writetime`
- [ ] `docs/BUSINESS_BRAIN.md` Codex row updated from "Variable" to confirmed cost (or documented as usage-metered with a monthly budget cap)
- [ ] No API keys, tokens, or auth credentials committed (per `feedback_credential_issuer_copy_paste_leak`)
- [ ] All TDD tests pass: `uv run pytest tests/config/test_subscriptions_yaml.py -v`
- [ ] No regression: `uv run pytest tests/config/ -v` passes

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | — |
| Codex | (pending) | — |
| Gemini | (pending) | — |

**Overall result:** (pending adversarial review)

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk:** $200/mo Codex cost is sourced from auto-memory (`project_hermes_codex_quota`), not from a live account screenshot. Implementer must verify the exact plan name and active monthly cost against the OpenAI account before writing the value. If cost differs, the totals math also changes.
- **Risk:** `github_copilot` uses `annual_cost` + `monthly_equivalent` instead of `monthly_cost`. The TDD arithmetic test must sum `monthly_cost` where present and `monthly_equivalent` where `monthly_cost` is absent to get the accurate total.
- **Risk:** If Codex is usage-metered (no flat monthly plan), a `monthly_cost` field may be misleading. In that case, use a `monthly_budget_cap` or `monthly_typical_spend` field and document the distinction inline to avoid false precision downstream.
- **Open:** `docs/BUSINESS_BRAIN.md` says Codex cost is "Variable by authenticated account." After confirming cost, decide whether to add a fixed cost row or leave it as "variable with $X/mo observed spend cap" and update the narrative at lines 60–63.

---

## Complexity: T1

**T1** — modifies two config/doc files with no logic dependencies. Math is additive; values are confirmable from the live account. TDD tests are data-validation checks, not functional tests.
