# Disagreement report — plan #3403 (2026-07-08)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | MINOR |
| claude-r2 | MINOR |
| claude-r3 | **MINOR** |
| claude-r4 | **MAJOR** |
| claude-r5 | **MINOR** |
| claude-r6 | **MINOR** |
| claude | **MINOR** |
| codex-r1 | MAJOR |
| codex-r2 | MAJOR |
| codex-r3 | MAJOR |
| codex-r4 | MAJOR |
| codex-r5 | MAJOR |
| codex-r6 | MAJOR |
| codex | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| disagreement-r3 | | Provider | Verdict | |
| disagreement-r4 | | Provider | Verdict | |
| disagreement-r5 | | Provider | Verdict | |
| disagreement-r6 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r3 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r4 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r5 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r6 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
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

### claude-r6

(no findings unique to this provider)

### claude

- **Runtime device staleness has no contract.** Pseudocode line 261 bakes `DICTATE_DEVICE_ALSA=<selected_device>` (e.g. `plughw:1,0`) into a static GNOME binding string, but ALSA card numbers are not stable across USB re-enumeration — replugging the Plantronics or a boot-order change can renumber it, leaving `Super+Shift+V` invoking `arecord -D plughw:1,0` against a wrong/absent device. `codex_dictate_toggle` (line 295) says "record from DICTATE_DEVICE_ALSA or chosen default" — "chosen default" is undefined, and the launcher is never specified to source `voice-dictation-detect.sh` for runtime re-selection or fallback. The Risks bullet (line 456) only addresses device flakiness *in tests*. Silent hotkey failure after replug is the same failure class this issue exists to repair. Fix options: launcher probes the baked device and falls back to `--choose` on failure, or the risk explicitly names "re-run installer after replug" as the documented remediation in the README.
- **Opt-in `uv` path can abort when `uv` is absent.** Pseudocode line 243 runs `uv pip install --python "$target" faster-whisper` under `DICTATE_BOOTSTRAP_INSTALL=1` without a `command -v uv` guard, and no TDD row covers missing `uv` (the closest, `test_python_install_command_pins_target_interpreter` line 348, stubs `uv` as present). A naïve `set -e` implementation aborts bootstrap on a machine that opts in but lacks `uv` — the exact abort class the missing-`arecord` tests were added to prevent, applied inconsistently here.
- **The inert-warning command's executability is untested.** Line 280's inert command is `bash -lc '…'` — the stored gsettings string must itself contain single quotes, and line 281's mitigation ("keep the inert message single-quote-free") only protects the inner message, not the quoting layers the installer's `gsettings set` invocation must survive. Claude r6 already flagged "inert command quote fragility"; the resolution was a prose note, not verification. `test_inactive_install_replaces_stale_hotkey_with_inert_warning` (line 341) asserts only that the command "is an inert warning command, not `codex-dictate.sh`" — a mangled, unexecutable string passes that assertion. The test should additionally execute the captured command string (with stubbed `notify-send`/`logger`) or at minimum `bash -n` its payload.
- **Bootstrap hook is syntax-checked only.** Files-to-Change (line 316) adds a "guarded voice-dictation install hook" to `scripts/memory/bootstrap-machine.sh`, but the only coverage is `bash -n` (line 363). Nothing asserts the guard exists (the 2.10 precedent is `bash "${SET_AGY_MODEL}" || true` plus an `-x` existence check). The installer's exit-0 contract makes this low-probability, but a hook without the `|| true`/existence guard breaks every fresh machine's bootstrap if the installer is missing or a future edit lets a non-zero code escape — and no test would catch it.
- **Reproduction environment is single-session.** All evidence (line 76 onward) is stamped 2026-07-09T02:31–02:34Z from one session. I re-reproduced both probes live during this review (default rc=1 "Host is down", `plughw:1,0` rc=0), so the claims hold now — but the plan does not require the implementer to re-verify the broken-`default` state before trusting it at implementation time. Given the issue's own history of the failure mode *changing between observations* (no-device → device-visible-default-broken, line 131), the live-convergence AC (line 366) should note that a third state (default healed) is possible and the installer must converge correctly there too. The pseudocode handles it implicitly (default is simply never probed), so this is documentation-tightening only.
- Checks run with no finding: all 24 review-artifact paths exist; both cited commits exist with matching content; issue labels exact-match; `docs/plans/README.md` row exists; `gsettings` relocatable-schema AC syntax executes correctly live; `.gitignore` covers both `__pycache__/` and `scripts/review/results/`; all three Codex r6 MAJOR blockers have corresponding new test rows; Gemini UNAVAILABLE degradation matches the SOUL T3→T2 convention; test-harness pattern directories exist as cited.

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

### codex-r6

(no findings unique to this provider)

### codex

- Plan Acceptance Criteria lines 366-376 require live installer convergence and GNOME hotkey verification, and Pseudocode lines 221-261 writes `~/.local/share`, `~/.local/bin`, and `gsettings`. Current Codex environment is workspace-write only, and `gsettings get` emitted `dconf-CRITICAL ... unable to create file '/home/vamsee/.cache/dconf/user': Read-only file system`. The plan does not state that the live installer/hotkey convergence step requires escalated execution or a user-run/manual verification path, so closeout can fail even after repo tests pass.
- Plan Evidence lines 118-127 claims `arecord -l` sees Plantronics and `arecord -D plughw:1,0` exits `0`. Current retrieval contradicts that: `/proc/asound/cards` still lists Plantronics, but `arecord -l` returns `no soundcards found...` and `arecord -D plughw:1,0` exits `1`. The plan’s conditional skip at lines 375-377 helps, but the embedded “usable concrete device” proof is stale and must be refreshed before label movement.
- Plan Evidence line 103 lists `/mnt/local-analysis/workspace-hub/tools/voice-dictation/codex-dictate.sh` under “Hotkey and symlink state,” but current `ls` returns `No such file or directory`. This conflicts with the same plan’s lines 27-29 claim that current `main` has no launcher and the user-level symlink points at a source directory without it.
- Plan line 414 says `Overall result: PENDING -- r6 MAJOR findings are addressed in this draft; r7 re-review is required before status:plan-review`. That is not implementation-ready evidence. Until r7 exists and the header/artifact map are refreshed per lines 390-392, the plan cannot be moved through the plan-review gate.

### disagreement-r1

(no findings unique to this provider)

### disagreement-r2

(no findings unique to this provider)

### disagreement-r3

(no findings unique to this provider)

### disagreement-r4

(no findings unique to this provider)

### disagreement-r5

(no findings unique to this provider)

### disagreement-r6

- ### claude-r5
- ### codex-r5
- ### disagreement-r5
- ### gemini-r5

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

### gemini-r6

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
