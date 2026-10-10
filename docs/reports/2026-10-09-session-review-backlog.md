# Session review backlog — 2026-10-09 (public summary)

Source: every Claude Code and Codex session from 2026-09-09 to 2026-10-09 on the four reachable fleet machines (ace-win-2 270, ace-win-1 641, ace-linux-1 1115, ace-linux-2 107; 2,133 sessions, 950 substantive after dropping automated distill, routine and reviewer runs). 243 raw unfinished items were deduplicated to 123 rows and checked against live PR/issue state and the owner decision board saved on 2026-10-09.

This file lists rows for **public repositories and fleet operations** in full. Rows for private repositories (client wikis, private data, strategy, admin, personal) are counted below only; the full table is kept off this repository with the owner decision boards.

Classes: **MERGE-APPROVED** owner approved, only the merge is left · **AGENT** an agent can finish it · **OWNER** needs an owner decision, sign-off or manual step · **COMPUTE** solver run, owned by the compute session · **PARKED** deferred by the owner. A bare `#n` means the section's own repo.

## workspace-hub
| ID | P | Class | Item | Remaining work | Refs | Last activity |
|---|---|---|---|---|---|---|
| HUB-01 | P0 | MERGE-APPROVED | Fleet snapshot labelling (E02) | Mark the draft ready and merge it. | #4026, #3944 | 2026-10-09 |
| HUB-02 | P0 | MERGE-APPROVED | Local private-repo CI runner (T03) | Mark the draft ready and merge it. This is the CI route around the Actions billing block. | #4025 | 2026-10-10 |
| HUB-03 | P1 | MERGE-APPROVED | Team summary generator and scheduler fingerprint sign-off (E01) | Merge #3969 (`gh pr merge 3969`). Then review and merge #3970 (task-dispatch readiness, #3968) and #4033 (review document links). | #3969, #3970, #4033, #3967, #3968 | 2026-10-10 |
| HUB-04 | P1 | AGENT | Snapshot writer routed through the fail-closed labeller | Implement #4027: bring the VM writer in-repo, run the labeller before staging, and diagnose the safety-net refusal. Per E03, retire dated files in favour of a single latest.json. Fix the S01 test, which fails on main; latest.json has not refreshed since 09-27. Confirm the next daily run is green, then close #3944. | #4027, #3944 | 2026-10-10 |
| HUB-05 | P1 | OWNER | Local CI one-time setup on ace-linux-1 (after HUB-02) | Create the ghrunner user, enable linger, create a fine-grained token (statuses write, contents and PRs read), run gh auth as ghrunner, clone the repos, run install-local-ci.sh and enable local-ci.timer. | #4025 | 2026-10-10 |
| HUB-06 | P1 | AGENT | Drop deckhand from the local-CI repo list (T04) | Remove deckhand from repos.yaml as a follow-up to #4025. | #4025 | 2026-10-10 |
| HUB-07 | P1 | OWNER | Source-watch timer retirement (card E12/M09) | Mark #3981 ready and merge it. Then run disable-cnh-source-watch-timer.sh --apply on ace-linux-1, comment out the routine entry and close worldenergydata#720. If #4032 merges first, regenerate the #3981 scheduler report. The stale codex-e12 merge is covered by OPS-04. | #3981, worldenergydata#720 | 2026-10-10 |
| HUB-08 | P1 | OWNER | Post-merge apply steps for merged label/memory PRs | The PRs are merged but none of these steps shows as run: relabel-agent-to-ai.sh --apply (#3979, optionally with --include-closed); relabel-status-to-dispatch.sh --apply (#3980); sync-canonical-labels.sh --apply (#3971); the X02 schedule-pause scripts (#4024). F3 (route.py precedence) also needs a decision. | #3979, #3980, #3971, #4024 | 2026-10-10 |
| HUB-09 | P1 | AGENT | L2 labels-as-queue (clean rebuild) | Run a valid cross-review on #4032; the earlier Claude/Agy runs gave NO_OUTPUT and Codex failed. Close the superseded #4016. Then the owner merges. The bulk migration/archive script stays deferred. | #4032, #4016, #3999 | 2026-10-10 |
| HUB-10 | P1 | AGENT | L6 auto-safe repo hygiene | Merge origin/main into #4013. Resolve the overlap with #3978/#4012 in favour of main: keep the unpushed-HEAD check and the linked-worktree classification. Then review. The owner confirms the #3475 digest re-affirmation at merge. | #4013, #4003, #3992 | 2026-10-10 |
| HUB-11 | P1 | OWNER | mystran registry entry and #3475 digest re-attestation | Check the 3 failing tests against main (agent). Confirm the change still applies after #3969's sign-off. Merge #4030 and close #3909. | #4030, #3909 | 2026-10-10 |
| HUB-12 | P1 | OWNER | CableDyn registry link | Merge #4031, then close #3931. | #4031, #3931 | 2026-10-10 |
| HUB-13 | P1 | OWNER | L8 prune wave 1 | Merge the paired private-org PR first, then #4019. Remove the temporary org clone afterwards. | #4019 | 2026-10-10 |
| HUB-14 | P1 | OWNER | AGENTS.md hub-contract coverage | Merge the two private-wiki AGENTS.md PRs. One PR's verify-gate never started because of billing, so it needs an admin-merge or the `verified` label plus a verification record. Decide the wording PR and whether to trim llm-wiki/AGENTS.md to 20 lines. Then close #3958. | #3958, private-wiki PRs, private-wiki PRs, a private-wiki PR | 2026-10-10 |
| HUB-15 | P1 | OWNER | ace-win-2 seat mapping (implements E05) | Merge #4029. An agent then updates the 10-01 ecosystem-loop handoff note. | #4029, #4024 | 2026-10-10 |
| HUB-16 | P1 | OWNER | OrcaFlex licence seat and leak-remediation rule | Confirm whether the Python session holding the OrcaFlex seat on the standby Windows host is still needed; OrcaFlex/OrcaWave dispatch is blocked until it is released. Review draft #4028 (leak remediation must also scrub commit, PR and issue text). | #4028 | 2026-10-10 |
| HUB-17 | P1 | AGENT | L3 routing/protocol follow-through | #4010 merged while CHANGES-REQUIRED was open. Verify the three #4010 review findings on main. Then rebuild the dispatch coordinator loop (closed #4011) cleanly on main for #4000. | #4010, #4011, #4000 | 2026-10-09 |
| HUB-19 | P2 | AGENT | Snapshot dry-run mutates files (E07 MAJOR) | Verify on main that `commit-learning-artifacts.sh --dry-run` no longer writes through redact_copy. If it still does, fix it and the test that asserts the mutation (test_commit_learning_artifacts_redaction.py:99). | codex/e07-memory-snapshots | 2026-10-09 |
| HUB-20 | P2 | OWNER | Reporting conventions decisions C01–C06 | Reply on #3925 with "all recommended" or exceptions; C06 then starts the 60-minute synthetic pilot. Resolve M4: which prevails, owner presentation instructions or client document control? Fleet adoption is unverified. | #3925 | 2026-10-10 |
| HUB-21 | P2 | OWNER | Rewire governance leftovers | Apply the branch-protection settings for L5 (#4002). Apply the completeness labels before closing #3998. Decide whether to close #3989 as a duplicate. | #4002, #3998, #3989 | 2026-10-09 |
| HUB-22 | P2 | AGENT | Review packet builder r2 MAJORs | Confirm on main (after #3974) whether these are fixed: the path collision; a mixed packet and manifest left by a failed publish; verify not checking packet bytes; env-var values bypassing redaction; the misclassified gh auth probe. Fix whatever remains and close #3973. | #3973, #3974 | 2026-10-08 |
| HUB-23 | P2 | AGENT | Identifier-gate retirement rollout | Verify the rollout on each fleet machine and record the result per machine. Delete the leftover temporary archive (deletion was blocked by policy). Close #3936. | #3936 | 2026-10-09 |
| HUB-24 | P2 | AGENT | Session closeout automation | Implement the hooks and receipts for worktrees, branches, stashes and multiple providers. 181 unrelated worktree changes stay preserved until ownership review (OPS-04). | #2256 | 2026-10-09 |
| HUB-25 | P2 | AGENT | Simulation study workflow epic | Revise the plan for r2 blockers F1–F8 (budget stop, Pilot B conservation criterion, Pilot A definition, scheduler rule, citation gate failing open, undeclared dependency). Then put the 11-card decision board to the owner. | #3894 | 2026-10-09 |
| HUB-26 | P2 | AGENT | ecosystem-sync.sh pushes directly to main | Route the sync through the PR path required by #3957. | #3985 | 2026-10-09 |
| HUB-27 | P3 | AGENT | OrcaFlex integrity, rainflow, solver-marker and generator-consolidation issues | Revise the plans for MAJOR findings: cycle tables, reversal convention, deletion safety. Fix the #3841 solver markers. File the gate:completeness scorer defect (python not resolvable from MSYS bash; stale matrix snapshot). The owner chooses the bundle route (transfer or rebuild). | #3838, #3839, #3841, #3843 | 2026-09-12 |
| HUB-28 | P3 | AGENT | Soul drift and abs-path gate drift | Address the #3833 drift gate. File the abs-path regression (1015 violations against the 463-entry baseline); run it on a Linux node without --update-baseline. | #3833, #3834, #3835 | 2026-09-11 |
| HUB-29 | P3 | AGENT | Small unmerged branches and test debt | Commit and PR codex/o03-audit-fix. Handle the standards catalog N1 TTL cap and file R1/R2. Fix the next-wave-handoff-bundle catalog entry and the whitespace drift. Resolve the fleet check-kit B1–B3 and matrix R1/R2. Fix the test_cron_audit KeyError 'repository-sync'. Address the missing validate-queue-state.sh in pre-commit. Confirm whether the plan-gate retirement M1/M2 residue landed. | — | 2026-10-09 |

## digitalmodel
| ID | P | Class | Item | Remaining work | Refs | Last activity |
|---|---|---|---|---|---|---|
| DM-01 | P1 | OWNER | Plate-buckling study | Merge #2311 on its own and close draft #2290. | #2311, #2290 | 2026-10-10 |
| DM-02 | P1 | OWNER | FFS epic Wave 1 plan-lites | Reply "Wave 1 approved" on #1057 and choose A (loaders read the private dataset at run time; recommended) or B (user-supplied tables) for the #2175 Annex C/E tables. Implementation follows. | #1057, #2175, #2181–#2185 | 2026-10-10 |
| DM-03 | P2 | OWNER | Crack-FE report Rev C | Provide the Rev C review comments. An agent then applies them in crack_fe_report.py, regenerates the report, updates the revision metadata and does browser verification. | #2157 | 2026-10-06 |
| DM-04 | P2 | AGENT | Crack-FE assessment MAJOR findings | Fix four phases:<br>• P3: run() can bypass receipt_problems through an injected validator, and extrapolated life is exported as case=base.<br>• P0b: NCNV is accepted as collapse without corroboration.<br>• P1: Threshold accepts a NaN dk_th.<br>• P0a: receipt provenance gaps.<br>Then re-review. | #2157 | 2026-09-26 |
| DM-06 | P1 | AGENT | Hull parametric forms #2241 items 3–4 (A01 approved) | Dispatch the Codex jobs for semi-sub/spar generators and moonpools, one at a time. Per T05, PR the docs/2241-brep-validity-plan file and then delete the branch. Finish the item 2 second-provider review and post the changes to #2241. Still open: bracing and AQWA-comparator decisions. Item 5 waits on items 1–2. | #2241 | 2026-10-10 |
| DM-07 | P1 | AGENT | .sim validity checker findings (merged #2307) | Verify on main and fix with regressions: the first passing Line skips later Lines; a missing completion flag defaults to success; SimulationPaused/StoppedUnstable are accepted as completed. | #2307 | 2026-10-09 |
| DM-08 | P2 | AGENT | OrcaFlex generator rework (#2093) | On rework/2093-orcaflex-generator: clear GIT_DIR, GIT_WORK_TREE and GIT_COMMON_DIR before the checkout probe (openfoam_batch_config.py:275–280); add .gitattributes eol rules for the smoke template and reference files; restore sys.path in test_mooring_semantic_preservation.py:124. Add regressions and open a fresh PR on current main (#2294 is closed). | #2093, #2294 | 2026-10-09 |
| DM-09 | P2 | AGENT | Full-suite failures | Triage the 213 failures and 13 errors (assetutilities is missing from the env) into buckets, and propose a disposition for the owner. | #2312 | 2026-10-09 |
| DM-10 | P1 | OWNER | PyPI publication controls after #2309 | Create the `pypi` environment and protect it with a required reviewer. Address the documented OIDC exposure. Issue the publication decision card. | #2309 | 2026-10-09 |
| DM-11 | P2 | OWNER | Archive manifest human holds | Decide the 1,283 human-hold files. The removal list is then reconciled; #2304 closed without merging. | #2293, #2304 | 2026-10-09 |
| DM-12 | P2 | AGENT | Installation report post-merge verification | Run the tests the reviewers could not run. Verify the 156/156 retained-audit rebuild and reconcile the "149 of 156 verified" config line with the summary. Advance #2131. | #2168, #2131 | 2026-10-08 |
| DM-13 | P2 | AGENT | Naval-arch R02 findings | Fix the citation, clipping, performance and size-limit findings listed in #2314. Split mesh_hydrostatics.py (756 lines; the guardrail is 400). Reproduce the 31–51% Holtrop discrepancy. | #2239, #2314 | 2026-10-09 |
| DM-14 | P2 | AGENT | Riser W510 significant-range follow-up | Establish caller-wide sections_m geometry validity. Fix the coupling within 0.1 mm of End B, which loses its upper-side requirement. The confirmation review could not run tests. | #2292 | 2026-10-08 |
| DM-15 | P2 | AGENT | Campaign state and solver benchmark pack | Finish the remaining #2298 slices. Address the #2300 review findings left after #2302 merged: licence wait included in the timed span, divide-by-zero at compare.py:61, a lock that is not machine-wide (runner.py:124), and no variant/repeat/warmup validation. Add failure-path tests. | #2298, #2300, #2302 | 2026-10-08 |
| DM-16 | P2 | AGENT | Mudmat eccentricity bug | Bearing capacity reduces the wrong dimension under eccentricity. Fix it with a regression test. | #2105 | 2026-09-15 |
| DM-18 | P3 | OWNER | Diffraction contract issues | Decide the reference-point split and the #1581 rescope (AQWA fail-closed plus provenance). Procure the AQWA manual (PMAS/FISK reference). Then plans are revised; #1582 lands first. | #1579–#1582, #2107, #2108, #2111, #2112 | 2026-09-19 |
| DM-19 | P3 | AGENT | ANSYS example decks | Add padeye negative tests and fix the minors. Run the two-mesh singularity check, then the golden. Write the offline pressure parser (24 loaded faces). Owner cards: hole region, a third mesh run, PLANE182 or PLANE183. | #2094 | 2026-09-15 |
| DM-20 | P3 | PARKED | CP report draft visual check | C14 "Later" (the report is open on ace-win-2). #2281 closed at 11/16 per C13; cases A–E are in DMD-11. | #2281 | 2026-10-10 |
| DM-21 | P3 | OWNER | Private architecture trial A01: verdict inconclusive | Read the private trial report and decide whether to continue. | — | 2026-10-09 |
| DM-22 | P3 | AGENT | ABS ships citation branch | Merge the llm-wiki branch docs/abs-gn-ships-2017. Fix the calc-011 line 362 locator ("ABS §2, Table 4"). | #2259, #2271 | 2026-10-01 |

## Fleet operations
| ID | P | Class | Item | Remaining work | Refs | Last activity |
|---|---|---|---|---|---|---|
| OPS-01 | P0 | OWNER | GitHub Actions billing block | Clear the spending limit or rely on HUB-02/HUB-05. Then rerun CI on the open private-wiki PRs. | private-wiki PRs, private-wiki PRs | 2026-10-10 |
| OPS-02 | P2 | OWNER | Owner-only host actions | Run `sudo snap remove codex` on ace-linux-1 and ace-linux-2. Grant sudo on the Linux workstations. Set a quiet window for the git update on ace-win-2 and ace-win-1. Install the ws helper. An agent then fixes the non-interactive SSH PATH ($HOME/bin) and closes #3964. | workspace-hub#3964 | 2026-10-09 |
| OPS-03 | P1 | AGENT | Relaunch the 15 goals that never ran (T01) | Relaunch them three at a time on ace-win-2 and carry out the remaining board answers. | — | 2026-10-10 |
| OPS-04 | P2 | AGENT | Worktree and residue hygiene (report first, per #3978) | On ace-linux-1: dirty Codex worktrees, the locked n05/t04, and local-only heads. On ace-win-2: Codex task worktrees with unpushed commits, the CP worktrees (cp2259, cp2264, cp-fixture), the interrupted #2241 clone, the ci-pr443/449/455 worktrees after merge, and the review-exit worktree. Also the stale riser w2 worktrees on ace-win-1, a private-wiki locked agent worktree and the /tmp scratch dirs. | workspace-hub#3978 | 2026-10-10 |
| OPS-05 | P3 | AGENT | Fleet repo consistency | Confirm no rescue branch reached a public repo. Reconcile ws checkouts across the five hosts. List unpublished branches. CAD-DEVELOPMENTS fetch returns 403 and needs the owner to restore access. | — | 2026-10-10 |
| OPS-06 | P3 | OWNER | SSH to another office workstation | Provide administrative access so OpenSSH can be enabled. | — | 2026-10-07 |
| OPS-07 | P2 | AGENT | `codex exec` denied in goal sessions (E09) | The PM tests and reports the cause. | — | 2026-10-09 |
| OPS-08 | P2 | COMPUTE | Fleet compute program toward client results | Schedule licensed and open-source runs on the campaign contract. Blocked on HUB-16 (seat) and DM-15. | digitalmodel#2298 | 2026-10-10 |

## worldenergydata
| ID | P | Class | Item | Remaining work | Refs | Last activity |
|---|---|---|---|---|---|---|
| WED-02 | P2 | AGENT | Catalog lane follow-up | Rebase #1136 now that #1149 is merged. Mark #1150 ready after CI. Check whether the 11 failures in test_cost_estimator.py and test_integrations.py also occur on main. | #1136, #1150, #1144 | 2026-10-09 |

## Private repositories (counts only)

| Class | Rows |
|---|---|
| AGENT | 31 |
| COMPUTE | 3 |
| MERGE-APPROVED | 4 |
| OWNER | 26 |
| PARKED | 2 |

Public rows above: 57 (AGENT 31, COMPUTE 1, MERGE-APPROVED 3, OWNER 21, PARKED 1). Private rows: 66.
