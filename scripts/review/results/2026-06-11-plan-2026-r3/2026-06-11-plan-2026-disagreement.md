# Disagreement report — plan #2026 (2026-06-11)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- GitHub issue #2026 body requires operator-facing tasks that the plan does not cover: “6. [ ] State report command: show all threads, counts by state” and “7. [ ] Migration: scan existing inbox and label all current emails.” The plan’s Files to Change only creates library modules and docs/tests (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:492-508`), and its acceptance criteria only require exported Python functions plus tests/scans (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:562-578`). No CLI/report command or initial inbox migration/labeling deliverable is specified. This leaves required issue scope unimplemented.
- Plan D4 promises “default CLI behavior that prints planned operations unless an explicit `--apply-labels` flag is supplied” (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:281-285`), but the plan does not create or modify any CLI entrypoint in Files to Change (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:492-508`) and does not include an acceptance criterion or test for `--apply-labels` (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:546-548`, `562-578`). The promised safe label-apply path is therefore not actually executable or verifiable from the plan.
- D2 is internally inconsistent about account email mapping. It says “Production account mapping should come from local config/credentials” (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:241`), then gives a default config with literal email addresses (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:245-253`) and pseudocode that falls back to “default ace/personal config” when no local config exists (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:366-369`). The test list reinforces this fallback with `test_account_config_defaults_to_ace_and_personal` for “missing local config” (`docs/plans/2026-06-11-issue-2026-email-state-tracking.md:519`). The plan needs to decide whether tracked code may embed these literal account emails or whether defaults are alias-only and literal normalization requires local config.

### gemini

- **`AttributeError` in config loading:** Plan section "Pseudocode" defines `load_account_scope(config_path=None, env=None)` and then attempts `env.get("EMAIL_QUEUE_ACCOUNTS_CONFIG")`. However, `pending_work_report` calls `load_account_scope()` without arguments, defaulting `env` to `None`. This will trigger a runtime `AttributeError: 'NoneType' object has no attribute 'get'`.
- **Schema mismatch for grace sweep:** Plan section "Pseudocode" for `sweep_grace` filters records using the condition `now - completed_at > grace_days`. However, the quoted schema in "Evidence (embedded verification)" for `docs/design/email-queue-state-schema.yaml` does not contain a `completed_at` field (only `ts_utc`). The plan fails to add `completed_at` to the schema or instruct the use of `ts_utc`.
- **Missing state transition edges for `extracted`:** Plan section "D8 - State Machine Reactivation Edge" requires updating the transition table to allow missing-extraction transitions to `inbound` (e.g., `purged -> inbound`). However, the `reactivate_reply` pseudocode executes a direct transition to `extracted` (`to_state="extracted"`) if `linked_extraction` exists. The plan fails to mandate updating the transition table to authorize `awaiting-reply -> extracted`, `completed -> extracted`, or `purged -> extracted`, ensuring the validator will reject these reactivations.
- **Contradictory batch sweep locking:** Plan section "Pseudocode" for `sweep_grace` specifies processing records in batches of 100 and claims to "rebuild snapshot/meta before releasing the batch lock". However, it loops over each item to call `_transition_locked`, which only accepts a single event and explicitly acquires an exclusive file lock (`acquire fcntl LOCK_EX`) to execute a full snapshot rebuild internally. This yields 100 redundant file locks and snapshot rebuilds per batch, actively defeating the batched rebuild intent.
- **Missing warning metadata for no-id reactivation:** Plan section "D5 - Dedup Key Correction" states that "the implementation should emit a warning metadata field when it sees a no-id reactivation." However, the corresponding pseudocode (`reactivate_reply` and `_transition_locked`) provides no mechanism or logic to inject or emit this warning metadata field.
- **Unused state directory fallback:** Plan section "D1 - Runtime State Location" requires defaulting to `~/.hermes/email-state/`, and "Pseudocode" defines `resolve_state_dir(env)` for this purpose. However, this helper function is never called. The main wrapper functions strictly require `log_path` as a positional argument, contradicting the claim that the wrapper itself provides a default runtime state location.

