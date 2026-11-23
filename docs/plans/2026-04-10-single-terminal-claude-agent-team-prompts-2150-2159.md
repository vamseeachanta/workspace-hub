# Single-Terminal Claude Agent-Team Prompt Pack

Date: 2026-04-10
Repo: `vamseeachanta/workspace-hub`
Issue set: `#2150`-`#2159`
Execution mode: single terminal, Claude internal agent team

## Live gate status

Current live GitHub state when this pack was generated:
- Open issues with `status:plan-approved`: `0`

That means these prompts must start in verification / approval-check mode.
They are intentionally written so Claude:
1. checks approval first,
2. stops with a blocker dossier if approval is missing,
3. only implements when the issue is actually approved.

## Internal team pattern for every prompt

Use this exact internal role framing in Claude:
- Planner
- Implementer
- Tester
- Reviewer
- Synthesizer

## Global execution rules for every prompt

Paste these rules at the top of every Claude run:

```text
You are Claude operating as a 5-role internal agent team in a single terminal:
1. Planner
2. Implementer
3. Tester
4. Reviewer
5. Synthesizer

Repository: vamseeachanta/workspace-hub
Working directory: /mnt/local-analysis/workspace-hub

Hard gates:
- First inspect AGENTS.md and repo-local workflow constraints.
- First inspect the GitHub issue with gh.
- First verify whether the issue has label status:plan-approved.
- If status:plan-approved is absent, do NOT implement. Produce a blocked execution dossier only.
- If status:plan-approved is present, use TDD and targeted validation.
- Do not ask the user questions.
- Do not expand scope beyond the issue.
- Stay within the owned paths listed in the prompt.
- If a prerequisite contract from another issue is missing, stop and report the blocker instead of inventing a new contract.

Required preflight commands:
- git status
- gh issue view ISSUE_NUMBER --repo vamseeachanta/workspace-hub --json number,title,body,labels,comments
- read AGENTS.md

Required final output:
- approval gate result
- scope summary
- exact owned paths
- exact validation commands run or proposed
- implementation summary OR blocker dossier
- adversarial review verdict: PASS / MINOR / MAJOR
- exact GitHub comment text to post
```

## Launch pattern

```bash
PROMPT=$(python3 - <<'PY'
from pathlib import Path
text = Path('docs/plans/2026-04-10-single-terminal-claude-agent-team-prompts-2150-2159.md').read_text()
start = text.index('## Prompt for #2150')
end = text.index('## Prompt for #2151')
print(text[start:end])
PY
)
claude -p --permission-mode acceptEdits --output-format text "$PROMPT"
```

Adjust section slicing for the desired issue.

---

## Prompt for #2150

```text
ISSUE_NUMBER: 2150
ISSUE_TITLE: feat(operations): implement Windows no-SSH readiness evidence writer and local drop path

Mission:
Execute issue #2150 in a single terminal only.

Issue summary:
Implement the Windows no-SSH readiness evidence writer and canonical local drop path. Support PowerShell and/or Git Bash launch paths. Capture machine identity, workspace, AI CLI, licensed-tool presence, and no-SSH access-mode evidence.

Owned paths:
- scripts/readiness/
- config/workstations/
- tests/workstations/
- tests/analysis/
- docs/modules/ai/

Read-only paths:
- scripts/windows/
- docs/plans/
- .claude/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- unrelated package or lock files

Specific execution instructions:
1. Check approval first. If not approved, stop and produce a blocked implementation dossier.
2. Inspect existing adjacent files, especially:
   - scripts/readiness/nightly-readiness.sh
   - scripts/readiness/compare-harness-state.sh
   - config/workstations/registry.yaml
   - any adjacent Windows launcher/writer scripts
3. Determine whether issue #2151 schema contract is already implemented. If not, treat missing bundle contract as a blocker or implement only the minimal scaffolding clearly marked as blocked by missing contract.
4. If approved and executable, write or tighten failing tests first.
5. Implement only the writer/drop-path behavior, not the full reporting pipeline.
6. Review adversarially for:
   - no-SSH assumptions
   - Windows path handling
   - Git Bash vs native path mismatch
   - degraded-case behavior
   - incorrect licensed-tool detection

Validation commands:
- bash -n scripts/readiness/*.sh
- uv run pytest tests/workstations/test_registry.py tests/workstations/test_dispatch.py -q
- any new targeted tests you add for Windows writer behavior

If blocked, output:
- blocker reason
- missing approval status
- missing prerequisite contracts
- exact files that would be changed once approved
- exact tests that should fail first once approved
```

## Prompt for #2151

```text
ISSUE_NUMBER: 2151
ISSUE_TITLE: feat(operations): define per-machine readiness evidence bundle schema and status vocabulary

Mission:
Handle #2151 as a schema-first, test-first issue.

Issue summary:
Define a versioned readiness evidence bundle schema and normalized status vocabularies for access mode, check status, and overall summary status. Provide Linux and Windows example bundles and schema validation tests.

Owned paths:
- docs/modules/ai/
- scripts/analysis/
- tests/analysis/
- tests/fixtures/

Read-only paths:
- scripts/readiness/
- config/workstations/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- unrelated src/ packages

Specific execution instructions:
1. Check approval first. If not approved, stop with a blocked schema dossier.
2. Inspect whether a readiness bundle contract or validator already exists.
3. If approved and executable:
   - add failing schema tests first
   - define schema version, required fields, enums, timestamp rules, source-writer field
   - add valid Linux and Windows examples
   - add invalid examples for enum, timestamp, and missing-field failures
4. Keep this issue focused on contract + tests. Do not absorb downstream writer/renderer work.
5. Review adversarially for:
   - enum drift
   - missing provenance
   - Linux/Windows parity gaps
   - versioning ambiguity
   - timestamp ambiguity

Validation commands:
- uv run pytest tests/analysis -k "schema or readiness" -q
- any validator-specific tests you add
- optional CLI --help smoke if you add a validator helper

If blocked, output:
- proposed schema fields
- proposed enums
- exact fixture paths
- exact validator/test file paths
- approval blocker note
```

## Prompt for #2152

```text
ISSUE_NUMBER: 2152
ISSUE_TITLE: test(reporting): add golden fixture corpus for weekly review run artifacts and validator coverage

Mission:
Execute #2152 as a fixtures-and-tests issue. Avoid product-code changes unless a tiny validator fix is necessary.

Issue summary:
Add valid and invalid fixture corpus for weekly review run artifacts and expected validator outcomes. Include fixture naming and refresh guidance and wire fixtures into tests.

Owned paths:
- tests/analysis/
- tests/fixtures/
- docs/modules/ai/

Read-only paths:
- scripts/analysis/
- scripts/readiness/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- unrelated application code

Specific execution instructions:
1. Check approval first. If not approved, stop with a fixture-plan dossier.
2. Inspect existing validator tests and existing fixture conventions.
3. If approved and executable:
   - create failing tests first
   - add smallest useful valid fixtures: minimal, full, degraded, multi-machine
   - add invalid fixtures: missing keys, bad enums, bad timestamps, malformed sections
   - document expected validator outcomes
4. Do not invent validator behavior if the schema contract is absent; report dependency cleanly.
5. Review adversarially for:
   - fixture brittleness
   - overlarge fixtures
   - invalid cases failing for wrong reasons
   - mismatch with schema contract

Validation commands:
- uv run pytest tests/analysis -k "fixture or validator or weekly" -q
- any validator smoke command already present in repo

If blocked, output:
- exact fixture tree to create
- exact valid/invalid cases
- exact tests to add
- dependency on schema/validator implementation if applicable
```

## Prompt for #2153

```text
ISSUE_NUMBER: 2153
ISSUE_TITLE: feat(reporting): implement weekly review history index and latest manifest writer

Mission:
Execute #2153 with strict TDD and deterministic serialization behavior.

Issue summary:
Implement history/index and latest manifest writing for weekly review outputs, including bootstrap, append, duplicate run-id rejection, and rerun behavior.

Owned paths:
- scripts/analysis/
- tests/analysis/
- docs/modules/ai/

Read-only paths:
- scripts/readiness/
- tests/fixtures/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- unrelated renderer/publication code unless directly required

Specific execution instructions:
1. Check approval first. If not approved, stop with a history/manifest implementation dossier.
2. Inspect whether any history/latest writer already exists.
3. If approved and executable:
   - add failing tests first for bootstrap, append, duplicate run-id rejection, rerun semantics
   - implement minimal deterministic writer behavior
   - ensure latest only advances on validated successful publication input
4. Do not absorb renderer or bundle assembly work.
5. Review adversarially for:
   - run-id collisions
   - rerun corruption
   - nondeterministic ordering
   - partial-write behavior

Validation commands:
- uv run pytest tests/analysis -k "history or latest or manifest" -q
- optional CLI --help or dry-run smoke if you add a command wrapper

If blocked, output:
- proposed file contract
- proposed index fields
- proposed duplicate/rerun rules
- exact tests to add first
```

## Prompt for #2154

```text
ISSUE_NUMBER: 2154
ISSUE_TITLE: feat(reporting): implement Markdown/HTML publication layout renderer for weekly review outputs

Mission:
Execute #2154 as a renderer-only issue consuming normalized validated inputs.

Issue summary:
Implement Markdown and HTML renderer outputs for weekly review publication summaries with stable sections and snapshot-style tests.

Owned paths:
- scripts/analysis/
- tests/analysis/
- tests/unit/
- docs/modules/ai/
- tests/fixtures/

Read-only paths:
- scripts/work-queue/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- raw artifact validators or history writers except for input discovery

Specific execution instructions:
1. Check approval first. If not approved, stop with a renderer dossier.
2. Inspect existing HTML rendering patterns in repo, especially any reusable review/report renderer tests.
3. If approved and executable:
   - add failing snapshot/golden tests first
   - implement Markdown + HTML rendering only
   - keep section order stable: ecosystem health, machine readiness, settings/routing, freshness, accessibility, follow-on issues
   - normalize or freeze dynamic fields in tests
4. Do not do schema validation inside the renderer.
5. Review adversarially for:
   - unstable ordering
   - relative-link drift
   - Markdown/HTML mismatch
   - missing warning/error callouts

Validation commands:
- uv run pytest tests/unit/test_generate_html_review.py -q
- uv run pytest tests/analysis -k "renderer or snapshot or publication" -q

If blocked, output:
- intended renderer module path
- intended snapshot fixture strategy
- exact tests to add
- missing upstream input contract
```

## Prompt for #2155

```text
ISSUE_NUMBER: 2155
ISSUE_TITLE: feat(knowledge): build shared machine/path resolver library for session lookup and registry consumers

Mission:
Execute #2155 as a focused library extraction/integration issue. Avoid broad repo-wide refactors.

Issue summary:
Create a shared machine/path resolver handling machine identity by key/hostname/alias/ssh target plus Linux/Windows workspace and path normalization, with initial consumer integration.

Owned paths:
- src/
- scripts/operations/
- scripts/lib/
- tests/workstations/
- config/workstations/
- docs/modules/ai/

Read-only paths:
- scripts/windows/
- scripts/readiness/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- unrelated registry/schema docs

Specific execution instructions:
1. Check approval first. If not approved, stop with a resolver-design dossier.
2. Inspect current fragmented normalization logic across shell and Python.
3. If approved and executable:
   - choose one canonical library location
   - add failing tests first for machine key, hostname, alias, ssh target, Linux paths, Windows paths, unknown-host fallback
   - integrate only 1-2 consumers max
   - keep shell wrappers thin if Python becomes canonical
4. Do not expand registry schema in this issue.
5. Review adversarially for:
   - alias ambiguity
   - dual source of truth between shell and Python
   - path rewrite irreversibility
   - unknown-host behavior

Validation commands:
- uv run pytest tests/workstations/test_registry.py tests/workstations/test_dispatch.py -q
- any new focused resolver tests you add

If blocked, output:
- proposed canonical module path
- duplication inventory
- exact tests to add first
- first 1-2 consumers to migrate
```

## Prompt for #2156

```text
ISSUE_NUMBER: 2156
ISSUE_TITLE: feat(knowledge): add registry coherence validator for accessibility registry and seeded output

Mission:
Execute #2156 as a validator-only issue with good/bad fixtures and clear failure behavior.

Issue summary:
Validate coherence among workstation registry, accessibility registry, and seeded output: machine existence, alias/workspace/path consistency, provenance and machine/path metadata retention.

Owned paths:
- src/
- scripts/analysis/
- tests/workstations/
- tests/fixtures/
- config/workstations/
- docs/modules/ai/

Read-only paths:
- scripts/readiness/
- docs/plans/
- docs/document-intelligence/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- seeded registry generators unless tiny import wiring is required

Specific execution instructions:
1. Check approval first. If not approved, stop with a validator dossier.
2. Discover the actual seeded accessibility registry path before proposing implementation.
3. If approved and executable:
   - add positive and negative fixtures first
   - implement validator CLI/module only
   - ensure machine-readable failures and non-zero exit on incoherence
4. Do not mutate data or repair bad artifacts in this issue.
5. Review adversarially for:
   - false positives
   - hidden dependency on unlanded seeded registry contract
   - provenance omission
   - alias conflict handling

Validation commands:
- uv run pytest tests/workstations/test_registry.py -q
- any new validator test files you add
- optional validator CLI smoke against fixtures if implemented

If blocked, output:
- discovered seeded registry location or missing-path blocker
- exact coherence rules
- exact fixtures/tests to add first
```

## Prompt for #2157

```text
ISSUE_NUMBER: 2157
ISSUE_TITLE: feat(operations): implement native PowerShell probe collector for Windows readiness bundles

Mission:
Execute #2157 as a collector-only issue. Keep it separate from higher-level bundle writing.

Issue summary:
Implement a PowerShell probe collector that emits normalized Windows readiness probe JSON for hostname/user/workspace path/access_mode/AI CLI/licensed-tool/source metadata across healthy, degraded, and partial-permission scenarios.

Owned paths:
- scripts/windows/
- tests/fixtures/
- tests/reporting/
- docs/modules/ai/

Read-only paths:
- scripts/readiness/
- config/workstations/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- scheduler registration or full writer orchestration

Specific execution instructions:
1. Check approval first. If not approved, stop with a collector dossier.
2. Inspect whether a PowerShell collector or adjacent probe scripts already exist.
3. If approved and executable:
   - add fixture-driven tests first
   - implement the collector as a focused probe-emitter only
   - prefer fixture validation over live PowerShell assumptions on Linux
4. If PowerShell is unavailable in the current environment, mark live execution as environment-blocked but still implement fixture-backed parsing/tests if approval exists.
5. Review adversarially for:
   - quoting
   - missing-field semantics
   - degraded-case stability
   - licensed-tool probe brittleness

Validation commands:
- any new targeted pytest tests you add for collector output and fixtures
- if available: pwsh -File <collector>.ps1 ...

If blocked, output:
- intended script path
- intended JSON output fields
- exact fixture/test plan
- whether live PowerShell execution is additionally environment-blocked
```

## Prompt for #2158

```text
ISSUE_NUMBER: 2158
ISSUE_TITLE: feat(operations): add Git Bash launcher and path-normalization bridge for Windows evidence writer

Mission:
Execute #2158 as a launcher/path-bridge issue only.

Issue summary:
Implement Git Bash entrypoint and native↔POSIX path bridge for the Windows readiness evidence writer, including support for spaces and non-default Git install locations.

Owned paths:
- scripts/windows/
- tests/fixtures/
- tests/reporting/
- docs/modules/ai/

Read-only paths:
- scripts/readiness/
- scripts/lib/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- repo-wide path-normalization refactors

Specific execution instructions:
1. Check approval first. If not approved, stop with a launcher dossier.
2. Inspect current cygpath/native-path usage elsewhere in repo.
3. If approved and executable:
   - add failing path/launcher tests first
   - implement launcher with dry-run mode
   - explicitly cover spaces, non-default install path, missing cygpath, quoting, and command rendering
4. Do not absorb scheduler registration or writer implementation here.
5. If writer entrypoint from #2150 does not yet exist, stop after launcher skeleton + tests + blocker note.
6. Review adversarially for:
   - path escaping bugs
   - hardcoded Git path assumptions
   - incorrect native/POSIX conversion

Validation commands:
- any new targeted path/launcher tests you add
- dry-run launcher smoke only

If blocked, output:
- exact writer dependency missing
- exact launcher/bridge files to create
- exact edge-case tests to add first
```

## Prompt for #2159

```text
ISSUE_NUMBER: 2159
ISSUE_TITLE: feat(reporting): build publication bundle assembler for weekly review outputs

Mission:
Execute #2159 as an assembler-only issue consuming existing validated artifacts and renderer outputs.

Issue summary:
Build the publication bundle assembler that creates deterministic `latest/`, `history/<run-id>/`, shared assets, and manifest outputs for weekly review publication.

Owned paths:
- scripts/reporting/
- tests/reporting/
- tests/fixtures/
- docs/modules/ai/

Read-only paths:
- scripts/analysis/
- docs/plans/
- AGENTS.md

Forbidden paths:
- digitalmodel/
- monitoring-dashboard/
- schema validation logic
- renderer implementation logic

Specific execution instructions:
1. Check approval first. If not approved, stop with an assembler dossier.
2. Discover existing artifact layout, if any.
3. If approved and executable:
   - add failing tests first for latest tree, history tree, asset dedupe, relative path generation, degraded publication case
   - implement assembler only
   - add dry-run/tree-manifest mode before copy/write mode
4. Do not absorb renderer/history/schema responsibilities.
5. If manifests or renderer outputs from upstream issues are missing, stop with a fixture-backed skeleton plus blocker note.
6. Review adversarially for:
   - nondeterministic ordering
   - broken relative links
   - duplicate asset handling
   - accidental absolute paths or path traversal

Validation commands:
- any new targeted tests under tests/reporting/
- assembler dry-run smoke into /tmp or another temp dir

If blocked, output:
- exact upstream contract missing
- exact output tree contract to implement once approved
- exact tests to add first
```

## Recommended next step

Given live state (`0` open `status:plan-approved` issues), the best immediate use of these prompts is:
- run them in read-only approval-check / implementation-dossier mode now, or
- add plan approvals first, then rerun in implementation mode.

## Fastest candidate prompts after approval

Based on issue shape and repo adjacency, the likely lowest-risk first executions are:
1. `#2151` schema + status vocabulary
2. `#2152` fixture corpus
3. `#2155` shared machine/path resolver

These are the best early building blocks for the rest of the cluster.
