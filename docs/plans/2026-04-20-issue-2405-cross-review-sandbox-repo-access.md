# Plan for #2405: Cross-review sandbox repo access — pre-verification attestation

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2405
> **Review artifacts:** populated after cross-review dispatch

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/review/cross-review.sh` (536 lines) — orchestrator with iteration-cap, Opus-fallback on Codex quota, 2-of-3 consensus logic.
- `scripts/review/submit-to-codex.sh` (293 lines) — Codex sandbox dispatcher via `codex exec --skip-git-repo-check`.
- `scripts/review/submit-to-gemini.sh` (284 lines) — Gemini dispatcher via `gemini -p`.
- `scripts/review/prompts/plan-review.md` — prompt template (adversarial stance NOT baked in by default; prepended per-invocation).
- `scripts/review/render-structured-review.py` — parses provider JSON into canonical review artifact shape.
- `scripts/review/validate-review-output.sh` — VALID / NO_OUTPUT / INVALID_OUTPUT classification.

### Standards
Not applicable.

### LLM Wiki pages consulted
Not applicable.

### Documents consulted
- `docs/plans/_template-issue-plan.md` §Evidence subsection (added 2026-04-20 at commit `4226f8695`) — necessary but insufficient without this issue.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` review-stance contract — demands reviewers verify claims against live state.
- `scripts/review/results/2026-04-20-v3-plan-239{2,4,5}-{codex,gemini}.md` — empirical confirmation: 6/6 MAJOR on v3 iter-3 citing "unverified" despite embedded evidence.
- Memory `feedback_codex_needs_pushed_artifact.md`, `feedback_codex_sandbox_write_blocked.md` — prior documentation of Codex sandbox read/write isolation.

### Dependency Matrix

| Issue | State | Relationship | Behavior |
|---|---|---|---|
| #2208 | CLOSED | retrieval contract this extends to reviewer | — |
| #2206 | OPEN status:plan-approved | conformance checks could later enforce attestation presence | — |
| #2392/#2394/#2395 | CLOSED blocked | **unblocks re-file of these** | successful completion of this issue enables fresh iteration budget |

### Gaps identified
- No mechanism exists today for reviewers to affirmatively verify claims against live repo state.
- `submit-to-codex.sh` / `submit-to-gemini.sh` pass plan text only; no pre-processing enrichment.
- Review prompt demands verification the reviewer infrastructure cannot provide.

### Evidence (embedded verification)

**Issue statuses** (via `gh issue view` 2026-04-20T16:05Z):
- `#2405` — OPEN — title matches this plan
- `#2208` — CLOSED — retrieval contract
- `#2206` — OPEN status:plan-approved — pyramid conformance

**File existence** (`ls -la` 2026-04-20T16:05Z):
```
EXISTS: scripts/review/cross-review.sh (536 lines)
EXISTS: scripts/review/submit-to-codex.sh (293 lines)
EXISTS: scripts/review/submit-to-gemini.sh (284 lines)
EXISTS: scripts/review/prompts/plan-review.md
EXISTS: scripts/review/render-structured-review.py
EXISTS: scripts/review/validate-review-output.sh
MISSING (new — this plan creates): scripts/review/attest-plan-claims.sh
MISSING (new — this plan creates): tests/review/test_attest_plan_claims.py
```

**Empirical "unverified" evidence** (iter-3 Codex finding quoted from `scripts/review/results/2026-04-20-v3-plan-2395-codex.md`):
> "Unverified resource-intelligence claims: the 'Resource Intelligence Summary' asserts specific paths, issue states, and script counts as facts, but this review packet provides no verifiable evidence beyond prose and fabricated quoted output."

Distinct sources: **9** (exceeds ≥3 minimum).

---

## Cross-Machine Tier Assignment (§7)

| Artifact | Path | Tier | Authority |
|---|---|---|---|
| Attestation script | `scripts/review/attest-plan-claims.sh` | 1 git-tracked | authoritative |
| Attestation output (per-run) | `scripts/review/results/<timestamp>-<source>-attestation.txt` | 1 git-tracked via commit of review artifacts | durable per-review |
| Modified dispatchers | `scripts/review/submit-to-{codex,gemini}.sh` | 1 git-tracked | authoritative |
| Prompt template | `scripts/review/prompts/plan-review.md` | 1 git-tracked | authoritative |
| Tests | `tests/review/test_attest_plan_claims.py` | 1 git-tracked | authoritative |

Attestation is produced by a local process (has repo access) and then embedded in the prompt shipped to the sandboxed provider. Provider sees signed evidence rather than plan-asserted claims.

---

## Threat Model

**Input surfaces:** the plan file itself (parsed by attestation script).
**Trust boundaries:**
- Local environment is trusted to run `gh` / `ls` / `sed` faithfully — attestation is only as trustworthy as the machine running it. Acceptable because plan-review is a developer-local operation.
- Attestation SHA is included in the dispatch log so if a reviewer later contests a finding, the attestation can be re-run against the pinned commit and compared.

**Mitigations:**
- Attestation runs `gh`/`ls`/`sed` with hardcoded flags — no shell interpolation from plan content.
- Plan file paths are allowlist-restricted to `docs/plans/*.md`.
- Commands executed are pinned (no arbitrary command execution from plan content).
- Rate-limit: max 20 `gh issue view` calls per attestation run (hard cap; prevents runaway plans from hitting API limits).

**Threat tests:**
- `test_attestation_rejects_plan_outside_allowlist`
- `test_attestation_rejects_shell_metacharacters_in_extracted_paths`
- `test_attestation_caps_gh_calls_at_20`
- `test_attestation_commands_are_pinned_not_derived`

---

## AC ↔ Test Map

| AC | Test(s) |
|---|---|
| Attestation script runs against any plan file | `test_attestation_runs_on_sample_plan` |
| Extracts issue numbers from plan | `test_extract_issue_numbers` |
| Extracts file paths from plan | `test_extract_file_paths` |
| Runs `gh issue view` for each extracted issue | `test_gh_issue_view_invoked_per_issue` |
| Runs `ls -la` for each extracted file path | `test_ls_invoked_per_path` |
| Produces deterministic output for identical inputs | `test_attestation_deterministic` |
| Output embedded into prompt as `## Attested Evidence` section | `test_dispatcher_includes_attestation_in_prompt` |
| Dispatch still works when attestation fails (fail-soft) | `test_dispatcher_fails_soft_on_attestation_failure` |
| Attestation SHA logged for reproducibility | `test_attestation_sha_logged` |
| Rate limit honored | `test_attestation_caps_gh_calls_at_20` |
| Path allowlist enforced | `test_attestation_rejects_plan_outside_allowlist` |
| End-to-end regression: v3 #2392 plan with attestation → Codex produces non-"unverified" verdict | `test_e2e_iter3_plan_no_longer_unverified` (integration, may be skipped if Codex unavailable) |

---

## Deliverable

An `attest-plan-claims.sh` script that:
1. Parses a plan file at `docs/plans/<slug>.md`.
2. Extracts claimed issue numbers (regex: `#\d{3,5}`).
3. Extracts claimed file paths (regex matching backticked paths or plain paths in Evidence block).
4. Runs `gh issue view <n> --json number,state,title` for each issue (capped at 20, rate-limited).
5. Runs `ls -la <path>` for each file path claim.
6. Emits a structured `## Attested Evidence (verified YYYY-MM-DDTHH:MM:SSZ)` block with the captured output.
7. Returns the attestation as stdout for dispatcher consumption.

Then `submit-to-codex.sh` and `submit-to-gemini.sh` are modified to run `attest-plan-claims.sh` on the input plan file, prepend the attestation block to the prompt, and include a pointer in the prompt instructing the reviewer that the attestation is independent verification.

---

## Pseudocode

```bash
# scripts/review/attest-plan-claims.sh
#!/usr/bin/env bash
set -euo pipefail
PLAN_FILE="$1"
[[ "$PLAN_FILE" =~ ^docs/plans/.*\.md$ ]] || die "plan path outside allowlist"

# Extract citations
ISSUE_NUMBERS=$(grep -oE '#[0-9]{3,5}' "$PLAN_FILE" | sort -u | head -20)
FILE_PATHS=$(grep -oE '`[a-zA-Z0-9._/\-]+\.(py|md|yaml|sh|json|toml)`' "$PLAN_FILE" \
  | sed 's/`//g' | sort -u | head -40)

echo "## Attested Evidence (verified $(date -u +%Y-%m-%dT%H:%M:%SZ) at commit $(git rev-parse HEAD))"
echo ""
echo "**Issue states** (independently verified via \`gh issue view\`, not plan-asserted):"
for n in $ISSUE_NUMBERS; do
  num="${n#\#}"
  gh issue view "$num" --json number,state,title --jq '"- #\(.number) \(.state) \(.title)"' \
    2>/dev/null || echo "- #$num (gh-lookup-failed)"
done

echo ""
echo "**File existence** (independently verified via \`ls -la\`):"
for f in $FILE_PATHS; do
  if [[ -e "$f" ]]; then echo "- EXISTS: $f"
  else echo "- MISSING: $f"; fi
done

echo ""
echo "_Attestation SHA: $(sha256sum "$PLAN_FILE" | cut -c1-16)_"
```

Dispatcher modification (conceptually):
```bash
# in submit-to-codex.sh and submit-to-gemini.sh, before constructing FULL_PROMPT:
if [[ -f "$CONTENT_FILE" ]] && [[ "$CONTENT_FILE" == *docs/plans/* ]]; then
  ATTESTATION="$(bash "${SCRIPT_DIR}/attest-plan-claims.sh" "$CONTENT_FILE" 2>/dev/null || echo "")"
fi

FULL_PROMPT="${SCOPE_PREFIX}${PROMPT}

---
${ATTESTATION}

---
CONTENT TO REVIEW:
---

${CONTENT_TEXT}"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/review/attest-plan-claims.sh` | main attestation script |
| Create | `tests/review/test_attest_plan_claims.py` | TDD suite |
| Create | `tests/review/fixtures/sample_plan_with_citations.md` | test fixture |
| Modify | `scripts/review/submit-to-codex.sh` | call attestation; embed output in prompt |
| Modify | `scripts/review/submit-to-gemini.sh` | same |
| Modify | `scripts/review/prompts/plan-review.md` | document that `## Attested Evidence` block is independent verification; reviewer MUST prefer attestation over plan text when conflicts arise |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | update review-stance contract: "independently verify against live state" → "prefer `## Attested Evidence` over plan text; treat plan as assertion, attestation as verification" |
| Update | `docs/plans/README.md` | add this plan row |

---

## Acceptance Criteria

- [ ] All tests pass: `uv run pytest tests/review/test_attest_plan_claims.py -v`
- [ ] No regression: existing `cross-review.sh` behavior unchanged when attestation fails
- [ ] Attestation runs in <5 seconds for a typical plan (20 issues + 40 paths)
- [ ] Rate-limit (20 `gh` calls) enforced + tested
- [ ] Path allowlist enforced + tested
- [ ] Integration smoke: re-run one of the v3 plans (#2392 v3) through updated dispatcher → Codex produces a review that cites attested evidence rather than flagging "unverified" (the specific verdict may still be MAJOR on content grounds, but the "unverified" convergent finding should not appear)
- [ ] Updated prompt template + skill file landed
- [ ] Review artifacts posted

---

## Adversarial Review Summary

| Provider | Verdict | Artifact |
|---|---|---|
| Claude self | PENDING | will run pre-dispatch |
| Codex | PENDING | — |
| Gemini | PENDING | — |

---

## Risks and Open Questions

- **Risk:** `gh` rate limit on attestation runs (5000 req/hr personal, but plans with many issue citations + rapid iteration could hit it). Mitigation: 20-cap per run; attestation cached for 5 min per plan-SHA.
- **Risk:** Attestation could fail silently in CI. Mitigation: fail-soft (review proceeds without attestation, logs warning); dispatcher prints `[WARN] attestation failed — review will fall back to plan-asserted evidence only` so the reviewer's findings are still interpretable.
- **Risk:** Attestation could become a DoS vector if a plan cites 1000s of issues. Mitigation: hard cap at 20; out-of-budget citations listed as `(skipped: budget exhausted)` so the plan author sees the limit.
- **Open:** Should `sed -n` line excerpts also be attested? Plan default: no for v1 (out of scope — line-accuracy is less frequent defect class than existence/status); can add in follow-on.
- **Open:** Cache attestations by plan-SHA? Plan default: yes, 5-minute TTL, local file cache only.

---

## Complexity: T2

Single new script + 2 dispatcher modifications + tests + skill/prompt documentation. Well-bounded.
