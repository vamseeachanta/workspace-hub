# Plan for #2968 (F1): role-overlay harness reconciler

> **Status:** draft → plan-review
> **Complexity:** T3 (systemic, cross-machine, writes to harness state)
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2968
> **Parent epic:** https://github.com/vamseeachanta/workspace-hub/issues/2967
> **Decisions inherited:** Q1 composable roles · Q2 licensed-win declare-only (epic #2967 decision log)
> **Client:** N/A

---

## Resource Intelligence Summary

### Existing substrate (extend, not greenfield)
- `config/workstations/registry.yaml` — has `role`, `schedule_variant`, `telegram_hermes` per machine. F1 adds a `harness_profile` block.
- `scripts/readiness/compare-harness-state.sh` — already SSH-diffs ace-linux-2 harness readiness; **prior art for the dry-run drift report.** Uses ssh target `ace2`, a2 hub `/mnt/workspace-hub`.
- `scripts/readiness/remediate-harness.sh` — prints fix commands for FAIL checks (R-PLUGINS etc.); reads `.claude/state/harness-readiness-<machine>.yaml`. F1's apply path generalizes this from "print" to "converge".
- `scripts/memory/bootstrap-machine.sh` — machine bootstrap entry; F1's reconciler is invoked from here + a nightly cron.
- `~/.claude/settings.json` divergence (probe 2026-06-08): a1 4010B (deny-list+hooks+effortLevel), a2 675B (none). This is the role-invariant `_base` gap F1 closes first.

### Gaps identified
- No `harness_profile` / role-overlay concept; no `harness-roles.yaml`.
- No state-classification taxonomy on disk → reconciler can't know what's safe to touch.
- No idempotent apply for the user-settings/hook/skill layer (only readiness *checks* exist).

### Evidence
- Probe outputs on epic #2967 body. compare-harness-state.sh/remediate-harness.sh read in this session. Codex architecture + plan reviews on #2967 (managed-surface boundary, dry-run-first, fail-closed conflict).
- Source count: 6. ✔

---

## Deliverable
An idempotent reconciler that converges each **managed** machine to `git base + (_base ∪ its role overlays)` for the role-managed surface (user-settings policy keys, hook set, skill families), **dry-run by default**, never touching secrets/private/uncataloged-live state — closing the verified ace-linux-2 safety-deny-list+hooks gap as its first applied overlay.

---

## Scope (F1 only — cron catalog is F2, dispatch is F3)
F1 delivers the **role model + reconciler for the settings/hook/skill surface**. Cron materialization is explicitly F2 (#2969); F1's `harness-roles.yaml` *declares* `schedule_jobs` per role but does NOT write crontab.

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `config/workstations/harness-roles.yaml` | role overlay defs (`_base`, control-plane, comms-dispatch, sim-worker, licensed-solver) per locked Q1 schema |
| Modify | `config/workstations/registry.yaml` | add `harness_profile: {roles: [...], managed: bool}` per machine (a1 control-plane/managed; a2 comms-dispatch+sim-worker/managed; licensed-win-1/2 licensed-solver/managed:false; macbook deferred) |
| Create | `config/workstations/harness-state-classes.yaml` | the 6-class taxonomy mapping (role-managed / git-managed / machine-private / secret / intentionally-divergent / uncataloged-live) |
| Create | `scripts/readiness/harness-reconcile.py` | the reconciler: `--dry-run` (default, drift report) / `--apply` (flagged); deep-merge required keys; fail-closed on overlay conflict + uncataloged-live |
| Create | `tests/readiness/test_harness_reconcile.py` | TDD (below) |
| Update | `docs/plans/README.md` | index |

## Merge semantics — DETERMINISTic (Codex MAJOR #2/#3)
The reconciler is **purely additive and identity-keyed**; it never removes local entries.

- **`permissions.deny` (array of strings):** `result = sorted(set(local) ∪ set(_base.required))`. Set-union + dedup + lexical sort → stable, idempotent, never drops a local deny rule. The `_base` deny entries are a **required subset**; missing ones are added.
- **`hooks` (object: event → list of groups, each `{matcher?, hooks:[{type,command,...}]}`):** identity of a hook = `(event, type, command)`. Union by identity; **stable order = required-canonical first, then preserved local, deduped by identity.** If an identity exists locally with a *different* non-identity field (e.g. timeout), that is a **conflict → fail closed** (surface, do not silently overwrite). Required hook absent → append. Local-only hooks (not in any role) → **preserved** (never removed; if a hook is in no class it is `uncataloged-live` → blocks `--apply` until classified).
- **scalar keys (`effortLevel`, `env.*`):** set to required value; if local differs AND key is in the `intentionally-divergent` allowlist → skip; else → drift, converged on `--apply`, conflict surfaced in `--dry-run`.
- **Idempotency contract:** after `--apply`, a second `--apply` produces a **byte-identical** `settings.json` (canonical key order + sorted arrays + identity-dedup). Asserted in tests.

## Live-session apply gating (Codex MAJOR #1)
`~/.claude/settings.json` is read by Claude Code **at session start** (affects new sessions, not the running one). But ace-linux-2 runs **live Hermes gateway + WhatsApp bridge + deckhand sweep** that may read settings/hooks differently. Therefore:
- Before `--apply`, detect active daemons (`pgrep` hermes gateway / whatsapp bridge / deckhand). If active AND the overlay would change the `hooks` surface → **refuse** with a clear message unless `--apply --allow-live-reload` is passed explicitly.
- Document reload semantics in the plan output; default posture is **stage-and-defer** (write a pending overlay + notify) rather than hot-modify a live comms host.

## Pseudocode (reconciler)
```
load harness-roles.yaml, registry.yaml, state-classes.yaml
for THIS machine (hostname → registry id):
    if not harness_profile.managed: report "declare-only (routing), skipping"; exit 0
    overlay = deep_merge(_base, *[roles[r] for r in profile.roles])   # fail-closed on key conflict
    current = read ~/.claude/settings.json (+ hook/skill inventory)
    drift = []
    for key in overlay.user_settings_required_keys:
        if current[key] != expected: drift.append((key, current, expected))
    detect uncataloged-live (e.g. settings keys/hooks present locally but in no class) → BLOCK apply
    if --dry-run: print drift report; exit 0
    if --apply:
        backup ~/.claude/settings.json
        for each drift: additive deep-merge expected key (NEVER wholesale replace; preserve unknown local keys)
        never read/write secret-class paths
        re-run drift check → must be empty (idempotent); else fail
```

## TDD Test List
| Test | Verifies | Expected |
|---|---|---|
| test_compose_union_two_roles | a2 = comms-dispatch ∪ sim-worker | merged skill_families/keys = union |
| test_base_applies_to_all_managed | _base in every managed machine's overlay | deny-list+hooks present |
| test_overlay_conflict_fails_closed | same key, different values in two roles | raises (no last-writer-wins) |
| test_managed_false_skips | licensed-win-1 managed:false | reconciler exits 0, writes nothing |
| test_dry_run_writes_nothing | --dry-run on drifted fixture | settings.json unchanged, drift reported |
| test_apply_is_additive | --apply merges required key | unknown local keys preserved |
| test_apply_idempotent | --apply twice | second run = no-op |
| test_secret_class_never_read | secret paths in classes | reconciler never opens them (monkeypatch open guard) |
| test_uncataloged_live_blocks_apply | local hook in no class | --apply blocked until classified |
| test_deny_union_dedup_sorted | merge deny arrays w/ overlap | sorted set-union, no dupes, no local dropped |
| test_hooks_union_by_identity | same (event,type,command) twice | single entry, stable order |
| test_hooks_conflict_fails_closed | same identity, different timeout | raises (no silent overwrite) |
| test_apply_byte_identical_on_rerun | --apply twice | second output byte-identical to first |
| test_dry_run_no_artifacts | --dry-run | no backup/lock/temp/cache/state file created (not just settings.json) |
| test_inventory_never_reads_uncataloged_private | private path during inventory | open-guard proves it is never read |
| test_apply_refuses_on_live_daemon | a2 daemons active, hooks change | --apply refuses w/o --allow-live-reload |

## Acceptance Criteria
- [ ] `harness-reconcile.py --dry-run` on ace-linux-2 reports the `_base` deny-list+hooks gap.
- [ ] `--apply` (flagged) closes that gap via additive deep-merge; unknown local keys preserved; backup written.
- [ ] Re-run is a no-op (idempotent).
- [ ] Secret-class paths never read/written (test-proven).
- [ ] Overlay key-conflict and uncataloged-live both fail closed.
- [ ] licensed-win-1/2 (`managed:false`) are skipped; macbook absent.
- [ ] `uv run pytest tests/readiness/test_harness_reconcile.py -v` passes; no regression in tests/readiness/.
- [ ] `--dry-run` creates **zero** artifacts (no backup/lock/temp/cache/state), not just leaves settings.json unchanged.
- [ ] `hooks`/`deny` arrays merge by deterministic identity (union+dedup+stable order); second `--apply` is byte-identical.
- [ ] `--apply` on ace-linux-2 **refuses** (or stage-defers) when live Hermes/WhatsApp/deckhand daemons are active and the hook surface would change, unless `--allow-live-reload` is explicit.
- [ ] Inventory phase proves (test) it never reads uncataloged/private paths.
- [ ] Cross-review (T3): Claude + Codex (+ Gemini if available). **Codex r1 = MAJOR; folded (array semantics + live gating).**

## Risks and Open Questions
- **Risk (Codex blast-radius):** apply could disturb live Hermes/Telegram session behavior on a2 → mitigated by additive deep-merge + backup + dry-run-first + `managed` opt-in.
- **Risk (FUSE/control-plane):** the reconciler runs *locally on each machine* against `~/.claude/settings.json` (NOT a git checkout), so it sidesteps the FUSE-slow worktree problem — it reads role defs from the already-present repo and writes only to the user settings file.
- **Open (user):** for `--apply` rollout, enable on ace-linux-2 first (closes the safety gap) or ace-linux-1 first (lower client-impact blast radius)? Recommendation: **a2 first** — it has the actual gap and is the lower-stakes harness for the safety-base overlay.

## Complexity: T3
Writes to harness state across machines; gated dry-run→apply; full TDD + 3-agent review.

---
## Adversarial Review Summary
| Provider | Verdict | Key findings (folded) |
|---|---|---|
| Codex r1 | **MAJOR → resolved** | (1) array merge undefined for hooks/deny → added deterministic identity-keyed union+dedup+stable-order spec; (2) live-session apply could disrupt a2 daemons → added daemon-detection gate + `--allow-live-reload` + stage-defer default; (3) array idempotency → byte-identical rerun AC; (4) dry-run zero-artifacts AC; (5) a2-live-safety AC; (6) uncataloged-private inventory read test |
| Claude | inline (author) | structured per epic #2967 architecture review |
| Gemini | pending/optional | dispatch if quota (T3 → 3-agent) |

**Overall:** MAJOR addressed in-plan; remaining gate = user approval.
