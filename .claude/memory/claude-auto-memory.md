# Claude Code Auto-Memory Snapshot

> Git-tracked snapshot of Claude Code's auto-generated MEMORY.md index.
> Last captured: 2026-07-27
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md

# Workspace Hub Memory

> Curated live index. The COMPLETE record (title-only pointers) is split across
> `MEMORY-archive.md` + `archive/aged-out.md` — grep BOTH for anything not
> below; full detail lives in each topic file here.

## Active & Recent Projects
- [D&C days ROOT CAUSE + fix program (wed#1062, EPIC #1063)](project_dc_days_root_cause_war_codes.md) — 2026-07-26: THREE incompatible "drilling days" definitions live, 0/56 wells agree (6.6× gap); benchmark's = calendar spud→first-oil (proven 32/32), extract mixes calendar + WAR-union at an undocumented 250d threshold. **Reference basis = BSEE WAR `WELL_ACTIVITY_CD`, reproduces Roy's own numbers to the day.** Root cause = Roy's 2025 question "which completion method?" NEVER ANSWERED. **EPIC #1063 + 18 children #1064–#1081 filed as fresh-context briefs** (ordered, dependency-sketched). NEXT: #1064 basis decision w/ Roy (HARD BLOCKER); quick wins #1071/#1072/#1073/#1074/#1077 need nothing
- [OrcaFlex: dm INITIATIVE #1640 (single umbrella ref)](project_orcaflex_ecosystem_review_2026_07_25.md) — **QUOTE dm#1640 FOR ALL OF IT** (tier above epic; spans 7 epics #1234/#938/#1080/#1095/#807/#622/#1553; `initiative` label created). GOAL: arm the gate -> clear 3 CI blockers -> fix wrong numbers, IN THAT ORDER. ROOT CAUSE: dm `main` has NO `required_status_checks` + 0 required reviews -> 60.3% of merges were red, 46 Codex findings 0 resolved. ✅ **PR #1636 MERGED (`4d465406`, content-verified)** = #1550 te->kg at the OrcFxAPI boundary + unit guard + mutation matrix + native-unit fence + coupling-block labels; +24 tests. ✅ CLOSED: #1550/#704/#705/#530/#531/#504/#506. ⚠ SAVED from wrong close: #508 (`upgrade_spec` raises NotImplementedError), #476 (no 'superseded' note) — triage reports were WRONG both ways; verify against code. **ISSUES REHOMED into existing epics** (#1640 is now a thin cross-cutting tracker): #938<-#1631/#718/#719 · #1080<-#1630/#810/#632/#878 · #1095<-#1641/#508/#476 · #807<-#1629/#41 · #622<-#1633 · #1553<-#1554 · #1234<-#1637/#1638/#1639. #1640 keeps only #1634/#1632/#1635/#1447/#611/#801. ⚠ CI: 3 shards red on EVERY run = 11 tests / 3 root causes / 0 code defects (#1637 `<nav>` scrape · #1638 SI-only regex FALSE POSITIVE · #1639 index cards) — must land BEFORE #1634 arms the ruleset. NEXT: #1638 (smallest, turns a red shard green)
- [Model-generation reopen slate (2026-07-25)](project_model_generation_reopen_slate_2026_07_25.md) — ecosystem-wide closed-issue review: wh#3106/#3056/#1019 + llm-wiki#638 REOPENED; wh#3107/#3109 closed as Fable-premised; #3043 epic retargeted. Skill corpus measured 3,196 files / 253k lines. NEXT: wh#3051 registry flip (blocks all the rest)
- [Model-registry generation drift + R-MODEL-DRIFT blind spot](project_model_generation_drift_registry_blindspot.md) — nightly guard checks ONLY `openai_primary`; Claude lane has zero drift coverage → cross-review escalated to a weaker model than the authoring session. ✅ wh#3600 FILED (durable guard fix); wh#3051 = one-off value update. NEXT: #3600 needs-plan → decide what the Claude lane diffs against
- [WO April validation QA/QC with Roy (wed #846)](project_wo_april_validation_roy_qaqc.md) — 2026-07-25 ✅ per-well listing + drilling-days resolution MERGED+LIVE (#1056/#1057: 0/253 bores changed drilling across vintages); QA/QC hub PR #1058 armed. ⚠️ NEW: DRILLING_DAYS col = two bases (calendar ≤250d / WAR-union beyond) → batch-drilled wells undercount (PS004 44d @ 28,692 ft; Big Foot systematic) — unresolved, awaiting owner's parallel-story notes. NEXT: owner deletes old Gmail draft, sends v2 (Roy picks #846 completion boundary)
- [Equality matrix reclassification (wh#3592)](project_equality_matrix_reclassification_3592.md) — 2026-07-23 ✅✅ CLOSED end-to-end; 5/5 all-CONFORMS on Linux. REMAINING on-box: ace-win-1 #2815, ace-win-2 #3595; ⚠️ owner one-liner pending: `systemctl --user disable --now claude-routine-mx-720-cnh-source-watch.timer`
- [India family trip Jul 21–Aug 19](reference_us_india_travel_apps.md) — 2026-07-19 ✅✅ prep complete, family departed. NEXT: ~Aug 18 return check-in (OTP via achantav@gmail.com); Sep 18 DS-11 reminder. Runbook in topic file
- [iPhone media extraction pipeline](project_iphone_media_taildrop_pipeline.md) — 2026-07-19 ✅✅ two phones archived 3-2-1 (Drive free 30.4GiB). Follow-ons EPIC wh#3589. NEXT: #3586 capacity plan gates next phone
- [External SSH via Tailscale for fleet](project_external_ssh_tailscale_fleet.md) — 2026-07-24 ✅ mosh+tmux persistence LIVE on ace-linux-1 (wh PR #3597 merged: 50k scrollback + resurrect/continuum reboot survival; other boxes = pull + 2 git clones). ⚠ ace-linux-1 has TWO tailscaled daemons — system owns 100.121.119.6, userspace/Taildrop node shows OFFLINE → verify Taildrop lane. NEXT: 24h BatchMode re-test gpu-claw + disable key expiry. Traps in topic file
- [agy replaces gemini (wh#3573)](project_agy_replaces_gemini_provider_swap.md) — 2026-07-18 ✅✅✅ COMPLETE. RULE live: cross-review = Claude+Codex+Agy. Follow-ons #3577-#3580 (gemini uninstall ~2026-08-01)
- [Floorhand multi-metro outreach (12 shops)](project_floorhand_multi_metro_outreach.md) — 2026-07-26 ✅✅ **SESSION CLOSED, PRs #180–#185 ALL MERGED** (handoff on main). 12 two-page pamphlets + requirements-intake instrument + partner terms; 3 emails addressed & READY TO SEND (Siva/Geeta/Naveen). Pitch spine: no certs published, out-of-state SEO outranks locals, 50% tariffs, succession. Partner model SETTLED = **flat 50-50 gross, paid as shop pays** (don't re-litigate — tiers/ramps rejected). Review online: repo · Drive `floorhand-review-2026-07` · artifact gallery. ⚠ Ottawa ownership unconfirmed; ⚠ **analysis engine NOT BUILT** → `digitalmodel` `manufacturing/` domain. NEXT: owner attaches PDFs + sends
- [Sun Manufacturing Floorhand pamphlet](project_sun_manufacturing_floorhand_pamphlet.md) — 2026-07-17 ✅ emailed; Austin replied POSITIVE (2 new machines = CAD/CAM opening). RULE: future pamphlets copy `strategy/floorhand-pamphlet-TEMPLATE.html`. NEXT: on meeting pick → calendar + meeting kit; nudge if silent
- [Fidelity returns analysis + dashboard](project_fidelity_returns_analysis.md) — 2026-07-17 ✅ COMPLETE (PR #152). Traps banked in topic file. No open work
- [Elliott Services Floorhand FFS brochure](project_elliott_floorhand_brochure.md) — 2026-07-17 ✅ PR #178 MERGED; send-ready `~/floorhand-elliott-brochure.pdf`. NEXT (HITL): pick send route + flip draft footer → SEND
- [Krishna daily schedule (wh#3528)](project_krishna_daily_schedule.md) — 2026-07-14: morning chain APPROVED; living artifact = dated #3528 comments. NEXT: evening-chain yes/adjust → calendar #3529
- [wed #844 cost-basis + costing program](project_wed844_cost_basis_timeseries_dispatch.md) — 2026-07-24 review: hardening #1023 CLOSED (80 projects/$509bn, priors hold); program on EPIC #1038 (cost map + CAPEX estimator, #1040-#1044). ✅ main CI green restored (PR #1054 merged 07-24). STILL OPEN: A1–A4 undecided (blocks #651+circulation), cost↔FDAS stacks DISCONNECTED (NPV on lease_assumptions.xlsx), field_benchmark stale (#831). Detail in topic file
- [llm-wiki-acma OCR lane gpu-claw (#267)](project_llm_wiki_acma_ocr_lane_gpu_claw.md) — 2026-07-13 ✅ smoke merged; full-queue = #272 (blocked on staging path)
- [wed parametric economics sweep + HF](project_wed_parametric_economics_sweep.md) — 2026-07-13 ✅ PR #1004 merged. C9 un-withhold DONE website-side (#978 closable). See [[project_wed_economics_c9_session_handoff]]
- [Fleet dispatch ecosystem (wh#3497)](project_fleet_dispatch_ecosystem_epic.md) — 2026-07-13 ✅ Phase-6 smoke rc 0; #563 OPEN. RULE: map detail PRIVATE-only. NEXT: merge #563 → soak → VPN retire
- [aceengineer.com redesign — Subsea7 theme](project_aceengineer_website_redesign_subsea7.md) — 2026-07-12: navy/teal, no literal "AI". PR #59 OPEN (stacked). NEW: navigability issue awsite#76
- [ace-win-1 batch mini-runs (dm#1553)](project_ace_win1_batch_operability_program.md) — 2026-07-12: E/I/A/B/skill MERGED; F awaits HUMAN merge. NEXT: D dm#1557 sweep catalog
- [dm#1528 sloshing reduced-order](project_dm1528_sloshing_reduced_order.md) — 2026-07-12: coeff 0.16·Π. REMAINING (blocked on user hull data): run dm#1562
- [HF projection + staged promotion (wh#3433)](project_hf_projection_staged_promotion.md) — 2026-07-11: PR #3465 plan-approved; gated behind DRAFT #3452
- [World Energy Field Explorer program](project_world_energy_field_explorer_program.md) — 2026-07-11 feature-complete (shell/84 countries/56 wells/architecture); open: #962 SVGs, #966 HF viz, #955/#959/#960 ingest
- [Rama Lakshmi Indian passport Tatkaal re-issue](project_ramalakshmi_indian_passport_tatkal.md) — 2026-07-24 ✅ case SETTLED = II-B-2 (2008 book expired 19/02/2018 is her only one; `rld.md` "6-Nov-2027" is WRONG). Package + collection sheet + day-of checklist in `_relations/RLD/2026-07_tatkal_reissue_application.md`; ₹5,000 at POPSK Kakinada. ⚠️ husband gravely ill — do NOT propose renewing his. NEXT: get her 8 answers (§8) *stale: 2026-07-28*
- [Devakrishna passport renewal (DS-11)](project_devakrishna_passport_renewal.md) — DEFERRED until family returns (passport exp Jun 2027 OK). On return: DS-11 + appointment
- [wed field-hub top-down IA](project_wed_field_hub_ia_epic.md) — 2026-07-07: #755/#756/#848-#850 LIVE; remaining #759/#761
- [International field-dev epic (wed #713)](project_wed_international_field_dev_epic.md) — 6 country chains MERGED; #720 Mexico source recovered, DI-loader UNBUILT; ⚠️ mx-720 watcher = LOCAL systemd timer (owner one-liner above). NEXT: #720 loader; #722
- [FDAS public tier + HSE finding](project_fdas_public_tier_dashboard_hse.md) — HSE does NOT favor dry-tree — don't pitch HSE. OPEN: dashboard + Roy email
- [wed economics C9 handoff](project_wed_economics_c9_session_handoff.md) — 2026-07-13: C9 WIP preserved; all merged

## Key Lessons (how to work)
- [Verify subagent line citations, not just claims](feedback_verify_subagent_line_citations_not_just_claims.md) — verifying a defect exists ≠ verifying it's at that line; cite the SYMBOL when coordinates can't be cheaply confirmed; never write "every line re-verified" unless each was opened
- [Report-hub design system (owner-approved)](feedback_report_hub_design_system.md) — hub grammar (self-contained, evidence badges, disposition pill, tiers, guided path) = THE design for ALL field-data surfaces; site must be navigable; data → HF `aceengineer/*`; ref impl wed PR #1058 + epics wed#1059/awsite#76
- [Rig-selector capability depth](feedback_rig_selector_capability_depth.md) — onshore/offshore = FIRST filter; equipment fields over more hull numbers; PDF links = floor not product (wed #1006)
- [One result everywhere](feedback_one_result_everywhere.md) — SINGLE result on website/HF/client surfaces; versioning internal only; new results auto-pop live
- [Public by default; client-custom is private](feedback_public_by_default_client_custom_private.md) — analysis/results PUBLIC; only client-commissioned work private; `withheld_columns` = temporary guardrail
- [Non-required checks hide regressions](feedback_non_required_checks_hide_regressions.md) — content-deleting change can break a NON-required job → silent red on main; verify whole-suite + `gh pr checks` (no `--required`)
- [Dispatch = deterministic scripts only](feedback_dispatch_deterministic_scripts_only.md) — licensed-host lane = pinned-input scripts; LLM work is ad-hoc, lands as committed code
- [AceEngineer standard HTML calc-report format](feedback_ace_standard_html_calc_report.md) — single-file HTML, TOC, formula cards + SVG; template `/mnt/local-analysis/ace_calc_report_TEMPLATE.html`; provenance=color
- [Placeholder links to filing issue](feedback_placeholder_links_to_filing_issue.md) — thin UI data → VISIBLE placeholder linking a `cat:data` issue
- [Fable 5 vs Opus 4.8 routing](reference_fable5_vs_opus48_session_comparison.md) — Fable=orchestration/planning, Opus=execution/merge-CI
- [Equality wedge ≠ drift recovery](feedback_equality_wedge_vs_drift_recovery.md) — main ahead AND behind → prove regenerable → backup tag → `reset --hard` (destructive, get OK)
- [Vamsee's technical-outreach email style](feedback_vamsee_technical_outreach_email_style.md) — reply into EXISTING thread; humble greeting; LIVE links; one ask. [[feedback_vamsee_email_style_skestates]]
- [Strict-up-to-date ruleset blocks green-PR merge](feedback_strict_uptodate_ruleset_no_admin_bypass.md) — `--admin` doesn't bypass rulesets; merge-when-CLEAN loop
- [Required check must never skip](feedback_required_check_must_not_skip.md) — job-level `if:` on required check deadlocks PRs (skipped ≠ success)
- [Verify against the real CI lint toolchain pre-push](feedback_verify_against_real_ci_lint_toolchain.md) — repo's EXACT black/isort/flake8; absent binary "passes" silently
- [Batch-merge PRs: no rebase, trust CLEAN](feedback_dependabot_merge_no_rebase_trust_clean.md) — no `update-branch` (livelock); merge on CLEAN; verify MERGED on remote
- [Unique live links → traffic + credibility](feedback_unique_live_links_traffic_credibility.md) — every capability gets its OWN indexable page
- [Always update the equality matrix](feedback_always_update_equality_matrix.md) — end fleet-touching work with `publish-equality.sh --rebuild`
- [One task at a time](feedback_one_task_at_a_time.md) — end turns with summary + exactly ONE next task
- [Keep data at fingertips](feedback_keep_data_at_fingertips.md) — delete only regenerable cruft; keep + back up data
- [Document discovered data sources as GH data issues](feedback_document_discovered_data_sources_as_issues.md) — side-finds → `cat:data` issues
- [Avoid "A&CE" branding](feedback_avoid_ace_branding.md) — use "AceEngineer"
- [wed PR titles: conventional types only](feedback_wed_pr_title_conventional_types_only.md) — `data(cost):` FAILS the required Validate-PR-Title check; use `feat/fix/docs(...)`, subject ≤80 chars
- [Agent can verify but NOT self-merge its own PR](feedback_agent_can_verify_but_not_self_merge_pr.md) — hand human the merge line (exceptions: digitalmodel, or explicit user "merge")
- [Epic wrap-up → open issues + parallel agents](feedback_epic_wrapup_issues_then_parallel_agents.md) — no dangling lists; ~3 lanes; worktrees made sequentially
- [Squash-merge breaks stacked PRs](feedback_squash_merge_breaks_stacked_prs.md) — spine squash auto-closes children; shared lanes → ONE integration PR
- [--delete-branch auto-closes stacked child PR](feedback_delete_branch_closes_stacked_child_pr.md) — merge parent WITHOUT delete → retarget child → merge → delete last
- [dev-primary equality "green" is self-healing](feedback_dev_primary_equality_green_is_self_healing.md) — fix drift via PR + STOP; cron re-greens
- [Autorun resets worktree branches → push immediately](feedback_autorun_clobbers_subagent_worktree_commits.md) — `commit && push -u`; verify on REMOTE
- [Small calcs go into digitalmodel domain modules](feedback_small_calcs_into_digitalmodel_domains.md) — `src/digitalmodel/<domain>/` + tiny test *stale: 2026-07-28*
- [Delegate token-heavy REVIEW to Codex (not authoring)](feedback_delegate_token_heavy_to_codex.md) — `submit-to-codex.sh` (`env -u CLAUDECODE`); verify output exists
- [Agent CAN --no-verify push a feature branch (not main)](feedback_prepush_no_verify_allowed_on_feature_branch.md) — auto-deny is default-branch-specific
- [Check issue state before implementing](feedback_check_issue_state_before_implementing_on_detached_head.md) — branch from origin/main + `gh issue view` + PR search FIRST
- [Verify generated/state files against origin/main](feedback_verify_generated_state_against_origin_not_working_copy.md) — `git show origin/main:<path>` before "stale" claims
- [Narrow grep gives false-"dead" before deletion](feedback_narrow_grep_false_dead_before_deletion.md) — whole-repo grep + adversarial "prove it's consumed"
- [Parallel agents must not share a mutable tool path](feedback_parallel_agents_shared_mutable_tool_path.md) — freeze/per-agent copy; verify each ARTIFACT
- [--amend clobbers parallel branch in shared checkout](feedback_amend_clobbers_parallel_branch_in_shared_checkout.md) — dedicated worktree when parallel; reflog recovery
- [Recover stale branch for PR](feedback_recover_stale_branch_for_pr.md) — cherry-pick onto fresh worktree from origin/main, push NEW branch
- [Agent cannot enable/spread a security-gate bypass](feedback_agent_cannot_enable_security_gate_bypass.md) — fixing a buggy gate OK; bypass routes to HUMAN
- [Externalize all config to YAML](feedback_externalize_all_config_to_yaml.md) — members/repos/constants/thresholds in reviewable .yml
- [Force-push denied → leaked-blob remediation](reference_force_push_denied_history_blob_remediation.md) — `reset --soft`+forward-commit; history blob needs USER force-push
- [Vamsee's email style](feedback_vamsee_email_style_skestates.md) — thanks + shared-benefit before ask; close "Thank you very much," + Vamsee
- [SVG-for-PDF portability](feedback_svg_pdf_portability_no_patterns_clippaths.md) — no `<pattern>`/clipPath/filter/mask in PDF-bound SVG; verify with `pdftocairo`

## Key References
- [US↔India travel apps for the family](reference_us_india_travel_apps.md) — e-Arrival Card MANDATORY (72h pre-arrival, OCI too); MPC for US re-entry; H2O roaming needs credit; Uber Reserve needs valid card
- [Family US passport scan locations](reference_family_us_passport_locations.md) — scans in achantas-data; Sabitha surname = DEEPTHIMAHANTI; Devakrishna expiry 22 Jun 2027; numbers stay in scans (PII rule)
- [gpu-claw WireGuard flap → detached runs](reference_gpu_claw_wireguard_flap_detached_runs.md) — nohup + GitHub-as-progress-channel pattern
- [Vessel-fleet data locations](reference_vessel_fleet_data_locations.md) — rig-spec DB complete (epic wed #991); NEXT #997 onshore + #1006 equipment fields
- [ace-linux-1 display: NVIDIA Maxwell dead on kernel 7.0](reference_ace_linux_1_display_nvidia_maxwell_dead.md) — purge nvidia stack → nouveau; never reinstall nvidia-535
- [ace-linux-1 OOM hang 2026-07-12](reference_ace_linux_1_oom_hang_2026_07_12.md) — earlyoom installed; OPEN: #3504-#3506 fingerprint triage
- [FUSE mount saturation = process storm](reference_fuse_mount_saturation_process_storm.md) — "filesystem timed out" = runaway jobs; diagnose `ps -eo ppid,stat,etimes,%cpu`
- [Verify licensed-run hosts headless via heartbeat](reference_ace_win_1_headless_verification_via_heartbeat.md) — queue-repo `heartbeat/<host>.json` = ONLY remote signal
- [wed local build/run recipe](reference_wed_local_build_run_recipe.md) — namespace-package PYTHONPATH; `--noconftest -o addopts=""`; sparse-clone 0-byte trap
- [NTFS-FUSE git stalls on /mnt/local-analysis](reference_ntfs_fuse_git_stalls_local_analysis.md) — porcelain git hangs; plumbing commits, local sparse clones
- [Squash-merge → false "orphaned" PR](reference_squash_merge_reachability_false_orphan.md) — verify merged work by CONTENT, not mergeCommit reachability
- [Claude Desktop install state (ace-linux-1)](reference_claude_desktop_install_state.md) — official dpkg 1.17377.0 pristine
- [Deckhand Telegram MTProto creds blocker](reference_deckhand_operator_telegram_creds.md) — sends as USER; needs user-run interactive login
- [Gmail create_draft attachment limit](reference_gmail_create_draft_attachment_limit.md) — no files >few KB inline; operator drag-drop or public link
- [Gmail search can't read Contacts/autocomplete](reference_gmail_search_no_contacts_autocomplete.md) — searches MESSAGES only
- [Emails are ephemeral; strategy repo is SSOT](feedback_emails_are_ephemeral_strategy_repo_is_ssot.md) — durable record → `aceengineer-strategy`
- [FDAS team roster](reference_fdas_team_members.md) — Shilling (Pres), White (EVP), Achanta (VP Eng), Hyatt (VP D&C), Ivers (chairman)
- [Headless Chrome HTML→PDF image gotchas](reference_headless_chrome_pdf_image_gotchas.md) — `--print-to-pdf` drops file:// images; use base64 data-URIs
- [rclone + Google Drive on this box](reference_rclone_gdrive_setup.md) — remote `gdrive:` OAuth-authorized; throttle `--tpslimit`
- [Claude hooks cannot see token/cost spend](reference_claude_hooks_cannot_see_spend.md) — hooks enforce tool-COUNT ceilings only
- [digitalmodel python env](reference_digitalmodel_python_env_venv.md) — use `.venv/bin/python` not `uv run`
- [ace-linux-2 headless VNC](reference_ace_linux_2_headless_vnc.md) — TigerVNC :1/5901; connect via `vnc-ace-linux-2.sh`
- [Cross-provider dream feed activity (2026-07)](reference_crossprovider_feed_activity_2026_07.md) — only Claude+Codex feed the dream; others `learnings=0` expected
- [ace-win-1 equality evidence stale](reference_ace_win_1_equality_evidence_stale.md) — acma-ansys05: no scheduler + no gh auth; fix ON-BOX (#2815)
