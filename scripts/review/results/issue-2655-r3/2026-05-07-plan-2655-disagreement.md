# Disagreement report — plan #2655 (2026-05-07)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MINOR |
| codex | UNAVAILABLE (codex CLI failed, rc=3: INCOMPATIBLE (0.129.0 in known-bad range [>= 0.124.0) — upstream openai/codex#19945; see workspace-hub #2479; run scripts/install/pin-codex.sh to downgrade) ) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **Matcher rewrite has wider blast radius than the test list covers.** Plan §Pseudocode lines 193-201 prescribes `if pattern represents a directory prefix ending in /: startswith else: equals`. This change applies to `match_remediation_rule()` which iterates `LEGACY_REMEDIATION_RULES` — all rules, not just `nested_repo_context_drift`. Reading `scripts/analysis/provider_session_ecosystem_audit.py:74,86-90,105-107,158-164` shows other rules with singleton patterns: `"scripts/work-queue/generate-html-review.py"`, `"scripts/work-queue/close-item.sh"`, `".claude/skills/workspace-hub/work-queue-workflow/SKILL.md"`, etc. Today, `…close-item.sh.bak` would silently match `legacy_work_queue_lifecycle` via `startswith`; after the rewrite it would not. The TDD Test List (lines 240-247) only adds `nested_repo_context_drift` tests — there is no regression assertion proving (a) other rules' exact-singleton patterns still match the exact path, or (b) their `.bak`/`.tmp` suffix variants no longer match. Either outcome may be desirable, but the plan does not state which, and §Files to Change row "Modify after approval `scripts/analysis/...py`" describes only the nested-rule rationale.
- **TDD list conflates RED-on-day-one with already-GREEN tests.** Acceptance #1 (line 253) demands the singleton-collision tests be RED before code changes. Per the empirical verification above, those *will* be RED. But two of the six tests in §TDD Test List — `test_codex_nested_worldenergydata_tests_route_to_worldenergydata_tests` (input `tests/unit/cost/test_proxy_comparison.py`) and `test_codex_nested_assethold_paths_route_to_assethold_root` (input `src/assethold/signals/watchlist.py`) — would already PASS today against the existing `path.startswith("tests/unit/cost/")` and `path.startswith("src/assethold/")` patterns at lines 178-181. The plan never labels which tests are RED-required vs GREEN-on-arrival; that distinction is the difference between "verifying a regression-guard" and "alleging code is broken when it isn't".
- **Acceptance criterion #2 redundancy/ambiguity.** Line 254 says "All #2655-added tests are collected and pass via a targeted `-k` or explicit test-id command, **in addition to** the broader file command: `uv run --no-project pytest tests/analysis/test_provider_session_ecosystem_audit.py -v`". The broader file command already runs the new tests. The criterion as stated requires running both with no rationale; if intent is "test names must be uniquely matchable by `-k`," say that. Otherwise this is unfalsifiable boilerplate.
- **`.md.draft` is a fabricated negative.** Line 244 demands a RED test for `.md.draft` suffix collision. There is no evidence in `analysis/provider-session-ecosystem-audit.json` (verified — only `.md` exact path appears with count=8) or in any prior-art workflow that `.md.draft` is a real artifact name in workspace-hub. `.md.bak` is plausible (editor backup); `.md.draft` is invented. This is a low-cost test, but it tests theoretical safety against a suffix that has zero observed occurrences. Either downgrade to a code-comment example or replace with a real observed-or-likely suffix (`.md~`, `.orig`).
- **Generated-artifact diff-bounding rule is described in prose, not enforced.** Acceptance #4 (line 256) says "compare the before/after `nested_repo_context_drift` remediation-hint block; if the only delta is `generated_at`, do not commit generated files; stop instead of committing if unrelated provider counts/rule IDs or large timestamp churn dominate the diff". This is a manual judgment call with no script and no diff-bound threshold (what counts as "dominate"?). Per `.claude/rules/patterns.md`, level-2 enforcement (script returning exit 0/1) beats level-0 prose. This is not a blocker for plan approval, but the criterion as written cannot be objectively verified by a reviewer or by the bot harness.
- **`tests/unit/cost/` pattern depends on workspace-hub never gaining a real `tests/unit/cost/`.** Verified today via `git ls-files` — workspace-hub has no such tree. But the rule mis-routes the moment any contributor adds `tests/unit/cost/test_X.py` to workspace-hub (e.g. for control-plane cost-tracking work). §Risks does not enumerate this collision. The corresponding `src/worldenergydata/` and `src/assethold/` patterns are similarly fragile but lower probability. A risk-bullet acknowledging "if workspace-hub ever owns code under these prefixes, this rule mis-routes" would close the gap.

### codex

- (none)

### gemini

- Plan § "Artifact Map" and "Existing repo code" cite `scripts/analysis/provider_session_ecosystem_audit.py`. Glob search returns zero matches; this file does not exist at HEAD in the current environment.
- Plan § "Artifact Map" and "Existing test proof" cite `tests/analysis/test_provider_session_ecosystem_audit.py`. Glob search returns zero matches; this file does not exist at HEAD in the current environment.
- Plan § "Documents consulted" cites `analysis/provider-session-ecosystem-audit.json`. Glob search returns zero matches for this file at the expected path; this file does not exist at HEAD in the current environment.
- Plan § "Documents consulted" cites `docs/ops/legacy-claude-reference-map.md`. Glob search returns zero matches; this file does not exist at HEAD in the current environment.
