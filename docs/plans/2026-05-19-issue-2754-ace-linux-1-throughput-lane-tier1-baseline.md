# Plan for #2754: throughput(workstations): activate ace-linux-1 provider/machine lane

> **Status:** draft — r1 adversarial review returned MAJOR; patched locally and awaiting re-review
> **Complexity:** T2
> **Date:** 2026-05-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2754
> **Review artifacts:** scripts/review/results/2026-05-19-plan-2754-claude.md | scripts/review/results/2026-05-19-plan-2754-codex.md | scripts/review/results/2026-05-19-plan-2754-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/readiness/telegram-hermes-readiness.sh` — thin shell wrapper for the real readiness implementation. It must remain callable but is not the primary integration target.
- Found: `scripts/readiness/telegram_hermes_readiness.py` — primary readiness implementation; it reads `config/workstations/registry.yaml`, computes host failures/warnings, and controls `dispatchable`. Tier-1 baseline failures must be wired here, not only in the wrapper.
- Found: `config/workstations/registry.yaml` — single source of truth for workstation identity/capability data. It names `dev-primary` as `hostname: ace-linux-1`, `role: primary-dev`, `telegram_mode: coordinator`, and `workspace_root: /mnt/local-analysis/workspace-hub`.
- Adjacent residue: `docs/plans/machine-prompts/2026-05-19/ace-linux-1-control-plane-dispatch-ledger.md` may exist in local dirty state, but it is not committed authority and this plan will not depend on it.
- Gap: `config/workstations/registry.yaml` lacks explicit required/on-demand tier-1 repo semantics, primary/reference checkout roles, and `/mnt/ace` constraints for ace-linux-1. This plan will extend the registry rather than create a competing machine truth source.
- Gap: no narrow validator exists that can compare the ace-linux-1 tier-1 baseline against observed live checkout placement without moving/cloning/deleting anything.

### Standards

Not applicable as engineering-calculation standards. Relevant governance standards are workflow/repo-location standards:

| Governance source | Status | Source |
|---|---|---|
| Issue planning workflow | applicable | `docs/plans/README.md` requires canonical plan artifact, README row, adversarial review, and user approval before implementation. |
| Repo/data location planning principle | applicable | Memory and `AGENTS.md` require repo placement changes under `/mnt/local-analysis` to be issue/plan driven, not ad-hoc moves; this plan enumerates live checkout state and explicitly forbids clone/move/delete/sync actions. |
| Parallel-first execution standard | applicable | `docs/standards/PARALLEL_FIRST_EXECUTION.md` requires non-trivial work to classify execution mode and not bypass issue/plan/approval/TDD gates. |

### LLM Wiki pages consulted

- N/A — this issue is workstation orchestration / repo placement governance, not a domain knowledge extraction issue. `llm-wiki` is itself one of the tier-1 repo placement decisions.

### Documents and issues consulted

- Issue [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754) — live body frames ace-linux-1 as a throughput lane; canonical infrastructure is assumed; no repo moves/deletes/sync rewrites are authorized unless separately planned and approved.
- Issue [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738) — ace-linux-1 Telegram dispatch coordinator hardening is already `status:plan-approved` and is the best first useful work route once readiness gates pass.
- Issue [#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758) — agent/runtime folder architecture contract will define broader folder authority; this plan must not preempt that architecture contract.
- Issue [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) — data/repo location contract planning exists separately and includes `/mnt/ace` / llm-wiki promotion concerns.
- Issue comments on [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754) — user decision captured that ace-linux-1 required tier-1 baseline is `workspace-hub`, `digitalmodel`, `assetutilities`, `llm-wiki`, and `worldenergydata`; `worldenergydata` must be on ace-linux-1 because it needs `/mnt/ace` data access unless a separate design reproduces that access elsewhere.

### Gaps identified

- A durable ace-linux-1 tier-1 baseline file must be created from the user decision: required vs optional/on-demand repos, path roles, and constraints.
- A read-only checker/test must be added so dispatch readiness can fail visibly when required ace-linux-1 tier-1 repos are missing or in an unauthorized path state.
- The plan must preserve the current live distinction between sibling checkouts (`/mnt/local-analysis/digitalmodel`, `/mnt/local-analysis/assetutilities`) and nested checkouts under `/mnt/local-analysis/workspace-hub/` without moving anything inline.
- The first dispatch target must be linked explicitly, and current readiness blockers must be kept separate from repo placement decisions.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-19T21:17:49-05:00 via `gh issue view`):

```json
{"number":2738,"state":"OPEN","title":"feat(hermes): harden ace-linux-1 Telegram gateway as dispatch coordinator","labels":["status:plan-approved", "machine:ace-linux-1"]}
{"number":2754,"state":"OPEN","title":"throughput(workstations): activate ace-linux-1 provider/machine lane","labels":["status:needs-plan", "machine:ace-linux-1", "cat:ai-orchestration", "cat:operations"]}
{"number":2758,"state":"OPEN","title":"Clarify agent/runtime folder architecture to reduce human and agent confusion","labels":["cat:developer-experience", "domain:repo-organization"]}
{"number":2731,"state":"OPEN","title":"feat(data-governance): inventory and normalize canonical data/repo locations for llm-wiki promotion","labels":["cat:data-pipeline", "cat:document-intelligence", "domain:knowledge"]}
```

**Live ace-linux-1 tier-1 checkout inventory** (verified 2026-05-19T21:17:49-05:00):

```text
workspace-hub	/mnt/local-analysis/workspace-hub	git	16	https://github.com/vamseeachanta/workspace-hub.git
digitalmodel	/mnt/local-analysis/digitalmodel	git	0	https://github.com/vamseeachanta/digitalmodel.git
digitalmodel	/mnt/local-analysis/workspace-hub/digitalmodel	git	0	https://github.com/vamseeachanta/digitalmodel.git
assetutilities	/mnt/local-analysis/assetutilities	git	0	https://github.com/vamseeachanta/assetutilities.git
assetutilities	/mnt/local-analysis/workspace-hub/assetutilities	git	0	https://github.com/vamseeachanta/assetutilities
worldenergydata	/mnt/local-analysis/workspace-hub/worldenergydata	git	0	https://github.com/vamseeachanta/worldenergydata.git
llm-wiki	/mnt/local-analysis/workspace-hub/llm-wiki	git	0	https://github.com/vamseeachanta/llm-wiki.git
assethold	/mnt/local-analysis/workspace-hub/assethold	git	0	https://github.com/vamseeachanta/assethold.git
aceengineer-website	/mnt/local-analysis/workspace-hub/aceengineer-website	git	0	https://github.com/vamseeachanta/aceengineer-website.git
aceengineer-strategy	/mnt/local-analysis/workspace-hub/aceengineer-strategy	git	0	https://github.com/vamseeachanta/aceengineer-strategy.git
```

**Top-level `/mnt/local-analysis` inventory** (verified 2026-05-19T21:17:49-05:00):

```text
/mnt/local-analysis first-level dirs:
assetutilities
digitalmodel
workspace-hub

git repos maxdepth2 under /mnt/local-analysis:
/mnt/local-analysis/assetutilities
/mnt/local-analysis/digitalmodel
/mnt/local-analysis/workspace-hub
```

**Alias/data mount state** (verified 2026-05-19T21:17:49-05:00):

```text
alias state:
/mnt/ace
drwxrwxrwx 45 nobody nogroup 4096 May 19 09:46 /mnt/ace
lrwxrwxrwx  1 root   root       8 Mar 13 14:03 /mnt/ace-data -> /mnt/ace
```

**Dispatch readiness probe** (`bash scripts/readiness/telegram-hermes-readiness.sh --host dev-primary`, verified 2026-05-19T21:17:49-05:00):

```json
{
  "overall_status": "fail",
  "hosts": {
    "dev-primary": {
      "hostname": "ace-linux-1",
      "dispatchable": false,
      "failures": [
        "TELEGRAM_ALLOWED_USERS allowlist must be configured",
        "TELEGRAM_BOT_TOKEN bot token env var must be configured",
        "workspace_root has uncommitted or untracked git changes"
      ],
      "workspace_root": "/mnt/local-analysis/workspace-hub",
      "telegram_mode": "coordinator"
    }
  }
}
```

**Reproduction proofs**: N/A — governance/operations planning issue. There is no alleged failing runtime behavior to reproduce beyond the live readiness probe above.

Distinct sources consulted: issue body/comments, live `gh issue view` output, live filesystem/git checkout inventory, `scripts/readiness/telegram-hermes-readiness.sh` output, `scripts/readiness/telegram_hermes_readiness.py`, `config/workstations/registry.yaml`, `docs/plans/README.md`, and `docs/standards/PARALLEL_FIRST_EXECUTION.md`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-19-issue-2754-ace-linux-1-throughput-lane-tier1-baseline.md` |
| Planning index row | `docs/plans/README.md` |
| Workstation registry extension | `config/workstations/registry.yaml` |
| Baseline schema / documentation | `docs/workstations/ace-linux-1-tier1-repo-baseline.md` |
| Read-only baseline checker | `scripts/workstations/check-tier1-repo-baseline.py` |
| Checker tests | `tests/workstations/test_check_tier1_repo_baseline.py` |
| Readiness integration test | `tests/readiness/test_telegram_hermes_readiness_tier1_baseline.py` |
| Plan review — Claude | `scripts/review/results/2026-05-19-plan-2754-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-19-plan-2754-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-19-plan-2754-gemini.md` |

---

## Deliverable

A repo-tracked ace-linux-1 workstation baseline will extend the existing workstation registry to define the machine's throughput role, required/on-demand tier-1 repos, primary/reference checkout roles, `/mnt/ace` constraint for `worldenergydata`, readiness gating, and first approved dispatch target without moving, cloning, deleting, or sync-rewriting repos inline.

---

## Scope Boundaries

### In scope

- Record ace-linux-1 as the control surface + high-context Linux execution lane.
- Record required tier-1 repos for ace-linux-1: `workspace-hub`, `digitalmodel`, `assetutilities`, `llm-wiki`, `worldenergydata`.
- Record optional/on-demand tier-1 repos for ace-linux-1: `assethold`, `aceengineer-website`, `aceengineer-strategy`.
- Record that `worldenergydata` is required on ace-linux-1 because it needs `/mnt/ace` data access unless a separate approved data-access design says otherwise.
- Add read-only validation so missing or misplaced required repos are surfaced as readiness evidence.
- Link the first useful approved dispatch target to [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738).

### Out of scope

- Moving, deleting, cloning, renaming, or syncing any repo during this issue.
- Deciding global folder architecture for all machines; [#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758) owns the broader contract.
- Deciding raw/private/public data promotion or llm-wiki source residency; [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) owns that domain.
- Performing broad repo cleanup or non-tier-1 placement work.
- Marking ace-linux-1 dispatchable while Telegram env gates or dirty workspace gates still fail.

---

## Pseudocode

```text
function load_baseline(registry_path, host):
    parse config/workstations/registry.yaml
    select machines[host] / dev-primary
    require hostname == ace-linux-1
    require repos plus tier1_baseline.required and tier1_baseline.optional are explicit
    require each tier1_baseline repo declares role, expected_path_policy, and dispatch_rationale
    return normalized baseline object from the single workstation registry

function discover_tier1_repos(registry_machine, tier1_repo_names):
    candidate_roots = ordered unique existing directories from:
        dirname(workspace_root), workspace_root, storage.local, each storage.remote_mount, and user-provided extra roots
    for each candidate root and tier1 repo name:
        probe <root>/<repo> and, when root is workspace_root, nested <workspace_root>/<repo>
        if path exists and is git worktree:
            collect path, remote, branch, dirty_count_tracked_only, and whether it is primary/reference/unknown
    return discovery table without mutating filesystem

function validate_baseline(baseline, discovery, mounts):
    for each required repo:
        fail if no discovered checkout exists
        fail if more than one checkout exists and no primary/reference role is declared
        fail if repo has data_mount_required and mount path is missing
    for each optional repo:
        record present/missing but do not fail if missing
        fail if present duplicates lack declared primary/reference roles
    return structured JSON report with failures, warnings, and observed paths

function integrate_with_readiness(host):
    run existing Python Telegram/Hermes readiness checks in scripts/readiness/telegram_hermes_readiness.py
    run tier1 baseline validation for host when tier1_baseline exists in registry
    append baseline failures to host.failures and baseline warnings to host.warnings
    recompute dispatchable=false whenever failures is non-empty
    include malformed checker output, timeout, or checker-missing cases as fail-closed failures
    do not hide existing Telegram env or dirty-worktree failures
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | Extend the existing single workstation truth source with ace-linux-1 required/on-demand tier-1 repo semantics, primary/reference checkout roles, and `/mnt/ace` constraints. |
| Create | `docs/workstations/ace-linux-1-tier1-repo-baseline.md` | Human-readable decision record for the ace-linux-1 baseline and first dispatch route. |
| Create | `scripts/workstations/check-tier1-repo-baseline.py` | Read-only validation of baseline vs observed live checkout state; no moves/clones/deletes. |
| Create | `tests/workstations/test_check_tier1_repo_baseline.py` | TDD coverage for required/optional repo validation, duplicate checkout warnings, and `/mnt/ace` requirement. |
| Modify | `scripts/readiness/telegram_hermes_readiness.py` | Include baseline checker output in dispatch readiness for `dev-primary`, append failures/warnings to the existing JSON schema, and recompute `dispatchable` fail-closed without weakening existing gates. |
| Verify/no-op | `scripts/readiness/telegram-hermes-readiness.sh` | Keep wrapper compatibility; change only if needed to expose an existing Python CLI option. |
| Create/modify | `tests/readiness/test_telegram_hermes_readiness_tier1_baseline.py` | Prove readiness fails when required baseline repos are absent and preserves existing Telegram/dirty failures. |
| Update | `docs/plans/README.md` | Add this plan to the canonical issue-plan index. |
| Post comment | [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754) | Link final plan/review summary and later record the first approved dispatch artifact. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_required_repos_must_be_present` | Missing required ace-linux-1 tier-1 repos fail validation. | Baseline requiring `worldenergydata`; discovery omits it. | Non-zero failure with repo name and no filesystem mutation. |
| `test_optional_repos_do_not_fail_when_missing` | Optional/on-demand repos are reported but do not block dispatch. | Baseline optional `assethold`; discovery omits it. | Success or warning-only result. |
| `test_worldenergydata_requires_mnt_ace` | `worldenergydata` baseline encodes `/mnt/ace` dependency. | Baseline declares `data_mount_required: /mnt/ace`; mount probe missing. | Failure naming `/mnt/ace`. |
| `test_duplicate_checkout_requires_primary_role_failure` | Duplicate `digitalmodel` / `assetutilities` checkouts are fail-closed unless primary/reference roles are declared. | Discovery has sibling and nested paths with no role declaration. | Failure lists both paths and refuses to choose silently. |
| `test_declared_primary_reference_duplicates_pass` | Duplicate checkouts become valid only when the registry declares primary/reference roles. | Discovery has sibling and nested paths; registry names one primary and one reference. | Success with observed paths retained in evidence. |
| `test_readonly_checker_does_not_mutate_paths` | Checker never runs clone/move/delete/sync operations. | Fake repos plus monkeypatched dangerous functions (`os.remove`, `shutil.rmtree`, write/open modes) and subprocess allowlist. | Only read-only git/path probes are invoked; destructive calls fail the test. |
| `test_readiness_includes_tier1_baseline_failures` | Existing Python readiness collector incorporates baseline failures. | Stub checker returns missing required repo. | `dispatchable=false` and failure appears alongside existing gates. |
| `test_readiness_preserves_existing_gate_failures` | Baseline integration does not mask Telegram env or dirty workspace failures. | Stub existing readiness failures + passing baseline. | Existing failure strings remain present. |
| `test_readiness_fail_closed_on_checker_error` | Checker crash, timeout, malformed JSON, or missing checker blocks dispatch. | Stub checker non-zero/timeout/bad output. | Host failure states baseline checker error and `dispatchable=false`. |

---

## Acceptance Criteria

- [ ] `config/workstations/registry.yaml` records ace-linux-1 (`dev-primary`) tier-1 baseline as `control-surface + high-context-linux-execution-lane` without creating a second machine truth source.
- [ ] Required repo list is exactly: `workspace-hub`, `digitalmodel`, `assetutilities`, `llm-wiki`, `worldenergydata`.
- [ ] Optional/on-demand repo list is exactly: `assethold`, `aceengineer-website`, `aceengineer-strategy`.
- [ ] `worldenergydata` includes an explicit `/mnt/ace` data-access constraint and a note that moving it elsewhere requires a separate approved data-access design.
- [ ] The read-only checker validates required vs optional repos without performing clone/move/delete/sync operations.
- [ ] The checker surfaces duplicate sibling/nested checkouts as fail-closed until primary/reference roles are declared, not as cleanup targets.
- [ ] `scripts/readiness/telegram-hermes-readiness.sh --host dev-primary` includes tier-1 baseline evidence from the Python readiness collector and still fails closed on Telegram env, checker errors, or dirty workspace state.
- [ ] Tests pass: `uv run pytest tests/workstations/test_check_tier1_repo_baseline.py tests/readiness/test_telegram_hermes_readiness_tier1_baseline.py -v`.
- [ ] Legal/security scan passes: `scripts/legal/legal-sanity-scan.sh`.
- [ ] The first approved dispatch target is linked as [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738), and the issue comment records the concrete artifact produced once dispatch is attempted after readiness passes.
- [ ] No repo is moved, deleted, cloned, renamed, or sync-rewritten by this issue.
- [ ] Plan review artifacts are saved under `scripts/review/results/` before this issue moves to `status:plan-review`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | Fanout timed out before a usable Claude review was produced; `scripts/review/results/2026-05-19-plan-2754-claude.md` records the timeout/unavailability. |
| Codex | MAJOR | Real blockers: wrong registry path, missing repo-location reference, competing baseline truth source, wrong readiness integration target, weak fail-closed/readiness tests, and issue acceptance mismatch. |
| Gemini | MAJOR | Real blockers: missing/incorrect cited paths, brittle discovery roots, duplicate checkout warnings not fail-closed, unsafe bash parsing/readiness integration, and weak read-only proof. Some path findings were stale/false after local verification, but the plan still needed correction. |

**Overall result:** MAJOR — this draft is not approval-ready. The corrections below have been applied locally and require re-review before `status:plan-review`.

Revisions made based on review:
- Replaced the non-existent `config/machines/telegram-hermes-machines.yaml` authority with `config/workstations/registry.yaml`.
- Removed reliance on the missing repo-location planning reference and restated the live issue/plan/no-move governance directly.
- Changed the implementation target from a separate `ace-linux-1-tier1-repos.yaml` file to an extension of the existing workstation registry single source of truth.
- Added `scripts/readiness/telegram_hermes_readiness.py` as the actual readiness integration target and kept the shell wrapper as compatibility/no-op.
- Made duplicate checkout ambiguity fail-closed unless primary/reference roles are declared.
- Added checker crash/timeout/malformed-output fail-closed tests and stronger read-only mutation guards.

---

## Risks and Open Questions

- **Risk:** The live filesystem currently shows duplicate `digitalmodel` and `assetutilities` checkouts at sibling and nested paths. This plan will require explicit primary/reference role declarations and will not clean them up inline.
- **Risk:** `workspace-hub` is dirty and readiness currently fails; ace-linux-1 must not be treated as dispatchable until unrelated residue is committed, preserved, or otherwise resolved.
- **Risk:** `llm-wiki` and `worldenergydata` are currently observed as nested checkouts under `workspace-hub`; broader architecture may later move or normalize this after [#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758), but this issue will only record and validate the ace-linux-1 baseline.
- **Risk:** Telegram env gates fail when the readiness script is run without the approved local secret environment. Implementation must not hardcode secrets or weaken the gate.
- **Open:** Should the first dispatch artifact for [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754) be limited to readiness/ledger evidence, or should it include one small execution action under already-approved [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738) after readiness passes?

---

## Complexity: T2

**T2** — governance/operations implementation with multiple repo-tracked artifacts, read-only validation code, readiness integration, and tests. It is not T3 because this issue only defines ace-linux-1's bounded baseline and defers global architecture to [#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758) and data-location policy to [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731).
