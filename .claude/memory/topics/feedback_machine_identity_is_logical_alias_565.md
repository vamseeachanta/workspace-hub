> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-31
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_machine_identity_is_logical_alias_565.md

---
name: feedback_machine_identity_is_logical_alias_565
description: "All fleet machine-identity work routes by logical alias (deckhand#565); physical names are private-tier only — and the rule applies to plan/handoff artifacts too"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 415e1ea0-c123-40b6-b864-8ad1d92aefdd
  modified: 2026-07-31T03:36:28.338Z
---

> **SUPERSEDED 2026-07-30 by deckhand#581 — read that first.** Owner decision: retire the
> logical-alias indirection; route by **canonical lowercase short hostname** in the **private tier
> only** (deckhand policy/queue/heartbeat, admin machine-ecosystem). **workspace-hub is PUBLIC and
> keeps neutral routing tokens** (`ace-linux-1`, `ace-linux-2`, `ace-win-1`, `ace-win-2`,
> `gpu-claw`) — no ACMA hostname in a public label. The field name `licensed_run.host_aliases`
> **stays**; only its values and validation change, to minimise call-site churn. Casefold on join
> (`tailscale status` reports Windows nodes uppercase). Historical `queue/requests/lr_*` records are
> **never rewritten** — a read-path-only compat map covers the 12 affected.
>
> Why #565's premise failed: it justified aliases as a privacy boundary that was never enforced
> (physical hostnames were already in public repos at scale — 794 files in digitalmodel alone, as
> OrcaFlex provenance stamps). Meanwhile the indirection caused an outage-class defect — an alias
> stayed bound to a retired machine while the live agent ran elsewhere, undetected ~18 days.
> **A hostname cannot silently drift from itself.** The two rules below that INVERT: heartbeat
> filenames now track hostnames (the freeze test becomes wrong, not merely stale), and tests
> rejecting hostname-shaped values must flip.
>
> Still true from #565: the private/public tier split, `verified_at` on physical bindings, deckhand
> as the promotable tier, and the "scan your own plan artifact" discipline below.

deckhand#565 (CLOSED, `status:plan-approved`) was the governing contract for **any** work
touching machine identity, routing labels, or the dispatch lane. Its rules:

- `host` values are **logical routing aliases**, never physical hostnames. The canonical set is
  `licensed_run.host_aliases` in `deckhand config/deckhand/policy.yml` — five entries, already
  committed and validated.
- The alias→physical binding lives **only** in the private tier
  (`aceengineer-admin/machine-ecosystem/`) and is a *claim* carrying `verified_at`, verification
  method, and `mismatch` status — never treated as settled fact.
- `test_heartbeat_filename_remains_exact_alias` **freezes** existing heartbeat filenames. Do not
  "normalize" them, even though the directory visibly mixes hostname-style and alias-style names.
- deckhand is the **promotable** tier: the physical-name ban applies there regardless of the repo
  being git-private. Physical detail belongs in `aceengineer-admin`.
- From **2026-09-01 UTC**, a policy omitting `host_aliases` fails startup. Declared-alias
  validation is already live; only the missing-list failure mode is deadline-gated.

**Why:** four namespaces exist for the same five boxes (equality label, hostname, tailnet node
name, lane alias). Any plan that picks a different key, or that keys routing to tailnet/physical
names, is a breaking change to a live fail-closed lane.

**How to apply:** before designing anything that names a machine, read the #565 plan at
`deckhand/docs/plans/2026-07-14-issue-565-logical-host-private-attestation.md`. Then run a
private-value scan over **your own artifact** — plans, handoffs, and issue comments are files like
any other. On deckhand#579 the plan itself reproduced physical hostnames, IPs, and account
principals while proposing to commit to deckhand; two drafts of self-review missed it and an
adversarial reviewer caught it. #565's redaction is also incompletely applied (three deckhand files
still leak), which implies the private-value scan test is absent or unwired from CI — so do not rely
on CI to catch it for you.

Related: [[feedback_verify_subagent_line_citations_not_just_claims]],
[[feedback_absence_of_signal_reads_as_success]], [[project_fleet_dispatch_ecosystem_epic]]
