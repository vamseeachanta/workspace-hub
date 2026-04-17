# Plan for #2323: Single-command cross-AI plan-review fan-out (Claude + Codex + Gemini)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2323
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2323-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/review/results/` — canonical sink for review artifacts; existing entries follow two conventions: (a) legacy `YYYYMMDDTHHMMSSZ-<file>-<stage>-<agent>.md` and (b) current `YYYY-MM-DD-plan-NNN-<agent>.md` (per issue-planning-mode skill).
- Found: `.planning/quick/review-NNNN-*.out` — session-transient outputs from current manual invocations (in git status of this session).
- Found: `scripts/enforcement/require-cross-review.sh` — exists for **commit** cross-review; does not handle **plan** review.
- Found: CLIs available on `vamsee@ace-linux-2`: `claude` (symlinked), `codex` (v0.121.0), `gemini` (v0.38.1).
- Gap: no wrapper script that fans a single prompt across providers and writes canonical artifacts + disagreement report.

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — orchestration work | n/a | — |

### LLM Wiki pages consulted
- Not applicable.

### Documents consulted
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` step 4 — adversarial review requires 2+ providers, artifacts at `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`.
- Issue #1326 — Gemini CLI NO_OUTPUT (must be tolerated or fixed first).
- Issue #1884 — cross-review enforcement cron (commit-level; this issue is plan-level).
- Issue #2089 — weekly Hermes + AI provider settings review (broader scope; this is one utility inside that scope).
- `docs/plans/README.md` — repeated practical lesson: "a concise file-path-based `claude -p` review prompt is often more reliable than embedding the full plan text inline".
- Prior manual reviews in `.planning/quick/review-2311-*.out` — prompt shape reference.

### Gaps identified
- No shared prompt template file; prompts drift between providers.
- No machine-readable disagreement report (who caught what).
- No provider-unavailable graceful-degrade logic (Gemini 429, codex auth).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2323-cross-ai-review-fanout.md` |
| Wrapper script | `scripts/review/plan-review-fanout.sh` |
| Shared prompt | `scripts/review/plan-review-prompt.md` |
| Result artifacts (per invocation) | `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md` |
| Disagreement report | `scripts/review/results/YYYY-MM-DD-plan-NNN-disagreement.md` |
| Tests | `scripts/review/tests/test_plan_review_fanout.bats` |
| Fixture plan | `scripts/review/tests/fixtures/fake-plan.md` |
| Docs update | `docs/plans/README.md` (add canonical-way-to-run section) |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2323-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2323-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-17-plan-2323-gemini.md` |

---

## Deliverable

`scripts/review/plan-review-fanout.sh <plan-file> [--providers claude,codex,gemini]` — runs adversarial review across configured providers in parallel, writes per-provider artifacts in the canonical naming convention, produces a disagreement report, and degrades gracefully on single-provider failure.

---

## Reviewer-stance contract (per user feedback on #2323, 2026-04-17)

The shared prompt at `scripts/review/plan-review-prompt.md` MUST force an adversarial reviewer stance across all providers. "Adversarial" here means **actively hunt for defects; default to assuming the plan is wrong and prove otherwise** — never charitable reading, never summary praise.

Required prompt clauses:
1. **Opening framing:** "You are an adversarial reviewer. Your job is to find what is wrong, missing, false, or risky. Assume the plan has defects until you have evidence otherwise."
2. **Anti-flatter rule:** "Do not restate the plan. Do not praise. Do not note what the plan does well. Focus exclusively on what is wrong, missing, or risky."
3. **Default-to-non-approve:** "Return APPROVE only if you have affirmatively verified each correctness-critical claim AND can find no gap. When in doubt, return MINOR or MAJOR — being wrong about MINOR is cheap; missing a MAJOR is expensive."
4. **Evidence over opinion:** "Each finding must cite a specific file path, plan section, or quoted claim. Statements without citations are not findings."
5. **Retrieval skepticism:** "Treat the plan's cited sources as assertions to verify, not facts. If a file path is named, assume it may not exist until checked. If a claim about behavior is made, assume it may be outdated."
6. **Silence is failure:** "If you have no concrete finding, explicitly say the plan was reviewed against [list checks] and none found — do not return an empty review."

Rationale: user feedback 2026-04-17 — "Make all the reviews adversarial in nature. Helps maximize productivity." Charitable reviews that endorse without hunting produce downstream rework that is much more expensive than a cold review.

---

## Pseudocode

> **Revised 2026-04-17** after pre-execution contradiction review (see "Execution-time revisions" section below).
> Reason: v1 pseudocode was empirically broken — Codex and Gemini both drop context when the plan is passed by path reference; Codex then falls back to GitHub MCP lookups and returns false MAJOR. Verified in this project's v1 adversarial review wave. Per-provider invocation shape is now:
> - **Claude** — path reference via `@$prompt_file` + plan path arg (claude -p resolves `@` sigils natively).
> - **Codex** — inline prompt text AND inline plan body concatenated into a single prompt argument.
> - **Gemini** — same inline-body treatment as Codex.

```
main(plan_file, providers=[claude,codex,gemini]):
    validate plan_file exists and matches docs/plans/YYYY-MM-DD-issue-NNN-slug.md
    issue_num = extract_issue_num(plan_file)
    today = YYYY-MM-DD
    prompt_file = scripts/review/plan-review-prompt.md

    tmpdir = mktemp -d
    for provider in providers:
        run_in_background:
            provider_cli_invoke(provider, plan_file, prompt_file) > tmpdir/<provider>.raw
            normalize_to_verdict_headings(tmpdir/<provider>.raw) > scripts/review/results/$today-plan-$issue_num-$provider.md
    wait for all
    summarize_disagreement(scripts/review/results/$today-plan-$issue_num-*.md) > disagreement.md

provider_cli_invoke(provider, plan_file, prompt_file):
    case provider:
        claude:
            # Path-reference style — claude -p resolves @file sigils natively.
            claude -p "@$prompt_file — review the plan at $plan_file. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS."
        codex:
            # INLINE style — Codex drops context on path refs and falls back to GitHub MCP (produces false MAJOR).
            prompt_body="$(cat $prompt_file)"
            plan_body="$(cat $plan_file)"
            codex exec --no-interactive "$prompt_body\n\n--- PLAN ($plan_file) ---\n$plan_body"
        gemini:
            # INLINE style — same reason as Codex. Run from /tmp cwd to dodge local .gemini/agents/*.md permissionMode bug.
            prompt_body="$(cat $prompt_file)"
            plan_body="$(cat $plan_file)"
            (cd /tmp && gemini -p "$prompt_body\n\n--- PLAN ($plan_file) ---\n$plan_body")
    on failure: write scripts/review/results/$today-plan-$issue_num-$provider.md with `## Verdict: UNAVAILABLE (reason)`

summarize_disagreement(artifact_glob):
    parse each artifact for VERDICT line
    compute: which providers returned which verdict, which findings keywords unique to each
    write table + per-provider unique findings bullets
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/review/plan-review-fanout.sh` | wrapper entry point |
| Create | `scripts/review/plan-review-prompt.md` | shared prompt template |
| Create | `scripts/review/lib/disagreement-diff.sh` (or `.py`) | parse + diff verdicts/findings |
| Create | `scripts/review/tests/test_plan_review_fanout.bats` | regression tests |
| Create | `scripts/review/tests/fixtures/fake-plan.md` | fixture with known weakness |
| Modify | `docs/plans/README.md` | document the canonical command |
| Update | `docs/plans/README.md` plan index | add row for this plan |

---

## TDD Test List

> **Revised 2026-04-17** — the v1 `test_prompt_is_file_path_based` test is dropped; it encoded a premise (no-inline-ever) that wave v1 proved empirically false for Codex/Gemini. New per-provider assertions replace it.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_extracts_issue_num_from_filename | `2026-04-17-issue-2323-slug.md` → `2323` | valid plan path | `2323` returned |
| test_rejects_nonconforming_filename | non-date-prefixed filename rejected | `bad-name.md` | exits 1 |
| test_writes_claude_artifact | claude produces artifact in canonical path | mock claude CLI returning fixed text | file exists at `scripts/review/results/.../2323-claude.md` |
| test_parallel_execution | 3 providers run in parallel, not serial | mocks with sleep 2 | total wall time <3 s |
| test_gemini_unavailable_does_not_abort_codex | Gemini fails, Codex succeeds | mock gemini exit 1 | gemini artifact has `UNAVAILABLE`, codex artifact normal |
| test_disagreement_report_captures_unique_finding | one reviewer flags X, others miss | fixture artifacts | disagreement.md lists X under that provider's unique column |
| test_claude_invocation_uses_path_reference | `claude -p` receives `@<prompt>` sigil + plan path, NOT plan body | mock claude recording invocation | command string contains `@$prompt_file` and `$plan_file`, does not contain first line of plan body |
| test_codex_invocation_inlines_plan_body | `codex exec --no-interactive` receives concatenated prompt+plan text | mock codex recording invocation | command string contains first line of plan body AND the `--- PLAN` delimiter |
| test_gemini_invocation_inlines_plan_body | `gemini -p` receives concatenated prompt+plan text | mock gemini recording invocation | command string contains first line of plan body AND the `--- PLAN` delimiter |
| test_gemini_runs_from_tmp_cwd | Gemini invocation chdir'd to /tmp to dodge local `.gemini/agents/*.md` permissionMode bug | mock gemini recording pwd | pwd at time of call is `/tmp` |
| test_prompt_file_contains_all_six_stance_clauses | shared prompt carries adversarial stance verbatim | `scripts/review/plan-review-prompt.md` | all 6 clause keywords present (adversarial reviewer, no praise, default-to-non-approve, evidence, retrieval-skepticism, silence-is-failure) |

---

## Acceptance Criteria

- [ ] `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-17-issue-2323-cross-ai-review-fanout.md` runs all three providers in parallel and produces 3 per-provider artifacts + 1 disagreement report.
- [ ] Wall time is dominated by the slowest provider, not the sum of providers.
- [ ] Artifacts match `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md` naming.
- [ ] Disagreement report lists per-provider verdict + unique-findings summary.
- [ ] Single-provider failure (simulated via mock) does not abort the other two; failing provider's artifact contains `UNAVAILABLE` verdict.
- [ ] `docs/plans/README.md` documents the command as the canonical way to run adversarial review.
- [ ] At least 5 tests pass.
- [ ] `scripts/review/plan-review-prompt.md` contains all 6 clauses from the "Reviewer-stance contract" section above; a regression test asserts their presence verbatim.
- [ ] **Two-fixture self-test** (replaces v1 circular AC): the repo ships `scripts/review/tests/fixtures/known-good-plan.md` and `scripts/review/tests/fixtures/known-broken-plan.md`. A test asserts that when the wrapper is run against each fixture with a mocked provider (mock returns a prompt-echo), the resulting per-provider artifact files contain distinguishable prompt text for the two fixtures. This tests the wrapper's plumbing, not the provider's adversarial behavior. The provider's adversarial behavior is tested separately by the `test_prompt_file_contains_all_six_stance_clauses` assertion and is out of scope for the wrapper's CI.

## Execution-time revisions (2026-04-17)

Two contradictions surfaced during pre-execution review against the approval-with-debt marker `.planning/plan-approved/2323.md`:

1. **File-path vs inline content.** v1 pseudocode + v1 AC #7 (`test_prompt_is_file_path_based`) encoded "never inline plan body." Empirical v1 wave proved Codex + Gemini both need INLINE plan body; without it, Codex falls back to GitHub MCP and returns false MAJOR. Resolution: invert per-provider — `claude -p` takes `@path` sigil; `codex`/`gemini` receive inline concatenated prompt+plan. v1 test is dropped; replaced by three per-provider invocation-shape tests (see TDD list).
2. **Circular self-test AC.** v1 AC #8 required the wrapper's self-test to produce non-APPROVE against a deliberately-weak fixture under adversarial stance. Wave v2 flagged this as circular: stance + weak fixture guarantees non-APPROVE regardless of wrapper correctness. Resolution: two-fixture prompt-plumbing test (see revised AC above); adversarial-behavior assertion is separated out as a prompt-contents-only test.

Both resolutions approved by user on 2026-04-17 before worktree spawn.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
**Wave v2 (2026-04-17, stance-contract applied, post-stance-section-added):**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Pseudocode's provider invocations are empirically broken (Codex/Gemini both need INLINE content, not path references — verified in this session's review waves); self-test AC is circular (weak fixture + stance → non-APPROVE regardless); cost guard is comment not code; no offline/mock test path; disagreement-report schema unspecified; Gemini #1326 reduces quorum without auto-emitted documentation |
| Codex | MAJOR | (see scripts/review/results/2026-04-17-plan-2323-codex.md) |
| Gemini | MAJOR | (see scripts/review/results/2026-04-17-plan-2323-gemini.md) |

**Overall result:** FAIL — MAJOR from all three even after stance-contract section was added. Plan requires revision before user approval.

**Blockers to resolve before approval:** see per-provider review artifacts under `scripts/review/results/2026-04-17-plan-2323-*.md`.

---

## Risks and Open Questions

- **Risk:** Provider CLIs may consume significant rate-limit budget when run 3× for every plan. Mitigation: document cost in the script header; do not auto-fire on cron by default.
- **Risk:** Gemini CLI issue #1326 (NO_OUTPUT) may make Gemini always return UNAVAILABLE until fixed. Mitigation: tolerate gracefully; ship without blocking on #1326.
- **Risk:** Extracting issue number from filename is brittle to naming drift. Mitigation: strict regex + clear error message.
- **Open:** Should the wrapper auto-run on plan commit via a hook? Recommend no — review is a cost decision, not automatic.
- **Open:** Should disagreement reports feed back into provider-routing-scorecard? Out of scope for v1; capture as follow-up.

---

## Complexity: T2

**T2** — shell wrapper + prompt file + small parser + tests. Depends on CLIs being installed (confirmed on dev-secondary).
