# Plan for #3548: Canonical remote Linux access architecture and runbook

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3548
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** single-lane implementation because the runbook and cross-links share one authority contract; parallel-readonly adversarial review and verification
> **Review artifacts:** `scripts/review/results/2026-07-15-plan-3548-{claude,codex,gemini}-r1.md`
> **Human-facing companion:** `docs/reports/2026-07-15-issue-3548-remote-linux-access-plan.html`

---

## Resource Intelligence Summary

### Existing repo code and documentation

- `config/workstations/registry.yaml` declares itself the single source of truth for workstation identity and capability data. Its Linux records currently name `ace-linux-1` and `ace-linux-2` as SSH targets and also contain point-in-time `tailscale_ip` values. The runbook will reference this authority without copying those addresses.
- `docs/ops/ace-linux-2-handoff-runbook.md` provides the closest durable command-oriented precedent. It covers SSH/VNC preflight, handoff boundaries, and evidence return, but its generic remote-access guidance and VNC behavior are narrower and partly stale.
- `docs/ops/machine-inventory.md` already names the workstation registry as canonical for SSH, workspace, and capabilities. It will gain a link to the new runbook rather than duplicate procedures.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` classifies normative operational policy as durable L3 and issues/plans/reviews as execution-bound L5. Therefore, the issue and this plan will not become the operational authority; the new runbook will.
- `docs/setup/README.md` owns bootstrap and audit navigation. It will link to remote access as a post-bootstrap operation rather than absorb the complete runbook.
- `config/tabby/REMOTE_ACCESS.md` and `config/tabby/TAILSCALE_SETUP.md` contain competing point-in-time instructions, duplicated endpoint values, stale helper locations, and public port-forwarding guidance. They will become clearly marked legacy pointers to the canonical runbook.
- `scripts/operations/connection/connect-workspace-linux.sh`, `connect-workspace-tailscale.sh`, `connect-workspace-tailscale.ps1`, and `ssh-dev-secondary.sh` embed conflicting targets or aliases. This plan will document the drift and route executable reconciliation to [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549); it will not modify those scripts.

### Standards and governance

| Contract | Status | Source |
|---|---|---|
| Issue → resource intelligence → plan → adversarial review → user approval → TDD | mandatory | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Normative operational documentation remains durable L3 | active | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` |
| Workstation identity and non-secret connection metadata use one registry authority | active | `config/workstations/registry.yaml` |
| Conventional OpenSSH over Tailscale is canonical; Tailscale SSH is optional | user-approved design | [#3547](https://github.com/vamseeachanta/workspace-hub/issues/3547), [#3548](https://github.com/vamseeachanta/workspace-hub/issues/3548) |
| No client identifiers or secrets enter public artifacts | mandatory | `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml`, `scripts/security/secrets-scan.sh` |
| Technical claims will cite primary sources | mandatory | Tailscale official documentation and OpenBSD `sshd_config(5)` |

### LLM Wiki pages consulted

- No relevant wiki page applies. This issue governs workstation operations, not reusable engineering-domain knowledge.

### Documents and issues consulted

- [#3548](https://github.com/vamseeachanta/workspace-hub/issues/3548) fixes the documentation-only scope, authority hierarchy, architecture, and acceptance criteria.
- [#3547](https://github.com/vamseeachanta/workspace-hub/issues/3547) fixes the four-child sequence, verification matrix, and `ace-linux-2`-before-`ace-linux-1` rollout order.
- [#2646](https://github.com/vamseeachanta/workspace-hub/issues/2646) and `docs/plans/2026-05-13-issue-2646-ace-linux-2-handoff-runbook.md` provide structural precedent, not current connection truth.
- [#318](https://github.com/vamseeachanta/workspace-hub/issues/318), [#316](https://github.com/vamseeachanta/workspace-hub/issues/316), and [#398](https://github.com/vamseeachanta/workspace-hub/issues/398) record historical intent without sufficient current-state evidence; their addresses, aliases, and installed-state claims will remain unverified.
- [#2094](https://github.com/vamseeachanta/workspace-hub/issues/2094), `docs/plans/2026-05-26-issue-2801-machine-equality.md`, and `docs/plans/2026-06-08-issue-2967-epic-consistent-experience-dynamic-workflows.md` establish declared-versus-observed separation and registry reuse.
- Drive-index command `uv run python scripts/data/drive-index-search/search.py "Tailscale SSH remote Linux runbook" --json --limit 20 --caller plan-resource-intel` produces no JSON envelope because `uv` stalls while creating a transient environment. The one-command search allowance is consumed; no drive result or coverage-gap claim will enter this plan.
- Official Tailscale references will include Linux installation, Tailscale SSH limitations, grants, device approval, key expiry, and connection types. OpenSSH hardening options will link to the OpenBSD `sshd_config(5)` manual.

### Gaps identified

- No canonical durable remote-Linux-access runbook exists.
- No documentation-contract test prevents authority drift, endpoint duplication, or resurrection of public port-forwarding advice.
- Existing durable and legacy documents do not consistently route operators to one authority.
- No durable drift ledger assigns each unverified claim to [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549), [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550), or [#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551).
- General headless-GUI guidance conflicts across the existing handoff runbook, VNC helper comments, and transient historical evidence; #3548 will record and route that conflict without changing VNC behavior.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-15T14:49:59Z with `gh issue view`):

- [#3547](https://github.com/vamseeachanta/workspace-hub/issues/3547) — OPEN — `status:needs-plan` — parent architecture and rollout sequence.
- [#3548](https://github.com/vamseeachanta/workspace-hub/issues/3548) — OPEN — `status:needs-plan`, `wip:ace-linux-1`, `lane:claude` — documentation child.
- [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549) — OPEN — `status:needs-plan` — helper/registry reconciliation.
- [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550) — OPEN — `status:needs-plan` — `ace-linux-2` canary rollout.
- [#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551) — OPEN — `status:needs-plan` — `ace-linux-1` rollout.
- [#2646](https://github.com/vamseeachanta/workspace-hub/issues/2646), [#318](https://github.com/vamseeachanta/workspace-hub/issues/318), [#316](https://github.com/vamseeachanta/workspace-hub/issues/316), and [#398](https://github.com/vamseeachanta/workspace-hub/issues/398) — CLOSED — historical evidence only.

**File existence** (verified 2026-07-15T14:49:59Z):

- MISSING: `docs/ops/remote-linux-access.md` — this issue will create it.
- EXISTS: `config/workstations/registry.yaml`.
- EXISTS: `docs/ops/ace-linux-2-handoff-runbook.md`.
- EXISTS: `docs/ops/machine-inventory.md`.
- EXISTS: `docs/setup/README.md` and `docs/README.md`.
- EXISTS: `scripts/legal/legal-sanity-scan.sh`, `scripts/security/secrets-scan.sh`, and `scripts/enforcement/check-no-abs-paths.sh`.

**Line excerpts**:

```text
config/workstations/registry.yaml:1-4
  Single source of truth for all workstations.
  HARD RULE: all machine identity/capability data lives here.

config/workstations/registry.yaml:19-20,185-186
  ssh: ace-linux-1 / tailscale_ip: 10.1.0.1
  ssh: ace-linux-2 / tailscale_ip: 10.1.0.2

scripts/operations/connection/connect-workspace-tailscale.ps1:8
  $WorkspaceHost = "100.107.64.76"

scripts/operations/connection/ssh-dev-secondary.sh:5
  ACE2_ALIAS="dev-secondary"
```

The conflicting literals prove documentation drift; they do not prove which value is live.

**Gap proof**:

```text
$ test -e docs/ops/remote-linux-access.md
exit 1
```

**Reproduction proofs:** N/A — this issue is documentation/governance-only. Runtime validation and live-state attestation belong to [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550) and [#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551).

**Distinct source count:** 12 issue/file/primary-documentation sources, excluding the unavailable drive-index search.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-15-issue-3548-remote-linux-access-runbook.md` |
| Human-facing plan companion | `docs/reports/2026-07-15-issue-3548-remote-linux-access-plan.html` |
| Documentation contract tests | `tests/docs/test_remote_linux_access_contract.py` |
| Canonical runbook | `docs/ops/remote-linux-access.md` |
| Fleet inventory cross-link | `docs/ops/machine-inventory.md` |
| Secondary-host handoff cross-link | `docs/ops/ace-linux-2-handoff-runbook.md` |
| Documentation navigation | `docs/README.md`, `docs/setup/README.md` |
| Legacy Tabby pointers | `config/tabby/REMOTE_ACCESS.md`, `config/tabby/TAILSCALE_SETUP.md` |
| Plan review — Claude | `scripts/review/results/2026-07-15-plan-3548-claude-r1.md` |
| Plan review — Codex | `scripts/review/results/2026-07-15-plan-3548-codex-r1.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-15-plan-3548-gemini-r1.md` |

---

## Deliverable

A tested `docs/ops/remote-linux-access.md` authority that will document secure Tailscale-plus-OpenSSH access, rollout safety, verification, recovery, troubleshooting, and drift ownership while related documents route to it without duplicating endpoint claims.

---

## Design and Pseudocode

```text
load canonical workstation identities from registry references
render topology without copying point-in-time addresses
state Tailscale transport and conventional OpenSSH authentication as separate layers
mark Tailscale SSH optional and direct router forwarding prohibited
order setup so recovery and key access precede SSH hardening
define verification matrix for external-network and post-reboot evidence
for each conflicting claim:
    record source paths
    mark current truth unverified
    assign evidence owner to #3549, #3550, or #3551
route narrower docs and legacy Tabby docs to the canonical runbook
```

The runbook will use command placeholders such as `<operator-user>` and `<tailnet-identity>` where identity-specific values would otherwise be copied. It may name the repo-governed machines `ace-linux-1` and `ace-linux-2`, but it will not publish or repeat literal connection addresses, keys, tokens, auth URLs, peer configurations, or router details.

---

## Implementation Tasks

### Task 1: Add the documentation contract test first

**Files:**

- Create `tests/docs/test_remote_linux_access_contract.py`.

**Test structure:**

```python
ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs/ops/remote-linux-access.md"
RELATED = [
    ROOT / "docs/README.md",
    ROOT / "docs/setup/README.md",
    ROOT / "docs/ops/machine-inventory.md",
    ROOT / "docs/ops/ace-linux-2-handoff-runbook.md",
]
LEGACY = [
    ROOT / "config/tabby/REMOTE_ACCESS.md",
    ROOT / "config/tabby/TAILSCALE_SETUP.md",
]
```

The tests will assert:

1. The runbook exists and contains the exact required sections `Authority`, `Architecture`, `Security controls`, `Setup sequence`, `Verification matrix`, `Rollback and recovery`, `Troubleshooting`, and `Drift ledger`.
2. The runbook names Tailscale as transport, conventional OpenSSH keys as authentication, and Tailscale SSH as optional.
3. The runbook contains no IPv4 literal and does not recommend router SSH port forwarding.
4. The authority section links `config/workstations/registry.yaml`, `scripts/operations/connection/`, and machine-local secret storage.
5. Every related durable document links `docs/ops/remote-linux-access.md`.
6. Both legacy Tabby documents carry a canonical-authority notice, contain no IPv4 literal, and contain no positive instruction to forward SSH from the router.
7. The drift ledger links [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549), [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550), and [#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551).
8. Every repo-relative Markdown link introduced by this issue resolves.

Run before implementation:

```bash
uv run pytest tests/docs/test_remote_linux_access_contract.py -q
```

Expected RED state: failures for the missing runbook, missing cross-links, and legacy duplicated endpoint guidance.

Commit after the complete RED→GREEN slice, not while tests are red.

### Task 2: Create the canonical runbook

**Files:**

- Create `docs/ops/remote-linux-access.md`.

The runbook will contain:

- status, scope, audience, and authority hierarchy;
- a small topology diagram showing outbound-only Tailscale connectivity and no router SSH forwarding;
- an architecture decision table comparing Tailscale+OpenSSH, optional Tailscale SSH, self-hosted WireGuard, and direct public SSH;
- prerequisites and machine-local secret boundaries;
- MFA, device approval, grants, MagicDNS, server-key-expiry, and client-device-expiry guidance;
- test-first SSH hardening order using a drop-in, `sshd -t`, reload-not-restart, a preserved recovery session, and a second-session proof;
- the approved `ace-linux-2` canary then `ace-linux-1` rollout order;
- external-network, post-reboot, rejection, router, and recovery evidence matrices;
- rollback and troubleshooting for MagicDNS, expired device keys, relayed connections, unreachable hosts, and authentication failures;
- a drift ledger that records sources, observed conflict, prohibited assumption, evidence owner, and follow-up issue;
- primary-source links to official Tailscale and OpenSSH documentation.

After creation, run the focused tests. Expected intermediate state: runbook-content tests pass; cross-link and legacy-pointer tests remain red.

### Task 3: Route durable documentation to the canonical runbook

**Files:**

- Modify `docs/ops/machine-inventory.md`.
- Modify `docs/ops/ace-linux-2-handoff-runbook.md`.
- Modify `docs/README.md`.
- Modify `docs/setup/README.md`.

Each file will add one clearly labeled link to `docs/ops/remote-linux-access.md`. The machine inventory will retain fleet facts, the handoff runbook will retain `ace-linux-2` work-handoff semantics, and setup navigation will retain bootstrap scope. None will copy the canonical setup, security, rollback, or endpoint guidance.

Run the focused tests. Expected intermediate state: durable cross-link tests pass; legacy-pointer tests remain red.

### Task 4: Retire competing legacy instructions

**Files:**

- Modify `config/tabby/REMOTE_ACCESS.md`.
- Modify `config/tabby/TAILSCALE_SETUP.md`.

Each file will become a concise legacy/client-tool pointer. It will retain only Tabby-specific UI notes that remain useful, remove point-in-time addresses and installed-state assertions, remove public port-forwarding advice, correct stale helper paths, and link the canonical runbook for architecture and operations.

Run the focused tests. Expected GREEN state: all documentation-contract tests pass.

### Task 5: Validate, review, and close the implementation slice

Run, in order:

```bash
uv run pytest tests/docs/test_remote_linux_access_contract.py -q
git diff --check
bash scripts/legal/legal-sanity-scan.sh --diff-only
bash scripts/security/secrets-scan.sh --repo workspace-hub
```

Expected: focused tests pass; whitespace check is silent; legal scan reports no block-severity violations; secrets scan reports `PASS: workspace-hub`.

The implementation will then receive a T2 adversarial artifact/code review. Findings that generalize beyond this issue will be promoted to a follow-up issue or durable rule rather than buried only in review artifacts.

Implementation commits will use pathspec serialization, for example:

```bash
git commit -m "docs(ops): add canonical remote Linux access runbook (#3548)" -- \
  tests/docs/test_remote_linux_access_contract.py \
  docs/ops/remote-linux-access.md \
  docs/ops/machine-inventory.md \
  docs/ops/ace-linux-2-handoff-runbook.md \
  docs/README.md docs/setup/README.md \
  config/tabby/REMOTE_ACCESS.md config/tabby/TAILSCALE_SETUP.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/docs/test_remote_linux_access_contract.py` | Enforce authority, security, cross-link, legacy-retirement, and drift-routing contracts |
| Create | `docs/ops/remote-linux-access.md` | Canonical durable operator runbook |
| Modify | `docs/ops/machine-inventory.md` | Link canonical access operations without duplicating them |
| Modify | `docs/ops/ace-linux-2-handoff-runbook.md` | Keep handoff scope narrow and link canonical access operations |
| Modify | `docs/README.md` | Make the runbook discoverable |
| Modify | `docs/setup/README.md` | Route post-bootstrap operators to the runbook |
| Modify | `config/tabby/REMOTE_ACCESS.md` | Remove competing endpoint/public-forwarding guidance and mark legacy scope |
| Modify | `config/tabby/TAILSCALE_SETUP.md` | Remove point-in-time state and stale helper paths; mark legacy scope |
| Update | `docs/plans/README.md` | Index this plan |

Explicitly unchanged: `config/workstations/registry.yaml`, all files under `scripts/operations/connection/`, live Tailscale/SSH/router state, and user SSH keys.

---

## TDD Test List

| Test name | What it will verify | Initial RED reason | GREEN condition |
|---|---|---|---|
| `test_canonical_runbook_has_required_sections` | Complete operator contract | Runbook missing | All eight sections exist |
| `test_runbook_separates_transport_and_authentication` | Tailscale transport + OpenSSH keys; Tailscale SSH optional | Runbook missing | Exact architecture terms exist |
| `test_runbook_has_no_literal_ipv4_or_public_ssh_forwarding` | No duplicated endpoints or public exposure advice | Runbook missing | No IPv4 literal; explicit no-forward rule |
| `test_runbook_declares_authority_hierarchy` | Registry → runbook → helpers → machine-local secrets | Runbook missing | All authority links exist |
| `test_related_durable_docs_link_canonical_runbook` | One discoverable operational authority | Cross-links missing | Four related docs link it |
| `test_legacy_tabby_docs_defer_to_canonical_authority` | Legacy docs cannot compete or publish endpoints | Current duplicated content | Both legacy docs become safe pointers |
| `test_drift_ledger_routes_each_followup` | Drift belongs to helper and rollout children | Ledger missing | #3549, #3550, #3551 linked |
| `test_new_markdown_links_resolve` | New relative links are valid | Links absent | Every introduced relative target exists |

---

## Acceptance Criteria

- [ ] The focused documentation-contract test demonstrates RED before implementation and GREEN afterward.
- [ ] `docs/ops/remote-linux-access.md` is the canonical authority and contains architecture, security controls, setup sequence, verification, rollback, troubleshooting, and drift ownership.
- [ ] The runbook contains no literal endpoint addresses, keys, tokens, auth URLs, peer configs, or router details.
- [ ] The runbook requires no router SSH forwarding and treats Tailscale SSH as optional only.
- [ ] Related durable docs link the canonical runbook without duplicating procedures.
- [ ] Legacy Tabby docs no longer present point-in-time endpoint or public-forwarding guidance as current authority.
- [ ] Drift is recorded but not reconciled; [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549), [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550), and [#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551) own executable/live truth.
- [ ] Focused tests, `git diff --check`, legal scan, and workspace-hub secrets scan pass.
- [ ] T2 adversarial artifact review completes with no unresolved MAJOR finding.
- [ ] The issue receives an implementation summary comment before closeout.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | `scripts/review/results/2026-07-15-plan-3548-claude-r1.md` |
| Codex | PENDING | `scripts/review/results/2026-07-15-plan-3548-codex-r1.md` |
| Gemini | PENDING | `scripts/review/results/2026-07-15-plan-3548-gemini-r1.md` |

**Overall result:** PENDING — implementation will remain blocked.

---

## Risks and Open Questions

- **Risk — stale data becomes authority:** the runbook could accidentally repeat a historical address or installed-state claim. Contract tests will prohibit literal IPv4 endpoints, and the drift ledger will mark current truth unverified.
- **Risk — security ordering causes lockout:** readers could disable password authentication before proving key and recovery access. The runbook will make recovery → transport → key proof → `sshd -t` → reload → second-session proof the mandatory order.
- **Risk — documentation scope absorbs implementation:** tempting fixes exist in registry and helpers. The plan will keep them explicitly unchanged and route them to [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549).
- **Risk — VNC conflict expands scope:** headless VNC guidance is adjacent but not part of the SSH architecture. The runbook will name the conflict and route it without changing VNC scripts or choosing an unverified server model.
- **Risk — legal/secret scanners self-match examples:** the runbook will use semantic placeholders and links instead of token-shaped examples, endpoint literals, or configuration bodies.
- **Open questions:** none. The user approves the architecture, authority hierarchy, issue tree, rollout order, safeguards, and verification matrix in the originating session.

---

## Complexity: T2

This issue will create a tested canonical runbook and reconcile navigation across multiple documentation surfaces while preserving strict security and implementation boundaries. It therefore requires a full plan, TDD, and multi-provider adversarial review.
