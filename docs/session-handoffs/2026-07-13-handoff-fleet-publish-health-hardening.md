# Session handoff — fleet publish-health monitoring + hardening (2026-07-12/13)

**Sessions:** ace-linux-1, Claude (Fable 5), 2026-07-12 → 2026-07-13.
**Origin:** machine hang investigation → equivalence-publish gate deadlock → fleet-wide publish-health monitoring → three latent fleet bugs found by that monitoring and fixed.

## Completed (all merged by owner, content-verified on origin/main)

| Item | Issue / PR | What |
|---|---|---|
| Hang root cause | memory `reference_ace_linux_1_oom_hang_2026_07_12` | runaway claude.exe 17.6G → swap 100% → livelock; systemd-oomd unarmed for swap; **earlyoom installed**; ~23G root-disk reclaimed; 67/87 stale worktrees removed |
| Gate deadlock fix | #3500 / PR #3501 | `equivalence-state` pushes with audited `GIT_PRE_PUSH_SKIP=1`; ref created (was NEVER created — every publish re-ran the full tier-1 suite 60+ min, forever) |
| Publish-health monitoring | #3502 / PR #3503 | comparator `absent-fingerprint` (registry roster) + `publish-slow`; sentinel writes `publish-health.json` + stamps duration into the fingerprint; equality-matrix `publish_health` row (PUBLISH-OK/-STALE/-GATED); skill `workspace-hub/equivalence-publish-health` (propagated) |
| gpu-claw enrollment | #3507 / PR #3508 | registry + harness-config entries (linux, contribute-minimal, ws root = relocation target `/home/undi/ws/workspace-hub`) |
| Rescued plan row | PR #3510 | dm#1521 aqwa-diagnostics row from ace-linux-2's staged-never-committed state |
| Sentinel fleet schedule | PRs in #3512 | **root cause of #3505/#3506**: win boxes were never in the `equivalence-sentinel` machines list; added ace-win-1/2 + gpu-claw + sim-worker role; gpu-claw into equality-report |
| setup-cron OS fix | PR #3515 | Task-Scheduler skip keyed on registry `os`, not `contribute-minimal` variant (gpu-claw got zero crons) |
| Machine-keyed fingerprints | #3516 / PR #3519 | role-keyed blobs clobbered same-role boxes (REPRODUCED); blobs now `<machine_id>.json`, registry-driven `resolve-identity`, self-cleaning migration, comparator labels machine_id-first |
| Box heals | #3504 closed | ace-linux-1 wedge reset (backup tag `backup/pre-wedge-reset-2026-07-12`); ace-linux-2 synced + staged work rescued to `save/al2-staged-2026-07-13` + uv snap→`~/.local/bin` symlink (cron PATH) |

## Fleet state at handoff

| Box | Heartbeat | Publishing | Notes |
|---|---|---|---|
| ace-linux-1 | live | ✅ | slow 05:2x-window publishes (210s) — matrix flags `publish-slow`; watch |
| ace-linux-2 | live | ✅ | cron fixed (uv symlink); stash `pre-sync-churn-2026-07-13` on box (recoverable churn) |
| gpu-claw | live, dispatching | ✅ (as `unknown.json`, migrates to `gpu-claw.json` next cycle) | **crons NOT installed** — inbound ssh tunnel down 2.5h+ while outbound healthy (evidence for wh#3497 tunnel-topology item) |
| ace-win-1 | live | ❌ | operator session needed: gh auth + scheduler apply + hub pull (#3505; no remote path by design) |
| ace-win-2 | live | ❌ | operator session (or scheduler self-render if its jobs pull the hub — unverified) (#3506) |

Blob migration is self-driving: each box's next 6h sentinel cycle republishes machine-keyed and cleans its own legacy blob (boxes need their normal checkout auto-sync to pick the new script up first).

## Open items → owners

1. **gpu-claw crons** (owner or tunnel): console one-liner —
   `cd /home/undi/ws/workspace-hub && git pull --ff-only && PATH=$HOME/.local/bin:$PATH bash scripts/cron/setup-cron.sh`
   Do NOT execute the repo moves in `/home/undi/ws/RELOCATION-ISSUE.md` while dispatch is live; the `ws/digitalmodel` symlink must be removed before the eventual `mv`.
2. **#3505/#3506 win-box operator sessions** — UNBLOCKED by #3519; steps in the issues.
3. **Delete rescue branch** (owner, content landed via #3510): `git push origin --delete save/al2-staged-2026-07-13`
4. **Watch items (self-driving via matrix):** primary 05:2x `publish-slow` pattern (if chronic slow-but-green: split slow/failed verdicts or bump the 60s threshold); blob-migration convergence; gpu-claw staleness until crons land.
5. **wh#3497 tunnel-topology check** — today's asymmetric gpu-claw outage (outbound fine, inbound dead) is direct field evidence.

## No-external-action status

Nothing user-facing sent (no email/Telegram). All GitHub activity is in vamseeachanta repos: issues #3500–#3516 range + PRs listed above, all owner-merged. Remote machines touched only where owner-named: ace-linux-2 (heal, authorized), gpu-claw (non-disruptive onboarding, authorized). No repo moves, no deletions beyond owner-approved cleanup.

## Key artifacts

- Memory: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/reference_ace_linux_1_oom_hang_2026_07_12.md` (full incident + hardening trail)
- Skill: `.claude/skills/workspace-hub/equivalence-publish-health/SKILL.md`
- Worktree audit (removal manifest): session scratchpad `worktree-audit.tsv` / `worktree-removal.log` (session-temp; the 20 kept worktrees are enumerated in the #3502-era analysis and memory)
