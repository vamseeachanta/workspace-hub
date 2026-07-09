# Disagreement report — plan #3403 (2026-07-08)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | MINOR |
| claude-r2 | MINOR |
| claude-r3 | **MINOR** |
| claude-r4 | **MAJOR** |
| claude-r5 | **MINOR** |
| claude | **MINOR** |
| codex-r1 | MAJOR |
| codex-r2 | MAJOR |
| codex-r3 | MAJOR |
| codex-r4 | MAJOR |
| codex-r5 | MAJOR |
| codex | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| disagreement-r3 | | Provider | Verdict | |
| disagreement-r4 | | Provider | Verdict | |
| disagreement-r5 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r3 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r4 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r5 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude-r1

(no findings unique to this provider)

### claude-r2

(no findings unique to this provider)

### claude-r3

(no findings unique to this provider)

### claude-r4

(no findings unique to this provider)

### claude-r5

(no findings unique to this provider)

### claude

- **AC line 379's example residue list does not match the residue actually on disk.** The plan names `2026-07-08-plan-3403-disagreement.md` as an example — no such file exists — and omits `2026-07-08-plan-3403-claude.md.err`, which does exist (0 bytes, 22:21 fanout). The actual set is `claude.md`, `claude.md.err`, `codex.md`, `codex.md.err`, `gemini.md`. The governing rule ("every non-cited artifact matching `*plan-3403*` not listed in the Review artifacts header") is computed rather than glob-hardcoded, so it still covers reality — but the stale examples are exactly the defect class Claude r5 flagged, reproduced one revision later. Recompute the example list or drop it and keep only the rule.
- **The cleanup rule and the mandated r6 re-review are mutually inconsistent as written.** Line 399 requires an r6 re-review before `status:plan-review`, but the Review-artifacts header (line 10) and Artifact Map stop at r5. AC line 379 requires removing every `*plan-3403*` artifact "not listed in this plan's `Review artifacts` header" before the plan-review commit — so the r6 artifacts this plan itself mandates would be classified as removable residue unless the header is updated in the same revision. The plan must state that the header is refreshed to include the final round's artifacts before the cleanup criterion is evaluated.
- **Claude r5 finding 3 was not addressed and remains live.** Files-to-Change (line 310) still lists `docs/plans/README.md` as a pending "Update | Add this plan to the index," but the row already exists uncommitted at `docs/plans/README.md:206`, and the plan file itself is untracked on `main` on a machine with a known silent auto-sync pusher (`feedback_autosync_silent_pusher`; current git status shows the modification pending sweep). An implementer following the plan verbatim can double-add the row, and the uncommitted plan/index/artifacts can be swept into an unrelated `chore(sync)` commit before the deliberate plan-review commit at AC line 378. The plan should acknowledge the row exists and pull the commit-and-push step forward.
- **The no-Python inactive path underspecifies the hotkey rewrite that the no-mic path specifies explicitly.** Pseudocode line 247 says "keep any existing codex-dictate hotkey inactive/warning-only" when `faster_whisper` is unavailable, but unlike the no-mic branch (lines 230–233, which spells out the inert `notify-send`/`logger` rewrite), it never says whether the pre-existing binding — which on the live machine points at the real launcher — is rewritten to the inert command or left pointing at a launcher that will fail at transcription time. `test_python_missing_keeps_hotkey_inactive_by_default` says "uses inactive warning behavior," implying a rewrite; align the pseudocode so implementer and test converge.
- **Nested-quoting hazard in the inert warning command (pseudocode line 232).** The `bash -lc '…"$msg"…'` string must survive being stored as a GVariant string through `gsettings set`. It works today only because the message text contains no single quotes; any future edit to the message that introduces one breaks the binding silently. Worth a one-line constraint in the plan ("message must remain single-quote-free" or build the command via a helper) so the fragility is explicit.

### codex-r1

(no findings unique to this provider)

### codex-r2

(no findings unique to this provider)

### codex-r3

(no findings unique to this provider)

### codex-r4

(no findings unique to this provider)

### codex-r5

(no findings unique to this provider)

### codex

- Plan lines 185-187 make the load-bearing deliverable “restores `Super+Shift+V` dictation” and selects a usable ALSA device when `default` is broken, but the TDD list lines 318-340 never verifies that `tools/voice-dictation/codex-dictate.sh` actually passes `DICTATE_DEVICE_ALSA` into its `arecord` command. The tests only verify installer binding strings (`test_concrete_capture_device_selected_after_successful_probe`, line 321; live gsettings AC lines 357-359). A restored or edited launcher can ignore the selected device and still pass the planned tests until the live hotkey fails.
- Plan lines 363-364 rely on `~/.local/share/voice-dictation/dictate-test.sh 5 "$dev"` for the live smoke path, but no TDD row verifies `tools/voice-dictation/dictate-test.sh` accepts the selected device argument and uses it in `arecord -D`. The prior branch version does this, but the plan is to restore/update the file (lines 300-302), and the current planned coverage only syntax-checks it (line 339). This leaves the hardware smoke command itself unprotected.
- Plan lines 198-204 check `DICTATE_DEVICE_ALSA` before checking whether `arecord` exists. The TDD list has `test_missing_arecord_returns_inactive` (line 319) and explicit-device tests (lines 323-324), but no combined case for `DICTATE_DEVICE_ALSA` set while `arecord` is absent. That path is correctness-critical for fresh machines with inherited env config: a naïve `set -e` implementation could abort in `probe_capture_device`, or report “explicit device unusable” instead of the actionable missing-`alsa-utils` reason.

### disagreement-r1

(no findings unique to this provider)

### disagreement-r2

(no findings unique to this provider)

### disagreement-r3

(no findings unique to this provider)

### disagreement-r4

(no findings unique to this provider)

### disagreement-r5

- ### claude-r4
- ### codex-r4
- ### disagreement-r4
- ### gemini-r4

### gemini-r1

(no findings unique to this provider)

### gemini-r2

(no findings unique to this provider)

### gemini-r3

(no findings unique to this provider)

### gemini-r4

(no findings unique to this provider)

### gemini-r5

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
