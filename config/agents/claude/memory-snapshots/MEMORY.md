# Workspace Hub Memory

> Curated live index. The COMPLETE 302-entry record (title-only pointers) is split
> across `MEMORY-archive.md` (121 recent) + `archive/aged-out.md` (181 aged) —
> grep BOTH for anything not below; full detail lives in each topic file here.

## Active & Recent Projects
- [Fleet dispatch ecosystem (wh#3497)](project_fleet_dispatch_ecosystem_epic.md) — 2026-07-13: EPIC, ace-linux-1 single dispatch surface + others headless. ✅ **PHASE-6 SMOKE rc 0 on gpu-claw** (csv+json only; dm#1560 CLOSED); 4 defects burned → #561/#562/dm#1563 MERGED, #563 OPEN (leak-check .csv false-pos); twins filed dm#1564 (orcaflex base-config — will hit ace-win-1 canary) + dm#1565 (work dirs in scope repo). HEARTBEAT ×5; ace-linux-2 promo prompt at /mnt/local-analysis/HANDOVER-onboard-ace-linux-2-execution-host.md. RULE: map detail PRIVATE-only. NEXT: merge #563; reboot test + 48h soak + tunnel-topology check → VPN retire (deckhand#557)
- [aceengineer.com redesign — Subsea7 theme](project_aceengineer_website_redesign_subsea7.md) — 2026-07-12: capabilities-first + Subsea7 theme (navy #0b3d5c/teal #2BB2A6), iceberg logo, no literal "AI". PR #59 OPEN (stacked #57→#58→#59; Vercel preview=review). Part of wh#3485
- [Cloud routines migrated to ace-linux-1](project_cloud_routines_migrated_to_ace_linux_1.md) — 2026-07-12 ✅ COMPLETE: all 10 recurring routines local as systemd timers (`~/claude-routines/`); cloud EMPTIED (~36 deleted, API-verified `list`→`[]`); 6 runs green; audit tools `bin/audit.sh`/`audit-unit.sh` added. Gmail SOLVED via `bin/gmail-imap.py` (X-GM-RAW + App-Password, read-only, live-proven on wh#2423). NEXT: `bin/audit.sh` after Mon 08:30 CDT — 5 timers get their true first fire (Persistent doesn't back-fill on fresh install)
- [ace-win-1 batch mini-runs → operability (dm#1553)](project_ace_win1_batch_operability_program.md) — 2026-07-12: EPIC + 8 children. Batch lives INSIDE digitalmodel; agent serial. E/I/A/B/skill ✅ MERGED. F onboarding: deckhand #556 + mkt-a #237 awaiting HUMAN merge. NEXT: D dm#1557 sweep catalog
- [HF-backed website capability surfaces (wh#3485)](project_hf_backed_website_capability_surfaces.md) — 2026-07-11: EPIC — HF datasets LIVE on aceengineer.com, self-perpetuating, CI-enforced. Children C1-C9. NEXT (owner-gated): C1 registry → C2 build.js fetch
- [wed #971 economics life-to-date fix](project_wed971_economics_life_to_date_fix.md) — 2026-07-12: #971/#979/#981 MERGED. PIVOT: ONE result = V50 wed-latest; client surfaces say just "economics". NEXT: #982 (V50-only reports), #974 (capabilities envelopes)
- [dm#1528 sloshing fill/drain reduced-order](project_dm1528_sloshing_reduced_order.md) — 2026-07-12: ITEM-3 DONE + COEFF CORRECTION 0.31→0.16·Π (grid-converged, GCI 9.5%); ITEM-1 damping CFD-confirmed; ITEM-2 #1552 MERGED. ITEM-4 handover FILED dm#1562 (model `dm1528_coupled_antiroll_model.py`; +Kc·V sign-trap banked). REMAINING (blocked on user hull Δ/GM/T_roll): run #1562 → real roll-reduction %
- [HF projection + staged promotion (wh#3433)](project_hf_projection_staged_promotion.md) — 2026-07-11: PR #3465 plan-approved; schema chain #3428-#3432 (PR #3468); gated behind DRAFT #3452. Pilots dm#1505/wed#927 blocked
- [Tier-1 replan planning factory (wh#3050)](project_tier1_replan_planning_factory.md) — 2026-07-11 ✅ 105 plans; tracks CLOSED, execution owner-gated. Handover `/tmp/tier1-and-ecosystem-planning-EXIT-handover-2026-07-11.md`
- [World Energy Field Explorer program](project_world_energy_field_explorer_program.md) — 2026-07-10: wed EPIC #939 + #940-#951 + dm#1523. NEXT: #942 panel (dm#1519) or remaining #945
- [Devakrishna passport renewal (DS-11)](project_devakrishna_passport_renewal.md) — 2026-07-06: BLOCKED awaiting child/parent details + ZIP
- [RUNSPEC Monte Carlo UQ ingest](project_runspec_monte_carlo_uq_ingest.md) — 2026-07-06: llm-wiki #822 ✅. NEXT: plan dm #1427; wed #833 open
- [Tank sloshing → dm capability + Scott email](project_tank_sloshing_capability.md) — 2026-07-05: dm #1424/#1425/#1428 MERGED; Scott email STAGED (not sent)
- [Richard D'Souza outreach + llm-wiki deepwater](project_richard_dsouza_outreach.md) — 2026-07-04: email STAGED; HOLDING for field-dev
- [Ecosystem review 2026-07-04 (Fable 5)](project_ecosystem_review_2026_07_04.md) — 12 issues/6 repos; NEXT: CI-recovery slice (wed #526 + wshub #3380)
- [wed field-hub top-down IA](project_wed_field_hub_ia_epic.md) — 2026-07-07: #755/#756/#848-#850 LIVE; #757 plan-APPROVED (`/tmp/handoff-757-codex.md`); remaining #759/#761
- [Motion-forecast offering (dm #1356)](project_motion_forecast_offering_epic.md) — 2026-07-04: CORE COMPLETE; NEXT: merge #1402. Conclusions consumed by dm#1553
- [Field-dev life-cycle poster](project_field_development_lifecycle_megaproject_poster.md) — 2026-07-03: wed #738 OPEN. NEXT: owner review → 9 LT fields → LNG variant
- [International field-dev epic (wed #713)](project_wed_international_field_dev_epic.md) — 2026-07-13: 6 country chains MERGED (Norway/UK/Brazil/Spain/Canada/Australia) + benchmark. #720 Mexico SOURCE RECOVERED (nightly watcher WIN, plan-review). NEXT: implement #720 DI-loader; #722 missing-sources
- [Under-pressured gas-field screen (wed #708)](project_underpressured_gas_field_screen.md) — 2026-07-03: #728+#729 MERGED; 10,103 severe wells; #709 TX blocked on RRC
- [ace share cleanup+dedup](project_ace_share_cleanup_dedup.md) — 2026-07-04: ~1.72 TB deleted; Immich LIVE (:2283). Epic #3370 OPEN: archive import, Tailscale, backups
- [Subsea7 FDG deck + slogan](project_subsea7_fdg_deck.md) — 2026-07-11 ✅ COMPLETE (dm #1507 + wed #929 CLOSED); follow-on dm #1530 hardening. NEXT (user): FutureOn outreach; Subsea7 ~Sep
- [Reed Goodman / Collide lead](project_reed_goodman_collide_lead.md) — 2026-07-03 PARKED: onepager + reply ready. NEXT: email Reed
- [Devakrishna school: STAAR + enrollment](project_devakrishna_school_staar_enrollment.md) — 2026-07-01: STAAR Level III both; complete Digital Academy of TX transfer app
- [Household utility bills](project_household_utility_bills.md) — 2026-06-30: DON'T switch electricity mid-contract; shop ~Jan 2027
- [Voice dictation rollout](project_voice_dictation_ecosystem.md) — 2026-06-30: branch COMMITTED not pushed; ace-linux-1 only
- [Tug brochure + 3-repo epics](project_tug_analysis_brochure_epics.md) — 2026-06-30: dm PR #1209 OPEN; brochure needs user logo
- [Data-source catalog + domain-DB flywheel](project_data_source_catalog_flywheel.md) — 2026-07-03: #1281 COMPLETE; NEXT: approve #1282
- [dm #1142 repo-health](project_dm_1142_repo_health.md) — 2026-06-29: FIX 2 PR #1159 open; remaining 4.7GB .git
- [Seamless ecosystem dev epic (#3290)](project_seamless_ecosystem_development_epic.md) — 2026-06-27: #3291-#3296 plan-approved (delegable)
- [EPIC dm #1080 tubular/structural](project_dm_1080_tubular_structural_epic.md) — 2026-06-28: #1098/#1099 merged; #1094 → lane:codex needs-plan
- [Howard Day GT-R CFD (NDA)](project_howard_day_cfd_landspeed_study.md) — 2026-06-27: drag&lift analytically FIRST; authorize L1 only; HD waiting since May 11
- [Contact directory collation](project_contact_directory_collation.md) — 2026-06-28: master_contacts.csv (2,690) UNCOMMITTED
- [mkt-a Noble warm-window notes](project_mkt-a_noble_warm_window_call_2026_06_26.md) — Noble #38 time-sensitive; 4 files UNCOMMITTED
- [Subsea intervention DB epic (wed #582)](project_subsea_intervention_database_epic.md) — #585 @ plan-review; feeds dm #890
- [Collide PE solver (dm #836)](project_collide_pe_solver_program.md) — 161 posts scraped; NEXT: push+PR (user-gated)
- [Chuck's UDW well access article](project_chuck_udw_well_access_article_backing.md) — thesis=ACCESS/CONCENTRATION; memo UNCOMMITTED
- [FDAS public tier + HSE finding](project_fdas_public_tier_dashboard_hse.md) — HSE does NOT favor dry-tree — don't pitch HSE. OPEN: dashboard + Roy email
- [CAD/CAM discovery epic (dm #1004)](project_cad_cam_discovery_epic_1004.md) — 525k files/5.4TB scanned; PR #1010 OPEN
- [Ecosystem Pages + career](project_ecosystem_pages_and_career_initiative.md) — wshub #3223 + 19 issues; "public repo"≠"safe to publish"

## Key Lessons (how to work)
- [One result everywhere](feedback_one_result_everywhere.md) — SINGLE result on website/HF/client surfaces, clean product language, no version labels; versioning internal only. NEW results auto-"pop" live, no staging gate
- [Dispatch = deterministic scripts only](feedback_dispatch_deterministic_scripts_only.md) — licensed-host lane runs pinned-input scripts reproducible from committed files; LLM work is ad-hoc/one-time, lands as committed code, then flows autonomously
- [AceEngineer standard HTML calc-report format](feedback_ace_standard_html_calc_report.md) — ALL calcs: single-file HTML, TOC 2-level, formula cards + SVG flowcharts; template `/mnt/local-analysis/ace_calc_report_TEMPLATE.html`; HTML/CSS formulas not MathJax; provenance=color
- [Placeholder links to filing issue](feedback_placeholder_links_to_filing_issue.md) — thin UI data → VISIBLE placeholder linking a filed `cat:data` issue, not silent omission
- [Fable 5 vs Opus 4.8 routing](reference_fable5_vs_opus48_session_comparison.md) — Fable=orchestration/planning, Opus=execution/merge-CI
- [Equality wedge ≠ drift recovery](feedback_equality_wedge_vs_drift_recovery.md) — main ahead AND behind → can't self-heal; prove regenerable → backup tag → `reset --hard origin/main` (destructive, get OK)
- [Vamsee's technical-outreach email style](feedback_vamsee_technical_outreach_email_style.md) — reply into EXISTING thread; humble greeting; every capability gets a LIVE link; one ask. [[feedback_vamsee_email_style_skestates]]
- [Strict-up-to-date ruleset blocks green-PR merge](feedback_strict_uptodate_ruleset_no_admin_bypass.md) — `--admin` doesn't bypass rulesets; use merge-when-CLEAN loop or owner flips strict off
- [Required check must never skip](feedback_required_check_must_not_skip.md) — job-level `if:` on a required check deadlocks PRs (skipped ≠ success); job must always run
- [Verify against the real CI lint toolchain pre-push](feedback_verify_against_real_ci_lint_toolchain.md) — run the repo's EXACT black/isort/flake8; absent binary "passes" silently
- [Batch-merge PRs: no rebase, trust CLEAN](feedback_dependabot_merge_no_rebase_trust_clean.md) — don't `update-branch` (CI livelock); merge on `mergeStateStatus==CLEAN`; verify MERGED on remote
- [Unique live links → traffic + credibility](feedback_unique_live_links_traffic_credibility.md) — every capability gets its OWN indexable page, never a shared "dashboards" section
- [Always update the equality matrix](feedback_always_update_equality_matrix.md) — end fleet-touching work with `publish-equality.sh --repo /mnt/local-analysis/workspace-hub --rebuild`
- [One task at a time](feedback_one_task_at_a_time.md) — end turns with summary + exactly ONE next task, never an option menu
- [Keep data at fingertips](feedback_keep_data_at_fingertips.md) — delete only regenerable cruft; keep + back up data even if re-fetchable
- [Document discovered data sources as GH data issues](feedback_document_discovered_data_sources_as_issues.md) — side-finds → `cat:data` issues (one per source family)
- [Avoid "A&CE" branding](feedback_avoid_ace_branding.md) — use "AceEngineer"
- [Agent can verify but NOT self-merge its own PR](feedback_agent_can_verify_but_not_self_merge_pr.md) — hand human the `gh pr merge` line (exception: digitalmodel on explicit user "merge")
- [Epic wrap-up → open issues + parallel agents](feedback_epic_wrapup_issues_then_parallel_agents.md) — no dangling candidate lists; ~3 lanes; pre-make worktrees sequentially
- [Squash-merge breaks stacked PRs](feedback_squash_merge_breaks_stacked_prs.md) — spine squash auto-closes children; shared `__init__.py` lanes → ONE integration PR
- [--delete-branch auto-closes stacked child PR](feedback_delete_branch_closes_stacked_child_pr.md) — merging parent with `--delete-branch` CLOSES (not retargets) the child; merge parent WITHOUT delete → retarget child to main → merge → delete last. Recover closed child via fresh `gh pr create` (can't reopen; base ref 404)
- [dev-primary equality "green" is self-healing](feedback_dev_primary_equality_green_is_self_healing.md) — fix drift via PR + STOP; cron re-greens
- [Autorun resets worktree branches → push immediately](feedback_autorun_clobbers_subagent_worktree_commits.md) — `commit && push -u`; verify delegated work on REMOTE
- [Small calcs go into digitalmodel domain modules](feedback_small_calcs_into_digitalmodel_domains.md) — `src/digitalmodel/<domain>/` + tiny test, not standalone briefs
- [Delegate token-heavy REVIEW to Codex (not authoring)](feedback_delegate_token_heavy_to_codex.md) — `submit-to-codex.sh` (`env -u CLAUDECODE`); verify output exists
- [Agent CAN --no-verify push a feature branch (not main)](feedback_prepush_no_verify_allowed_on_feature_branch.md) — auto-deny is default-branch-specific; fuser stale index.lock before rm
- [Check issue state before implementing](feedback_check_issue_state_before_implementing_on_detached_head.md) — branch from origin/main + `gh issue view` + PR search BEFORE coding
- [Verify generated/state files against origin/main](feedback_verify_generated_state_against_origin_not_working_copy.md) — `git show origin/main:<path>` before "stale" claims
- [Narrow grep gives false-"dead" before deletion](feedback_narrow_grep_false_dead_before_deletion.md) — whole-repo `grep -rI` + adversarial "prove it's consumed"; dead RUNNER ≠ live DATA
- [Parallel agents must not share a mutable tool path](feedback_parallel_agents_shared_mutable_tool_path.md) — freeze/per-agent copy; verify each agent's ARTIFACT
- [--amend clobbers parallel branch in shared checkout](feedback_amend_clobbers_parallel_branch_in_shared_checkout.md) — dedicated worktree when parallel; reflog recovery; SKIP_COVERAGE_REASON = sanctioned bypass
- [Recover stale branch for PR](feedback_recover_stale_branch_for_pr.md) — cherry-pick onto fresh worktree from origin/main, push NEW branch
- [Agent cannot enable/spread a security-gate bypass](feedback_agent_cannot_enable_security_gate_bypass.md) — fixing a buggy gate OK; bypass routes to HUMAN
- [Externalize all config to YAML](feedback_externalize_all_config_to_yaml.md) — members/repos/constants/thresholds in reviewable .yml, never hardcoded
- [Force-push denied → leaked-blob remediation](reference_force_push_denied_history_blob_remediation.md) — `reset --soft origin/<branch>`+forward-commit; history blob needs USER force-push; de-identify BEFORE first commit
- [Vamsee's email style](feedback_vamsee_email_style_skestates.md) — thanks + shared-benefit before ask; close "Thank you very much," + Vamsee/VP of Operations
- [SVG-for-PDF portability](feedback_svg_pdf_portability_no_patterns_clippaths.md) — no `<pattern>`/clipPath/filter/mask in PDF-bound SVG; verify with `pdftocairo`; rule `.claude/rules/svg-pdf-portability.md`

## Key References
- [Vessel-fleet data locations](reference_vessel_fleet_data_locations.md) — rig-spec DB in `worldenergydata-vessel_fleet`; Noble 31/31 DONE (PR #989 merged + #990 open); program EPIC wed #991 (#992-#998: all contractors + onshore → rig-selection insights)
- [ace-linux-1 OOM hang 2026-07-12](reference_ace_linux_1_oom_hang_2026_07_12.md) — runaway claude.exe→swap→livelock; systemd-oomd UNARMED for swap; earlyoom installed. Gate deadlock FIXED (wh#3500/#3501) + fleet publish-health monitoring LIVE (wh#3502/#3503: sentinel 4.5s vs 60min, matrix publish_health row, skill propagated 22 links). Wedge RESOLVED (backup tag backup/pre-wedge-reset-2026-07-12 + reset, all-regenerable state). OPEN: #3504/#3505/#3506 — dev-secondary/ace-win-1/ace-win-2 never published a fingerprint; triage per equivalence-publish-health skill ON each box
- [FUSE mount saturation = process storm](reference_fuse_mount_saturation_process_storm.md) — "filesystem timed out" often = runaway jobs saturating mount I/O; diagnose `ps -eo ppid,stat,etimes,%cpu`; fix = kill storm (user-gated) or local sparse clone
- [Verify licensed-run hosts headless via heartbeat](reference_ace_win_1_headless_verification_via_heartbeat.md) — queue-repo `heartbeat/<host>.json` = ONLY remote signal. Always-on needs Password/S4U + AtStartup (ONLOGON dies at logoff)
- [wed local build/run recipe](reference_wed_local_build_run_recipe.md) — namespace-package PYTHONPATH; contract-test loop `--noconftest -o addopts=""`; sparse-clone 0-byte trap → explicit-path commit + `[ -s ]`, never `git add -A`
- [NTFS-FUSE git stalls on /mnt/local-analysis](reference_ntfs_fuse_git_stalls_local_analysis.md) — porcelain git hangs; use plumbing commits, local sparse clones, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`
- [Squash-merge → false "orphaned" PR](reference_squash_merge_reachability_false_orphan.md) — verify merged work by CONTENT (`git cat-file -e origin/main:<file>`), not mergeCommit reachability
- [Claude Desktop install state (ace-linux-1)](reference_claude_desktop_install_state.md) — official dpkg 1.17377.0 pristine
- [Deckhand Telegram MTProto creds blocker](reference_deckhand_operator_telegram_creds.md) — sends as USER (Telethon); needs user-run interactive login
- [Gmail create_draft attachment limit](reference_gmail_create_draft_attachment_limit.md) — no files >few KB inline; operator drag-drop or public link
- [Gmail search can't read Contacts/autocomplete](reference_gmail_search_no_contacts_autocomplete.md) — MCP searches MESSAGES only; stage draft with blank To
- [Emails are ephemeral; strategy repo is SSOT](feedback_emails_are_ephemeral_strategy_repo_is_ssot.md) — durable record → `aceengineer-strategy`, then move on
- [FDAS team roster](reference_fdas_team_members.md) — Shilling (Pres), White (EVP), Achanta (VP Eng), Hyatt (VP D&C), Ivers (chairman)
- [Headless Chrome HTML→PDF image gotchas](reference_headless_chrome_pdf_image_gotchas.md) — `--print-to-pdf` drops file://+background images; use `<img>` base64 data-URIs
- [rclone + Google Drive on this box](reference_rclone_gdrive_setup.md) — remote `gdrive:` OAuth-authorized; throttle `--tpslimit`
- [Claude hooks cannot see token/cost spend](reference_claude_hooks_cannot_see_spend.md) — hooks enforce tool-COUNT ceilings only
- [digitalmodel python env](reference_digitalmodel_python_env_venv.md) — use `.venv/bin/python` not `uv run` (uv broken for several repos)
- [ace-linux-2 headless VNC](reference_ace_linux_2_headless_vnc.md) — TigerVNC :1/5901 (`tigervncserver@:1`); connect via `vnc-ace-linux-2.sh`
- [Cross-provider dream feed activity (2026-07)](reference_crossprovider_feed_activity_2026_07.md) — only Claude+Codex feed the dream; gemini/hermes `learnings=0` expected, not a bug
- [ace-win-1 equality evidence stale](reference_ace_win_1_equality_evidence_stale.md) — acma-ansys05: no scheduler + no gh auth → evidence stales; fix ON-BOX (`gh auth login` + collect+publish + scheduler job, #2815)
