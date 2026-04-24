# Disagreement report — plan #2475 (2026-04-23)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **§7 + §93-95: Artifact Map points to review files that do not exist; the files that do exist are empty or UNAVAILABLE, yet the plan claims "first review MAJORs addressed."** The plan header line 7 cites `scripts/review/results/2026-04-23-plan-2475-claude.md` and `…-gemini.md`. On disk both are 0 bytes. Only `…-codex.md` has content, and its verdict is `UNAVAILABLE (codex CLI failed, rc=2: unexpected argument '--no-interactive')`. The Gemini `.err` sidecar shows the provider aborted on `/tmp/*` permission warnings. The Adversarial Review Summary table §180 asserts "Claude MAJOR (r1) … Addressed in v2" — but there is no Claude review content to address. No provider produced a substantive r1 verdict, so the plan's "v2 revisions made; fresh re-review required" is the only true statement in §185; the rest of the table is fabricated from absent artifacts.
- **§87, §93-95: Artifact Map uses 2026-04-24 paths while the actual plan and review files are 2026-04-23.** `ls docs/plans/2026-04-2*-issue-2475*` returns only `2026-04-23-…`, and `ls scripts/review/results/2026-04-23-plan-2475-*` confirms all review artifacts live under the 2026-04-23 prefix. The plan even acknowledges that "review artifact date drift" was a prior Claude-r1 MAJOR (§181) — yet §87 and §93-95 still point at `2026-04-24` paths. The "addressed in v2" claim is falsified by the artifact map itself.
- **§173 acceptance criterion ("Plan review artifacts exist and contain no MAJOR blocker") is satisfied by a 0-byte file.** "Exist" without a content requirement means empty Claude/Gemini artifacts trivially pass — there is no VERDICT section to fail. Combined with finding #1, the gate here is effectively vacuous: a provider that silently crashes will be treated as "no blocker." The criterion must require each artifact to contain an explicit `## Verdict` line with APPROVE/MINOR/MAJOR/UNAVAILABLE text (the prompt's §51 escape hatch is `UNAVAILABLE`, not empty output).
- **§157 `manifest_template_valid_yaml` validation has a shell typo and violates the plan's own machine-command rule.** The command line is:
-    ```
-    `uv run --no-project python -c 'import yaml; yaml.safe_load(open("docs/solver/templates/semantic-proof-evidence-manifest.yaml"))'``
-    ```
-    Two issues: (a) trailing double-backtick breaks markdown-rendered copy-paste; (b) `uv run` is explicitly forbidden on licensed-win-1 per `docs/plans/licensed-win-1-execution-guide.md:107` and §168's acceptance criterion ("uses machine-appropriate commands (`python`, not `uv run`)"). The plan does not declare whether the TDD checks run on dev-primary or licensed-win-1. As written, a licensed-win-1 operator running validation will fail immediately. Either declare the check is dev-primary-only or rewrite it to use `python -c ...`.
- **§161 `markdown_links` check is self-referential / weakly discriminating.** The grep searches the protocol doc for tokens including its own filename stem (`docs/solver/orcawave-orcaflex-native-load-run-proof-protocol`). A file trivially matches a grep for its own title if the title appears anywhere in the body. The intent was to confirm cross-references between protocol doc and prompt doc — that should be expressed as two directional checks: (a) `grep licensed-win-1-semantic-proof-load-run-prompt docs/solver/orcawave-…-proof-protocol.md` and (b) `grep orcawave-orcaflex-native-load-run-proof-protocol docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md`. As currently written it is not a meaningful test.
- **§121 "if yaml/openpyxl/numpy are missing, install them with `python -m pip install pyyaml openpyxl numpy`" has no network-blocked fallback.** Corporate licensed machines commonly firewall PyPI. The protocol does not define a `missing-dependency` failure class in §117's classification matrix (only "missing license/API" and "unrelated environment failure"). `pip install` failing is neither, and operators will have to decide ad-hoc. Add an explicit `dependency-install-blocked` class with guidance to return a skip-with-reason.
- **§122 "attempt minimal calculate/run only when safe and bounded" has no machine-enforced ceiling.** §113-114 says run proof is "allowed only when fixture has a documented short analysis duration or OrcaWave frequency/heading grid small enough for an expected <15 minute wall-clock run." §193 risk acknowledges runaway runs. Neither section names a concrete watchdog contract (e.g., "abort and return `runtime/disk guard exceeded` if wall-clock > 15 min; set OrcaWave max frequencies < N; set OrcaFlex StageDuration < T"). Operator judgment will vary. Codify numeric bounds in the protocol doc before first execution.
- **§121 prerequisites say "git pull workspace-hub and digitalmodel" but neither the current `licensed-win-1-execution-guide.md` nor this plan specify the dual-repo command shape for licensed-win-1.** Per the user's global CLAUDE.md memory, `digitalmodel/` is a separate git repo requiring `cd digitalmodel && git pull`. The existing execution guide lines 46-48 only show `git pull origin main` at D:\workspace-hub root. If `digitalmodel` is a submodule vs. a sibling checkout on licensed-win-1, the pull shape differs materially. Plan must commit to one shape and include the exact commands in the licensed-win-1 prompt.
- **§160 `no_implementation_scope_creep` expected output is ambiguous vs. the command's path filter.** The command restricts diff to `docs/plans docs/solver scripts/solver queue digitalmodel/src digitalmodel/tests`. The expected output reads "only docs/plans and docs/solver files for this issue." A mechanical reading of the command lists all six paths; the assertion is really "no matches under `scripts/solver queue digitalmodel/src digitalmodel/tests`." Rewrite the expected output as a precise negation, e.g., `grep -v -E "^(docs/plans|docs/solver)/" returns empty`.
- **§74 line excerpt is off-by-one.** The plan cites `docs/architecture/solver-queue.md` lines 11-12 as "licensed-win-1 polls via git, runs OrcFxAPI, and pushes completed/failed results." Line 11 is the architecture narrative paragraph that contains that description, but line 12 is blank (the markdown section break before the `### Data Flow` subheading). Not load-bearing, but illustrates the retrieval-citation hygiene issue the prompt §15 warns about.

### codex

- (none)

### gemini

- Plan § "TDD / Validation List" for `prompt_self_contained` executes `grep -E "OrcFxAPI|python -m pip install|#2475|#2455|#2456|#2457|Evidence manifest|Return format" docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md`. This regex uses logical OR (`|`). It will return exit code 0 if even ONE term is found, failing to verify the claim that "all anchors found".
- Plan § "TDD / Validation List" for `protocol_classification_matrix` executes `grep -E "semantic mismatch|solver-version/default drift|unrelated environment failure|load-only proof|run proof|skip-run" docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md`. This regex uses logical OR (`|`). It will pass if only a single term exists, failing to verify the claim that "required terms found" (plural).
- Plan § "TDD / Validation List" for `markdown_links` uses `grep -E "..." docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md`. Searching across multiple files with logical OR will return success if all anchors exist in just ONE of the files, failing to verify inter-document references correctly.
- Plan § "TDD / Validation List" for `manifest_template_valid_yaml` specifies the command `uv run --no-project python -c 'import yaml; yaml.safe_load(open("docs/solver/templates/semantic-proof-evidence-manifest.yaml"))'``. This command contains a trailing double backtick (``'```) which will create a syntax error in the shell, preventing the validation from executing.
- Plan § "Artifact Map" lists the current plan path as `docs/plans/2026-04-24-issue-2475-licensed-load-run-proof-protocol.md` and references review artifacts dated `2026-04-24`. However, the prompt header and Plan § "Resource Intelligence Summary" claim `Date: 2026-04-23` and list `2026-04-23` review paths. This date drift contradicts the claim that it was cleanly "Addressed in v2".
- Plan § "Files to Change" states that `docs/plans/README.md` will be modified to "Add plan index row", but Plan § "TDD / Validation List" contains no test to verify this update occurred.

