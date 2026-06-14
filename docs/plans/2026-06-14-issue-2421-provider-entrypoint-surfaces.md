# Plan for #2421: Normalize Workspace-Hub Provider Entrypoint Surfaces

> **Status:** draft-needs-r2-review
> **Complexity:** T2
> **Date:** 2026-06-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2421
> **Client:** N/A
> **Project:**
> **Lane:** lane:claude
> **Review artifacts:** r1: `scripts/review/results/2026-06-14-plan-2421-claude.md`, `scripts/review/results/2026-06-14-plan-2421-codex.md`, `scripts/review/results/2026-06-14-plan-2421-gemini.md`; r2 pending

---

## Resource Intelligence Summary

### Existing repo code

- Current root `AGENTS.md` is the canonical workflow entrypoint and already references `config/agents/SHARED_SOUL.md`, plan-first issue gates, TDD, AI review policy, and model-release readiness. It is exactly 20 lines, so implementation must replace or extend an existing line without adding a new line.
- Current root `CLAUDE.md` is a thin adapter and already points to `AGENTS.md`, `config/agents/claude/SOUL.runtime.md`, `.claude/rules/`, and `issue-planning-mode`.
- Current root `GEMINI.md` is a thin adapter but still points to `docs/work-queue-workflow.md` as a current workflow/gate-evidence surface and carries direct Gemini invocation guidance that diverges from the repo's review wrapper.
- Current `.codex/CODEX.md` is a Codex adapter but still references Codex delta required gates using `WRK-* mapping` wording.
- Current `.gemini/GEMINI.md` is a Gemini adapter but still requires every task to map to `WRK-*` / `.claude/work-queue/` and references deleted work-queue lifecycle skills.
- Current `config/agents/codex/SOUL.delta.md` is the source for generated Codex runtime artifacts and still contains active required-gate references to `WRK-*`, `.claude/work-queue/`, `work-queue-workflow`, and `workflow-gatepass`.
- Current `config/agents/codex/SOUL.runtime.md` and `config/agents/codex/AGENTS.runtime.md` preserve the same stale Codex delta guidance because `scripts/agents/build-soul-runtime.sh` regenerates them from `SOUL.delta.md`.
- Current `tests/helpers/stale_reference_docs.py` already defines banned stale-reference patterns for `.claude/work-queue/`, deleted `work-queue-workflow` skill, and deleted `workflow-gatepass` skill.
- Current `tests/docs/test_banned_stale_references.py` already runs those stale-reference patterns against a `STRICT_FILES` allowlist, but that allowlist does not include `.codex/CODEX.md`, `.gemini/GEMINI.md`, or Codex delta/runtime files.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane contract | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` defines `AGENTS.md` as canonical and provider directories as adapters, not alternatives. |
| Model-release readiness | applicable | `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` scopes provider-entrypoint shape normalization out to a follow-up and requires canonical anchors for discoverability. |
| AI review routing | applicable | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` keeps new workflow logic in `.claude/` skills/rules/hooks with thin `.codex/` and `.gemini/` adapters. |
| Harness file size | applicable | `.claude/rules/coding-style.md` limits `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, and `GEMINI.md` to 20 lines. |
| Existing stale-reference enforcement | applicable | `tests/helpers/stale_reference_docs.py` + `tests/docs/test_banned_stale_references.py` are the existing mechanism to extend, not duplicate. |
| Issue planning gate | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` requires plan, adversarial review, and user approval before implementation. |

### LLM Wiki pages consulted

- No LLM wiki pages apply. This issue is workspace-hub harness/control-plane normalization and will not touch wiki content.

### Documents consulted

- [#2421](https://github.com/vamseeachanta/workspace-hub/issues/2421) defines provider-entrypoint normalization scope: root and hidden provider surfaces, canonical vs secondary topology, and anchor consistency.
- [#2421 comment](https://github.com/vamseeachanta/workspace-hub/issues/2421#issuecomment-4481368731) asks implementers to maintain `implementation-notes.html` with design decisions, deviations, tradeoffs, and open questions.
- [#2447](https://github.com/vamseeachanta/workspace-hub/issues/2447) defines two overlapping residual gaps: `.codex/CODEX.md` legacy WRK reference and `GEMINI.md` deprecated workflow pointer.
- [llm-wiki #684](https://github.com/vamseeachanta/llm-wiki/pull/684) merged the existing ASCP artifact at `llm-wiki/coordination/AGENT_SESSION_PROTOCOL.md` and left a workspace-hub provider-pointer follow-up. This plan will add pointers to that existing protocol; it will not fork or re-author the protocol as a new workspace-hub standard.
- `docs/plans/2026-06-10-issue-2889-provider-harness-parity.md` records current provider-runtime evidence and the relationship between `AGENTS.md`, provider runtime artifacts, and local runtime symlinks.
- `config/agents/README.md` defines source vs generated provider config files and says runtime artifacts are built outputs, not hand-edit surfaces.
- `tests/docs/test_stage_transition_reference_confinement.py` already scans `.gemini/**/*.md`; Gemini adapter edits must preserve that test.
- `tests/docs/test_workspace_hub_model_release_readiness.py` constrains `CONTROL_PLANE_CONTRACT.md` and readiness-contract text; topology edits must preserve those assertions.
- `scripts/review/plan-review-fanout.sh` is the canonical plan-review invocation wrapper and currently uses `gemini -p` from `/tmp`; root `GEMINI.md` should avoid hardcoding a conflicting direct invocation and point at the wrapper/policy instead.

### Gaps identified

- There is no single provider-entrypoint topology section that lists canonical, adapter, source, runtime, and local symlink surfaces in one place.
- Root `GEMINI.md` still advertises `docs/work-queue-workflow.md` as current workflow evidence.
- `.gemini/GEMINI.md`, `.codex/CODEX.md`, `config/agents/codex/SOUL.delta.md`, and generated Codex runtimes still carry active stale WRK/work-queue guidance.
- The existing stale-reference test helper can catch some of this drift, but its `STRICT_FILES` list does not include the affected provider adapter/delta/runtime files.
- There is no targeted current-workflow-anchor test for active provider adapters.
- The llm-wiki ASCP protocol is not discoverable from workspace-hub provider entrypoints even though [llm-wiki #684](https://github.com/vamseeachanta/llm-wiki/pull/684) explicitly left that follow-up.

### Evidence

**Issue statuses** (verified 2026-06-14T15:29:57Z):

- [#2421](https://github.com/vamseeachanta/workspace-hub/issues/2421) — OPEN — labels include `dispatch:ready`, `cat:harness`, `lane:claude`; no `status:plan-approved`.
- [#2447](https://github.com/vamseeachanta/workspace-hub/issues/2447) — OPEN — residual Codex/Gemini onboarding-surface cleanup.
- [llm-wiki #684](https://github.com/vamseeachanta/llm-wiki/pull/684) — MERGED 2026-06-14 — existing ASCP protocol/helper landed in llm-wiki.

**File existence** (`find . -maxdepth 3 ...`, verified 2026-06-14T15:29:57Z):

- EXISTS: `AGENTS.md`
- EXISTS: `CLAUDE.md`
- EXISTS: `GEMINI.md`
- EXISTS: `.claude/global/CLAUDE.md`
- EXISTS: `.codex/CODEX.md`
- EXISTS: `.gemini/GEMINI.md`
- EXISTS: `config/agents/SHARED_SOUL.md`
- EXISTS: `config/agents/codex/SOUL.delta.md`
- EXISTS: `config/agents/codex/SOUL.runtime.md`
- EXISTS: `config/agents/codex/AGENTS.runtime.md`
- EXISTS: `tests/helpers/stale_reference_docs.py`
- EXISTS: `tests/docs/test_banned_stale_references.py`
- EXISTS: `scripts/agents/build-soul-runtime.sh`
- EXISTS: `scripts/agents/install-soul-runtime.sh`
- MISSING (new): `tests/docs/test_provider_entrypoint_surfaces.py`
- MISSING (new): `docs/reports/2026-06-14-issue-2421-implementation-notes.html`

**Line excerpts**:

`AGENTS.md` is at the line cap and has a candidate line to update in place:

```markdown
- Parallelization never bypasses gates: planning/review/recon may run in parallel; implementation requires `status:plan-approved` and TDD; write-capable parallel lanes require isolated worktrees, explicit owned/read-only/forbidden paths, orchestrator verification, and serialized commit/push/closeout.
```

`GEMINI.md` currently points to deprecated workflow anchors:

```markdown
- Current workflow surface: `AGENTS.md`, `docs/work-queue-workflow.md`, `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`, and `.gemini/`
- Gate evidence: use current workflow anchors in `AGENTS.md`, `docs/work-queue-workflow.md`, and `docs/governance/SESSION-GOVERNANCE.md`
```

`.gemini/GEMINI.md` currently carries WRK/work-queue gates:

```markdown
1. Every task maps to WRK-* in `.claude/work-queue/`
4. Workflow lifecycle skills are mandatory: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` + `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
```

`tests/helpers/stale_reference_docs.py` already has reusable stale-reference patterns:

```python
("legacy local work-queue path", re.compile(r"\.claude/work-queue/")),
("deleted legacy work-queue workflow skill", re.compile(r"\.claude/skills/workspace-hub/work-queue-workflow/SKILL\.md")),
("deleted legacy workflow gatepass skill", re.compile(r"\.claude/skills/workspace-hub/workflow-gatepass/SKILL\.md")),
```

`docs/standards/CONTROL_PLANE_CONTRACT.md` defines adapter boundaries:

```markdown
**`AGENTS.md`** is the canonical entry point for every repository.
Provider-specific configuration lives in dedicated directories. These are **adapters**, not alternatives to `AGENTS.md`.
```

`config/agents/README.md` defines generated runtime artifacts:

```markdown
| `<provider>/SOUL.runtime.md`, `codex/AGENTS.runtime.md` | built artifacts (`scripts/agents/build-soul-runtime.sh`) | **never** |
```

**Gap proofs**:

```text
$ rg -n -- "work-queue-workflow.md|WRK-|\\.claude/work-queue|work-queue-workflow/SKILL|workflow-gatepass/SKILL" AGENTS.md CLAUDE.md GEMINI.md .codex/CODEX.md .gemini/GEMINI.md config/agents/codex/SOUL.delta.md config/agents/codex/AGENTS.runtime.md config/agents/codex/SOUL.runtime.md
config/agents/codex/SOUL.runtime.md:161:- Codex review iteration cap: 3 per WRK/non-WRK plan; ...
config/agents/codex/SOUL.runtime.md:181:1. **Every implementation task maps to a WRK-* in `.claude/work-queue/`** OR a GitHub issue ...
config/agents/codex/SOUL.runtime.md:182:2. **Workflow lifecycle skills are mandatory**: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` + `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` ...
config/agents/codex/SOUL.delta.md:40:- Codex review iteration cap: 3 per WRK/non-WRK plan; ...
config/agents/codex/SOUL.delta.md:60:1. **Every implementation task maps to a WRK-* in `.claude/work-queue/`** OR a GitHub issue ...
config/agents/codex/SOUL.delta.md:61:2. **Workflow lifecycle skills are mandatory**: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` + `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` ...
config/agents/codex/AGENTS.runtime.md:161:- Codex review iteration cap: 3 per WRK/non-WRK plan; ...
config/agents/codex/AGENTS.runtime.md:181:1. **Every implementation task maps to a WRK-* in `.claude/work-queue/`** OR a GitHub issue ...
config/agents/codex/AGENTS.runtime.md:182:2. **Workflow lifecycle skills are mandatory**: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` + `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` ...
.codex/CODEX.md:6:... Codex-specific extensions ... (WRK-* mapping, workflow lifecycle skills, ...)
GEMINI.md:5:- Current workflow surface: `AGENTS.md`, `docs/work-queue-workflow.md`, ...
GEMINI.md:7:- Gate evidence: use current workflow anchors in `AGENTS.md`, `docs/work-queue-workflow.md`, ...
.gemini/GEMINI.md:6:1. Every task maps to WRK-* in `.claude/work-queue/`
.gemini/GEMINI.md:9:4. Workflow lifecycle skills are mandatory: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` + `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
```

**Reproduction proofs**:

N/A — this is governance/harness documentation normalization, not a reported runtime failure.

Distinct source count: 15 ([#2421](https://github.com/vamseeachanta/workspace-hub/issues/2421), [#2447](https://github.com/vamseeachanta/workspace-hub/issues/2447), [llm-wiki #684](https://github.com/vamseeachanta/llm-wiki/pull/684), `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `.gemini/GEMINI.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md`, `config/agents/README.md`, `scripts/agents/build-soul-runtime.sh`, `tests/helpers/stale_reference_docs.py`, `tests/docs/test_banned_stale_references.py`, `tests/docs/test_workspace_hub_model_release_readiness.py`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-14-issue-2421-provider-entrypoint-surfaces.md` |
| Plan index | `docs/plans/README.md` |
| Existing stale-reference helper | `tests/helpers/stale_reference_docs.py` |
| Existing stale-reference test | `tests/docs/test_banned_stale_references.py` |
| New entrypoint topology tests | `tests/docs/test_provider_entrypoint_surfaces.py` |
| Canonical contract update | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Claude adapter | `CLAUDE.md` |
| Gemini root adapter | `GEMINI.md` |
| Gemini hidden adapter | `.gemini/GEMINI.md` |
| Codex adapter | `.codex/CODEX.md` |
| Codex delta source | `config/agents/codex/SOUL.delta.md` |
| Generated runtime outputs | `config/agents/codex/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md` |
| Implementation notes | `docs/reports/2026-06-14-issue-2421-implementation-notes.html` |
| Plan review — Claude r1 | `scripts/review/results/2026-06-14-plan-2421-claude.md` |
| Plan review — Codex r1 | `scripts/review/results/2026-06-14-plan-2421-codex.md` |
| Plan review — Gemini r1 | `scripts/review/results/2026-06-14-plan-2421-gemini.md` |

---

## Deliverable

Workspace-hub will have a tested provider-entrypoint topology where active Claude, Codex, and Gemini adapter surfaces point to `AGENTS.md`, current issue-planning gates, generated runtime artifacts, and the existing llm-wiki ASCP protocol without deprecated WRK/work-queue active guidance.

---

## Pseudocode

```text
extend_existing_stale_reference_enrollment:
    add .codex/CODEX.md, .gemini/GEMINI.md, config/agents/codex/SOUL.delta.md,
        config/agents/codex/SOUL.runtime.md, config/agents/codex/AGENTS.runtime.md
        to the existing STRICT_FILES list
    run existing scan_stale_reference_hits against those paths
    verify deleted work-queue skills and .claude/work-queue paths are caught

test_active_provider_entrypoints_avoid_deprecated_workflow_doc_anchor:
    for active root/hidden adapter files:
        assert "docs/work-queue-workflow.md" is absent
    keep docs/work-queue-workflow.md itself as retained legacy/compatibility docs

test_provider_entrypoints_reference_current_workflow_anchors:
    for each active adapter file:
        assert "AGENTS.md" is present
    assert GEMINI.md references docs/plans/README.md or issue-planning-mode
    assert .gemini/GEMINI.md references issue-planning-mode
    assert .codex/CODEX.md references config/agents/codex/AGENTS.runtime.md

test_control_plane_contract_documents_entrypoint_topology:
    read docs/standards/CONTROL_PLANE_CONTRACT.md
    assert table names canonical, adapter, source, runtime, and local symlink surfaces
    assert llm-wiki ASCP protocol is cited as repo-local concurrency precedent

test_agents_line_budget_and_concurrency_pointer:
    read AGENTS.md
    assert line count remains <= 20
    assert existing "Parallelization never bypasses gates" line now mentions claim/coordination for contested work
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `tests/docs/test_banned_stale_references.py` | Enroll `.codex/CODEX.md`, `.gemini/GEMINI.md`, and Codex delta/runtime files in the existing stale-reference scanner. |
| Create | `tests/docs/test_provider_entrypoint_surfaces.py` | Add targeted topology/current-anchor tests not covered by the stale-reference helper. |
| Modify | `docs/standards/CONTROL_PLANE_CONTRACT.md` | Add canonical vs adapter vs generated runtime topology and cite llm-wiki ASCP as the current repo-local coordination precedent. |
| Modify | `AGENTS.md` | Update the existing "Parallelization never bypasses gates" policy line in place to mention claim/coordination for contested work while staying at 20 lines. |
| Modify | `GEMINI.md` | Replace deprecated work-queue workflow anchors with current issue-planning/review-wrapper anchors and the llm-wiki ASCP pointer. |
| Modify | `.gemini/GEMINI.md` | Replace WRK/work-queue gates with GitHub issue planning, TDD, review, legal/security, and current workflow anchors. |
| Modify | `.codex/CODEX.md` | Remove legacy `WRK-* mapping` wording and point to GitHub issues plus Codex runtime source. |
| Modify | `config/agents/codex/SOUL.delta.md` | Replace active WRK/work-queue required gates while preserving review-iteration cap semantics in provider-neutral terms. |
| Regenerate | `config/agents/codex/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md` | Built outputs from `scripts/agents/build-soul-runtime.sh` after Codex delta changes. |
| Create | `docs/reports/2026-06-14-issue-2421-implementation-notes.html` | User-requested running implementation notes with design decisions, deviations, tradeoffs, and open questions. |
| Modify | `docs/plans/README.md` | Add this plan to the issue-plan index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_existing_stale_reference_scanner_covers_provider_adapters` | Existing stale-reference scanner is extended rather than duplicated. | `tests/docs/test_banned_stale_references.py::STRICT_FILES` | Includes `.codex/CODEX.md`, `.gemini/GEMINI.md`, `config/agents/codex/SOUL.delta.md`, `config/agents/codex/SOUL.runtime.md`, and `config/agents/codex/AGENTS.runtime.md`. |
| `test_active_provider_entrypoints_avoid_deprecated_workflow_doc_anchor` | Active adapters no longer advertise `docs/work-queue-workflow.md` as current guidance while the legacy doc itself remains allowed. | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `.gemini/GEMINI.md` | No active adapter contains `docs/work-queue-workflow.md`. |
| `test_active_provider_entrypoints_reference_current_workflow_anchors` | Active adapters point at current canonical workflow surfaces. | Same active adapter set | Each references `AGENTS.md`; Gemini/Codex adapters reference `docs/plans/README.md` or `issue-planning-mode` as appropriate. |
| `test_control_plane_contract_documents_topology` | Control-plane contract explicitly distinguishes canonical entrypoints, adapters, source deltas, generated runtimes, and local symlinks. | `docs/standards/CONTROL_PLANE_CONTRACT.md` | Required topology terms and file paths are present. |
| `test_agents_line_budget_and_contested_work_pointer` | `AGENTS.md` stays within line budget and carries the contested-work coordination pointer by modifying an existing line. | `AGENTS.md` | `<= 20` lines and the "Parallelization never bypasses gates" line mentions claim/coordination. |
| `test_codex_runtime_regenerated_from_delta` | Codex built runtimes reflect updated source delta and do not preserve active stale required gates. | `config/agents/codex/SOUL.delta.md`, `config/agents/codex/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md` | Required-gate sections reference GitHub issues/current lifecycle skills and not `.claude/work-queue/`, deleted work-queue skills, or active `WRK-* mapping`. |

---

## Acceptance Criteria

- [ ] Red tests fail before edits: `uv run pytest tests/docs/test_provider_entrypoint_surfaces.py tests/docs/test_banned_stale_references.py -q`.
- [ ] Existing stale-reference scanner is reused by adding provider adapter/delta/runtime paths to `STRICT_FILES`.
- [ ] `docs/standards/CONTROL_PLANE_CONTRACT.md` explicitly lists canonical, adapter, source, generated runtime, and local symlink surfaces.
- [ ] `AGENTS.md` remains `<= 20` lines and its existing parallelization policy line mentions claim/coordination for contested work.
- [ ] `GEMINI.md`, `.gemini/GEMINI.md`, `.codex/CODEX.md`, `config/agents/codex/SOUL.delta.md`, `config/agents/codex/SOUL.runtime.md`, and `config/agents/codex/AGENTS.runtime.md` no longer use `.claude/work-queue/`, deleted work-queue skills, or `docs/work-queue-workflow.md` as active guidance.
- [ ] Codex review-iteration-cap semantics are preserved without `WRK-* mapping` as an active required gate.
- [ ] Root `GEMINI.md` points at the repo's review policy/wrapper rather than hardcoding a conflicting direct Gemini command.
- [ ] `docs/reports/2026-06-14-issue-2421-implementation-notes.html` records design decisions, deviations, tradeoffs, and open questions.
- [ ] Targeted tests pass: `uv run pytest tests/docs/test_provider_entrypoint_surfaces.py tests/docs/test_banned_stale_references.py -q`.
- [ ] Existing constrained docs tests pass: `uv run pytest tests/docs/test_workspace_hub_model_release_readiness.py tests/docs/test_stage_transition_reference_confinement.py tests/docs/test_work_queue_policy_consistency.py -q`.
- [ ] Runtime drift check passes: `bash scripts/enforcement/check-soul-runtime-drift.sh`.
- [ ] Legal/security scan passes: `bash scripts/legal/legal-sanity-scan.sh --diff-only`.
- [ ] Adversarial plan review artifacts exist for r2 with no MAJOR findings, or provider unavailability is documented and remaining reviews have no blockers.
- [ ] Implementation remains blocked until the user applies `status:plan-approved` to [#2421](https://github.com/vamseeachanta/workspace-hub/issues/2421).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | Reuse existing stale-reference helper; correct grep evidence; descope new ASCP standard; resolve AGENTS line-budget conflict; preserve Codex iteration-cap semantics. |
| Codex r1 | MAJOR | Resolve ASCP authority/path decision; include generated Codex runtimes in stale-anchor contract; do not treat unavailable/empty artifacts as approval evidence; review Gemini command inconsistency. |
| Gemini r1 | UNAVAILABLE | Gemini CLI failed before returning a usable review. |

**Overall result:** FAIL — r1 MAJOR findings require this revised plan and fresh r2 review before `status:plan-review`.

Revisions made based on review:
- Replaced the proposed duplicate stale-reference test with an extension of `tests/docs/test_banned_stale_references.py`.
- Removed the proposed new workspace-hub ASCP standard and changed scope to pointer-only discoverability for the existing llm-wiki ASCP artifact.
- Added generated Codex runtime outputs to the stale-anchor contract.
- Specified that `AGENTS.md` will update the existing parallelization policy line in place.
- Corrected the gap-proof output to include all actual matches.
- Added review-wrapper/Gemini invocation consistency to scope.

---

## Risks and Open Questions

- **Risk:** Rewriting adapter files may exceed the 20-line harness budget. The plan will update existing lines rather than append lines, with an explicit line-count test.
- **Risk:** Codex runtime artifacts are generated. The implementation must edit `config/agents/codex/SOUL.delta.md` first, then rebuild runtimes, rather than hand-edit generated files.
- **Risk:** A broad `WRK-*` purge could remove legitimate review-iteration-cap context. The implementation must preserve the cap semantics in provider-neutral terms instead of deleting the mechanism.
- **Risk:** The existing llm-wiki ASCP artifact may later move into workspace-hub. This plan only adds pointers to the existing artifact; any ownership transfer should be a separate issue or explicit user decision.
- **Open:** Whether [#2447](https://github.com/vamseeachanta/workspace-hub/issues/2447) should close as subsumed once [#2421](https://github.com/vamseeachanta/workspace-hub/issues/2421) lands, or remain open for separate historical cleanup notes.

---

## Complexity: T2

This is a multi-file harness/documentation normalization with targeted tests and generated runtime outputs. It does not require cross-repo code changes or runtime behavior changes beyond provider-entrypoint guidance, so T2 is sufficient.
