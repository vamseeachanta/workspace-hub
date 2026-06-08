# Plan for #2970 (F3): registry-driven dispatch + single provider-routing policy

> **Status:** draft → plan-review
> **Complexity:** T3 (cross-machine dispatch + cross-provider policy)
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2970
> **Parent epic:** https://github.com/vamseeachanta/workspace-hub/issues/2967
> **Depends on:** F1 #2968 (roles), F2 #2969 (role-tagged catalog)
> **Coordinates:** #2720 (lease contract) · #2524 (dispatch ledger) · #2519 (hermes orchestrate) · #2847 (failover)
> **Client:** N/A

---

## Resource Intelligence Summary

### Existing substrate (F3 connects + hardens; not greenfield)
- `scripts/operations/workstation-dispatch.sh` — ALREADY matches a task's `requires:` capabilities against registry and SSH-executes (or runs locally); has `--task/--requires/--command/--machine/--dry-run`. **Gaps:** matches DECLARED capabilities only (no live probe), is NOT role-aware (`harness_profile.roles`), and uses no atomic lease.
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (#1515) — provider roles exist **as prose**: Claude=orchestrator, Codex=worker+adversarial reviewer, Gemini=adversarial reviewer; 3-agent default + reduction rules. **Gap:** not a machine-readable single policy any script/agent queries → each session re-improvises.
- `config/ai-tools/provider-routing-scorecard.{json,py}` — utilization-based provider *recommendation* (separate concern: load-balancing, not role-routing).
- `config/workstations/registry.yaml` — `telegram_hermes.{dispatch_enabled,telegram_mode,data_access_profile}` + (F1) `harness_profile.roles`.
- `docs/ops/telegram-hermes-multimachine-control-plane.md` (#2720) — fail-closed git-ref lease: `refs/heads/dispatch/leases/<issue>-<mode>`; non-forced push = atomic winner.
- Memory rules to ENCODE: codex-exec is CPU-starved on ace-linux-1 → Codex = review/independent only there, not heavy authoring; delegate heavy review to Codex; Gemini = recon/cross-review; Hermes = dispatch lane.

### Gaps identified
- No single machine-readable provider-routing policy → "consistent AI-provider experience" is by-convention only.
- Dispatch trusts declared capabilities (Codex finding: registry is truth AND target → needs LIVE probe).
- No atomic lease / TTL / split-brain handling in workstation-dispatch.sh.

### Evidence
- workstation-dispatch.sh header read (capability match + SSH, no leases/probe/roles). AI_REVIEW_ROUTING_POLICY.md read (prose). provider-routing-scorecard.json read (utilization). #2720 lease contract. Memory feedback (codex CPU-starvation, delegate-to-codex). Source count: 6. ✔

---

## Deliverable
(a) Role- and **live-probe**-aware machine dispatch with atomic git-ref leases (TTL + split-brain safe); (b) **one machine-readable `provider-routing-policy.yaml`** that every machine/agent resolves identically — the consistent AI-provider experience.

---

## Design

### Part A — provider-routing policy (the goal-#1 piece)
`config/ai-tools/provider-routing-policy.yaml` — single source:
```yaml
roles:                       # task-type → ordered provider preference
  orchestrate:   [claude]
  plan:          [claude]
  implement:     [codex, claude]      # bounded coding → codex; heavy authoring → claude
  review:        [codex, gemini, claude]   # adversarial; ≥2 distinct for T2+
  recon:         [gemini]
  dispatch:      [hermes]
machine_overrides:           # encode hard-won machine facts
  ace-linux-1:
    codex: {heavy_authoring: false, reason: "codex-exec CPU-starved here — review/bounded only"}
reduction_rules:             # from AI_REVIEW_ROUTING_POLICY.md
  user_requests_lighter: "drop to 2-agent, document"
  provider_unavailable: "continue, record missing reviewer"
```
A resolver `scripts/ai/provider_route.py` exposes `route(task_type, machine, attrs) -> [providers]` (pure + CLI). **Resolution order (Codex #4 — no ambiguity):** (1) start from the role's provider list; (2) apply **hard constraints** from `machine_overrides` + task attributes (e.g. `authoring_weight: heavy` removes codex on ace-linux-1) — constraints PRUNE the candidate set; (3) only then rank the SURVIVORS by the utilization scorecard. Constraints always dominate the scorecard, so the scorecard can never re-select a provider a constraint removed. Task attributes (`authoring_weight`, `needs_large_context`, etc.) are typed inputs, not free text.

`AI_REVIEW_ROUTING_POLICY.md` becomes a thin doc that POINTS at this file — but ONLY after a **consumer inventory** (Codex #5): grep for everything that reads the .md (prompt assembly, docs linters, grep-based checks) and confirm none depend on its embedded tables before converting; migrate or keep a generated table if any consumer needs it.

### Part B — registry-driven machine dispatch (Codex MAJOR folded)
Extend `workstation-dispatch.sh` (+ a `dispatch_select.py` core) to:
1. **Role match**: select machines where `task.roles ∩ machine.harness_profile.roles ≠ ∅` (F1 model), in addition to `requires:` capability match.
2. **Two-phase live probe** (Codex #3): a cached probe is used ONLY to skip obviously-bad hosts at *selection*; it NEVER proves readiness. After lease acquisition AND immediately before command execution, run a **just-in-time** probe (license/mount/auth/`git rev-parse`); JIT failure → release lease, do not execute (fail-closed). Cache is a negative filter, not a positive proof.
3. **Lease = versioned CAS + fencing token** (Codex #1/#2 — the load-bearing fix):
   - The lease ref blob stores `{holder, generation:N, token:<uuid>, ttl, renewed_at}`. Creation: non-forced push (arbiter for the FIRST holder). **Reclaim/renewal is a compare-and-swap on the ref SHA**: a contender must read generation N, and push an update that the server accepts only if the ref still points at the SHA it read (lost-update-safe); it writes generation N+1 with a new token. Two would-be reclaimers cannot both win — exactly one CAS succeeds.
   - **Fencing**: the holder's `token` is threaded into execution; every external side effect (GitHub mutation, repo write) is tagged/guarded by the token, and the worker re-verifies it still holds the current token before/through execution. A worker whose token was superseded **aborts its own side effects** → a partition that makes a healthy worker look dead cannot cause double-commit.
   - **Reclaim safety**: stale-reclaim requires BOTH `now - renewed_at > ttl` AND a failed liveness probe, with `ttl` set larger than worst-case (clock-skew + probe-latency + renewal-interval). Workers **renew through execution** (heartbeat the lease), so a slow-but-alive worker keeps its lease.
   - **Idempotency fallback**: tasks that cannot be made fencing-safe must be declared `idempotent: true` (dedup key) to be lease-eligible; non-idempotent, non-fenceable tasks are refused.
4. Canonical state stays GitHub labels + git-ref leases (Telegram = notification only).

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `config/ai-tools/provider-routing-policy.yaml` | single machine-readable provider policy |
| Create | `scripts/ai/provider_route.py` | pure resolver + CLI (`route(task_type, machine)`) |
| Modify | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | point at the YAML (single source; keep prose rationale) |
| Create | `scripts/operations/dispatch_select.py` | pure core: role+capability match, live-probe gating, lease decision |
| Modify | `scripts/operations/workstation-dispatch.sh` | call dispatch_select; add role match, live probe, git-ref lease w/ TTL |
| Create | `tests/operations/test_dispatch_select.py` + `tests/ai/test_provider_route.py` | TDD |

## TDD Test List
| Test | Verifies | Expected |
|---|---|---|
| test_route_review_multi_provider | route('review', a1) | [codex, gemini, ...] ≥2 |
| test_machine_override_codex_authoring | route('implement', ace-linux-1) | codex not first for heavy authoring (override applied) |
| test_route_unknown_tasktype_fails_closed | route('bogus', …) | raises / empty + flagged |
| test_dispatch_role_match | task roles ∩ machine roles | only role-matching machines eligible |
| test_live_probe_excludes_declared_but_unproven | declares cap, probe fails | machine excluded (fail-closed) |
| test_route_hard_constraint_prunes_before_scorecard | authoring_weight=heavy on a1 | codex removed even if scorecard ranks it #1 |
| test_lease_create_non_forced_push_is_arbiter | two first-contenders | exactly one wins |
| test_lease_reclaim_is_cas_on_generation | two reclaimers see gen N | exactly one CAS succeeds → gen N+1 |
| test_superseded_token_aborts_side_effects | worker token superseded | worker refuses to commit (fencing) |
| test_reclaim_needs_ttl_AND_liveness_fail | past TTL but alive (heartbeat) | NOT reclaimed |
| test_jit_probe_after_lease_before_exec | cached-capable but JIT probe fails | release lease, no execution |
| test_non_idempotent_unfenceable_refused | task not fenceable, not idempotent | refused (not lease-eligible) |

## Acceptance Criteria
- [ ] `provider_route.py route review ace-linux-1` returns the policy order; the codex-authoring override is applied on a1 (machine_overrides honored).
- [ ] `AI_REVIEW_ROUTING_POLICY.md` references the YAML as the single source (no duplicated rule tables).
- [ ] Dispatch excludes a machine that declares a capability but fails the **live probe**.
- [ ] Dispatch acquires an atomic git-ref lease (non-forced push arbiter); stale-past-TTL reclaim + split-brain handling tested.
- [ ] `uv run pytest tests/ai/test_provider_route.py tests/operations/test_dispatch_select.py -v` passes; no regression.
- [ ] Lease reclaim is a **versioned CAS** (generation + ref-SHA), not TTL-alone; double-reclaim impossible (test-proven).
- [ ] **Fencing token** threaded through execution; a superseded worker aborts its own side effects (test-proven); non-fenceable + non-idempotent tasks refused.
- [ ] **JIT probe** runs after lease acquisition and immediately before execution; cache is a negative filter only.
- [ ] Provider resolution: hard constraints prune BEFORE scorecard ranking (test-proven).
- [ ] `AI_REVIEW_ROUTING_POLICY.md` migration preceded by a committed consumer inventory.
- [ ] Cross-review (T3): Claude + Codex (+ Gemini if available). **Codex r1 = MAJOR; folded.**

## Risks and Open Questions
- **Risk:** live probe adds latency/SSH dependency; cache probe results with a short TTL; probe failure = exclude, never crash dispatch.
- **Risk:** lease reclaim vs a genuinely-slow (not dead) coordinator → require liveness probe failure + TTL both, not TTL alone.
- **Open (user):** should `provider_route.py` be consumed by the existing review scripts (`scripts/review/*`) in this slice, or only ship the policy+resolver and wire consumers in a fast-follow? Recommendation: ship policy + resolver + dispatch wiring; wire review scripts as fast-follow to bound blast radius.
- **Open (user):** keep Gemini in the default review set given recent quota 429s, or make it best-effort? Recommendation: keep default, degrade-on-429 per existing reduction rule.

## Adversarial Review Summary
| Provider | Verdict | Key findings (folded) |
|---|---|---|
| Codex r1 | **MAJOR → resolved** | (1) lease reclaim must be **versioned CAS** not TTL-alone (else double-execution); (2) split-brain needs a **fencing token** (else partitioned-alive worker loses lease mid-run); (3) cached live-probe can't prove readiness → **JIT probe before execution**; (4) provider precedence ambiguous → **hard constraints prune before scorecard ranking** + typed task attrs; (5) .md→pointer migration needs a **consumer inventory** first. |
| Gemini | pending/optional | dispatch if quota (T3 → 3-agent) |

**Overall:** MAJOR addressed in-plan; remaining gate = user approval.

## Complexity: T3
Cross-machine dispatch (versioned-CAS leases + fencing) + cross-provider policy; full TDD; 3-agent review.
