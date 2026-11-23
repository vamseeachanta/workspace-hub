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
| claude-r8 | **MAJOR** |
| claude | MINOR |
| codex-r1 | MAJOR |
| codex-r2 | MAJOR |
| codex-r3 | MAJOR |
| codex-r4 | MAJOR |
| codex-r5 | MAJOR |
| codex-r6 | MAJOR |
| codex-r7 | MAJOR |
| codex-r8 | MAJOR |
| codex | MINOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| disagreement-r3 | | Provider | Verdict | |
| disagreement-r4 | | Provider | Verdict | |
| disagreement-r5 | | Provider | Verdict | |
| disagreement-r6 | | Provider | Verdict | |
| disagreement-r7 | | Provider | Verdict | |
| disagreement-r8 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r3 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r4 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r5 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r6 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r7 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r8 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
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

### claude-r8

(no findings unique to this provider)

### claude

- **Tilde in the prescribed GNOME binding command will not expand — a literal implementation produces a dead hotkey.** Pseudocode line 275 sets the binding command to `env DICTATE_DEVICE_ALSA=… DICTATE_PYTHON=… bash ~/.local/share/voice-dictation/codex-dictate.sh`. GNOME media-keys spawns this via `g_spawn` — no shell, no tilde expansion — and `bash` receives the literal string `~/.local/share/…` as `argv[1]`, which it opens as a filename without expanding (tilde expansion is a shell parse-time feature, not applied to received arguments). The plan's own live evidence (line 107) shows the working binding uses the absolute `/home/vamsee/…` path. The pseudocode must specify `$HOME`-expanded absolute paths in the stored command. No test in the TDD list asserts absolute-path expansion of the written command.
- **The acceptance-criteria suite cannot detect defect #1.** AC lines 409–411 verify the live binding by substring (`DICTATE_DEVICE_ALSA=…`, `DICTATE_PYTHON=…`, `codex-dictate.sh`) — a tilde-broken command passes all three. The hardware smoke test (AC line 416) invokes `dictate-test.sh` directly from a shell, bypassing the stored binding entirely. So a hotkey that fails on every keypress satisfies every listed criterion. The plan already has the right pattern for the *inert* command (`test_inert_warning_command_executes`, line 387) but never applies it to the *active* command. Add an executability assertion (execute the captured active binding payload with stubbed `arecord`/state dir) or an AC that runs the stored command string end-to-end.
- **Runtime explicit-device conflation, pseudocode lines 311–323.** The installer bakes `DICTATE_DEVICE_ALSA` into the GNOME binding (line 275), so every hotkey invocation sets `explicit_device = true` — a genuine user env override and the installer-baked value are indistinguishable at runtime. Consequences: (a) the "Configured microphone failed; trying auto-detected microphone" notification fires for installer-baked devices where nothing was user-"configured"; (b) after USB renumbering, every hotkey press permanently pays a failed start attempt plus re-detection, and nothing prompts the user to re-run the installer to re-converge the binding. Behavior is safe but the plan should either say the stale-binding state is accepted indefinitely or have the fallback path suggest re-running the installer.
- **The three-provider code-stage default (AC line 429) is unreachable on this machine and predictably churns.** Gemini returned UNAVAILABLE with the identical auth error for 8 consecutive rounds (`disagreement-r8`: no `GEMINI_API_KEY`/`GOOGLE_API_KEY`/`~/.gemini/oauth_creds.json`). "If Gemini remains unavailable" is not a contingency here — it is the certain outcome absent an auth fix that is out of this plan's scope. Stating the code-stage gate as Claude+Codex (T2 per SHARED_SOUL gate 4) with Gemini as opportunistic would remove 8 more guaranteed-stub artifacts per round.
- **Line 295's quoting constraint is stated imprecisely.** "keep the inert message single-quote-free because it is stored through gsettings as a quoted command string" — the stored command *necessarily contains* single quotes (the `bash -lc '…'` wrapper); the actual constraint is that the *message text inside* the wrapper must not contain single quotes. Test line 387 covers the executable outcome, so this is wording-only, but an implementer reading line 295 literally could "fix" the wrapper quotes and break the payload.
- No findings against the plan's factual substrate: every file path, commit, label, symlink, gsettings value, gitignore behavior, and the ALSA `default`-broken/`plughw:1,0`-working reproduction were checked live and all reproduce (Plantronics is currently attached; `default` still fails "Host is down").

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

### codex-r8

(no findings unique to this provider)

### codex

- `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:459` self-declares the plan not ready: “PENDING -- r8 MAJOR findings are addressed in this draft; r9 re-review is required before `status:plan-review`.” That is fine for a draft, but it means this exact artifact cannot be advanced until this r9 artifact is recorded and the header/artifact map are refreshed per lines 431-433. The current header at line 10 and Artifact Map lines 163-194 stop at r8.
- The deliverable overpromises relative to the acceptance criteria. Line 200 says the deliverable “restores `Super+Shift+V` dictation on ace-linux-1,” but lines 414-417 allow closeout when detection is inactive by recording the reason and substituting inactive installer convergence for hardware smoke. Live retrieval now shows `/proc/asound/cards` has NVidia/Plantronics entries while `arecord -l` reports `arecord: device_list:277: no soundcards found...`; under the current acceptance criteria, the plan can pass without restoring working dictation. Either qualify the deliverable as “when a usable capture device is available in the writable desktop session” or require a later hardware-available verification before claiming restoration.
- The plan-review commit/push step acknowledges divergence but does not state the conflict-resolution rule. Line 432 says to run `git fetch origin`, inspect divergence, then “commit/push this plan,” while live `git status --short --branch` shows `main...origin/main [ahead 1, behind 2]` and `git log --left-right HEAD...origin/main --` shows one local commit versus two upstream commits. Without an explicit “rebase/merge first, then re-run pathspec status before pushing” instruction, the plan still leaves room for a rejected push or accidental mixed-history closeout at the plan gate.

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

(no findings unique to this provider)

### disagreement-r8

- ### claude-r7
- ### codex-r7
- ### disagreement-r7
- ### gemini-r7

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

### gemini-r8

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
