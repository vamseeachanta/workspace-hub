# Session Handoff — 2026-05-04 (#2628 Phase 1, halted by disk-full)

## Why we stopped

Disk-full hit during ws-hub worktree creation for sub-task G. Bash tool returned `pwd: write error: No space left on device`. All subsequent Bash commands failed (no exit code, no output). Read tool still works because it doesn't write to /tmp.

## What was accomplished this session

| Item | State | Reference |
|---|---|---|
| #2580 (citations + capsys) | CLOSED status:done | both PRs landed (#542, #544) |
| #2510 (chip CAD plan) | OPEN status:plan-approved | r15 patches landed, label re-anchored |
| #2559 (OCIMF Tandem wiki) | CLOSED status:done | landed at 14b46c0ce |
| #2614 (hydrodynamics 16-failure sweep) | CLOSED status:done | 4 PRs landed (#549/#550/#551/#553) |
| #2616 (mystery-tests sweep) | CLOSED status:done | 5 cluster trackers filed |
| #2621 Cluster B (worldenergydata skipif) | CLOSED status:done | digitalmodel#568 admin-merged |
| #2622 Cluster C (drop -p no:capture) | CLOSED status:done | digitalmodel#569 admin-merged |
| **#2628 (domain-divided CI)** | OPEN **status:plan-approved** | **plan at `62af5be26` with all 5 decisions locked** |

## Phase 1 (sub-tasks A+F+G) — DISPATCH WAS HALTED

Worktrees attempted:
- `dm-2628-phase1-a-domains` — partial (background command never reported done)
- `dm-2628-phase1-f-codeowners` — partial
- `ws-2628-phase1-g-agents` — confirmed FAILED mid-checkout (disk-full)

Need cleanup of all three before retry next session.

## Decisions locked in #2628 r1 (2026-05-04)

- **D1**: keep `misc` as transitional bucket; force-migrate by Phase 5
- **D2**: silent in Phase 2 (no PR comments); evidence-only at Phase 3
- **D3**: 2-week cutover overlap window
- **D4**: pytest.ini --maxfail=50 removal ATOMIC with .claude/quality-gates.yaml v2 in Phase 2
- **D5**: Cluster A (#2623) is polluter bisect, not autouse purge fixture

## Open trackers awaiting work (with locked strategies)

- #2623 Cluster A — bisect (D5)
- #2624 Cluster D — adds redis/psycopg2/motor only to `infrastructure-core` domain
- #2625 Cluster E — picked up organically by `marine-engineering` domain owners post-cutover

## Next-session checklist

1. **Free disk space FIRST** before any operation:
   - `df -h /mnt/local-analysis /tmp /`
   - `du -sh /mnt/local-analysis/agent-worktrees/* | sort -h`
   - Remove stale `/tmp/dm-citations-fix`, `/tmp/dm-yml-fix`, `/tmp/dm-qg-repro` (~500MB-1GB each)
   - Clear `/tmp/qg-*.log`, `/tmp/comment-*.md`, `/tmp/plan-*.md`, `/tmp/*-2628-*.md` from this session
2. **Verify and prune partial Phase 1 worktrees**:
   - `git worktree list` (from digitalmodel and workspace-hub)
   - Remove anything matching `2628-phase1-*` that's incomplete
3. **Resume Phase 1 dispatch**:
   - 3 parallel agents per `superpowers:dispatching-parallel-agents`
   - A: write `tests/DOMAINS.md` in digitalmodel (16-domain table per #2628 plan §Sub-task A)
   - F: write `digitalmodel/CODEOWNERS` (default `@vamseeachanta` per D1 of session)
   - G: insert "always test by domain during dev" directive into workspace-hub `agents.md` + `CLAUDE.md` per #2628 plan §Sub-task G
   - Each lands as separate PR, file-disjoint, any merge order
4. After Phase 1 lands, dispatch Phase 2 (B+C with locked D2/D4)

## Latent followups still tracked

- digitalmodel#552 — CRLF/LF inconsistency in aqwa_backend.py (low priority)
- workspace-hub#2129 — broader quality-gates audit umbrella

## Memory worth promoting next session

The "session disk-full halted dispatch" event suggests a memory entry like `feedback_disk_full_halts_bash_silently` — when Bash tool returns no output and exit-fails, suspect disk exhaustion before suspecting hooks or shell corruption. Read tool still works (different write path).

Also: per-session worktree count grew to ~10+ (4 from #2614 + 2 from #2616 quick-wins + 3 from Phase 1 attempt + various ws-hub plan worktrees + the pre-existing /tmp/dm-* scaffolds). Each worktree is a full digitalmodel checkout (~250MB). Worth a `feedback_worktree_disk_quota_aware` rule: track cumulative agent-worktree disk usage and prune aggressively after each cluster of work lands.
