# Plan for #2889: Per-Provider Harness-Parity Cell

> **Status:** implemented; pending PR/closeout
> **Complexity:** T2
> **Date:** 2026-06-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2889
> **Client:** N/A
> **Project:**
> **Review artifacts:** plan r1: `scripts/review/results/2026-06-10-plan-2889-r1-claude.md`, `scripts/review/results/2026-06-10-plan-2889-r1-codex.md`, `scripts/review/results/2026-06-10-plan-2889-r1-gemini.md`; plan r2: `scripts/review/results/2026-06-10-plan-2889-r2-claude.md`, `scripts/review/results/2026-06-10-plan-2889-r2-codex.md`, `scripts/review/results/2026-06-10-plan-2889-r2-gemini.md`, `scripts/review/results/2026-06-10-plan-2889-r2-disagreement.md`; plan r3: `scripts/review/results/2026-06-10-plan-2889-r3-claude.md`, `scripts/review/results/2026-06-10-plan-2889-r3-codex.md`, `scripts/review/results/2026-06-10-plan-2889-r3-gemini.md`; plan r4: `scripts/review/results/2026-06-10-plan-2889-r4-claude.md`, `scripts/review/results/2026-06-10-plan-2889-r4-codex.md`, `scripts/review/results/2026-06-10-plan-2889-r4-gemini.md`; code r1: `scripts/review/results/2026-06-10-code-2889-r1-codex.md`, `scripts/review/results/2026-06-10-code-2889-r1-gemini.md`; code r2: `scripts/review/results/2026-06-10-code-2889-r2-codex.md`, `scripts/review/results/2026-06-10-code-2889-r2-gemini.md`. User approved implementation on 2026-06-11 with `status:plan-approved` already present on the issue; the degraded review-tooling record is accepted for this measurement-only scope.

---

## Resource Intelligence Summary

### Existing Repo Code

- `scripts/readiness/collect-equality.sh` emits the per-machine `.claude/state/equality-<machine>.yaml` self-report with `schema_version: 3`. It currently captures broad provider presence under `dimensions.harness.providers`, repo skill count under `dimensions.skills`, Hermes memory presence under `dimensions.memory`, behavior gates, scheduler booleans, and git provenance. Gap: it does not emit provider-specific `memory:read`, `skills:invoke`, or `workflow:gates` predicates.
- `scripts/readiness/collect-equality.ps1` is the Windows companion for `ace-win-1` and `ace-win-2`. It delegates schema/provenance/solver emission to `collect-equality.sh`, but its contract is pinned by `tests/readiness/test_collect_equality_ps1_schema.py` and `tests/readiness/fixtures/equality-ace-win-1.sample.yaml`. Any new dimension must update this golden fixture and key-tree parity test.
- `tests/readiness/test_collect_equality.py` has collector contract tests, including `test_collect_emits_schema_v3`, no-secret assertions, solver schema tests, and stale-checkout provenance tests. The plan must update these tests to schema v4 and add provider-harness emission coverage.
- `tests/readiness/test_collect_equality_ps1_schema.py` asserts the exact Windows fixture dimension set and exact `.ps1` fixture key-tree parity with `.sh --stdout`. Adding `dimensions.provider_harness` without updating this file will break Windows parity by construction.
- `scripts/readiness/build-equality-matrix.py` joins equality reports and renders rows from `DISPLAY_DIMS`. It already applies `UNREACHABLE`, malformed report, and `STALE-CHECKOUT` precedence before cold/uniform verdict families. Gap: it has no provider-harness row expansion or CSS/verdict mapping for `PARITY`, `DIVERGES`, `EXPECTED-DIVERGENCE`, and `ABSENT`.
- `tests/readiness/test_build_equality_matrix.py` has focused renderer/verdict tests, including `STALE-CHECKOUT` precedence and HTML rendering tests. Provider rows must be tested there or in a new adjacent readiness test file, not only in `tests/workstations`.
- `scripts/readiness/harness-config.yaml` is the matrix roster source. It currently lists four active workstations (`dev-primary`, `dev-secondary`, `ace-win-1`, `ace-win-2`) and two unreachable workstations (`home-win`, `macbook-portable`).

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue planning workflow | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` requires issue -> resource intel -> plan -> adversarial review -> user approval before implementation. |
| Hard gates / provider identity | applicable | `AGENTS.md`, `config/agents/SHARED_SOUL.md`, and provider runtime artifacts under `config/agents/*/` define the cross-provider planning, TDD, and approval gates. |
| Harness retrieval bundle | applicable | `docs/plans/README.md` says harness plans should consult `CONTROL_PLANE_CONTRACT.md`, `config/agents/`, and `.claude/rules/`; `docs/standards/CONTROL_PLANE_CONTRACT.md`, `config/agents/`, and `.claude/rules/` all exist in this checkout. |
| Security / legal scan | applicable | `scripts/legal/legal-sanity-scan.sh` must pass before implementation closeout; provider predicates must not read or emit auth tokens, raw environment values, cron lines, or client identifiers. |

### LLM Wiki Pages Consulted

- No LLM wiki pages apply. This issue modifies workspace-hub harness/equality measurement only and does not touch wiki content.

### Documents Consulted

- [#2889](https://github.com/vamseeachanta/workspace-hub/issues/2889) body and comments define the exact v1 contract: providers `Claude/Codex/Hermes`, capabilities `memory:read`, `skills:invoke`, `workflow:gates`, row shape `harness:<provider>:<capability>`, and verdict family `PARITY/DIVERGES/EXPECTED-DIVERGENCE/ABSENT`.
- [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) is the parent equivalence-status epic; #2889 implements requirement R2 for AI harness parity across providers.
- [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) is still open and labeled `status:needs-plan`; it blocks the broader substrate revival. This plan proposes a measurement-only implementation before #2894 completes, but live cron/substrate evidence should not be claimed complete under #2889.
- [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755) is the ace-linux-2 activation lane. The 2026-06-10 ace-linux-2 probe found live provider CLIs and active processes, but also stale memory, provider skill adapter breakage, and possible cron environment drift.
- [#2841](https://github.com/vamseeachanta/workspace-hub/issues/2841) is closed and records locked harness/skills/memory consistency decisions: Claude dream as canonical consolidator, two independent lanes (`Claude` and `Codex+Hermes`), and weekly checks.
- `AGENTS.md` and `config/agents/SHARED_SOUL.md` define provider-agnostic hard gates and symlink/runtime patterns.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` defines `AGENTS.md` as the canonical entry point and provider directories as adapters, not alternate sources of truth.
- `config/agents/claude/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md`, `config/agents/codex/MEMORY.runtime.md`, and `config/agents/hermes/SOUL.runtime.md` are the repo-tracked runtime surfaces the predicates can inspect safely.
- `scripts/agents/install-soul-runtime.sh` defines intended local runtime symlink targets for Hermes and Codex.
- `.claude/rules/completeness-before-close.md` defines the opt-in closeout completeness gate for issues carrying `gate:completeness`.
- `.claude/rules/security.md` is referenced by the runtime hard gates, but is absent in this checkout; implementation must still enforce secrets-safe behavior through tests and `scripts/legal/legal-sanity-scan.sh`.
- `.claude/memory/agents.md` currently says ace-linux-2 lacks `digitalmodel` and `worldenergydata`; the 2026-06-10 SSH probe showed those checkouts now exist under `/mnt/local-analysis`, so the matrix must report stale machine memory rather than trust that file blindly.

### Gaps Identified

- No provider capability schema exists in equality reports.
- No provider-harness row expansion exists in the matrix renderer.
- No test ensures a provider skill adapter fails when `.codex/skills` is a regular file containing `../.claude/skills` instead of a symlink or directory.
- No test covers Windows `.ps1` fixture/key-tree parity after adding a provider dimension.
- No test distinguishes legacy v3 reports from schema v4 reports; provider rows must fail closed as `MISSING-EVIDENCE` for legacy reports.
- No test covers all four active workstations in the provider-harness row matrix.

### Evidence

**Issue statuses** (verified 2026-06-10 via `gh issue view` in the planning session):

- [#2889](https://github.com/vamseeachanta/workspace-hub/issues/2889) - OPEN - labels include `status:needs-plan`.
- [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) - OPEN - parent equivalence-status epic.
- [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) - OPEN - labels include `status:needs-plan`.
- [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755) - OPEN - labels include `status:plan-approved` and `status:working`.
- [#2841](https://github.com/vamseeachanta/workspace-hub/issues/2841) - CLOSED.

**File existence** (verified 2026-06-10 in `/mnt/local-analysis/workspace-hub`):

- EXISTS: `scripts/readiness/collect-equality.sh`
- EXISTS: `scripts/readiness/collect-equality.ps1`
- EXISTS: `scripts/readiness/build-equality-matrix.py`
- EXISTS: `scripts/readiness/harness-config.yaml`
- EXISTS: `tests/readiness/test_collect_equality.py`
- EXISTS: `tests/readiness/test_collect_equality_ps1_schema.py`
- EXISTS: `tests/readiness/test_build_equality_matrix.py`
- EXISTS: `tests/readiness/fixtures/equality-ace-win-1.sample.yaml`
- EXISTS: `AGENTS.md`
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `config/agents/SHARED_SOUL.md`
- EXISTS: `config/agents/claude/SOUL.runtime.md`
- EXISTS: `config/agents/codex/AGENTS.runtime.md`
- EXISTS: `config/agents/codex/MEMORY.runtime.md`
- EXISTS: `config/agents/hermes/SOUL.runtime.md`
- EXISTS: `.claude/rules/`
- EXISTS: `.claude/rules/completeness-before-close.md`
- EXISTS: `.claude/memory/agents.md`
- MISSING: `.claude/rules/security.md`
- MISSING (new): `scripts/readiness/provider_harness_parity.py`
- MISSING (new): `tests/readiness/test_provider_harness_parity.py`

Direct file-existence proof:

```text
$ ls -ld AGENTS.md docs/standards docs/standards/CONTROL_PLANE_CONTRACT.md .claude/rules .claude/rules/completeness-before-close.md .claude/rules/security.md .claude/skills/coordination/issue-planning-mode/SKILL.md .claude/memory/agents.md
ls: cannot access '.claude/rules/security.md': No such file or directory
.claude/memory/agents.md
.claude/rules
.claude/rules/completeness-before-close.md
.claude/skills/coordination/issue-planning-mode/SKILL.md
AGENTS.md
docs/standards
docs/standards/CONTROL_PLANE_CONTRACT.md
```

**Line excerpts**:

`docs/standards/CONTROL_PLANE_CONTRACT.md` defines the provider-adapter boundary:

```markdown
**`AGENTS.md`** is the canonical entry point for every repository.
Provider-specific configuration lives in dedicated directories. These are **adapters**, not alternatives to `AGENTS.md`.
```

`.claude/rules/completeness-before-close.md` defines the closeout gate for `gate:completeness` issues:

```markdown
When closing an issue that OPTED IN (carries the `gate:completeness` label) and reached `status:plan-approved`, a test-/evidence-based completeness score (0-100%) must be computed...
```

`scripts/readiness/build-equality-matrix.py` currently defines a flat display list and existing CSS classes:

```python
DISPLAY_DIMS = ["compute", "data_access", "solvers", "harness", "python_cmd", "skills",
                "kanban", "memory", "behavior", "scheduler"]
```

`scripts/readiness/collect-equality.sh` currently emits provider presence only under the broad harness dimension:

```bash
prov() { have "$1" && echo present || echo absent; }
```

`scripts/readiness/collect-equality.sh` currently has a measured-path allowlist that must be kept in sync with provider-harness inputs:

```bash
MEASURED=(.claude/skills .claude/memory/context.md .claude/dispatch .claude/rules \
          .claude/hooks/plan-approval-gate.sh .claude/settings.json \
          scripts/readiness/harness-config.yaml config/scheduled-tasks/schedule-tasks.yaml)
```

`tests/readiness/test_collect_equality_ps1_schema.py` currently pins the exact Windows fixture dimension set:

```python
EXPECTED_DIMS = {"compute", "data_access", "solvers", "harness", "skills",
                 "kanban", "memory", "behavior", "scheduler"}
```

**Gap proof**:

```bash
$ rg -n "harness:codex:memory:read|provider_harness|EXPECTED-DIVERGENCE|memory:read|skills:invoke|workflow:gates" scripts/readiness tests/readiness; echo "exit=$?"
exit=1
```

**Reproduction proofs**:

N/A - #2889 is a harness measurement enhancement, not a reported runtime failure. The live ace-linux-2 probe was captured in https://github.com/vamseeachanta/workspace-hub/issues/2889#issuecomment-4673336469 and will be converted into fixture cases, not treated as an implementation failure to reproduce.

Distinct source count: 18 ([#2889](https://github.com/vamseeachanta/workspace-hub/issues/2889), [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887), [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894), [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755), [#2841](https://github.com/vamseeachanta/workspace-hub/issues/2841), `collect-equality.sh`, `collect-equality.ps1`, `build-equality-matrix.py`, `harness-config.yaml`, `test_collect_equality.py`, `test_collect_equality_ps1_schema.py`, `test_build_equality_matrix.py`, `AGENTS.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `config/agents/SHARED_SOUL.md`, provider runtime files under `config/agents/`, `.claude/rules/completeness-before-close.md`, `.claude/memory/agents.md`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-10-issue-2889-provider-harness-parity.md` |
| Plan index | `docs/plans/README.md` |
| Provider capability helper | `scripts/readiness/provider_harness_parity.py` |
| Equality collector | `scripts/readiness/collect-equality.sh` |
| Windows collector companion | `scripts/readiness/collect-equality.ps1` |
| Matrix renderer | `scripts/readiness/build-equality-matrix.py` |
| Harness roster/config | `scripts/readiness/harness-config.yaml` |
| Windows equality golden fixture | `tests/readiness/fixtures/equality-ace-win-1.sample.yaml` |
| Provider capability tests | `tests/readiness/test_provider_harness_parity.py` |
| Collector contract tests | `tests/readiness/test_collect_equality.py` |
| Windows collector contract tests | `tests/readiness/test_collect_equality_ps1_schema.py` |
| Matrix verdict/render tests | `tests/readiness/test_build_equality_matrix.py` |
| Legal/security scan | `scripts/legal/legal-sanity-scan.sh` |
| Plan review - Claude r1 | `scripts/review/results/2026-06-10-plan-2889-r1-claude.md` |
| Plan review - Codex r1 | `scripts/review/results/2026-06-10-plan-2889-r1-codex.md` |
| Plan review - Gemini r1 | `scripts/review/results/2026-06-10-plan-2889-r1-gemini.md` |
| Plan review - Claude r2 | `scripts/review/results/2026-06-10-plan-2889-r2-claude.md` |
| Plan review - Codex r2 | `scripts/review/results/2026-06-10-plan-2889-r2-codex.md` |
| Plan review - Gemini r2 | `scripts/review/results/2026-06-10-plan-2889-r2-gemini.md` |
| Review disagreement summary r2 | `scripts/review/results/2026-06-10-plan-2889-r2-disagreement.md` |
| Plan review - Claude r3 | `scripts/review/results/2026-06-10-plan-2889-r3-claude.md` |
| Plan review - Codex r3 | `scripts/review/results/2026-06-10-plan-2889-r3-codex.md` |
| Plan review - Gemini r3 | `scripts/review/results/2026-06-10-plan-2889-r3-gemini.md` |
| Plan review - Claude r4 | `scripts/review/results/2026-06-10-plan-2889-r4-claude.md` |
| Plan review - Codex r4 | `scripts/review/results/2026-06-10-plan-2889-r4-codex.md` |
| Plan review - Gemini r4 | `scripts/review/results/2026-06-10-plan-2889-r4-gemini.md` |

---

## Deliverable

The equality matrix will render nine provider-harness rows for the four active machines in `scripts/readiness/harness-config.yaml`:

- `harness:claude:memory:read`
- `harness:claude:skills:invoke`
- `harness:claude:workflow:gates`
- `harness:codex:memory:read`
- `harness:codex:skills:invoke`
- `harness:codex:workflow:gates`
- `harness:hermes:memory:read`
- `harness:hermes:skills:invoke`
- `harness:hermes:workflow:gates`

Each row will preserve existing matrix precedence (`UNREACHABLE`, malformed report -> `MISSING-EVIDENCE`, `STALE-CHECKOUT`) before applying provider verdicts. Fresh schema-v4 reports will grade provider cells as `PARITY`, `DIVERGES`, `EXPECTED-DIVERGENCE`, or `ABSENT`, with Codex/Hermes evaluated against Claude on the same machine. Legacy schema-v3 reports without `dimensions.provider_harness` will grade provider rows as `MISSING-EVIDENCE`, not crash or silently pass.

---

## Capability Predicate Contract

The report schema will bump from `schema_version: 3` to `schema_version: 4` and add:

```yaml
dimensions:
  provider_harness:
    schema_version: 1
    providers:
      claude:
        present: true
        installed: true
        "memory:read": {status: present, reason: claude_memory_context_found}
        "skills:invoke": {status: present, reason: repo_skill_tree_found}
        "workflow:gates": {status: present, reason: hard_gates_runtime_found}
      codex:
        present: true
        installed: true
        "memory:read": {status: present, reason: codex_memory_runtime_found}
        "skills:invoke": {status: absent, reason: adapter_not_directory_or_symlink}
        "workflow:gates": {status: present, reason: codex_agents_runtime_active}
      hermes:
        present: true
        installed: true
        "memory:read": {status: present, reason: hermes_memory_store_found}
        "skills:invoke": {status: expected_divergence, reason: external_skill_dirs_configured}
        "workflow:gates": {status: present, reason: hermes_soul_runtime_active}
```

Allowed capability statuses: `present`, `absent`, `expected_divergence`, `unknown`.

Allowed verdicts: `PARITY`, `DIVERGES`, `EXPECTED-DIVERGENCE`, `ABSENT`, plus existing matrix-precedence verdicts.

Provider `present` / `installed` is not inferred from repo-tracked runtime artifacts alone. A provider is installed on a machine only when a local executable exists (`claude`, `codex`, `hermes`) or a machine-local provider runtime path exists (`~/.codex/AGENTS.md`, `~/.hermes/SOUL.md`) and is readable. Repo files under `config/agents/` can support capability evidence only after the local provider installation check passes.

Provider verdicts are Claude-reference-based:

- For `harness:claude:<capability>`, `PARITY` means the Claude reference capability is present on that machine; `ABSENT` means Claude itself is not installed; `MISSING-EVIDENCE` means Claude is installed but the capability cannot be established.
- For `harness:codex:<capability>` and `harness:hermes:<capability>`, compare the target capability against `harness:claude:<capability>` on the same machine.
- If the Claude reference capability is absent or unknown, Codex/Hermes cells return `MISSING-EVIDENCE`, not `PARITY`, because the same-machine reference is unavailable.
- If Claude has the capability and the target provider is not installed, return `ABSENT`.
- If Claude has the capability and the target provider has it, return `PARITY`.
- If Claude has the capability and the target provider lacks it with an allowlisted structural reason, return `EXPECTED-DIVERGENCE`.
- If Claude has the capability and the target provider lacks it without an allowlisted reason, return `DIVERGES`.

Predicate definitions:

- `memory:read`
  - Claude: `present` only if Claude is installed and repo `.claude/memory/context.md` or `.claude/memory/agents.md` exists and is readable; stale content is a separate evidence issue, not a read failure.
  - Codex: `present` only if Codex is installed and `config/agents/codex/AGENTS.runtime.md` plus `config/agents/codex/MEMORY.runtime.md` exist and contain hard-gate/memory sections; the predicate must not inspect `~/.codex/auth.json`.
  - Hermes: `present` only if Hermes is installed and `config/agents/hermes/SOUL.runtime.md` exists and local `~/.hermes/memories` or an accepted repo-backed memory equivalent is non-empty; output emits only counts/reason codes.
- `skills:invoke`
  - Claude: `present` only if Claude is installed and `.claude/skills` is a directory or symlink with at least one `SKILL.md`.
  - Codex: `present` only if Codex is installed and `.codex/skills` is a directory or symlink resolving to the repo `.claude/skills` tree; a regular file containing `../.claude/skills` is `absent` with reason `adapter_not_directory_or_symlink`.
  - Hermes: `present` only if Hermes is installed and Hermes configuration points to repo `.claude/skills` or another explicit skill registry. If Hermes intentionally uses external skill directories, use `expected_divergence` only with an allowlisted reason and non-empty target evidence.
- `workflow:gates`
  - Claude: `present` only if Claude is installed and `AGENTS.md` or `config/agents/claude/SOUL.runtime.md` contains `Plan ALL issues`, `USER APPROVES`, and `TDD mandatory`, and `.claude/skills/coordination/issue-planning-mode/SKILL.md` exists.
  - Codex: `present` only if Codex is installed, the active local runtime path `~/.codex/AGENTS.md` exists or symlinks to `config/agents/codex/AGENTS.runtime.md`, and the resolved active runtime contains `Plan ALL issues`, `USER APPROVES`, `TDD mandatory`, and references mandatory lifecycle skills. Static repo text alone is supporting evidence, not sufficient.
  - Hermes: `present` only if Hermes is installed, the active local runtime path `~/.hermes/SOUL.md` exists or symlinks to `config/agents/hermes/SOUL.runtime.md`, and the resolved active runtime contains the same planning/TDD/user-approval gates. Static repo text alone is supporting evidence, not sufficient.

Expected-divergence reasons are allowlisted constants, not free-form strings. Unknown or arbitrary false reasons yield `DIVERGES`.

---

## Pseudocode

```text
define PROVIDERS = ["claude", "codex", "hermes"]
define CAPABILITIES = ["memory:read", "skills:invoke", "workflow:gates"]

function collect_provider_capabilities(workspace_root, home_dir):
    result = empty provider_harness structure
    for provider in PROVIDERS:
        provider_present = command_exists(provider) or local_provider_runtime_exists(provider, home_dir)
        result[provider]["present"] = provider_present
        result[provider]["installed"] = provider_present
        result[provider]["memory:read"] = evaluate_memory_read(provider, workspace_root, home_dir)
        result[provider]["skills:invoke"] = evaluate_skills_invoke(provider, workspace_root, home_dir)
        result[provider]["workflow:gates"] = evaluate_workflow_gates(provider, workspace_root, home_dir)
    return result after redacting absolute auth paths, env values, token-like strings, and cron lines

function collect_equality_sh():
    provider_yaml = run provider_harness_parity.py --workspace "$WS" --home "$HOME" --format yaml
    if helper fails, provider_yaml = schema-valid provider_harness block with unknown statuses
    emit schema_version: 4
    insert provider_yaml under dimensions.provider_harness

function provider_capability_verdict(provider, capability, provider_record, claude_record):
    if provider == "claude":
        if provider_record.present == false: return ABSENT
        if provider_record[capability].status == "present": return PARITY
        return MISSING-EVIDENCE
    if claude_record.present != true or claude_record[capability].status != "present":
        return MISSING-EVIDENCE
    if provider_record.present == false: return ABSENT
    status = provider_record[capability].status
    if status == "present": return PARITY
    if status == "expected_divergence" and reason is allowlisted: return EXPECTED-DIVERGENCE
    if status == "absent": return DIVERGES
    return MISSING-EVIDENCE

function verdict_for(dim_or_row, machine, reports, baselines, roster, probed_repos):
    if roster[machine].status == "unreachable": return UNREACHABLE
    if report missing or malformed: return MISSING-EVIDENCE
    if is_stale(report): return STALE-CHECKOUT
    if dim_or_row starts with "harness:":
        if report.schema_version < 4 or dimensions.provider_harness missing: return MISSING-EVIDENCE
        provider, capability = parse exact row name "harness:<provider>:<capability>"
        return provider_capability_verdict(provider, capability,
            report.dimensions.provider_harness.providers[provider],
            report.dimensions.provider_harness.providers["claude"])
    if dim_or_row in COLD_DIMS: return cold_verdict(...)
    return uniform_verdict(...)

function display_rows():
    base rows = existing DISPLAY_DIMS
    provider rows = for provider in PROVIDERS for capability in CAPABILITIES:
        "harness:<provider>:<capability>"
    render base rows through existing verdict_for
    render provider rows through existing verdict_for
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/readiness/provider_harness_parity.py` | Holds provider/capability constants, secrets-safe capability evaluation, exact row-name parsing, allowlisted expected-divergence reasons, and stdlib-only YAML/JSON-subset emission helpers compatible with the Windows collector's bare `python` path. |
| Modify | `scripts/readiness/collect-equality.sh` | Bumps report schema to v4, invokes the helper, emits `dimensions.provider_harness`, and updates the measured-path allowlist for newly read provider runtime/adapter files. |
| Inspect/possibly modify | `scripts/readiness/collect-equality.ps1` | Confirms the Windows companion still delegates schema emission to `.sh`; no standalone provider logic should be duplicated here unless the `.sh` delegation contract requires argument/env forwarding. |
| Modify | `scripts/readiness/build-equality-matrix.py` | Renders exact provider row names by integrating provider-row handling into the existing `verdict_for()` precedence path, and adds CSS classes for `parity`, `expected-divergence`, and `absent`. |
| Modify | `scripts/readiness/harness-config.yaml` | Adds an optional config roster for the v1 providers/capabilities only if constants are not kept solely in the helper; must not add Gemini rows in this issue. |
| Modify | `tests/readiness/fixtures/equality-ace-win-1.sample.yaml` | Updates the Windows golden fixture to schema v4 with `dimensions.provider_harness`. |
| Create | `tests/readiness/test_provider_harness_parity.py` | Unit-tests capability extraction, exact row parsing, redaction, allowlisted expected-divergence reasons, and the ace-linux-2 `.codex/skills` pseudo-symlink failure mode. |
| Modify | `tests/readiness/test_collect_equality.py` | Updates schema test to v4 and adds `.sh --stdout` provider-harness block/no-secret tests. |
| Modify | `tests/readiness/test_collect_equality_ps1_schema.py` | Updates `EXPECTED_DIMS`, golden fixture parse checks, and `.ps1` fixture key-tree parity. |
| Modify | `tests/readiness/test_build_equality_matrix.py` | Adds all four active-machine provider row rendering, legacy-v3 missing-evidence behavior, and stale-checkout precedence tests for provider rows. |
| Modify | `docs/plans/README.md` | Keeps this issue plan indexed with current conservative status. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_provider_harness_constants_use_exact_issue_capability_names` | Constants preserve `memory:read`, `skills:invoke`, `workflow:gates` and build exact row names. | helper constants | rows include `harness:codex:memory:read`; shortened memory-only row names are rejected. |
| `test_skill_adapter_rejects_regular_file_pseudo_symlink` | `.codex/skills` as a regular file containing `../.claude/skills` is not accepted as skill parity. | temp workspace with `.claude/skills/a/SKILL.md` and `.codex/skills` regular file | Codex `skills:invoke` is `absent` with reason `adapter_not_directory_or_symlink`; verdict `DIVERGES` when Claude skills are present. |
| `test_claude_reference_skills_parity_when_repo_skills_exist` | Claude is the reference provider for same-machine skill access. | temp workspace with `.claude/skills/a/SKILL.md` | `harness:claude:skills:invoke` verdict `PARITY`. |
| `test_codex_memory_read_uses_runtime_and_readback_files` | Codex memory predicate uses repo runtime/readback files, not auth/token contents. | temp workspace with `config/agents/codex/AGENTS.runtime.md` and `config/agents/codex/MEMORY.runtime.md` | Codex `memory:read` capability true; evidence contains only booleans, counts, enums, and reason codes. |
| `test_workflow_gates_requires_plan_user_approval_and_tdd_text` | `workflow:gates` is a concrete predicate, not just provider presence. | runtime file missing one hard-gate phrase | capability `absent` with reason naming the missing gate. |
| `test_hermes_memory_read_requires_nonempty_memory_store_or_repo_equivalent` | Hermes memory predicate follows #2889 without leaking home paths. | temp home with `.hermes/memories/topic.md` | Hermes `memory:read` true; output contains count/reason only. |
| `test_provider_absent_yields_absent_not_diverges` | Missing provider binary/state is not misclassified as a parity mismatch when Claude reference is present. | report with `providers.claude.memory:read=present` and `providers.codex.present=false` | `harness:codex:*` verdict `ABSENT`. |
| `test_target_provider_parity_is_reference_based_on_claude_same_machine` | Codex/Hermes verdicts compare target capability to Claude on the same report, not target status alone. | Claude `memory:read=present`, Codex `memory:read=absent`; then Claude `memory:read=absent`, Codex `memory:read=absent` | first case `DIVERGES`; second case `MISSING-EVIDENCE`, not `PARITY`. |
| `test_repo_runtime_files_do_not_make_provider_installed` | Repo-tracked `config/agents/*` files are not enough to mark a provider present on a machine. | temp workspace with `config/agents/codex/AGENTS.runtime.md` but no `codex` executable or `~/.codex/AGENTS.md` | Codex `present=false`; Codex rows grade `ABSENT` when Claude reference is present. |
| `test_workflow_gates_requires_active_local_runtime_path` | `workflow:gates` verifies active runtime install/symlink state, not only static repo text. | repo has `config/agents/codex/AGENTS.runtime.md`; temp home lacks `.codex/AGENTS.md` | Codex `workflow:gates` is absent/unknown with reason `active_runtime_missing`. |
| `test_expected_divergence_is_explicit_reason_only` | Structural divergence is only emitted for allowlisted reasons. | capability false with reason `external_skill_dirs_configured` | verdict `EXPECTED-DIVERGENCE`; arbitrary reason yields `DIVERGES`. |
| `test_collect_emits_schema_v4_with_complete_provider_harness` | Bash collector emits the new schema and all provider/capability records. | controlled WORKSPACE_HUB fixture | `schema_version == 4`, `dimensions.provider_harness.schema_version == 1`, and all `providers.{claude,codex,hermes}.{memory:read,skills:invoke,workflow:gates}` records exist with valid status/reason fields. |
| `test_collect_provider_harness_no_forbidden_fields` | Collector output does not leak tokens, auth paths, env values, or cron lines. | fixture env with token-like values and cron-like strings | YAML contains no token patterns, raw `$HOME` auth paths, or cron lines. |
| `test_provider_harness_helper_is_windows_stdlib_safe` | Helper does not require dependencies unavailable when `collect-equality.sh` uses bare `python` for Windows/Git Bash. | Windows OS override seam with no PyYAML/PEP-723 dependency install | collector emits `dimensions.provider_harness` instead of crashing with an import error. |
| `test_ps1_sample_output_parses_schema_v4_with_provider_harness` | Windows golden fixture schema and dimension set are updated. | `tests/readiness/fixtures/equality-ace-win-1.sample.yaml` | schema v4 and exact dimension set includes `provider_harness`. |
| `test_ps1_field_parity_with_sh_stdout_includes_provider_harness` | Windows fixture key-tree matches `.sh --stdout` after new dimension. | `.sh` through Windows EQ override seam | fixture key tree equals live `.sh` key tree. |
| `test_matrix_renders_nine_provider_capability_rows_for_four_active_machines` | Renderer includes all 3 providers x 3 capabilities across the active roster. | fixture equality reports for `dev-primary`, `dev-secondary`, `ace-win-1`, `ace-win-2` | HTML contains nine provider row headers and 36 provider cells. |
| `test_legacy_v3_report_provider_rows_missing_evidence` | Old reports fail closed for new rows. | schema-v3 report without `provider_harness` | provider row verdict `MISSING-EVIDENCE`. |
| `test_stale_checkout_precedence_still_dominates_provider_rows` | Existing stale-checkout guard applies to new provider rows. | equality report with stale provenance | provider rows for that machine show `STALE-CHECKOUT`. |

---

## Acceptance Criteria

- [ ] User approval explicitly accepts proceeding with this measurement-only #2889 plan before the broader [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) substrate revival completes; without that approval, #2889 remains draft/needs-decision.
- [ ] TDD tests are written before implementation and fail for the missing provider-harness behavior.
- [ ] Overall equality report schema is bumped from v3 to v4, and legacy v3 reports grade provider rows as `MISSING-EVIDENCE`.
- [ ] `uv run pytest tests/readiness/test_provider_harness_parity.py -v` passes.
- [ ] `uv run pytest tests/readiness/test_collect_equality.py -v` passes.
- [ ] `uv run pytest tests/readiness/test_collect_equality_ps1_schema.py -v` passes.
- [ ] `uv run pytest tests/readiness/test_build_equality_matrix.py -v` passes.
- [ ] Full readiness regression passes: `uv run pytest tests/readiness -v`.
- [ ] Existing workstation tests still pass: `uv run pytest tests/workstations -v`.
- [ ] `bash scripts/readiness/collect-equality.sh --stdout --machine dev-primary` emits `dimensions.provider_harness` without secrets, absolute auth paths, raw environment values, raw cron lines, or token contents.
- [ ] `provider_harness_parity.py` uses only Python stdlib dependencies, or the collector has a tested Windows-safe invocation path; `collect-equality.sh` must not require PyYAML/PEP-723 dependency resolution on the Windows bare-`python` path.
- [ ] `uv run --script scripts/readiness/build-equality-matrix.py` renders all nine provider/capability rows.
- [ ] A fixture modeled on the 2026-06-10 ace-linux-2 probe reports `.codex/skills` regular-file pseudo-symlink as `DIVERGES`, not `PARITY`.
- [ ] The implementation does not modify live provider auth files, live memory stores, cron entries, or remote ace-linux-2 state; this issue measures parity only.
- [ ] Legal/security scan passes: `bash scripts/legal/legal-sanity-scan.sh`.
- [ ] Completeness score is produced before close per the repo closeout gate.

---

## User Gates Before Plan Approval

Resolved by user approval on 2026-06-11:

1. **[#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) sequencing:** User approval accepted proceeding with measurement-only [#2889](https://github.com/vamseeachanta/workspace-hub/issues/2889) before the broader substrate revival in [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) is complete.
2. **Review-tooling disposition:** User approval accepted the degraded review record: Gemini r4 `APPROVE`, Claude unavailable after repeated empty timeouts, and Codex r4 timeout without final verdict.
3. **Missing security rule:** `.claude/rules/security.md` remains outside #2889 scope; this implementation will keep enforcing secrets-safe behavior through tests and `scripts/legal/legal-sanity-scan.sh`.
4. **Measurement-only boundary:** This plan will not mutate live provider auth files, memory stores, cron entries, active runtime symlinks, or remote ace-linux-2 state. Remediation of `.codex/skills`, `WORKSPACE_HUB` cron env drift, `/mnt/dde` vs `/mnt/local-analysis`, or runtime symlink installs belongs in [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755), [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894), or a follow-up issue.
5. **Implementation approval:** [#2889](https://github.com/vamseeachanta/workspace-hub/issues/2889) has `status:plan-approved`; the stale lower `status:needs-plan` label was removed on 2026-06-11 without self-applying approval.

---

## Adversarial Review Summary

R1 was run on 2026-06-10 and all reviewers returned `MAJOR`. R2 was also run on 2026-06-10 after the first local revision; Claude was unavailable, Codex returned `MAJOR`, and Gemini returned `MAJOR` from a `/tmp` overlay with several false file-existence claims. R3 was run after the r2 patch; Claude was unavailable, Codex returned `MAJOR`, and Gemini returned `APPROVE` with one dependency risk. R4 was run after the r3 patch; Gemini returned `APPROVE`, Claude was not rerun because prior r2/r3 attempts both timed out empty, and Codex timed out before producing a final verdict. The plan is not approval-ready until the review-tooling gap is retried successfully or the user explicitly accepts the degraded review record.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | Missing Windows collector/fixture/test updates; active four-machine scope under-tested; `workflow:gates` unspecified; existing readiness tests omitted; schema-version decision missing; pseudocode returned inside provider loop; #2894 sequencing needed explicit user approval. |
| Codex r1 | MAJOR | Predicate names shortened incorrectly; four-active-machine scope under-tested; pseudocode returned inside provider loop; `workflow:gates` unspecified; measured-path allowlist omitted provider inputs; Gemini scope inconsistent with #2889. |
| Gemini r1 | MAJOR | Plan cited files incorrectly; omitted Windows collector; did not specify Bash/Python YAML delegation; introduced verdict taxonomy without renderer/CSS/precedence integration. Main-session recheck found the file-existence portion was stale/false, while the Windows/Bash/verdict findings were valid. |
| Claude r2 | UNAVAILABLE | Fanout was manually terminated after about 200 seconds with zero output. |
| Codex r2 | MAJOR | Correctly caught false missing-file claims, wrong r1 artifact paths, missing reconciliation of Gemini r1 false retrieval, and missing disagreement artifact in the map. |
| Gemini r2 | MAJOR | Several file-existence claims were false due `/tmp` overlay retrieval, but the warning about duplicating matrix precedence outside `verdict_for()` was valid. |
| Claude r3 | UNAVAILABLE | Short path-based review timed out after 180 seconds with empty output. |
| Codex r3 | MAJOR | Caught that parity must be Claude-reference-based on the same machine, provider presence must not be inferred from repo runtime files, `workflow:gates` must verify active local runtime state, and collector tests must assert all 3x3 records. |
| Gemini r3 | APPROVE | No blockers; noted a Windows dependency risk if the helper relies on non-stdlib Python dependencies. |
| Claude r4 | UNAVAILABLE | Not rerun; prior r2/r3 attempts both timed out with empty output, so r4 used Codex/Gemini only. |
| Codex r4 | UNAVAILABLE | Timed out after 360 seconds before producing a final verdict; partial transcript showed plan inspection but no structured review response. |
| Gemini r4 | APPROVE | Confirmed r3 blockers and Windows dependency risk were addressed; no required fixes. |

**Overall result:** Gemini r4 APPROVE, Claude/Codex unavailable; user accepted the degraded review-tooling record for this measurement-only implementation.

Revisions made based on r1/r2/r3 review:

- Added `collect-equality.ps1`, Windows golden fixture, and readiness tests to artifact map, files-to-change, TDD list, and acceptance criteria.
- Restored exact capability names: `memory:read`, `skills:invoke`, `workflow:gates`.
- Added a concrete `workflow:gates` predicate.
- Added schema-v4 decision and legacy-v3 fail-closed behavior.
- Added four-active-machine row/cell testing requirement.
- Added measured-path allowlist update requirement for provider runtime/adapter inputs.
- Removed Gemini from v1 row scope.
- Reconciled Gemini r1/r2 file-existence retrieval against direct local evidence: `CONTROL_PLANE_CONTRACT.md`, `.claude/rules/`, `.claude/rules/completeness-before-close.md`, `AGENTS.md`, and `.claude/memory/agents.md` exist; only `.claude/rules/security.md` is missing.
- Corrected r1 review artifact paths to the non-empty `*-r1-*` files and added the disagreement artifact.
- Replaced the provider-loop pseudocode with a post-loop return.
- Integrated provider-row verdict logic into the existing `verdict_for()` precedence path instead of creating a parallel precedence function.
- Added explicit #2894 sequencing approval criterion.
- Made provider verdicts explicitly Claude-reference-based on the same machine.
- Split provider installation/presence from repo-tracked runtime file existence.
- Tightened `workflow:gates` to require active local runtime paths (`~/.codex/AGENTS.md`, `~/.hermes/SOUL.md`) in addition to repo runtime text.
- Added tests requiring all 3 providers x 3 capabilities to be emitted by `collect-equality.sh --stdout`.
- Added tests that static repo runtime files alone cannot mark a provider installed.
- Added a Windows dependency-safety test and acceptance criterion so the provider helper cannot silently rely on non-stdlib Python packages unavailable to the Windows collector.

---

## Risks and Open Questions

- **Risk:** `build-equality-matrix.py` is already central. Provider-harness row parsing and verdict logic should live in a small helper where possible, with renderer integration kept narrow.
- **Risk:** Capability predicates can become too broad. The v1 implementation should only ship `memory:read`, `skills:invoke`, and `workflow:gates`; shell-context evidence can support reason codes but must not expand the row set.
- **Risk:** Expected divergence can hide defects. It must require allowlisted reasons and non-empty evidence.
- **Risk:** Local home-state inspection can leak auth details. The helper must inspect metadata/counts and repo runtime text only, never token-bearing auth files.
- **Risk:** The Windows collector currently runs the shell collector through a bare `python` path rather than `uv`. The provider helper must stay stdlib-only or carry a tested Windows-safe invocation path.
- **Open:** Whether the missing `.claude/rules/security.md` should become a separate follow-up issue. Recommendation: do not repair it in #2889; keep #2889 focused on provider-harness parity and enforce the security baseline through tests plus `scripts/legal/legal-sanity-scan.sh`.
- **Open:** Whether `/mnt/dde` vs `/mnt/local-analysis` ace-linux-2 repo-root divergence should become a separate acceptance criterion under [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755). Recommendation: measure it here only as evidence; remediate through #2755.

---

## Complexity: T2

**T2** - focused harness extension across a shell collector, Windows companion contract, Python renderer/helper, fixtures, and tests. The work is multi-file and correctness-sensitive, but it is measurement-only and does not require cross-repo writes, provider auth changes, or live machine mutation.
