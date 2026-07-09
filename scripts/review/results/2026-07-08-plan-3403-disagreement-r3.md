# Disagreement report — plan #3403 (2026-07-08)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | MINOR |
| claude-r2 | MINOR |
| claude | **MINOR** |
| codex-r1 | MAJOR |
| codex-r2 | MAJOR |
| codex | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude-r1

(no findings unique to this provider)

### claude-r2

(no findings unique to this provider)

### claude

- **Artifact Map rows 160–162 cite dead review artifacts.** `scripts/review/results/2026-07-08-plan-3403-claude.md` and `-codex.md` are 0-byte failed-run residue (the 66 KB `.err` sibling holds the crash), and `-gemini.md` is the UNAVAILABLE stub — yet the map lists them as the canonical "Plan review — Claude/Codex/Gemini" artifacts, contradicting the header (line 10) which correctly cites the `-r1`/`-r2` files. Codex r2 flagged "stale failed review state / artifact paths stale" and the revision list (lines 325–338) does not include cleaning this up. The map also gives no filename for the required post-FAIL re-review round (r3), while an unexplained `2026-07-09-plan-3403-claude.md` already sits in the results directory.
- **Acceptance criterion #4 recreates the residue the plan deletes, making `test_stale_pycache_removed` order-dependent.** `uv run python -m py_compile tools/voice-dictation/transcribe.py` (line 299) writes its output to the PEP 3147 default location — `tools/voice-dictation/__pycache__/transcribe.cpython-*.pyc` — which is exactly the directory the Files-to-Change table deletes (line 257) and that `test_stale_pycache_removed` (line 284) asserts absent. Run the acceptance checklist top-to-bottom and the test suite fails afterward. Fix: syntax-check without a cache write (e.g. `python -c "compile(open(f).read(), f, 'exec')"`), or drop the pycache assertion from the persistent test suite and make the deletion a one-time implementation step.
- **Pseudocode Python-selection path falls through to binding with an empty interpreter.** Lines 217–220: when `choose_python_with_faster_whisper()` returns empty and the uv install *succeeds*, `selected_python` is never re-assigned before "bind GNOME hotkey with env … DICTATE_PYTHON=…" — binding with an empty `DICTATE_PYTHON`. The failure branch ("keep hotkey inactive/warning-only") also has no explicit return, so control appears to reach the bind line regardless. `test_python_missing_keeps_hotkey_inactive` (line 283) covers install-failure but no test covers the install-success re-selection path.
- **Inert-binding pseudocode creates a new fleet-wide hotkey on machines that never had one.** Line 214: "if GNOME keybinding exists **or can be written**: bind the configured hotkey to [warning command]". Because the installer is wired into `bootstrap-machine.sh` (line 260), every GNOME machine in the fleet — including ones that never installed voice dictation — would get a new `Super+Shift+V` binding pointing at a notifier. The gap statement (line 69) and the covering test (`test_inactive_install_replaces_stale_hotkey_with_inert_warning`, line 281) both scope this to a *pre-existing* binding only. Pseudocode contradicts its own gap/test; should be "rewrite an existing codex-dictate binding to inert; never create one on an inactive machine."
- **Installer never checks for a text injector.** The plan's own principle is "never bind a failing launcher" (line 303), applied to mic and Python — but not to xdotool/wtype, which the launcher needs to deliver the transcript. Verified mitigation: the branch launcher degrades at runtime (notify + transcript on stdout, `codex-dictate.sh` lines 31–40), so this is not a hard failure — but the user speaks 5 seconds of audio before learning nothing will be typed. A one-line installer warning ("no injector found; transcripts will print only") plus a README note would close the asymmetry cheaply.

### codex-r1

(no findings unique to this provider)

### codex-r2

(no findings unique to this provider)

### codex

- `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:161` maps “Plan review -- Codex” to `scripts/review/results/2026-07-08-plan-3403-codex.md`, but `wc -c` shows that file is `0` bytes. The header correctly cites `...-codex-r1.md` and `...-codex-r2.md` at line 10. Leaving the zero-byte file in the Artifact Map lets a later gate treat failed-run residue as review evidence.
- `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:217-220` does not define correct control flow after `choose_python_with_faster_whisper()` returns empty. It says to install `faster-whisper` or keep the hotkey inactive, then immediately says to bind GNOME with `DICTATE_PYTHON=...`. There is no re-selection after a successful install and no explicit return on failure, so the plan still permits binding a launcher with an empty or unusable interpreter.
- `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:213-215` says inactive installs should bind the warning command if a GNOME keybinding “exists or can be written.” Because the same plan wires the installer into fleet bootstrap at lines 259-260, this can create a new `Super+Shift+V` warning hotkey on every inactive GNOME machine, not only replace a stale `codex-dictate` binding. That contradicts the scoped gap at line 69 and test at line 281, both of which target an existing stale binding.
- The acceptance list never runs the installer on the live user path. Lines 300-303 test the helper and assert binding properties, but there is no acceptance command like `bash scripts/agents/install-voice-dictation.sh` followed by `gsettings get ... command` to verify the actual `Super+Shift+V` convergence. That misses the issue’s desired outcome from `gh issue view 3403`: “installer should converge the symlink/hotkey and test command path” when a capture device is visible.
- `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:300-301` makes the live mic smoke test unconditional. Current live retrieval contradicts the embedded audio state: `cat /proc/asound/cards` shows the Plantronics card, but `arecord -l` returns `arecord: device_list:277: no soundcards found...`. The issue body explicitly has two states: no capture device visible and device visible. The plan needs separate acceptance for inactive/no-capture convergence and a connected-mic smoke precondition, or closeout can block on hardware state rather than implementation correctness.

### disagreement-r1

(no findings unique to this provider)

### disagreement-r2

- ### claude-r1
- (no findings unique to this provider)
- ### codex-r1
- (no findings unique to this provider)
- ### disagreement-r1
- ### gemini-r1
- (no findings unique to this provider)
- (no findings unique to this provider)

### gemini-r1

(no findings unique to this provider)

### gemini-r2

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
