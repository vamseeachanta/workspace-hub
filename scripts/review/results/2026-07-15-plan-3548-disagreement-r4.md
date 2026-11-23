# Disagreement report — plan #3548 (2026-07-15)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | UNKNOWN |
| claude-r2 | UNAVAILABLE (claude CLI failed, rc=124: no stderr captured) |
| claude-r3 | **MAJOR** |
| claude | **MAJOR** |
| codex-r1 | UNAVAILABLE (codex CLI failed, rc=124: Reading additional input from stdin... OpenAI Codex v0.144.4 -------- workdir: /mnt/local-analysis/workspace-hub-3548-plan model: gpt-5.6-sol provider: openai approval: never sandbox: danger-full-access reasoning effort: medium reasoning summaries: none session id: 019f6681-379d-79c3-bc85-7344350e859e -------- user # Adversarial plan review  You are an **adversarial reviewer**. Your job is to find) |
| codex-r2 | MAJOR |
| codex-r3 | MINOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| disagreement-r3 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r3 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
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

### claude

- **The plan's own secrets-scan command exits 1 on the implementing host; the acceptance criterion is unsatisfiable as written.** Plan line 290 runs `bash scripts/security/secrets-scan.sh --repo workspace-hub`, line 293 expects "the secrets scan reports `PASS: workspace-hub`", and line 356 makes "workspace-hub secrets scan pass" an acceptance criterion. Empirically, that command returns `ERROR: gitleaks not found in PATH` with **exit 1**. `secrets-scan.sh:62-66` hard-exits when `command -v gitleaks` fails — it has no vendor-location fallback, unlike `legal-sanity-scan.sh:22-36` which degrades to `grep` when `rg` is absent. A filesystem sweep of six standard install locations found no `gitleaks` binary. The issue carries `wip:ace-linux-1`, so this is the host that will run it. The plan must either declare gitleaks a named prerequisite with an install step, or drop the criterion.
- **Even with gitleaks installed, the secrets scan cannot see the deliverable, and plan line 293 conflates two scanners with different input semantics.** `secrets-scan.sh:96` invokes `gitleaks detect --source "${repo_path}"` without `--no-git`; the script's own comment at `:93-94` states the distinction explicitly — *"Use gitleaks protect --staged for pre-commit staged-files check; use gitleaks detect (without --no-git) for full git history scan."* `detect` reads committed objects, so a staged-but-uncommitted file is invisible to it. Plan line 293 asserts *"Staging before `--diff-only` is load-bearing because `git diff --name-only HEAD` excludes untracked files"* — true for the **legal** scan (`legal-sanity-scan.sh:187`, verified) — then places the secrets scan in the same pre-commit block and expects it to gate the same content. Staging does nothing for `gitleaks detect`. Net effect: `docs/ops/remote-linux-access.md` — the entire deliverable, and the one file the plan's own Risk section (line 383) fears "could accidentally repeat a historical address" — is never examined by the secrets scan before commit. This is r3 finding 1's defect class, fixed for the legal scanner and left live in its sibling. The script exposes no staged mode; either run `gitleaks protect --staged` directly, move the scan after the commit, or state that the secrets scan does not gate this slice.
- **[#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551) owns no drift row, so test 6's requirement that it appear is decorative.** Task 1 item 6 (line 207) requires the ledger to link #3549, #3550, **and #3551**, and the TDD table's GREEN condition (line 339) repeats it. But Task 2 (line 241) assigns rows to #3549 (endpoint/alias), #3550 (capability divergence), and #3550 again (x11vnc/TigerVNC). No drift class routes to #3551. The assertion is satisfiable by a bare mention anywhere in the section, enforcing nothing about `ace-linux-1` truth ownership — which plan line 47 says remains unverified for #318/#316/#398 addresses and installed-state claims. Either assign those rows to #3551 or drop it from the test.
- **Task 1 item 5's anti-self-match property is still asserted rather than mechanized, and the prescribed prior art is verified-available but unused.** Line 206: *"A line-oriented positive-forwarding check will reject only affirmative headings, router-to-host mappings, and imperative `open|map|forward` instructions that name SSH or port 22 … This avoids matching the prohibition itself."* The required prohibition sentence (an "independent exact prohibition sentence") will itself be a line containing an imperative-shaped `forward` plus `22` — e.g. "Do not forward port 22 to this host." Separating affirmative from negated imperatives by regex is precisely the fragility SHARED_SOUL's *"Enforcement scripts must not block their own artifacts"* rule targets; it prescribes a per-line sentinel, and the named prior art is real — `scripts/enforcement/check-no-abs-paths.sh:111` is `[[ "$line" == *'# abs-path-allowed' ]] && continue`. r3 finding 6 raised this; the revision restated the claim with more adjectives instead of adopting the sentinel. Specify the mechanism.
- **Validation runs only the focused test file, though Task 3 modifies a file two other test suites scan.** Plan lines 275, 217 and acceptance criterion line 356 run only `tests/docs/test_remote_linux_access_contract.py`. `docs/ops/machine-inventory.md`-adjacent edits aside, `docs/README.md` (Task 3, line 252) appears in `tests/docs/test_banned_stale_references.py::STRICT_FILES` and `tests/docs/test_legacy_reference_allowlist.py::SCAN_FILES`; both currently **pass** for that file, so a Task 3 regression there would go undetected. Compounding this: `uv run pytest tests/docs/ -q` is already **2 failed, 15 passed** on inherited `origin/main` state (`AGENTS.md:2`, `docs/plans/README.md:274`), so no known-RED baseline is recorded and an implementer cannot distinguish new breakage from inherited. Per `feedback_non_required_checks_hide_regressions`, run the directory suite and record the two known failures as the baseline.
- **The Artifact Map points at empty evidence, and the current round has zero provider signal.** Lines 10 and 126–128 present `scripts/review/results/2026-07-15-plan-3548-{claude,codex,gemini}.md` as the current-round artifacts. On disk: `...-claude.md` is **0 bytes**, its `.err` sidecar is **0 bytes** (no diagnostic captured), `...-codex.md` does **not exist**, and `...-gemini.md` is the 338-byte UNAVAILABLE stub. Line 375 labels Round 4 "PENDING" while three stale/empty files already occupy those exact paths. Codex r3 finding 4 explicitly holds that documented T3→T2 degradation does not authorize T2→T1; this plan is self-declared T2 (line 392), so round 4 needs a second provider signal before the human gate. r3 itself did clear T2 (Claude MAJOR + Codex MINOR); round 4 currently has none.

### codex-r1

(no findings unique to this provider)

### codex-r2

(no findings unique to this provider)

### codex-r3

- The endpoint contract checks IPv4 only; a point-in-time Tailscale IPv6 endpoint could pass.
- The IPv4 allowlist is token-wide across all changed documents rather than context-bound to approved lines in the canonical runbook.
- The rejection contract omits keyboard-interactive authentication, which rollout issues #3550 and #3551 explicitly require.
- A second provider signal is required before the human gate; documented T3-to-T2 degradation does not authorize T2-to-T1.

### disagreement-r1

(no findings unique to this provider)

### disagreement-r2

(no findings unique to this provider)

### disagreement-r3

- ### claude-r2
- ### codex-r2
- ### disagreement-r2
- ### gemini-r2

### gemini-r1

(no findings unique to this provider)

### gemini-r2

(no findings unique to this provider)

### gemini-r3

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
