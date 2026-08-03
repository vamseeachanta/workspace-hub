# Plan for #3571: equality/reconcile tooling gaps — private host identity, junction restore guard, flock false-skip

> **Status:** adversarial-reviewed  <!-- r1 Claude inline (4 findings, fixed) · r2 Codex MAJOR (5 findings, all fixed as r3 inline patches per the r3-inline loop-break pattern — precedence reordered to flag>map>file, expected_hostname cross-check, atomic rename-based lock steal, propagate destructive-site audit, hermetic non-dry-run guard AC) -->
> **Complexity:** T2
> **Date:** 2026-07-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3571
> **Client:** N/A  <!-- plan touches no wiki content; the private machine registry is referenced as an external source of truth only -->
> **Project:** —
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-17-plan-3571-claude.md | scripts/review/results/2026-07-17-plan-3571-codex.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/collect-equality.sh:47-60` — hardcoded hostname→machine case map; unknown Windows hosts hard-fail. `EQ_PUBLIC_HOST` (line 34) already sanitizes serialized identity when the wrapper passes it.
- Found: `scripts/windows/equality-report.ps1:62-71` — `Get-EqualityMachineLabel` duplicates the same hardcoded map in PowerShell; `-Machine` bypasses it.
- Found: `scripts/readiness/reconcile-ecosystem.sh` — emits AUTO-SAFE remediation commands that invoke `equality-matrix-cron.sh` with no machine argument; on a host absent from the map every printed remediation is un-runnable (verified live 2026-07-17 on ace-win-1).
- Found: `scripts/readiness/publish-equality.sh:49-51` — `flock -n 9 || { say "another publish in flight; skipping"; exit 0; }`. On Git for Windows bash `flock` does not exist; command-not-found is indistinguishable from lock-held, so publish **silently no-ops with exit 0** (verified live 2026-07-17).
- Found: `scripts/skills/resync-skill-links.sh` + `scripts/propagate-ecosystem.sh` — create/repair shared-skill links across sibling repos; on Windows these materialize as NTFS junctions targeting `workspace-hub/.claude/skills`. No guard anywhere prevents a `git restore`/recursive delete on a junctioned path from following the reparse point into the canonical tree (4,215-file wipe incident 2026-07-16, issue body).
- Found: `tests/readiness/test_collect_equality.py`, `test_publish_equality.py`, `test_reconcile_ecosystem.py`, `test_windows_scheduler_single_source.py` — existing contract-test surfaces for every script this plan touches.
- Gap: no local (off-repo) machine-identity source; no lock fallback when `flock` is absent; no reparse-point guard in any restore/propagate path; no rule documenting the junction hazard.

### Standards
Not applicable (harness/infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages (harness/infrastructure issue). External source of truth consulted instead: the private client machine registry (`llm-wiki-acma/docs/operations/machine-equality-hosts.yml`, commit `d12da52` there, validated by that repo's issue-285 privacy checker) — binds each equality column to its physical hostname. Owner decision 2026-07-17 (issue comment): direct hostnames live ONLY in private client repositories; public workspace-hub surfaces carry logical labels.

### Prior art / constraints
- PR #3279 (closed): adding this box's hostname to the public map was rejected — the token collides with a private client codename; `legal-client-pii-gate` is authoritative. **This plan must not introduce any physical hostname into workspace-hub.**
- `.claude/rules/scheduler-mutation-safety.md`: no scheduler mutation is proposed here (scripts touched are collectors/publishers, not scheduler mutators) — registry untouched.
- 2026-07-14 ace-win-1 scheduler exit handoff: scheduled tasks pass `-Machine ace-win-1` explicitly, so D1 must not regress that path.

## Problem statement

Three defects from the 2026-07-16/17 incident (issue #3571):

1. **Junction-following restore hazard.** Sibling repos' `.codex/skills` / `.gemini/skills` may be NTFS junctions into `workspace-hub/.claude/skills`. Restoring or recursively deleting them follows the reparse point and empties the canonical tree.
2. **Windows host-identity gap.** Boxes whose OS hostname must not appear in the public repo cannot be resolved by the hardcoded host maps, so no-arg tooling paths (`equality-matrix-cron.sh`, reconcile's printed remediations) hard-fail on them.
3. **`flock` false-skip.** `publish-equality.sh` exits 0 without publishing whenever `flock` is absent (all Git for Windows hosts).

## Design

### D1 — local machine-identity file (public-token-free host resolution)

A gitignored, off-repo identity file will be introduced as a new resolution layer, provisioned once per box by the operator from the private client registry:

- Default path `~/.config/workspace-hub/machine-identity.yaml`, override via `WORKSPACE_HUB_MACHINE_IDENTITY`. Schema (2 keys): `machine: <logical-label>` (required), `public_host: <label>` (optional, defaults to `machine`).
- Resolution precedence in `collect-equality.sh` (and mirrored in `equality-report.ps1` / consumed by `reconcile-ecosystem.sh` when composing remediation commands) — **revised per r2 finding 2** so a stale/copied file can never override a correctly-mapped host:
  1. explicit `--machine` / `-Machine` / `RECONCILE_MACHINE` / `EQ_MACHINE` (unchanged, highest; when given, the identity file is not even read — r2 finding 1)
  2. existing hardcoded hostname map (unchanged — mapped hosts keep today's behavior bit-for-bit)
  3. **NEW:** identity file, consulted only when the hostname resolves nowhere in the map
  4. fail loud (unchanged)
- The identity file additionally supports optional `expected_hostname:` — permitted there because the file is off-repo and gitignored (owner decision: direct hostnames live only in private/local surfaces). When present and mismatching the actual OS hostname, resolution fails loud: a file copied to the wrong box dies instead of minting a false column (r2 finding 2).
- A malformed identity file (missing `machine:`, unparseable, or a label outside the known set) will fail loud — never silently fall through to the map. The known-label set will NOT be a fresh literal: it will be extracted once (from the labels the existing hardcoded maps already enumerate) into a small shared helper under `scripts/readiness/lib/`, consumed by the bash resolver and asserted identical by the PowerShell mirror's contract test — one canonical list, not a third copy (r1 finding 1).
- `reconcile-ecosystem.sh` will embed the resolved label into the remediation commands it prints (e.g. `EQ_MACHINE=<label> bash .../equality-matrix-cron.sh`), so printed remediations are runnable on identity-file boxes.
- Explicitly rejected alternative: collectors reading the private client repo checkout directly — couples public tooling to a private repo's presence/layout, breaks non-client boxes, and risks echoing private paths into evidence. The private registry stays the fleet source of truth; the identity file is its 2-line per-box projection.
- Docs: a short operator note in `docs/ops/` describing provisioning (copy the label from the private registry; never copy the hostname anywhere tracked).

### D2 — lock fallback in publish-equality.sh

- When `command -v flock` fails, fall back to a `mkdir`-based lock (`$LOCK.d`) with owner metadata (PID + start timestamp written inside) and a distinct log line (`lock: flock unavailable; using mkdir fallback`).
- Stale-lock steal will be **atomic via rename** (r2 finding 3): a would-be stealer renames `$LOCK.d` → `$LOCK.d.stale.$$` (rename is atomic; exactly one contender wins, the loser's rename fails and is treated as lock-held → skip exit 0), removes the renamed dir, then re-attempts `mkdir` exactly once. No process ever `rm`s a path still named `$LOCK.d`, so a freshly-created replacement lock can never be deleted by a slow contender.
- Cleanup will EXTEND the existing `cleanup()` body already installed via `trap cleanup EXIT` (a second `trap` statement would replace the worktree cleanup and leak one or the other); a test will assert both the worktree and the lock dir are gone after failure paths (r1 finding 2).
- Lock-held (either mechanism) keeps today's behavior: skip with exit 0 and the "another publish in flight" message. Command-not-found will no longer be conflated with lock-held.

### D3 — reparse-point guard for shared-skill link paths

- New helper `scripts/lib/reparse_guard.sh` — `is_reparse_point <path>` (Windows: `fsutil reparsepoint query` via cmd, or cygpath+PowerShell `LinkType` probe; POSIX symlink via `test -L`; plain dir → false).
- `resync-skill-links.sh --apply` and `propagate-ecosystem.sh --skills-only` will apply a concrete, fail-closed predicate (r1 finding 3): a reparse-point node may only be removed with link-node-only primitives (`rmdir`/`rm` of the junction itself — which never touch target contents); any recursive or child-enumerating deletion on a path that probes as a reparse point is refused with a named reason. Re-linking (remove link node, create new link) remains allowed.
- **Every destructive site in `propagate-ecosystem.sh` will be audited and routed through the guard, not just the primary link path** (r2 finding 4): this explicitly includes the backup-handling sites (`rm -rf "$backup"` and the `${link_path}.bak-*` moves), since a leftover `.bak-*` entry can itself be a junction whose recursive deletion follows into the canonical tree. The wave-3 work list will enumerate each `rm -rf`/child-enumerating call in `propagate-ecosystem.sh` and `resync-skill-links.sh` with its guard disposition.
- New rule `.claude/rules/windows-junction-restore-safety.md` (Level 0 prose now, per the enforcement gradient): never `git restore`/`checkout --`/recursively delete `.codex/skills`, `.gemini/skills`, or any shared-skill link path without checking `LinkType`/reparse status first; ` D` residue on these paths is intentional tooling state. The rule will cite the 2026-07-16 incident and the recovery procedure.

## Implementation waves (TDD — tests precede implementation in every wave)

**W1 — D2 flock fallback (smallest, highest silent-failure risk):**
1. `tests/readiness/test_publish_equality.py`: new cases — flock absent on PATH → publish proceeds via mkdir lock; concurrent second invocation → skips; stale lock dir → stolen with warning; flock present → unchanged behavior.
2. Implement the fallback in `publish-equality.sh`.

**W2 — D1 identity file:**
1. `tests/readiness/test_collect_equality.py`: precedence tests (flag > map > file > fail; mapped host + stale file → map wins with the file unread), malformed-file fail-loud, known-label enforcement, `expected_hostname` mismatch fail-loud, `public_host` serialization (evidence `host:` field never carries the OS hostname when the file provides `public_host`); `tests/readiness/test_reconcile_ecosystem.py`: printed remediations embed the resolved label. **Plus a PowerShell wrapper contract test** (r2 finding 1, `test_windows_scheduler_single_source.py` style): `equality-report.ps1 -Machine ace-win-1` with a malformed AND a conflicting identity file present must behave identically to today — the scheduled-task entrypoint is the regression surface, and explicit `-Machine` must short-circuit before any identity-file read or validation.
2. Implement in `collect-equality.sh`, `equality-report.ps1` (`Get-EqualityMachineLabel` gains the file layer), `reconcile-ecosystem.sh`.
3. Operator provisioning note in `docs/ops/`.

**W3 — D3 junction guard + rule:**
1. New `tests/skills/test_reparse_guard.py` (pure-logic classification with a fake probe seam; Windows-marked integration case) and a refusal test for `resync-skill-links.sh --apply` against a simulated reparse path.
2. Implement `scripts/lib/reparse_guard.sh`, wire into `resync-skill-links.sh` / `propagate-ecosystem.sh`, add the rule file.

## Acceptance criteria

1. All new tests green; existing readiness suite (109 tests at last count) stays green.
2. `bash scripts/readiness/equality-matrix-cron.sh` completes collect→build→publish on a box whose hostname is absent from the public map, given only the identity file — verified live on ace-win-1.
3. `publish-equality.sh` on a flock-less host actually pushes (verified by a commit reaching origin/main) and logs the fallback lock line.
4. `rg -i` over the full diff for any physical hostname token returns nothing; `scripts/legal/legal-sanity-scan.sh` passes.
5. Junction-guard verification is hermetic and non-dry-run (r2 finding 5): a fixture repo with a fake reparse-probe seam exercises the live `--apply` path of BOTH `resync-skill-links.sh` and `propagate-ecosystem.sh --skills-only`, asserting refusal fires before any destructive call and that no child path under the simulated link target is deleted. (`--dry-run` on ace-win-1 remains as a live smoke check, not the acceptance evidence.)
6. Rule file exists and is listed in `.claude/rules/README.md`.

## Risks

- **PowerShell/bash duplication drift (D1):** the identity-file parser will exist in both languages; mitigated by shared contract tests asserting identical precedence and by keeping the schema to 2 keys.
- **Lock-steal races (D2):** mkdir-lock staleness uses directory mtime; a >30 min publish would be stolen. Accepted: publishes take seconds; the steal logs loudly.
- **Reparse probing portability (D3):** `fsutil` may require elevation on some hosts; the guard will degrade to the PowerShell `LinkType` probe and, if both probes fail, refuse the destructive path (fail-closed).
- **Windows publish path beyond flock is unexercised (r1 finding 4):** the live failure stopped at the lock, so the sparse-worktree/`timeout`/`mktemp` sequence has never run on Git for Windows. Acceptance criterion 3 forces a real end-to-end push from ace-win-1; any additional Windows breakage it surfaces is explicitly in W1 scope.
- **Coverage claim check (per SHARED_SOUL):** the junction guard protects tooling-mediated deletions only; a human running raw `git restore` in a sibling is still exposed — the rule file plus preflight-template wording are the mitigation, and this limit is stated in the rule.
