# Disagreement report — plan #2754 (2026-05-19)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE |
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- Plan cites a non-existent machine registry path as existing evidence. In `Resource Intelligence Summary / Existing repo code`, the plan claims `config/machines/telegram-hermes-machines.yaml` exists and names `dev-primary`; fetching that path from `main` returned 404, and GitHub search found no matching file. The actual readiness default in `scripts/readiness/telegram_hermes_readiness.py` is `--registry config/workstations/registry.yaml`, and `config/workstations/registry.yaml` says it is the “Single source of truth for all workstations.”
- The plan cites a non-existent repo-location reference. In `Standards`, it names `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md`; fetching that path returned 404 and search found no match. That makes the plan’s quoted governance requirement unverifiable from the cited source.
- The planned artifact `config/workstations/ace-linux-1-tier1-repos.yaml` risks creating a second workstation truth source without reconciling the existing one. `config/workstations/registry.yaml` explicitly says “HARD RULE: all machine identity/capability data lives here” and already has `dev-primary.repos` plus `telegram_hermes.data_access_profile.repos`. The plan’s `Files to Change` does not update `config/workstations/registry.yaml`, even though the planned required/optional baseline differs from the existing registry, which includes `OGManufacturing` and omits `llm-wiki`.
- The readiness integration target is wrong or incomplete. `Files to Change` says to modify `scripts/readiness/telegram-hermes-readiness.sh`, but that file is only a thin wrapper around `uv run python scripts/readiness/telegram_hermes_readiness.py "$@"`. The actual dispatchability logic, registry loading, env gates, git checks, data access checks, and JSON output live in `scripts/readiness/telegram_hermes_readiness.py`; the plan does not list that Python file as a file to modify.
- The plan’s readiness test design cannot prove the real integration path. `TDD Test List` says `test_readiness_includes_tier1_baseline_failures` will stub the checker, but the plan does not specify whether the Python readiness collector invokes the checker, how checker failures/warnings are represented in the JSON schema, or how malformed checker output/timeout/checker-missing cases fail closed. This is correctness-critical because `scripts/readiness/telegram_hermes_readiness.py` currently computes `dispatchable` solely from its internal `entry["failures"]`/`entry["warnings"]` flow.
- The plan does not satisfy issue [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754)’s acceptance criteria. The issue requires “Live reachability and command path are verified,” “Provider/runtime availability is recorded,” and “First dispatch produces a concrete work artifact, issue comment, test result, review, or PR-ready change.” The plan’s deliverable is only a repo baseline plus checker, and its acceptance criterion defers the concrete dispatch artifact to “once dispatch is attempted after readiness passes.”
- The plan’s live inventory evidence conflicts with issue-comment history and cannot be trusted without a fresh local recheck. The plan says `worldenergydata` and `llm-wiki` are currently present under `/mnt/local-analysis/workspace-hub/`, while issue comment `4493124299` says both were missing from `/mnt/local-analysis` sibling checkout state and recommends different placement. Because local shell is unavailable in this review, the plan needs to carry exact commands and current output provenance sufficient to resolve that discrepancy.

### gemini

- Plan §Resource Intelligence Summary claims "Found: `scripts/readiness/telegram-hermes-readiness.sh`". No such file exists in the workspace at HEAD. Glob searches returned zero matches.
- Plan §Resource Intelligence Summary claims "Found: `config/machines/telegram-hermes-machines.yaml`". No such file exists in the workspace at HEAD.
- Plan §Resource Intelligence Summary claims "Found: `docs/plans/machine-prompts/2026-05-19/ace-linux-1-control-plane-dispatch-ledger.md`". No such file exists in the workspace at HEAD.
- Plan §Standards references `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md`, and `docs/standards/PARALLEL_FIRST_EXECUTION.md`. None of these files exist in the workspace at HEAD.
- Plan §Pseudocode for `discover_tier1_repos` rigidly hardcodes exact probe paths (`/mnt/local-analysis/<repo>` and `/mnt/local-analysis/workspace-hub/<repo>`). If a required checkout is placed elsewhere in the environment, the checker blindly reports it as missing instead of detecting actual filesystem state, yielding false negatives.
- Plan §Pseudocode for `validate_baseline` states it will "warn if more than one checkout exists and no primary path is declared." However, the §Pseudocode for `integrate_with_readiness` sets `dispatchable=false` only on failures. Emitting a mere warning for ambiguous duplicate paths contradicts the plan's own Risk assertion that explicit primary declarations are required, creating a fatal gap where readiness could pass without knowing which checkout path to use.
- Plan §Pseudocode for `integrate_with_readiness` intends to patch a bash script (`telegram-hermes-readiness.sh`) to consume the output of Python logic (`check-tier1-repo-baseline.py`) yielding a "JSON/text report". The plan completely omits the mechanism for how bash will safely parse this structured output (e.g., utilizing `jq`) to inject failures, risking masked errors or script breakage.
- Plan §TDD Test List states `test_readonly_checker_does_not_mutate_paths` relies on "Temporary fake repos and monkeypatched subprocess". This tests the fixture rather than the system constraint; monkeypatching `subprocess` does not detect or restrict native Python path operations (such as `shutil.rmtree` or `os.remove`), failing to empirically prove read-only execution.
