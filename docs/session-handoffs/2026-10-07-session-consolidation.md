# Session handoff — 2026-10-07 — consolidation of unfinished Claude/Codex work (ace-win-2 workstation)

One Claude session reviewed every Claude and Codex session on this workstation from the
previous seven days (~30 Claude transcripts, ~65 Codex rollouts), compared each against live
GitHub state, and drove the open work to `main` with subagents.

## Merged to main today

| Repo | PRs |
|---|---|
| workspace-hub | #3941, #3948, #3946, #3959 (fleet-snapshot relabel + hourly-job labeller), #3934, #3930 |
| digitalmodel | #2245 (W4 parallel runner), #2249 (W2b open-water riser), #2257 (W5 post-processing) |
| digitalmodel-data | #36 (W2b models), #33 (stack-up DB r1, flange masses), #37 (W3 gap matrix: 18/35 groups unblocked) |
| aceengineer-strategy | #273 |
| worldenergydata | #1132 |
| frontierdeepwater | #17 |
| llm-wiki | #925, #923 |

About 25 stale or superseded PRs were closed, each with a short reason (retired legal-scan
fixes, Deckhand PRs, superseded handoffs/plans, obsolete dependency bumps), plus deckhand
issue #550.

Post-merge health check: main CI green wherever it ran; no failures caused by today's merges;
public-repo diffs (workspace-hub, digitalmodel) contain no client names or physical hostnames.

## Waiting on the owner

The auto-mode permission classifier blocks agents from approving and merging their own or
peer agents' work (`[Self-Approval]`, "Merge Without Review"), from launching `codex exec`
("Create Unsafe Agents"), from `git worktree remove`, and from killing processes.

| Item | Action |
|---|---|
| aceengineer-strategy #282 (CP growth plan Rev 01, M1–M7 resolved) | Merge with a **merge commit** (not squash); the plan cites commit 7d6eed9 |
| digitalmodel #2280 (BRep experiment) | Needs a second-provider review, then owner merge |
| llm-wiki-fdas #87, #91–#94 | verify-gate needs the review record + `verified` label; #87 has Claude PASS and Codex PASS (round 3); merge #94 after #92 |
| llm-wiki-acma #398 | Conflicts with #415 in five files; decide which retention record wins |
| worldenergydata #1146 | Clean; merge it, then `@dependabot rebase` #1133/#1135/#1136 and merge |
| digitalmodel-data #35 (888 MB, 7,300 per-case JSON files) | Recommendation: move the 877 MB of per-case results to ace-linux-1 `/mnt/ace` with a SHA-256 manifest; keep ~11 MB of ledgers/summaries in git. Then update #38 (`capacity`→`allowable`, `missing` cases, stroke excursion; full list in the #38 thread) |
| ~15 owner-decision PRs | FFS / ship-plate / CP preliminary studies (dm #2289/#2290/#2291 + data #44/#46/#47), dm #2146 #2114 #2102 #2116, llm-wiki #942 #947, aceengineer-admin #54, hobbies #4, teamresumes #31 |
| Public-repo identifier flags | dm #2289 and ws #3739 contain physical host labels; scrub before merge. Commit fe4ca98 left two physical hostnames in workspace-hub history (fixed at tip by #3959); history rewrite is the owner's call |
| Fleet snapshot writer | Runs only on the collector VM outside version control; must call `fleet_snapshot_labels.py` (issue #3944) |
| llm-wiki Pages workflow | Fails with 404 until Pages is enabled or the workflow is disabled |

## Workstation state

- The C: drive hit 0 bytes free. Cause: eight full Codex clones of digitalmodel (~49 GB) plus a
  16 GB npm cache. The clones (all merged or pushed) and caches were removed, leaving 68 GB free.
- 18 clean, merged worktrees (~12 GB) are queued for owner removal via a script in the
  session scratchpad (`remove-stale-worktrees.ps1`); it re-checks each worktree before removing it.
- Kept because they hold uncommitted work: `wt-wiki-marine-equipment` (six new wiki pages, branch
  never pushed), `wt-admin-meeting-58-*`, and five `wt-hub-*` worktrees with harness-sync edits.
- Codex terminal sessions (idle since 2026-10-02) can be exited; their transcripts persist.
- Lesson: Codex should use worktrees, not full clones, and delete them once their PRs merge.

## Next session

Start with the owner-action table above. Do not re-triage the backlog; the classification
(merge-ready / finish / close / owner-decision) is recorded in this session's PR comments and here.

## Update 2026-10-08

Landed after the first draft of this handoff: digitalmodel-data #35 (per-case results moved to
`/mnt/ace` with a SHA-256 manifest, mirrored on ace-linux-2), #38 (W5 rerun on current digitalmodel), #53
(#33 stack-length gap closed at 19.686 m from the archived decks); llm-wiki-fdas #87, #91, #92, #94, #93;
llm-wiki-acma #398, #399. Parallel sessions merged workspace-hub #3786, aceengineer-admin #54,
digitalmodel #2102 and #2116, and worldenergydata #1147, which superseded #1146 (closed; dependabot rebases
requested).

The remaining items are cards on the owner's all-sessions decision board (2026-10-08) and wait for it:
A03 (#2280 review), A04 (study PRs dm #2289/#2290/#2291 + data #46/#44/#47), A05 (record the ace-linux-2
mirror; a ready patch is in this session's scratchpad as `a05/a05-mirror-manifest.patch`; open a backup
issue), T06 (marine-equipment pages to a draft PR), E09 (llm-wiki housekeeping). Most depend on the E01
settings change. llm-wiki-acma #409 fails only checks that also fail on main (hostname violations from #416,
workbook tests fixed by #418) and is ready once the owner accepts that reading.
