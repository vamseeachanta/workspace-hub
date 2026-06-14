# Disagreement report — plan #3057 (2026-06-13)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | MINOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **(MAJOR) The `classify_line` third-argument shape change has no backward-compat normalization or test — unlike the parallel `select_tasks` change that got both.** Plan Pseudocode (lines 401–416) defines `classify_line_detail(..., preserved_entries, ...)` iterating `for entry in preserved_entries: if match_fingerprint(line, entry.fingerprint)`, and the public wrapper `classify_line(line, catalog_keys, preserved_entries)` (413–416) delegates to it. This changes the third argument from a **list of bare fingerprint dicts** (today's contract — `cron_apply.py:138` and `cron-audit.py:113-116` both return bare fps; `cron_transaction.py:193` does `for fp in external_fingerprints: match_fingerprint(line, fp)`) to a **list of entry dicts with a `.fingerprint` member**. The existing passing test `tests/cron/test_cron_transaction.py:147-150` calls `ct.classify_line(line, ["run-task.sh"], fps)` with `fps = [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}]` (a bare fingerprint) and asserts `"preserved_external"`. Under the pseudocode's `entry.fingerprint` access, a bare dict yields no fingerprint → `match_fingerprint` fails → the deckhand line classifies as `"uncataloged"` → `plan_cutover` **aborts (fail-closed)**. The plan explicitly solved exactly this shape-compat problem for `select_tasks` (`normalize_machine_tokens` + `test_select_tasks_accepts_existing_string_machine_id_callers`, lines 368–370 / 509) but the Files-to-Change row for `cron_transaction.py` (480) and the test-list rows for `test_cron_transaction.py` (488) only cover env-line preservation and `select_tasks` back-compat — there is **no** `classify_line` bare-fingerprint normalization step and **no** test for it. An implementer following the pseudocode literally regresses the external-preservation guarantee the whole plan exists to protect.
- **(MINOR) The cross-path "byte-identical" parity claim contradicts the existing whitespace separators.** Acceptance criterion (line 550) and `test_setup_cron_and_cron_apply_use_shared_renderer_for_same_task` (510) require "Rendered schedule and command text are byte-identical for common selected tasks." But `setup-cron.sh` emits `print(f'{schedule}  {command}')` with **two** spaces, while `cron_transaction.py:278` `render_block` joins with **one** space (`f"{task['schedule']} {task['command']}"`). The plan never names a canonical join separator for the shared renderer, so either the parity test compares only the separate schedule/command fields (and the actual crontab *lines* still diverge by a byte, undermining the stated goal) or one of the two call sites must change its separator — which the plan does not call out. Pin the separator in the `cron_render.py` contract.
- **(MINOR / verify-during-impl) Idempotency depends on the unstated render-block separator surviving a re-parse.** `plan_cutover`'s idempotency invariant (cron_transaction.py:310 docstring) plus `test_run_cutover_second_pass_is_idempotent_after_expansion` (514) assume the rendered managed line re-parses to the same command key on pass two. This is plausibly fine given the raw+rendered key union (427), but it is coupled to finding #2's separator decision — a two-space → one-space normalization mid-line must not change the fallback full-command key for `notification-purge`. Worth an explicit assertion in the idempotency test.

### codex

- `docs/plans/2026-06-13-issue-3057-cron-hygiene-hardening.md` header says “post-r10 fixes need fresh review before `status:plan-review`” and the Artifact Map lists failed reviews only through `scripts/review/results/2026-06-13-plan-3057-r10/`, but the live tree already contains `scripts/review/results/2026-06-13-plan-3057-r11/2026-06-13-plan-3057-claude.md`, `.err`, `codex.md`, and `codex.md.err`. The plan’s review-artifact state is stale and will mislead the next gate operator about which review round is current.
- The revision log in `docs/plans/2026-06-13-issue-3057-cron-hygiene-hardening.md` is internally contradictory: it says “R4: explicitly scoped schedule-field parity out of this issue because `setup-cron.sh` honors `schedule_by_machine` while `cron_apply.py` still renders `task["schedule"]`,” then says “R5: moved effective `schedule_by_machine` selection into the shared renderer contract.” The current Deliverable/Pseudocode/Acceptance Criteria choose the R5 behavior, but the stale R4 note remains and creates avoidable reviewer ambiguity.

