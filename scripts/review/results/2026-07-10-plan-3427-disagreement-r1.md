# Disagreement report — plan #3427 (2026-07-10)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | **MAJOR** |
| codex | UNAVAILABLE (codex CLI failed, rc=124: Reading additional input from stdin... ) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **MAJOR — false evidence: the digitalmodel `workflow_api` runner exists on `origin/main`.** Plan §Resource Intelligence states "The current checkout has no `digitalmodel.workflow_api` runner" and §Evidence asserts `MISSING digitalmodel/src/digitalmodel/workflow_api/runner.py`. After `git fetch`, `git ls-tree -r origin/main` in digitalmodel shows `src/digitalmodel/workflow_api/{__init__,runner,golden,provenance}.py` plus `tests/workflow_api/goldens/` with four golden fixtures (buckling, FFS, mooring, wall-thickness). The local checkout is merely on feature branch `feat/wf-api-3307-digitalmodel-embed-port`, which lacks the file. This is exactly the `feedback_verify_generated_state_against_origin_not_working_copy` failure mode. The consequence is not cosmetic: the compatibility crosswalk (Deliverable, AC bullet 5, pseudocode line "assert ResultEnvelope … are evidence inputs") is scoped against an understated substrate, and the plan's #3285 row ("live implementation is partial") is stale in the same direction — dm adoption appears substantially landed on main. The contract's crosswalk must enumerate dm's runner/golden/provenance surface or it will be incomplete on day one.
- **MINOR — evidence refs are undeclared and taken from mutable feature-branch checkouts.** Every sibling EXISTS/MISSING row in §Evidence was evidently gathered from local working copies (all three siblings sit on `feat/wf-api-*` branches). The four EXISTS claims happen to hold on `origin/main` (I verified each), but the one MISSING claim was wrong (Finding 1), demonstrating the method is unsound. The evidence block cites timestamps but no git ref/SHA per repository. A T3 architecture plan's evidence contract should state the ref inspected (`origin/main@<sha>`).
- **MINOR — the primary deliverable was pre-authored and committed before review or approval.** Commit b8a26550f (already on this branch) lands the 318-line HTML decision manual alongside the plan. The plan discloses it ("EXISTS … (draft)", action "Update"), which keeps it inside the letter of the future-tense rule, but the substance of the normative deliverable exists before adversarial review and user approval. Reviewers and the user must treat the manual's entire body as ungated content; the "Update … incorporate review changes" framing under-represents that no gate has yet examined it. The manual body also contains the token "approved" — verify the draft nowhere presents itself as approved architecture before the plan passes its gate.
- **MINOR — HTML/YAML parity test tooling unspecified.** Pseudocode line "parse HTML manual and verify its sections … agree with YAML" and test `test_html_manual_matches_contract` name no parser or YAML dependency. workspace-hub's root `pyproject.toml` carries pytest but the plan should pin whether the test uses stdlib `html.parser`/`re` or adds a dependency — an added dependency would widen the change surface the plan claims is docs-plus-tests only.
- Checks run that produced **no** finding: issue states/labels (all 15 match), nine-child DAG completeness against the issue body's child map, locked-decision coverage (issue body vs plan pseudocode/tests — failure-run exclusion, per-repo datasets, append-only publication, revision pinning all present), `--diff-only` flag existence and semantics, `check-no-abs-paths.sh` existence, template section compliance, lane-label match, T3 classification, staleness-probe reproduction (exit 1), dm version-drift numbers, wed `data_as_of` runtime-timestamp claim, `tests/architecture/` precedent (four sibling contract tests already exist, so the test placement and `uv run pytest` invocation are consistent with repo practice).

### codex

(no findings unique to this provider)

### gemini

(no findings unique to this provider)

