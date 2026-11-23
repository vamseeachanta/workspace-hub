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
| claude-r7 | **MINOR** |
| claude | **MAJOR** |
| codex-r1 | MAJOR |
| codex-r2 | MAJOR |
| codex-r3 | MAJOR |
| codex-r4 | MAJOR |
| codex-r5 | MAJOR |
| codex-r6 | MAJOR |
| codex-r7 | MAJOR |
| codex | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| disagreement-r3 | | Provider | Verdict | |
| disagreement-r4 | | Provider | Verdict | |
| disagreement-r5 | | Provider | Verdict | |
| disagreement-r6 | | Provider | Verdict | |
| disagreement-r7 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r3 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r4 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r5 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r6 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r7 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
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

### claude-r7

(no findings unique to this provider)

### claude

- **BLOCKER — the runtime toggle's stop path is unreachable while recording.** Pseudocode `codex_dictate_toggle` (lines 298-310) runs device probing *before* the `if recording pid exists` check. `probe_capture_device` opens the device with `arecord -D` (lines 220-225). While a recording is in progress, `plughw:N,M` is held exclusively by the running `arecord`, so the probe of `DICTATE_DEVICE_ALSA` fails with EBUSY → the helper `--choose` fallback probes the same busy device(s) and also fails → "still no device" → `return 0 without recording`. Result: the second hotkey press can never stop the recording; `arecord` runs until killed manually. This defect was introduced by the r7 stale-device-fallback revision (line 474). Fix: check the recording PID first; device selection belongs only on the start branch.
- **BLOCKER — helper path resolution from the installed launcher is unspecified and the current design cannot find it.** Pseudocode lines 301/303 have the launcher invoke `scripts/agents/lib/voice-dictation-detect.sh` — a repo-relative path — but at runtime the launcher executes as `~/.local/share/voice-dictation/codex-dictate.sh` through a symlink (evidence lines 101-102). The branch launcher resolves its location with `cd "$(dirname "${BASH_SOURCE[0]}")" && pwd`, which returns the *logical* symlink directory (`~/.local/share/voice-dictation`), not the repo, so `../../scripts/agents/lib/...` resolves to nothing. The plan specifies neither `readlink -f`/`pwd -P` resolution nor baking an absolute helper path into the GNOME command env. The covering test (`test_codex_dictate_runtime_falls_back_when_bound_device_is_stale`, line 353) stubs the helper, so a test-green implementation can still fail on the real symlinked layout.
- **No test covers the toggle's stop branch.** Every launcher test in the TDD list (lines 351-353) exercises the recording-*start* path. Nothing verifies that a second press stops `arecord`, transcribes, and injects — precisely the branch finding 1 breaks. A stop-while-recording test (stubbed busy-device probe + existing PIDFILE → arecord stopped) would have caught finding 1 at TDD time.
- **Every push-to-talk start now pays a 1-3 second probe penalty, unacknowledged.** `probe_capture_device` records 1 second under `timeout 3` (line 221), and `codex_dictate_toggle` probes the baked device on every start press (lines 299-301). Users press the hotkey and speak immediately; the first ~1-2 s of speech is lost on every dictation. §Risks (lines 482-489) does not mention this latency regression. Consider probing only after an `arecord` start failure rather than pre-emptively.
- **Install-time and runtime explicit-device policies contradict each other silently.** At install, an unusable `DICTATE_DEVICE_ALSA` returns inactive with *no* fallback ("explicit device unusable", lines 210-213, test line 349). At runtime, an unusable explicit device is *silently overridden* by auto-detection (lines 299-301, test line 353). If intentional (install = strict, runtime = self-healing), the plan should state it and require the launcher to notify when it overrides the user's explicit device; as written, the same env var means two different contracts.
- **Plan self-declares non-ready state.** Line 437: "Overall result: PENDING … r8 re-review is required before `status:plan-review`." Consistent with the gate, but it means the header/Artifact Map refresh and computed artifact cleanup (AC lines 411-413) must run again after this round — the five unstamped residue files listed in Retrieval are currently present and non-cited.
- Checks run with no finding: branch/commit existence, tracked-file absence, bootstrap section anchor, standards/test-pattern/legal-scan file existence, plan-index row, issue labels, live symlink/hotkey/audio reproduction, gitignore coverage of review results and `__pycache__`, the relocatable-schema `gsettings` syntax in AC line 390, r7 MAJOR-findings-addressed claims, and Gemini-UNAVAILABLE degradation consistency with the SHARED_SOUL T3→T2 policy.

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

### codex-r7

(no findings unique to this provider)

### codex

- **MAJOR:** The plan can break non-Linux bootstrap because it drops the prior OS guard from the installer contract. `scripts/memory/bootstrap-machine.sh` says it “Works on: Linux, macOS, Windows” at lines 7-10, and the plan adds a guarded voice hook after section 2.10 at `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:331`. But the new installer pseudocode at lines 233-272 starts directly with ALSA/GNOME selection and has no macOS/Windows no-op path. The prior branch installer explicitly handled macOS and Windows at `feat/voice-dictation-ecosystem:scripts/agents/install-voice-dictation.sh` lines 32-42. The TDD list also has no macOS/Windows no-op test. This is a blocker because the bootstrap script is cross-platform.
- **MAJOR:** The installer pseudocode still permits runtime mutation of a repo-tracked README. Plan pseudocode says that when no injector exists, the installer should “document the same warning in the installed README path” at `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:269-271`. The same plan makes `~/.local/share/voice-dictation` a symlink to repo `tools/voice-dictation` at lines 226-231 and lists `tools/voice-dictation/README.md` as a restored/updated repo artifact at line 324. That means a machine-specific installer run can dirty a tracked README depending on local `xdotool`/`wtype`/`ydotool` state. The only related test at line 366 checks printed warning behavior, not “must not edit README during install.”
- **MINOR:** The plan’s plan-review closeout step says to “commit and push this plan” at `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:411-413`, but live `git status --short --branch` shows `main...origin/main [ahead 1, behind 2]`. The plan does not require fetching/rebasing or otherwise resolving divergence before the plan-review commit. That is likely to turn the approval-gate push into a rejected push or an accidental mixed-history operation.

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

(no findings unique to this provider)

### disagreement-r7

- ### claude-r6
- ### codex-r6
- ### disagreement-r6
- ### gemini-r6

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

### gemini-r7

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
