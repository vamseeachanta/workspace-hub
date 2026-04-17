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

## Pseudocode

```
main(plan_file, providers=[claude,codex,gemini]):
    validate plan_file exists and matches docs/plans/YYYY-MM-DD-issue-NNN-slug.md
    issue_num = extract_issue_num(plan_file)
    today = YYYY-MM-DD
    prompt_file = scripts/review/plan-review-prompt.md   # file-path based

    tmpdir = mktemp -d
    for provider in providers:
        run_in_background:
            provider_cli_invoke(provider, plan_file, prompt_file) > tmpdir/<provider>.raw
            normalize_to_verdict_headings(tmpdir/<provider>.raw) > scripts/review/results/$today-plan-$issue_num-$provider.md
    wait for all
    summarize_disagreement(scripts/review/results/$today-plan-$issue_num-*.md) > disagreement.md

provider_cli_invoke(provider, plan_file, prompt_file):
    case provider:
        claude: claude -p "@$prompt_file on plan file $plan_file — return sections VERDICT, RETRIEVAL, FINDINGS, BLOCKERS"
        codex:  codex exec --no-interactive "$(cat $prompt_file) $plan_file"
        gemini: gemini -p "$(cat $prompt_file) $plan_file"
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

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_extracts_issue_num_from_filename | `2026-04-17-issue-2323-slug.md` → `2323` | valid plan path | `2323` returned |
| test_rejects_nonconforming_filename | non-date-prefixed filename rejected | `bad-name.md` | exits 1 |
| test_writes_claude_artifact | claude produces artifact in canonical path | mock claude CLI returning fixed text | file exists at `scripts/review/results/.../2323-claude.md` |
| test_parallel_execution | 3 providers run in parallel, not serial | mocks with sleep 2 | total wall time <3 s |
| test_gemini_unavailable_does_not_abort_codex | Gemini fails, Codex succeeds | mock gemini exit 1 | gemini artifact has `UNAVAILABLE`, codex artifact normal |
| test_disagreement_report_captures_unique_finding | one reviewer flags X, others miss | fixture artifacts | disagreement.md lists X under that provider's unique column |
| test_prompt_is_file_path_based | wrapper never inlines full plan text | mock CLI record | invocation string contains `@$prompt_file` and plan path, not plan body |

---

## Acceptance Criteria

- [ ] `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-17-issue-2323-cross-ai-review-fanout.md` runs all three providers in parallel and produces 3 per-provider artifacts + 1 disagreement report.
- [ ] Wall time is dominated by the slowest provider, not the sum of providers.
- [ ] Artifacts match `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md` naming.
- [ ] Disagreement report lists per-provider verdict + unique-findings summary.
- [ ] Single-provider failure (simulated via mock) does not abort the other two; failing provider's artifact contains `UNAVAILABLE` verdict.
- [ ] `docs/plans/README.md` documents the command as the canonical way to run adversarial review.
- [ ] At least 5 tests pass.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Gemini #1326 may make 2+ provider rule unsatisfied; mock CLI approach unspecified; cost control is comment not guard; retry-artifact overwrite behavior unspecified |
| Codex | MAJOR | (see scripts/review/results/2026-04-17-plan-2323-codex.md — correctness + scope issues) |
| Gemini | MAJOR | (see scripts/review/results/2026-04-17-plan-2323-gemini.md — correctness + scope issues) |

**Overall result:** FAIL — MAJOR from Codex+Gemini. Plan requires revision before user approval.

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
