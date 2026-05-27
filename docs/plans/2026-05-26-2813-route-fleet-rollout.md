# Plan for #2813: Roll out the Codex-under-Claude route to the ecosystem machines

> **Status:** adversarial-reviewed (Claude MINOR + Codex MAJOR, both resolved) — awaiting user approval + Q2 decision
> **Complexity:** T2
> **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2813
> **Refs:** #2804 (route, merged #2809) · #2822 (worktree/clone dispatch, merged #2834) · **Client:** N/A
> **Supersedes:** the thin #2813 draft in open PR #2829 (`docs/follow-on-plans-2802-2804`) — that draft assumed a centrally-enumerable fleet; discovery (below) inverts that premise.
> **Review artifacts:** scripts/review/results/2026-05-26-plan-2813-claude.md | ...-codex.md

## Resource Intelligence Summary

Harness/Infrastructure issue (Codex-under-Claude route deployment). `Client: N/A`.

### Existing repo state
- Route codified on `main`: `scripts/install/{codex-bwrap.aa,setup-codex-sandbox.sh,teardown-codex-sandbox.sh}`, `docs/reports/2026-05-26-codex-under-claude-pilot.md`. Installer is guarded (`--check` default, `--dry-run`, explicit `--accept-userns-lpe-risk`, Ubuntu/AppArmor fail-fast, sentinel refuse-overwrite).
- Machine registry: `config/machine-baselines/<token>.{md,yaml}` (emitted by `scripts/setup/lib/emit-machine-status.sh`) + GitHub tracker #2753. Token policy: alias from `config/agents/machines.yaml` or sha256(hostname) fallback (`docs/setup/MACHINE_REGISTRY.md`).

### Reproduction / discovery proofs (verify-against-repo-state — the load-bearing step)
- **Empirical roster has ONE machine.** `git ls-files config/machine-baselines/` → only `0a36d305.{md,yaml}`. Tracker #2753 → 1 comment ("Machine baseline: ace-linux-1, Token: 0a36d305"). No `config/agents/machines.yaml` aliases exist. → The control plane knows only ace-linux-1.
- **User-confirmed live fleet (2026-05-26): `ace-linux-1`, `ace-linux-2` (Ubuntu); `ace-win-1`, `ace-win-2` (Windows).** ace-linux-2 / ace-win-* have not emitted a baseline yet.
- **ace-linux-1 route is functional but the AppArmor profile is unmanaged-by-installer.** `setup-codex-sandbox.sh --check` (2026-05-26): `profile file at dst: yes (managed-by-us: no)`, `config network_access: true`, `codex-cli 0.134.0`. The broker ran live Codex `task` jobs this session (#2822 reviews). → The profile was applied out-of-band during the pilot; the committed installer would **refuse to overwrite** it (no sentinel).
- **An SSH path to ace-linux-2 DOES exist (corrected per Codex plan-review #2, verified).** `config/workstations/registry.yaml`: `ace-linux-2: ssh: ace-linux-2, dispatch_enabled: true` (+ sshfs mounts `/mnt/remote/ace-linux-2/*`); readiness report `docs/reports/2026-04-27-issue-2519-ace-linux-2-readiness-probe.md`. The Windows machines are canonically `licensed-win-1` / `licensed-win-2` (both `ssh: null`, "physical/GUI access only", `dispatch_enabled: false`) — the user referred to them as `ace-win-1/2`. So the constraint is NOT "no path exists" (my first draft was wrong); it is **policy**: the issue forbids "batch/fleet auto-run" and requires the privileged userns/LPE-surface install to be a **per-machine, user-authorized sudo** decision. An unattended sudo-over-SSH install would violate that. `feedback_cross_machine_execution` reflects this per-machine policy, not an absence of SSH.
- **Installer does NOT set `network_access` (corrected per Codex plan-review #1, verified).** `setup-codex-sandbox.sh --with-network` only *logs* "add to config manually" — it never writes `~/.codex/config.toml`. So an install is incomplete without an explicit config edit; the runbook must include it.

### Gaps
- ace-linux-1's profile is not installer-managed (no teardown ownership).
- No committed coverage table recording per-machine route status.
- ace-linux-2 has no workspace-hub baseline / route install yet; the install is a per-machine action that cannot originate here.

## Decision: scope #2813 to what is actually deliverable from the control plane

A "fleet rollout" cannot be executed centrally (no SSH/push; sudo is per-machine user-authorized). So #2813 delivers:
1. **ace-linux-1 (Ubuntu) — reconcile to installer-managed** (user-authorized, this machine). Remove the out-of-band profile, reinstall via the committed installer so it carries the sentinel and is teardown-able.
2. **A committed per-machine coverage table** (append to the pilot report) recording route status for all 4 machines.
3. **A per-machine runbook** for the Ubuntu machines not reachable from here (ace-linux-2): the explicit, user-authorized steps to run when a session is on that machine.
4. **ace-win-1 / ace-win-2 (Windows) — documented N/A** with reason (the route is AppArmor/userns-based = Linux-only; the installer fail-fasts on non-Ubuntu).

Per-machine installs on ace-linux-2 complete **asynchronously** when an operator runs a session there; #2813 stays a tracking item until the coverage table shows all machines resolved. No silent/batch privileged auto-run (AC3).

## Per-machine target matrix (the enumerated roster — AC1)

| Machine (canonical) | OS | Route wanted? | Action | Who / where |
|---|---|---|---|---|
| ace-linux-1 | Ubuntu (confirmed) | yes | **Reconcile** out-of-band profile → installer-managed (sudo) + ensure `network_access=true`, verify `--check` shows `managed-by-us: yes` + `network_access: true` + broker smoke | this session (user-authorized sudo on ace-linux-1) |
| ace-linux-2 | Linux (distro auto-detected; SSH reachable per registry) | yes if Ubuntu+AppArmor | full runbook (profile install **+ explicit `network_access` config edit** + smoke + baseline). **Execution path is a user decision (Q2):** (a) user runs it during a session on ace-linux-2, or (b) user authorizes a single SSH-driven install from here. NOT an unattended batch auto-run either way. | per-machine, user-authorized (see Q2) |
| licensed-win-1 *(user-referred "ace-win-1")* | Windows (`ssh: null`, GUI-only) | **#2804 fix non-applicable** | none — the Ubuntu unprivileged-userns blocker does not exist on Windows (no AppArmor/bwrap); installer fail-fasts. **Scope-limited claim:** this means the *#2804 AppArmor fix* is N/A; whether Codex-under-Claude orchestration is separately wanted/working on Windows (native sandbox) is **out of #2813 scope** — flag a follow-up if desired. | n/a |
| licensed-win-2 *(user-referred "ace-win-2")* | Windows (`ssh: null`, GUI-only) | **#2804 fix non-applicable** | same as licensed-win-1 | n/a |

## Files to change

| Action | Path | Reason |
|---|---|---|
| Modify | `docs/reports/2026-05-26-codex-under-claude-pilot.md` | append "Fleet rollout coverage (#2813)" section: the matrix above + per-machine runbook |
| Update | `docs/plans/README.md` | add this plan's index row |
| (ops, no commit) | ace-linux-1 `/etc/apparmor.d/codex-bwrap` | reconcile to installer-managed via rm+setup (post-approval, user-authorized sudo) |

No source code changes. The installer + teardown already exist and are tested (#2804).

## Verification rubric (TDD N/A — ops/infra issue; live-probe evidence per #2798)

No new code → unit-test TDD does not apply; per the completeness gate (#2798) ops/infra issues use a **live-probe evidence rubric**:

| Check | Evidence required |
|---|---|
| ace-linux-1 reconciled | `setup-codex-sandbox.sh --check` shows `profile file at dst: yes (managed-by-us: yes)` + `network_access: true`; `teardown --check` recognizes the managed profile |
| ace-linux-1 functional | a broker `task --write` smoke test exits 0 (or cite the live `task` jobs already run this session) |
| ace-win-* N/A correct | reasoned from the committed preflight (`apparmor_parser not found` → fail-fast); captured live if/when a session runs on Windows |
| Coverage table | committed matrix with per-machine status; no machine silently assumed |
| Coverage completeness (testable, per Codex #5) | a scripted assertion that every machine in `config/workstations/registry.yaml` appears in the committed coverage section with a status — e.g. `for m in $(grep -oE 'hostname: \S+' config/workstations/registry.yaml \| awk '{print $2}'); do grep -q "$m" docs/reports/2026-05-26-codex-under-claude-pilot.md \|\| echo "MISSING: $m"; done` must print nothing |
| No batch privileged run | every install is an explicit, single-machine `--accept-userns-lpe-risk` invocation; no unattended sudo-over-SSH |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Reconcile on ace-linux-1 briefly removes the working profile → window where Codex can't sandbox | rm→setup is seconds; broker idle during the swap; verify with `--check` + smoke immediately after; reversible |
| Coverage claim overstated (the rule the issue cites) | matrix lists all 4 user-confirmed machines; ace-linux-2 marked PENDING (not "done"); only ace-linux-1 claimed after live `--check` evidence |
| Batch agent runs the privileged installer | installer defaults to `--check`, refuses to write without the explicit flag, no-ops on non-Ubuntu; plan forbids batch auto-run |
| ace-linux-2 never onboards → issue lingers | acceptable — #2813 is a tracking item; close when the matrix is fully resolved, or split ace-linux-2 into its own follow-on if it stalls |

## Reconcile mechanics for ace-linux-1 (user-decided 2026-05-26: reconcile to installer-managed)

`teardown-codex-sandbox.sh` **also refuses** a profile lacking our sentinel, so reconcile is an explicit, user-authorized sequence on ace-linux-1 (no code change). Hardened per Codex plan-review #3 (backup + content-verify + broker quiesce + post-checks — never blind-rm a live security profile), and per #1 the `network_access` config edit is explicit (the installer does NOT write it):
```bash
# 0) PRE: confirm what we're about to remove, and back it up
diff <(sudo cat /etc/apparmor.d/codex-bwrap) scripts/install/codex-bwrap.aa || true   # expect: differs only by sentinel/comments
sudo cp -a /etc/apparmor.d/codex-bwrap /root/codex-bwrap.bak.$(date +%s)               # rollback copy
pgrep -fa "app-server-broker.mjs serve" && echo "WARN: broker live — quiesce/idle Codex first"
# 1) unload + remove the out-of-band (sentinel-less) profile; abort if unload fails
sudo apparmor_parser -R /etc/apparmor.d/codex-bwrap && sudo rm -f /etc/apparmor.d/codex-bwrap
# 2) reinstall via the committed installer (stamps the MANAGED-BY sentinel + verifies userns)
bash scripts/install/setup-codex-sandbox.sh --accept-userns-lpe-risk
# 3) the installer does NOT write config — ensure network_access=true explicitly, then verify
grep -q 'network_access = true' ~/.codex/config.toml || printf '\n[sandbox_workspace_write]\nnetwork_access = true\n' >> ~/.codex/config.toml
bash scripts/install/setup-codex-sandbox.sh --check     # expect: managed-by-us: yes, network_access: true
# 4) functional smoke: a broker `task --write` exits 0 (or rely on this session's live task jobs)
```
Rollback: restore the `.bak` copy + `apparmor_parser -r`. A `--force-reconcile` installer flag (one-step overwrite of an unmanaged profile) is **out of scope** unless more machines surface with out-of-band profiles — it would need its own TDD.

Note on the **ace-linux-2 runbook**: it must include the same explicit `network_access=true` config edit (step 3) — `--accept-userns-lpe-risk` alone leaves the route incomplete (Codex #1).

## User decision Q2 — ace-linux-2 execution path (SSH exists; surfaced per Codex #2)

SSH + Hermes dispatch to ace-linux-2 are enabled in the registry, so the install is *feasible* from here. But the issue forbids batch/unattended privileged runs and requires per-machine user authorization for the userns/LPE-surface sudo. Two acceptable paths — pick one at approval:
- **(a) Runbook (default):** the install runs during a session ON ace-linux-2; this session only commits the coverage table + runbook; ace-linux-2 = PENDING until then.
- **(b) SSH-driven, single authorized run:** you authorize one interactive SSH install to ace-linux-2 now (sudo will prompt there). Not a batch/fleet auto-run — one explicit, authorized action. Then coverage = DONE after live `--check` over SSH.

## Acceptance criteria (from #2813)
1. Live machines enumerated (done: 4, user-confirmed + registry-checked — canonical names ace-linux-1/2, licensed-win-1/2). Per machine: Ubuntu+wanted → installed + `--check` evidence (incl. `network_access`) + broker smoke; else N/A with reason. → ace-linux-1 this session; ace-linux-2 per Q2; licensed-win-* N/A.
2. Per-machine coverage table committed (appended to the pilot report); coverage-completeness check passes.
3. No silent privileged auto-runs; each install explicit + user-authorized.

## Adversarial Review Summary
Claude (r1) MINOR + Codex (r2) MAJOR surfaced different defects → fixes applied inline (r3-inline); Codex's two MAJORs were independently verified against the repo before acting (network_access not written by installer; SSH-to-ace-linux-2 exists per `config/workstations/registry.yaml`).

| Provider | Verdict | Key findings (all resolved this revision) |
|---|---|---|
| Claude | MINOR | structural premise (fleet not centrally enumerable) + distro/Windows framing + branch-collision. Artifact: `scripts/review/results/2026-05-26-plan-2813-claude.md` |
| Codex | MAJOR | #1 installer doesn't set `network_access` (runbook fixed); #2 "no central path" false — SSH to ace-linux-2 exists (reasoning corrected → policy-based per-machine + Q2 decision); #3 reconcile hardened (backup/verify/quiesce/rollback); #4 Windows claim narrowed + canonical names; #5 coverage-completeness check added. Artifact: `scripts/review/results/2026-05-26-plan-2813-codex.md` |

**Post-revision:** no open MAJOR (both MAJORs verified + resolved). Ready for `status:plan-review` + user approval (incl. Q2).
