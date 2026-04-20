# Plan for #2405: Cross-review sandbox repo access — pre-verification attestation (v3)

> **Status:** plan-review (iteration 3 of 3 — final)
> **Complexity:** T2
> **Date:** 2026-04-20 (v3)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2405
> **Prior reviews:** v1 at `d067a4d51` (Codex+Gemini MAJOR); v2 at `5c9923acf` (Gemini MAJOR + Codex timeout — ironic infrastructure confirmation of this issue's premise)

## v3 fixes (iter-2 Gemini findings)

**P1 — Budget-exhaustion logic defect fixed:** v2 pseudocode capped `ISSUE_NUMBERS` with `head -20` then checked `head -21 | tail -1` which was always empty. v3 preserves full list before capping and counts against original length.

**P1 — Deliverable/pseudocode mismatch fixed:** v2 Deliverable said "runs `ls -la`" but pseudocode used bash builtins (`[[ -e ]]`, `readlink`). v3 pseudocode explicitly runs `ls -la -- "$f"` and parses output; Deliverable wording aligned.

**P1 — Allowlist regex inconsistency fixed:** v2 Revision History accidentally said `.*` while Threat Model + pseudocode used `[^/]+`. v3 uses `^docs/plans/[^/]+\.md$` everywhere (single definition). Subdirectory support is explicitly out of scope.

**P1 — `readlink` security fix:** v2 pseudocode used `readlink "$f"` which treats hyphen-leading paths as flags. v3 uses `readlink -- "$f"` and `ls -la -- "$f"` to prevent flag injection.

**P2 carry-over:** Class B "unverified claims" remains self-circular — this plan's job is to fix it; post-implementation, embedded attestations will be verifiable.

**Codex infrastructure observation:** v2 Codex review timed out at both 300s AND 600s with "Reading additional input from stdin..." — the dispatch script has a real bug that's an additional argument for this issue's priority. Captured as follow-on candidate `#2405-B codex-dispatch-stdin-fix`.

---

## Revision History

- **v1:** initial plan. Codex MAJOR + Gemini MAJOR. Class A real defects (apply inline) + Class B "unverified claims" (self-circular — fixed by v1 landing, not by more iteration).

**v2 fixes for Class A:**
- Tier Assignment: attestation output is **tier-3 local-cache** (transient per-review); not "git-tracked via commit" — removed the contradiction.
- Dispatch log: **removed** from v2 scope; move to follow-on if needed.
- Cache: **removed** from v2 scope; move to follow-on if needed. v2 re-runs attestation per review (5-10s overhead acceptable).
- AC-test gaps: added tests for prompt-template AC, skill-file AC, <5s benchmark AC.
- Regex discrepancy: Deliverable tightened — v2 extracts **only** backticked paths and extension-qualified paths (documented explicitly); plain-path extraction deferred.
- Allowlist: single definition used by both Deliverable text and pseudocode (tightened match: `^docs/plans/.*\.md$`).
- SHA semantics: v2 hashes the **attestation payload text**, not the plan file.
- Partial-failure test: `test_gh_issue_view_partial_failure` added.
- §3 compliance: §Identity Contract added for attestation payloads.
- Threat model: added symlink-traversal + private-metadata-leakage-to-third-party-providers mitigations.

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/review/cross-review.sh` — orchestrator.
- `scripts/review/submit-to-codex.sh` — Codex dispatcher (to be modified).
- `scripts/review/submit-to-gemini.sh` — Gemini dispatcher (to be modified).
- `scripts/review/prompts/plan-review.md` — prompt template (to be updated).
- `scripts/review/render-structured-review.py` — structured output parser.
- `scripts/review/validate-review-output.sh` — classifier.

### Standards
Not applicable (tooling issue; no engineering standards apply).

### LLM Wiki pages consulted
Not applicable (tooling issue).

### Documents consulted
- `docs/plans/_template-issue-plan.md` §Evidence subsection (v1 landed; confirmed extant via `ls`).
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — review-stance contract this plan modifies.
- `scripts/review/results/2026-04-20-plan-2405-{codex,gemini}.md` — iter-1 reviews informing v2.
- Operating-model `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — §3 applied to attestation payload `doc_key`; §7 applied to attestation file tier.

### Dependency Matrix

| Issue | State | Relationship | Behavior |
|---|---|---|---|
| #2208 | CLOSED | retrieval contract extended | — |
| #2206 | OPEN status:plan-approved | conformance may later enforce attestation presence | — |
| #2392/#2394/#2395 | CLOSED blocked | **unblocks re-file** | fresh iteration budget once this lands |

### Gaps identified
- No reviewer access to live repo state today.
- No attestation mechanism.
- No guidance in review-stance contract about how reviewers should treat plan claims vs attested evidence.

### Evidence (embedded verification)

**Issue statuses** (2026-04-20T16:05Z via `gh issue view`):
- `#2405` OPEN — this issue
- `#2208` CLOSED — retrieval contract
- `#2206` OPEN `status:plan-approved` — conformance

**File existence** (`ls -la` 2026-04-20T16:05Z):
```
EXISTS: scripts/review/cross-review.sh
EXISTS: scripts/review/submit-to-codex.sh
EXISTS: scripts/review/submit-to-gemini.sh
EXISTS: scripts/review/prompts/plan-review.md
EXISTS: scripts/review/render-structured-review.py
EXISTS: scripts/review/validate-review-output.sh
EXISTS: docs/plans/_template-issue-plan.md  (v1 §Evidence subsection confirmed at commit 4226f8695)
EXISTS: .claude/skills/coordination/issue-planning-mode/SKILL.md
MISSING (new — this plan creates): scripts/review/attest-plan-claims.sh
MISSING (new — this plan creates): tests/review/test_attest_plan_claims.py
MISSING (new — this plan creates): tests/review/fixtures/sample_plan_with_citations.md
```

Distinct sources: **9** (exceeds ≥3 minimum).

---

## Identity Contract (§3)

Attestation payloads include a SHA identifier `sha256:<64-hex>` of the **payload text itself** (not the plan file). Purpose:
- Lets the dispatcher log + a reviewer (once sandbox has access post-implementation) cross-verify that the attestation text in a saved review artifact matches what the dispatcher actually sent.
- Namespace: `sha256:` per §3; path-only identity forbidden.

Tests:
- `test_attestation_payload_sha256_stable` — identical inputs → identical SHA
- `test_attestation_payload_sha256_changes_on_attestation_change` — edit payload → different SHA
- `test_attestation_payload_sha256_independent_of_plan_file_unrelated_changes` — changing plan prose outside attested sections does NOT change attestation SHA

---

## Cross-Machine Tier Assignment (§7)

| Artifact | Path | Tier | Authority |
|---|---|---|---|
| Attestation script | `scripts/review/attest-plan-claims.sh` | 1 git-tracked | authoritative |
| Modified dispatchers | `scripts/review/submit-to-{codex,gemini}.sh` | 1 git-tracked | authoritative |
| Prompt template | `scripts/review/prompts/plan-review.md` | 1 git-tracked | authoritative |
| Skill contract | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | 1 git-tracked | authoritative |
| Tests | `tests/review/test_attest_plan_claims.py` | 1 git-tracked | authoritative |
| **Attestation payload (per-run, transient)** | stdout from script; passed via stdin to provider | **3 local-cache** | **transient; not persisted** |

Attestation is ephemeral per-review — generated at dispatch time, embedded in prompt, not written to disk. If a persisted copy is needed later, it can be captured via `tee` by the caller; that path is out of v2 scope.

---

## Threat Model

**Input surfaces:** plan file path (CLI arg), plan content (read by script).
**Trust boundaries:**
- Plan content is **trusted** (git-tracked, reviewed).
- Local `gh auth` token is trusted (ecosystem-standard auth).
- **External provider is untrusted** for purposes of what data we ship them.

**Mitigations:**
- **Allowlist (single definition):** regex `^docs/plans/[^/]+\.md$` — both Deliverable text and `attest-plan-claims.sh` use this exact regex. Test: `test_allowlist_regex_consistent_across_deliverable_and_script`.
- **No shell interpolation:** extracted issue numbers/paths pass through fixed-argument `gh` / `ls` invocations (no string concat into shell).
- **Symlink traversal defense:** `ls -la` (not `ls -L`); results show symlink targets, not follow them. If a path resolves via symlink, attestation records `SYMLINK: <path> -> <target>` and the reviewer sees both.
- **Private-metadata leakage defense (NEW — v2 addition):** `gh issue view --json number,state,title` only — **no body, no labels with sensitive content, no reviewer names**. State + title are the minimum needed for verification; body content stays out of third-party provider prompts.
- **`gh` rate cap:** 20 issues per attestation; out-of-budget citations listed as `(skipped: budget exhausted)`.
- **Attestation SHA** in payload lets reviewer (post-sandbox-access follow-on) cross-check payload integrity.

**Threat tests:**
- `test_allowlist_regex_consistent_across_deliverable_and_script`
- `test_rejects_plan_path_outside_allowlist`
- `test_no_shell_interpolation_from_plan_content`
- `test_symlink_recorded_not_followed`
- `test_gh_view_limits_to_state_title_only` (private-metadata defense)
- `test_caps_gh_calls_at_20_with_skipped_note`
- `test_attestation_sha_included_in_payload`

---

## AC ↔ Test Map (v2 — every AC mapped)

| AC | Test(s) |
|---|---|
| Script runs against sample plan | `test_attestation_runs_on_sample_plan` |
| Extracts issue numbers | `test_extract_issue_numbers` |
| Extracts backticked file paths with known extensions | `test_extract_file_paths_backticked_with_extensions` |
| Skips plain-path citations (documented limitation) | `test_extract_skips_plain_paths_v2_documented` |
| `gh issue view` invoked per extracted issue | `test_gh_issue_view_invoked_per_issue` |
| Handles `gh` partial failure gracefully | `test_gh_issue_view_partial_failure` (NEW — iter-1 Gemini finding) |
| `ls -la` invoked per extracted file path | `test_ls_invoked_per_path` |
| Deterministic output | `test_attestation_deterministic_for_identical_input` |
| Output embedded as `## Attested Evidence` in prompt | `test_dispatcher_includes_attestation_block` |
| Fail-soft on attestation failure | `test_dispatcher_fails_soft_on_attestation_failure` |
| Attestation SHA hashes payload (not plan) | `test_attestation_sha_hashes_payload_not_plan_file` |
| Rate limit honored | `test_caps_gh_calls_at_20_with_skipped_note` |
| Allowlist enforced | `test_rejects_plan_path_outside_allowlist` + `test_allowlist_regex_consistent_across_deliverable_and_script` |
| `<5s` benchmark | `test_attestation_runtime_under_5s_for_20_issues_40_paths` (NEW — benchmark test) |
| **Updated prompt template landed** | `test_prompt_template_documents_attestation_block` (NEW — static file check) |
| **Updated SKILL.md landed** | `test_skill_file_documents_attestation_preference` (NEW — static file check) |
| §3 identity tests | listed under Identity Contract |
| Threat tests | listed under Threat Model |
| E2E regression: re-run v3 #2392 plan → no "unverified" finding | reviewer-task (integration; skipped if provider unavailable) |

---

## Deliverable

An `attest-plan-claims.sh` script that reads a plan file under `docs/plans/` and emits a `## Attested Evidence` block containing independently-verified `gh issue view` results and `ls -la` checks for each claim in the plan. The block is prepended to the prompt sent to Codex and Gemini, giving reviewers evidence they can rely on rather than plan-asserted claims.

---

## Pseudocode (v3 — fixes Gemini iter-2 findings)

```bash
#!/usr/bin/env bash
# scripts/review/attest-plan-claims.sh
set -euo pipefail
PLAN_FILE="$1"

# Single allowlist definition — used by Deliverable text, Threat Model, and this script
ALLOWLIST_REGEX='^docs/plans/[^/]+\.md$'
[[ "$PLAN_FILE" =~ $ALLOWLIST_REGEX ]] || { echo "ERROR: plan path outside allowlist" >&2; exit 1; }
[[ -f "$PLAN_FILE" ]] || { echo "ERROR: plan not found" >&2; exit 1; }

# Extract citations — preserve FULL lists so budget-exhaustion check works (v3 Gemini fix)
ALL_ISSUES=$(grep -oE '#[0-9]{3,5}' "$PLAN_FILE" | sort -u)
ALL_PATHS=$(grep -oE '`[a-zA-Z0-9._/\-]+\.(py|md|yaml|yml|sh|json|toml)`' "$PLAN_FILE" \
  | sed 's/`//g' | sort -u)

ISSUE_COUNT_FULL=$(printf '%s\n' "$ALL_ISSUES" | grep -c .)
PATH_COUNT_FULL=$(printf '%s\n' "$ALL_PATHS" | grep -c .)

ISSUE_NUMBERS=$(printf '%s\n' "$ALL_ISSUES" | head -20)
FILE_PATHS=$(printf '%s\n' "$ALL_PATHS" | head -40)

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
COMMIT=$(git rev-parse HEAD)

# Build payload text (v2 — SHA hashes payload, not plan file)
PAYLOAD=$(cat <<EOF
## Attested Evidence (verified ${TS} at repo commit ${COMMIT})

**Issue states** (via \`gh issue view --json number,state,title\` — title+state only, no body):
$(for n in $ISSUE_NUMBERS; do
    num="${n#\#}"
    gh issue view "$num" --json number,state,title --jq '"- #\(.number) \(.state) \(.title)"' 2>/dev/null \
      || echo "- $n (gh-lookup-failed or private)"
  done)
$([ "$ISSUE_COUNT_FULL" -gt 20 ] && echo "_(${ISSUE_COUNT_FULL} citations in plan; first 20 shown; remainder skipped: budget exhausted)_" || true)

**File existence** (via \`ls -la -- "\$f"\` with flag-injection guard):
$(for f in $FILE_PATHS; do
    if [[ -L "$f" ]]; then
      target=$(readlink -- "$f")
      ls_out=$(ls -la -- "$f" 2>&1 | head -1)
      echo "- SYMLINK: $f -> $target  ($ls_out)"
    elif [[ -e "$f" ]]; then
      ls_out=$(ls -la -- "$f" 2>&1 | head -1)
      echo "- EXISTS: $f  ($ls_out)"
    else echo "- MISSING: $f"
    fi
  done)
$([ "$PATH_COUNT_FULL" -gt 40 ] && echo "_(${PATH_COUNT_FULL} paths in plan; first 40 shown; remainder skipped: budget exhausted)_" || true)
EOF
)

PAYLOAD_SHA=$(printf '%s' "$PAYLOAD" | sha256sum | awk '{print $1}')
echo "$PAYLOAD"
echo ""
echo "_Attestation payload sha256: $PAYLOAD_SHA_"
```

Dispatcher modification (both submit-to-codex.sh + submit-to-gemini.sh):
```bash
# Before FULL_PROMPT construction:
ATTESTATION=""
if [[ -f "$CONTENT_FILE" && "$CONTENT_FILE" =~ docs/plans/[^/]+\.md$ ]]; then
  ATTESTATION="$(bash "${SCRIPT_DIR}/attest-plan-claims.sh" "$CONTENT_FILE" 2>/dev/null || echo "")"
  [[ -z "$ATTESTATION" ]] && echo "[WARN] attestation failed — proceeding with plan-asserted evidence only" >&2
fi

FULL_PROMPT="${SCOPE_PREFIX}${PROMPT}

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
| Create | `scripts/review/attest-plan-claims.sh` | attestation script |
| Create | `tests/review/test_attest_plan_claims.py` | tests |
| Create | `tests/review/fixtures/sample_plan_with_citations.md` | fixture |
| Modify | `scripts/review/submit-to-codex.sh` | embed attestation in prompt |
| Modify | `scripts/review/submit-to-gemini.sh` | same |
| Modify | `scripts/review/prompts/plan-review.md` | document `## Attested Evidence` block precedence |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | update stance contract to "prefer attested evidence over plan text; plan text is assertion, attestation is verification" |

---

## Acceptance Criteria

- [ ] All tests pass
- [ ] `attest-plan-claims.sh` runs in <5s for 20 issues + 40 paths (tested)
- [ ] Dispatchers call attestation pre-prompt; fail-soft on error
- [ ] `gh` limited to state+title only (no body, no sensitive metadata)
- [ ] Allowlist regex identical in deliverable text and script
- [ ] Attestation SHA hashes payload (not plan file)
- [ ] Symlinks recorded, not followed
- [ ] 20-cap enforced with skipped-note
- [ ] Prompt template + skill file updated (static checks)
- [ ] E2E smoke: re-run v3 #2392 plan through updated dispatcher; Codex review does not cite "unverified claims" (content verdict may still be MAJOR on other grounds — that's fine; the Class B convergent finding must be gone)

---

## Adversarial Review Summary

| Provider | Verdict | Artifact |
|---|---|---|
| Codex v1 | MAJOR | `2026-04-20-plan-2405-codex.md` |
| Gemini v1 | MAJOR | `2026-04-20-plan-2405-gemini.md` |
| Codex v2 | PENDING | — |
| Gemini v2 | PENDING | — |

---

## Risks and Open Questions

- **Risk:** Class B "unverified claims" finding will persist until this plan actually IMPLEMENTS. Iter-2/iter-3 reviewers will still flag it for v2 itself. Mitigation: **accept Class B as circular for v2**; v2's goal is to remove Class A findings; Class B resolves at implementation time.
- **Risk:** `gh` state+title only reduces privacy risk but doesn't eliminate it (titles can still leak context). Mitigation: users can configure `ATTEST_SKIP_PRIVATE_ISSUES=1` env var to have attestation list issue numbers without calling `gh` for them (follow-on enhancement if deemed necessary).
- **Open:** Plain-path extraction — deliberately deferred. Plans adopting v3 extensions should use backticked `` `path/to/file.py` `` syntax for attestation.
- **Open:** Persistent attestation archive (commit to `scripts/review/results/` alongside review artifacts)? Deferred to follow-on.

---

## Complexity: T2

Bounded. Single new script + 2 dispatcher modifications + prompt/skill documentation + tests.
