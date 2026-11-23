# Disagreement report — plan #3548 (2026-07-15)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | UNKNOWN |
| claude-r2 | UNAVAILABLE (claude CLI failed, rc=124: no stderr captured) |
| claude | **MAJOR** |
| codex-r1 | UNAVAILABLE (codex CLI failed, rc=124: Reading additional input from stdin... OpenAI Codex v0.144.4 -------- workdir: /mnt/local-analysis/workspace-hub-3548-plan model: gpt-5.6-sol provider: openai approval: never sandbox: danger-full-access reasoning effort: medium reasoning summaries: none session id: 019f6681-379d-79c3-bc85-7344350e859e -------- user # Adversarial plan review  You are an **adversarial reviewer**. Your job is to find) |
| codex-r2 | MAJOR |
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

- **The `--diff-only` legal scan cannot see either new file, and the plan's stated rationale for its ordering is inverted.** `scripts/legal/legal-sanity-scan.sh:187` enumerates via `git diff --name-only HEAD`, which excludes untracked files; line 188 then `return 0`s on an empty list. Plan line 271 claims the pre-commit position "is load-bearing because a post-commit diff-only scan would pass without examining the committed files" — but the **pre**-commit scan equally never examines `docs/ops/remote-linux-access.md` or `tests/docs/test_remote_linux_access_contract.py` unless they are `git add`ed first, which no task specifies. Acceptance criterion "legal scan … pass" (line 335) is therefore satisfiable with the canonical runbook — the entire deliverable, and the only file the plan says might "accidentally repeat a historical address" (line 359) — never scanned. My `/tmp` repro: `git diff --name-only HEAD` printed nothing with an untracked file present.
- **`git commit -- <pathspec>` fails outright on untracked files.** Plan lines 278–284 pass `tests/docs/test_remote_linux_access_contract.py` and `docs/ops/remote-linux-access.md` — both `Create` actions per the Files-to-Change table (lines 293–294) — as pathspecs. Empirically: `git commit -m "test" -- newfile.md` → `error: pathspec 'newfile.md' did not match any file(s) known to git`. The commit command as written cannot execute.
- **`test -n "$(git diff --name-only)"` (line 265) is non-deterministic and proves nothing about the artifacts it is meant to guard.** Bare `git diff` compares working tree to **index**: it excludes untracked files and excludes anything staged. Once Tasks 3–4 modify the six tracked docs, the assertion is trivially true whether or not the runbook was ever created; if the operator stages first (required by finding 2), it returns empty and the assertion **fails**. It passes for the wrong reason or fails for the wrong reason, never for the right one.
- **Tests 5 and 8 collide with the actual link conventions of the files they target; GREEN is unreachable as specified.** `EXPECTED_CANONICAL_LINKS = {path: RUNBOOK for path in [*RELATED, *LEGACY]}` (line 182) maps each file to an **absolute** `Path`, with no per-file relative normalization. But `docs/README.md:77-87` uses directory-relative links (`modules/ai/AI_AGENT_GUIDELINES.md`), so the idiomatic link from that file is `ops/remote-linux-access.md` — which does not contain the substring `docs/ops/remote-linux-access.md`. Worse, `docs/ops/machine-inventory.md` and both `config/tabby/*.md` files contain **zero** markdown links today (grep for `](…​.md)` returns nothing; machine-inventory.md:5 cites paths as backticked literals instead). For 3 of 6 targets, "links the canonical runbook" has no established form in the file, and the plan never states which form satisfies the assertion.
- **The plan's own security thesis is scoped away from the only live endpoint in the repo, and misframes it as drift rather than exposure.** `gh repo view` confirms workspace-hub is **PUBLIC**. `connect-workspace-tailscale.ps1:8` publishes `$WorkspaceHost = "100.107.64.76"` — which *is* inside Tailscale's CGNAT `100.64.0.0/10` (second octet 107 falls in 64–127), unlike the registry's `10.1.0.1`/`10.1.0.2` that the plan correctly dismisses as synthetic at line 98 — alongside `$WorkspaceUser = "vamsee"` and `$WorkspaceHostname = "vamsee-linux1"` on lines 9–10. Plan line 92 characterizes this only as "a different address literal from the registry fields", and line 304 declares all of `scripts/operations/connection/` explicitly unchanged, routing remediation to [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549) — which `gh` shows is still `status:needs-plan`, i.e. unplanned and unscheduled. The contract test's IPv4 allowlist (line 191) covers six documentation files, of which grep shows four already contain zero or one IPv4 literal. The net effect: the acceptance criterion "no point-in-time machine endpoint addresses" (line 330) is mechanically enforced on the files that lack the real address and not on the file that has it. Threat-model inversion — the same class SHARED_SOUL's promote-generalizable-findings rule names explicitly.
- **Test 6's anti-self-match rationale (line 194) is a non-sequitur.** The claim: legacy docs must contain no "imperative to forward SSH", and "A separate assertion requires explicit language that router SSH forwarding is prohibited, **so** the prohibition cannot self-match the positive-pattern check." Adding a second assertion has no bearing on whether the first assertion's regex matches the prohibition sentence in the same file — the two run independently over the same bytes. The plan asserts the safety property without specifying a mechanism. SHARED_SOUL's "Enforcement scripts must not block their own artifacts" rule requires a per-line sentinel (prior art: `scripts/enforcement/check-no-abs-paths.sh:111`) or equivalent, not a claim.
- **No review round has ever met the T2 bar the plan sets for itself, and the current round is already failed, not "PENDING".** Plan line 351 records "Round 3 | PENDING", but on disk: `2026-07-15-plan-3548-claude.md` is **0 bytes**, its `.err` sidecar is **0 bytes** (no diagnostic captured), `...-gemini.md` already records `UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth)`, and `...-codex.md` **does not exist**. Line 10's "the fanout tool **will** write the current round" is false in the present tense for two of three providers. Per the plan's own table, r1 yielded 1 provider with signal (Claude MAJOR; Codex and Gemini UNAVAILABLE) and r2 also 1 (Codex MAJOR; Claude and Gemini UNAVAILABLE). SHARED_SOUL Hard Gate 4 sets T2 = 2 providers; the degradation must be documented as a degradation rather than reported as pending.
- **The declared RED state produces collection errors, not assertion failures.** `ENDPOINT_DOCS = [RUNBOOK, *RELATED, *LEGACY]` (line 183) and tests 3, 9, 10, 11, 12 all read `RUNBOOK`, which does not exist at RED. Those reads raise `FileNotFoundError`, not the "failures for the missing runbook" line 208 predicts. Acceptance criterion 1 (line 328) demands RED be *demonstrated*; a stack trace from an unguarded `read_text()` is weaker evidence than a failed assertion and is indistinguishable from a broken test file. Specify existence guards.
- **Tests 5 and 8 encode one contract under two names.** Test 5 (line 193): "Every related durable document links `docs/ops/remote-linux-access.md`." Test 8 (line 196): "Each file in `EXPECTED_CANONICAL_LINKS` contains the expected new canonical-runbook link." `EXPECTED_CANONICAL_LINKS` is constructed from `RELATED` + `LEGACY` (line 182), so test 8 is test 5 plus test 6's link half. Redundant coverage inflates the TDD test list without adding a distinct failure mode.
- **`0.0.0.0` in `SAFE_IPV4_LITERALS` (line 184) is unjustified and weakens the check it belongs to.** Line 155 permits protocol constants "only when operationally necessary", but no task states a necessity for a wildcard-bind literal in a runbook whose entire thesis (lines 221, 331) is outbound-only Tailscale with no router forwarding. A wildcard bind in an `sshd` drop-in is precisely the misconfiguration this document exists to prevent; allowlisting it means the contract test cannot catch it.

### codex-r1

(no findings unique to this provider)

### codex-r2

- Task 1 assertion 8 and `test_scoped_markdown_links_resolve` require every repo-relative link in `LINK_DOCS` to resolve, but `docs/README.md` and `docs/setup/README.md` contain six pre-existing broken targets that Task 3 does not repair. The documented GREEN state is therefore unsatisfiable within scope.
- Task 2 requires critical security and recovery content, but the tests enforce only headings, broad architecture words, authority references, endpoints, links, and issue numbers. Empty or unsafe security, setup, verification, recovery, and troubleshooting sections can pass.
- `ENDPOINT_SOURCES` does not cover all machine-specific literals already present in the legacy documents, and dynamic extraction stops guarding a stale literal after a helper removes it.
- The required capability divergence and headless VNC conflict lack explicit drift-ledger rows and test coverage. Merely checking for three follow-up issue links is insufficient.
- Task 2 requires primary Tailscale and OpenSSH citations, but no test asserts their presence or authority.

### disagreement-r1

(no findings unique to this provider)

### disagreement-r2

- ### claude-r1
- ### codex-r1
- ### disagreement-r1
- ### gemini-r1

### gemini-r1

(no findings unique to this provider)

### gemini-r2

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
