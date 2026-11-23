# Disagreement report — plan #3403 (2026-07-08)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | MINOR |
| claude-r2 | MINOR |
| claude-r3 | **MINOR** |
| claude-r4 | **MAJOR** |
| claude | **MINOR** |
| codex-r1 | MAJOR |
| codex-r2 | MAJOR |
| codex-r3 | MAJOR |
| codex-r4 | MAJOR |
| codex | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| disagreement-r3 | | Provider | Verdict | |
| disagreement-r4 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r3 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r4 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
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

### claude

- **AC line 373 targets a stale-residue glob that matches nothing, while the actual residue survives.** The criterion requires removing/excluding `scripts/review/results/2026-07-09-plan-3403-*` — zero such files exist. The real non-cited residue from the failed 22:15 fanout run is the **unstamped 2026-07-08 set**: `2026-07-08-plan-3403-claude.md` (0 bytes), `-codex.md` (0 bytes), `-codex.md.err`, `-gemini.md`, and `-disagreement.md`. As written, the cleanup AC is trivially satisfied and the zero-byte junk ships to `main` alongside the cited artifacts when they're committed. Fix the glob to the unstamped 07-08 pattern (or "any `*-3403-*` file not listed in the Review-artifacts header").
- **Pseudocode `install_voice_dictation()` mutates user state before device detection.** `prepare_share_dir()` runs first, so on an inactive machine (no mic) a pre-existing real `~/.local/share/voice-dictation` directory is still moved to a timestamped backup and replaced with a symlink before the installer declares inactive and returns 0. Non-destructive, but it's a user-visible mutation the inactive-guidance text doesn't mention, and no test in the TDD list pins whether inactive installs should or shouldn't touch the share dir (`test_existing_real_share_dir_is_backed_up_not_deleted` uses an active fixture). State the intended ordering explicitly so the implementer and tests converge.
- **`docs/plans/README.md` index row already exists in the working tree (line 206, uncommitted) while Files-to-Change lists it as a pending "Update".** An implementer following the plan verbatim could double-add the row. Worse, the edit is uncommitted on `main` in a repo with a known silent auto-sync pusher (`feedback_autosync_silent_pusher`) — it can get swept into an unrelated `chore(sync)` commit before the plan lands. Same exposure applies to the untracked plan file and all 16 review artifacts; AC line 373's commit-and-push step should happen promptly, not at closeout.
- **`test_transcribe_py_compiles_without_bytecode` has a vacuous second assertion.** The `python -c '... compile(p.read_text(), ...)'` invocation cannot write bytecode for the compiled file under any circumstances — `compile()` never persists `.pyc`. The "no bytecode file written" check tests the Python runtime, not the repo. Harmless, but it's dead weight in the TDD list; the syntax-check half is the only real assertion.
- **Gemini is UNAVAILABLE in all four rounds, and r5 will degrade identically.** The plan documents this per convention (fine for T2 — Claude+Codex satisfies the 2-provider gate), but the Review-artifacts header commits to producing `-gemini-r5` artifacts that will again be 338-byte UNAVAILABLE stubs unless non-interactive Gemini auth (`GEMINI_API_KEY`/oauth creds) is configured first. Worth a one-line note so r5 doesn't silently repeat the pattern as though it were new signal.

### codex-r1

(no findings unique to this provider)

### codex-r2

(no findings unique to this provider)

### codex-r3

(no findings unique to this provider)

### codex-r4

(no findings unique to this provider)

### codex

- Plan AC line 371 underspecifies the required code-stage review gate: “Code-stage adversarial review runs before closeout and non-empty artifacts or explicit `UNAVAILABLE` artifacts are present.” For a T2 plan, this permits a single generic artifact. `AGENTS.md` lines 15-17 requires cross-review before close, and `docs/standards/AI_REVIEW_ROUTING_POLICY.md` lines 25-33 says Claude, Codex, and Gemini review plan-stage and code/artifact-stage work by default; lines 34-42 only allow reduction when explicitly scoped down or a provider is unavailable. The plan needs to name the provider set and unavailable-artifact rule for code-stage review, not just “artifacts are present.”
- Plan AC line 373 only cleans “stale non-cited `scripts/review/results/2026-07-09-plan-3403-*` residue,” but the actual stale uncited residue is `scripts/review/results/2026-07-08-plan-3403-claude.md`, `.err`, `codex.md`, `codex.md.err`, `disagreement.md`, and `gemini.md`. Some are zero-byte, and `codex.md.err` is ~200 KB. This misses the residue actually present, so the plan can still move to `status:plan-review` with ambiguous stale review evidence.
- Plan line 416 says final revision-stamped review artifacts must be committed, and header line 10 cites `scripts/review/results/...` files, but `.gitignore` line 577 ignores `scripts/review/results/`. `git ls-files` only shows `docs/plans/README.md` among the checked review/plan paths. Without an explicit `git add -f` or unignore step, the plan’s commit/push criterion is operationally incomplete.

### disagreement-r1

(no findings unique to this provider)

### disagreement-r2

(no findings unique to this provider)

### disagreement-r3

(no findings unique to this provider)

### disagreement-r4

- ### claude-r3
- ### codex-r3
- ### disagreement-r3
- ### gemini-r3

### gemini-r1

(no findings unique to this provider)

### gemini-r2

(no findings unique to this provider)

### gemini-r3

(no findings unique to this provider)

### gemini-r4

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
