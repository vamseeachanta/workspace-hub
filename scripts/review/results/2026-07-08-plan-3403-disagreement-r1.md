# Disagreement report — plan #3403 (2026-07-08)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MINOR |
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **Reproduction claim mischaracterized.** The plan's Evidence section says "Failure mode observed matches issue claim: YES" — but the issue body alleges *no capture device visible* (HDMI-only), while the plan's own probe (and my live re-check) shows the Plantronics present and recording, with only ALSA `default` broken. Two distinct failure modes; the plan reproduced the second, not the alleged one. The TDD table covers both states, so scope is intact — only the characterization is false, and it sits inside the load-bearing Step-1.5 reproduce gate.
- **AC #5 hardcodes `plughw:1,0`**, contradicting the plan's own risk note that the headset appears/disappears (ALSA card numbers aren't stable across replug/boot). The smoke test should use the installer's *selected* device; also a 1-second recording is a near-meaningless speech smoke — use 3–5 s.
- **`choose_alsa_device` default-probe underspecified.** "Probe default without recording user audio" names no mechanism (opening a capture stream *is* recording), and the deterministic test `test_default_broken_uses_concrete_capture_device` states no way to simulate a broken `default` — it needs an `arecord` PATH shim the TDD table never mentions (only `gsettings` is stubbed).
- **Convergence gap for an already-bound hotkey on a now-micless machine.** The inactive path skips binding but never touches the *existing* `<Super><Shift>v` binding (bound live since June 30) — leaving a stale hotkey pointing at a failing tool, the exact symptom class the issue targets. The plan should choose: unbind, or leave-with-warning.
- **Review fanout pipeline is broken (operational).** The 2026-07-08 r1 artifacts are 0-byte for Claude and Codex (the 50 KB Codex transcript went to `.md.err`), Gemini UNAVAILABLE on auth. Zero usable signal was produced, and 0-byte files masquerade as completed reviews. The plan's Artifact Map and AC #9 depend on this same pipeline for the code-stage gate — fix output routing and clean up the 0-byte residue first.
- **Branch-only citation.** The consulted handoff doc exists only on `feat/voice-dictation-ecosystem`; the plan directs cherry-picking issue-scoped files only and omits the handoff from Files to Change, so post-landing the plan on main cites an unreachable document, and the branch's disposition is unstated.

### codex

- Plan §Pseudocode lines 166-184 calls `arecord -l` inside `choose_alsa_device()` before any dependency handling, but the TDD list lines 219-225 has no case for `arecord` missing. On a fresh Linux machine without `alsa-utils`, this can abort the bootstrap path instead of producing the promised inactive/manual guidance. The prior branch installer handled missing `arecord` only later via `command -v arecord ... || missing_apt+=("alsa-utils")` in `feat/voice-dictation-ecosystem:scripts/agents/install-voice-dictation.sh`, so the plan needs an explicit missing-command branch and test.
- Plan §Pseudocode line 172 says “default capture probe is known-good without recording user audio,” but the plan never defines the probe command and its own evidence lines 108-114 verifies devices by recording WAV files. The test list lines 219-225 also lacks a `default`-healthy case and lacks a probe-failure/stderr case. This leaves the core selection behavior under-specified: implementation can either record user audio during install or skip `default` even when it is the correct working device.
- Plan acceptance lines 237-238 and TDD line 225 use bare `python3 -m py_compile tools/voice-dictation/transcribe.py`. Root `AGENTS.md` under `## Commands` says “Python: `uv run` always — never bare `python3`.” The plan should use the repo command policy or explicitly justify why this harness check is exempt.
- Plan TDD line 223 only verifies that a temp-home install creates `~/.local/share/voice-dictation` as a symlink. It does not test the existing-real-directory case, while the prior branch installer contains `[[ -e "${SHARE_DIR}" && ! -L "${SHARE_DIR}" ]] && rm -rf "${SHARE_DIR}"` in `feat/voice-dictation-ecosystem:scripts/agents/install-voice-dictation.sh`. Since the plan says to restore/recreate from that branch and install into user home, it needs a non-clobbering or backup contract plus a test; otherwise the installer can delete local user files under that path.

### gemini

- (none)
