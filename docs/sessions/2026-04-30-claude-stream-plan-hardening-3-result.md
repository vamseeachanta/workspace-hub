# Claude stream-json lane result — `claude-stream-plan-hardening-3`

> **ENV-MISMATCH:** prescribed result path `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-stream-plan-hardening-3.md`
> is outside this sandbox's grant set (read/write/stat blocked, Glob denied at root).
> Fallback per memory `feedback_lane_result_path_outside_sandbox.md`: writing the durable deliverable here under `docs/sessions/`.
> Operator action: copy this file to the prescribed `agent-logs/` result path before downstream lane reconciliation reads it, OR adjust grant set on next provider-autofeed dispatch so lanes can write to `agent-logs/...` directly.

> Lane scope: planning/review only. **No** plan-approval label changes. **No** local marker writes. **No** implementation. Output is exact prompt-pack suggestions for safe adversarial re-review of plan-review-flagged artifacts.

---

## In-scope artifacts (plan-review surface)

Three live `status:plan-review` issues need safe re-review hardening per `docs/plans/nightly-immediate-batch2-20260430-plan-review-hardening.md` (batch2 inventory):

| Issue | Plan path | Current state | Why hardening |
|---|---|---|---|
| #2550 | `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` | Gemini latest = MAJOR; Codex/Claude fanout artifacts UNAVAILABLE/timeout | Needs clean re-fanout under hardened producer (codex 0.123.0 + Gemini neutral-cwd trust-env) |
| #2552 | `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` | Codex UNAVAILABLE; Gemini stale-workspace false-negative; Claude single-author canonicalized | Needs Codex re-run from non-hung CLI and Gemini re-run from a workspace whose `git ls-files` matches the reviewed bytes |
| #2564 | `docs/plans/2026-04-30-issue-2564-mnt-ace-raw-reference-review.md` | Engineering-critical; 2026-04-29 MAJOR artifacts authoritative; 2026-04-30 rerun timed out | Needs ≥2 substantive no-MAJOR reviewers under hardened producer before any approval candidacy |

Two structural-hardening plans remain in the same surface but are out-of-scope for *this* lane (they harden the producer/consumer themselves, not flagged plans):

- `docs/plans/2026-04-27-issue-2502-plan-review-artifact-metadata-stale-sha.md` — draft hardened (r15 APPROVE from Hermes subagent), still awaiting clean Codex/Gemini canonical artifacts.
- `docs/plans/2026-04-27-issue-2518-plan-review-fanout-provider-hardening.md` — `status:plan-approved`; provides timeout+stderr-promotion+trust-env primitives that the prompts below assume.

---

## Known producer constraints the prompt pack must honour

1. **codex-cli 0.124.0 upstream stdin-hang regression** — memory `feedback_codex_cli_0_124_upstream_regression.md` (logged 2026-04-23). All `codex exec` calls block on stdin redirection regardless of input size. Workaround: downgrade to `0.123.0` before invoking. If 0.124.0 is still installed, prompts MUST emit explicit `Verdict: UNAVAILABLE` rather than retrying.
2. **Gemini sandbox overlay blindness** — memory `feedback_gemini_sandbox_overlay_blindness.md` (2026-04-23 batch had ~54 false-positive file-missing claims). Prompts MUST require Gemini to verify each file-existence claim with `git ls-files` against the reviewed worktree before issuing MAJOR.
3. **Gemini trust-env requirement** — memory `feedback_gemini_trust_env_blocks_reviews.md`. Direct Gemini invocation must run from neutral cwd `/tmp` with `GEMINI_CLI_TRUST_WORKSPACE=true gemini --yolo -p "$combined"`. Without these, fanout exits 55 silently.
4. **Canonical artifact filename + metadata header** — per #2502 contract:
   - filename: `scripts/review/results/YYYY-MM-DDTHHMMSSZ-plan-<issue>-<provider>.md`
   - byte-0 header (ends at first blank line), required keys: `Review-Artifact-Version: 1`, `Review-Artifact-Role: provider-review`, `Issue`, `Plan-Path`, `Plan-Commit` (40-hex SHA or `WORKTREE:<plan_sha256>`), `Plan-SHA256`, `Reviewed-Revision` (== `Plan-Commit`), `Provider`, `Perspective`, `Verdict` ∈ `APPROVE|MINOR|MAJOR|UNAVAILABLE`, `Reviewed-At-UTC`.
5. **No self-approval** — memory `feedback_never_offer_to_self_label_plan_approved.md`. Prompts must NOT pre-authorize labelling, dispatch, or local marker writes.

---

## Prompt pack suggestions (exact text — copy-paste ready)

### Pack A — Safe Codex re-review (per issue, planning-only)

Use this prompt for each of #2550, #2552, #2564. Substitute `<ISSUE>`, `<PLAN_PATH>`, `<PLAN_SHA256>`, `<PLAN_COMMIT_OR_WORKTREE>`, `<RUN_STAMP>` (e.g. `2026-04-30T161205Z`).

```
You are reviewing plan #<ISSUE> at <PLAN_PATH> for adversarial defects.

HARD GATES (do not violate):
- This is a planning-only review. Do NOT propose label changes, do NOT write status:plan-approved, do NOT touch .planning/plan-approved/.
- Verdict must be one of APPROVE | MINOR | MAJOR | UNAVAILABLE.
- If your CLI version cannot read the plan reliably, return Verdict: UNAVAILABLE with a one-line reason. Do NOT guess.
- Cite every file-existence claim by exact line range. If you cannot read the file in this sandbox, classify the claim as UNVERIFIED, not as a defect.

PRECONDITION (operator-checked before dispatch):
- codex --version is 0.123.x or older. If 0.124.x, abort and emit UNAVAILABLE.
- The plan file at <PLAN_PATH> hashes to <PLAN_SHA256>. If not, refuse and emit UNAVAILABLE (sha-mismatch).

OUTPUT FORMAT (must be byte-0 metadata header followed by blank line, then prose):
Review-Artifact-Version: 1
Review-Artifact-Role: provider-review
Issue: <ISSUE>
Plan-Path: <PLAN_PATH>
Plan-Commit: <PLAN_COMMIT_OR_WORKTREE>
Plan-SHA256: <PLAN_SHA256>
Reviewed-Revision: <PLAN_COMMIT_OR_WORKTREE>
Provider: codex
Perspective: codex
Verdict: <APPROVE|MINOR|MAJOR|UNAVAILABLE>
Reviewed-At-UTC: <ISO-8601-Z>

(blank line)

## Verdict
<APPROVE|MINOR|MAJOR|UNAVAILABLE> — <one-line reason>

## Findings
- <severity> | <file:lines> | <defect> | <fix-direction>

## Blockers
- <empty if APPROVE/MINOR; one bullet per MAJOR-grade defect>

REVIEW SCOPE:
1. Treat the plan adversarially: hunt for contradictions, missing acceptance criteria, unverified resource references, past-tense claims of work that has not been committed, and approval-gating drift.
2. Cross-check every "EXISTS" / "VERIFIED" claim in the plan's Resource Intelligence Summary against the literal byte content provided. Do not trust filenames alone.
3. Flag any prompt language that pre-authorizes downstream agents (e.g. "after this lands, mark plan-approved") as MAJOR.
```

### Pack B — Safe Gemini re-review (per issue, planning-only, with overlay-blindness guard)

```
You are reviewing plan #<ISSUE> at <PLAN_PATH> for adversarial defects.

HARD GATES:
- Planning-only. No label changes. No marker writes.
- Verdict ∈ APPROVE | MINOR | MAJOR | UNAVAILABLE.

OVERLAY-BLINDNESS GUARD (mandatory — do this BEFORE any "file missing" claim):
- For every file path you intend to flag as missing, run `git ls-files <path>` against the worktree provided. If the file is in `git ls-files`, the file IS present and the apparent absence is sandbox overlay blindness, not a plan defect.
- If your sandbox cannot execute `git ls-files`, classify the file as UNVERIFIED and lower verdict severity by one step (MAJOR→MINOR; MINOR→informational).

PRECONDITION (operator-checked):
- Invocation: from `/tmp` with `GEMINI_CLI_TRUST_WORKSPACE=true gemini --yolo -p "$combined"`. If trust env is unset, abort and emit UNAVAILABLE (trust-env).
- The plan bytes you read hash to <PLAN_SHA256>. If not, emit UNAVAILABLE (sha-mismatch).

OUTPUT FORMAT: same byte-0 metadata header as Pack A, with `Provider: gemini` / `Perspective: gemini`.

REVIEW SCOPE: same as Pack A, plus:
- Explicitly distinguish "file confirmed missing via git ls-files" from "file invisible in this sandbox" in every Findings row. Use the literal token `[VERIFIED-MISSING]` or `[UNVERIFIED-OVERLAY]`.
- Any MAJOR that lacks a `[VERIFIED-MISSING]` citation is automatically downgraded to MINOR by the consumer pipeline; do not waste verdict weight on overlay artifacts.
```

### Pack C — Safe Claude re-review (per issue, planning-only)

```
You are reviewing plan #<ISSUE> at <PLAN_PATH> for adversarial defects.

HARD GATES: planning-only; verdict ∈ APPROVE | MINOR | MAJOR | UNAVAILABLE; no label/marker writes; no self-approval.

PRECONDITION: plan bytes hash to <PLAN_SHA256>; otherwise UNAVAILABLE (sha-mismatch).

OUTPUT FORMAT: byte-0 metadata header (Provider: claude / Perspective: claude) per #2502 contract; raw findings body after blank line.

REVIEW SCOPE:
1. Adversarial reading: contradictions, drift, past-tense claims of un-merged work, approval pre-authorization, missing acceptance criteria, unverifiable resource refs.
2. Cross-check Resource Intelligence Summary line-by-line against the literal plan bytes. Do not infer existence from the plan's own claims.
3. Flag any deliverable that prescribes writing `status:plan-approved` or `.planning/plan-approved/<issue>.md` from inside this review as MAJOR.
4. If the plan is engineering-critical (issue carries `cat:engineering-critical` or domain wiki labels), require ≥2 substantive non-Claude reviewers reaching MINOR-or-better before APPROVE; otherwise downgrade your own APPROVE to MINOR with reason "single-provider engineering-critical".
```

### Pack D — Disagreement-sidecar reconciliation prompt (planning-only)

After all three providers run, emit:

```
You are reconciling provider disagreement for plan #<ISSUE>, RUN_STAMP=<RUN_STAMP>.

INPUTS (read each from disk; do not paraphrase):
- scripts/review/results/<RUN_STAMP>-plan-<ISSUE>-claude.md
- scripts/review/results/<RUN_STAMP>-plan-<ISSUE>-codex.md
- scripts/review/results/<RUN_STAMP>-plan-<ISSUE>-gemini.md

OUTPUT: scripts/review/results/<RUN_STAMP>-plan-<ISSUE>-disagreement.md
- Header: Review-Artifact-Role: disagreement (NOT provider-review). Disagreement files do not satisfy provider slots per #2502.
- Body: enumerate each defect surfaced by ≥1 provider; group as: (a) all-providers-agree, (b) majority MAJOR, (c) singleton MAJOR with overlay-blindness suspicion, (d) verdict-only disagreement (no concrete finding).
- DO NOT propose plan-approved labelling. DO NOT recommend dispatch. Output is read-only synthesis.
```

### Pack E — Producer-precondition smoke prompt (run before any of A/B/C)

Operator runs this once per RUN_STAMP to capture environment health into the metadata-aware audit trail:

```
Capture and emit:
- codex --version (must be 0.123.x or older for valid review)
- gemini --version (capture; 55-exit failure modes must be flagged)
- env | grep GEMINI_CLI_TRUST_WORKSPACE (must equal "true")
- git rev-parse HEAD; git status --porcelain --untracked-files=no (capture base SHA + dirty-file list)
- For each plan in {<PLAN_PATH_2550>, <PLAN_PATH_2552>, <PLAN_PATH_2564>}: sha256sum of plan bytes; git ls-files matching to confirm tracked.

Write capture to: scripts/review/results/<RUN_STAMP>-precondition.log

If codex is 0.124.x OR GEMINI_CLI_TRUST_WORKSPACE is unset OR any plan is untracked-and-uncommitted, do NOT dispatch packs A/B/C; raise to operator instead. The provider re-fanout fails closed when the producer is degraded — that is the safe behaviour.
```

---

## Suggested dispatch order (operator-driven, no automation)

1. Run **Pack E** (precondition smoke). If degraded, stop here and surface to operator.
2. For each issue ∈ {#2550, #2552, #2564}, run **Pack A**, **Pack B**, **Pack C** in parallel under the hardened fanout (`scripts/review/plan-review-fanout.sh`, post-#2518).
3. Run **Pack D** to emit the disagreement sidecar per issue.
4. Update `docs/plans/nightly-immediate-batch2-20260430-plan-review-hardening.md` with the new RUN_STAMP and per-issue verdict matrix. **Do not** modify any approval label or local marker — that gate remains user-in-loop per memory `feedback_never_offer_to_self_label_plan_approved.md`.

---

## What this lane explicitly did NOT do

- Did not propose `status:plan-approved` for any of #2550 / #2552 / #2564.
- Did not write or modify any file under `.planning/plan-approved/`.
- Did not invoke any provider CLI (CLI invocation is the operator's call once preconditions are green).
- Did not commit anything (delivers prompt-pack text only; result file is untracked here under `docs/sessions/`).
- Did not assume codex-cli 0.124.0 is fixed (memory `feedback_codex_cli_0_124_upstream_regression.md` still authoritative; no contradicting evidence observed in this run).

---

## Provenance

- Repo: `/mnt/local-analysis/workspace-hub`, branch `main` (status uninspected — bash `git status` blocked under this grant set; treat as dirty per hard-gate guidance).
- Inputs read: `docs/plans/nightly-immediate-batch2-20260430-plan-review-hardening.md`, `docs/plans/2026-04-22-plan-hardening-safe-landing-sequence.md`, `docs/plans/2026-04-27-issue-2502-plan-review-artifact-metadata-stale-sha.md`, `docs/plans/2026-04-27-issue-2518-plan-review-fanout-provider-hardening.md`.
- Memory consulted: `feedback_codex_cli_0_124_upstream_regression`, `feedback_gemini_sandbox_overlay_blindness`, `feedback_gemini_trust_env_blocks_reviews`, `feedback_lane_result_path_outside_sandbox`, `feedback_never_offer_to_self_label_plan_approved`, `feedback_plan_past_tense_artifact_claims`, `feedback_attestation_enables_contradiction_detection`.
- Lane: `claude-stream-plan-hardening-3` of run `provider-autofeed-20260430-111336`.
