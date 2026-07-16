# Disagreement report — plan #3555 (2026-07-16)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- Plan §Phase 0 lines 154-166 violates the plan’s own TDD order. It says “The implementation will first run fresh interactive Claude and Codex sessions” and “write a schema-validated, de-identified attestation” before the TDD list’s line 272 claim that tests will be written and observed failing before implementation. The attestation has correctness-critical privacy behavior at lines 165-166, so validator/schema tests must exist and fail before publishing the JSON evidence artifact.
- Plan §Phase 3 line 198 and Acceptance Criteria line 285 require machine setup paths to call the canonical config sync, but the TDD list lines 252-270 has no test that `scripts/setup/new-machine-setup.sh` stops writing the old Claude setting directly. Current `scripts/setup/new-machine-setup.sh` lines 67-103 still runs `claude config set statusBarEnabled true` or merges `statusBarEnabled` into `~/.claude/settings.json`, which can bypass the proposed canonical `statusLine` renderer path.
- Plan TDD line 270 defines `test_live_codex_strict_config_when_available` as “config accepted and native selector renders all items,” but the plan does not specify an automatable probe. The installed CLI exposes `codex debug` subcommands only for `models`, `app-server`, and `prompt-input`; `codex features list` confirms `goals` but does not render or validate statusline items. Without a PTY/screenshot/manual-attestation harness explicitly in the plan, this test is underspecified and likely non-implementable as TDD.

