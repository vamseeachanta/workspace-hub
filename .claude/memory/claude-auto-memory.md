# Claude Code Auto-Memory Snapshot

> Git-tracked snapshot of Claude Code's auto-generated MEMORY.md index.
> Last captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md

# Workspace Hub Memory

> Curated live index. The COMPLETE record (title-only pointers) is split across
> `MEMORY-archive.md` + `archive/aged-out.md` — grep BOTH for anything not
> below; full detail lives in each topic file here.

## Active & Recent Projects
- [India family trip Jul 21–Aug 19 + travel apps](reference_us_india_travel_apps.md) — 2026-07-19 ✅✅ **PREP COMPLETE, family departs IAH 18:15 Jul 19** (PNR 78ANCY): e-Arrival cards filed+printed, checked in (passes at IAH desk — arrive 3h early), outbound seats together, return QR713 seats 23A window=Krishna, H2O roaming funded both lines, Uber Reserve RGIA→Secunderabad booked (flight-linked QR500, ₹2288 Visa ••1832), docs in `achantas-data/_travel/2026/`. **NEXT: ~Aug 18 return check-in** (OTP via achantav@gmail.com); optional GE apps from India; Sep 18 DS-11 reminder. Full runbook + traps in topic file
- [iPhone media extraction pipeline](project_iphone_media_taildrop_pipeline.md) — 2026-07-19 ✅✅ TWO PHONES ARCHIVED 3-2-1: iphone-14 (958/6GB) + iphone-sabitha (711/22GB) originals via USB AFC → `phone-media/` + Drive mirrors rclone-check-verified (1671 obj/27.3GiB; **Drive free 30.4GiB**). Low-res tree deleted; Taildrop+WebDAV lanes systemd-live. Follow-ons = EPIC wh#3589 (#3584-#3588). Krishna no phone. NEXT: #3586 capacity plan gates next phone
- [External SSH via Tailscale for ace-linux-1/2](project_external_ssh_tailscale_fleet.md) — 2026-07-18 ✅✅ **GOAL MET, verified from phone on cellular** (deckhand#571): ace-linux-1 (100.105.46.79) root-free userspace tailscaled + OpenSSH passthrough, persistence = user unit + linger; ace-linux-2 (100.93.161.27) Tailscale SSH (RunSSH=true, DNS warning cleared). ✅ ace-linux-1 reboot survival PASS 2026-07-19 (all lanes auto-recovered). PENDING (passive): router 22/2222 audit. Traps banked in topic file
- [agy replaces gemini as 3rd worker/reviewer (wh#3573)](project_agy_replaces_gemini_provider_swap.md) — 2026-07-18 ✅✅✅ **COMPLETE, #3573 CLOSED**: all 3 PRs MERGED (#3574 `a03d1a9`, #3575 `331cd23`, #3576 `3e8edba`, content-verified); labels migrated; handoff `docs/session-handoffs/2026-07-18-handoff-3573-agy-provider-swap.md` on main (`bc92523b4`). RULE now live: cross-review = Claude+Codex+Agy; `gemini` = deprecated alias only. Open follow-ons: #3577 exec-bit sweep, #3578 codex stdin-hang, #3579 equality row rename (after soak), #3580 gemini uninstall (~2026-08-01). Detail in topic file
- [Sun Manufacturing Floorhand pamphlet](project_sun_manufacturing_floorhand_pamphlet.md) — 2026-07-17: ✅ PR #179 MERGED; ✅ pamphlet EMAILED; ✅ Austin Bryant replied POSITIVE same day (shop installing 2 new machines = CAD/CAM opening). Floorhand design system banked (RULE: future pamphlets copy `strategy/floorhand-pamphlet-TEMPLATE.html`). AWAITING Austin's meeting pick (offered Wed–Fri Jul 22–24 ≥2 PM; calendar clear). NEXT: on pick → calendar event + meeting kit (pamphlet + P10/P50/P90 bidding + CAD/CAM angle); nudge Monday if silent. Contact details in topic file
- [Fidelity returns analysis + dashboard](project_fidelity_returns_analysis.md) — 2026-07-17 ✅ COMPLETE: Flow-vs-Return charts (monthly+yearly, per-acct+per-stock dropdown) MERGED PR #152 (`4182215`, content-verified). Recon 0.05% worst dev; traps banked (Yahoo split-adjust, IRA rollover half-missing, proxy-deposit cash credit). Build now self-contained (`prices/` + fetch_prices.py). No open work
- [Elliott Services Floorhand FFS brochure](project_elliott_floorhand_brochure.md) — 2026-07-17: 3-page partnership brochure (Floorhand brand); "verdict at point of inspection" positioning vs FFS authors E2G/Becht/Quest; ✅ PR #178 MERGED (v1 #177 too) — on main; +internal market-review.md. Send-ready `~/floorhand-elliott-brochure.pdf`. NEXT (HITL): pick send route (email draft vs hosted link) + flip "working draft" footer → SEND; then v4 refine + CEO outreach
- [Krishna daily schedule (wh#3528)](project_krishna_daily_schedule.md) — 2026-07-14: anchor-based day, epic #3528 + children #3529/#3530/#3531. ✅ Morning chain APPROVED (run ~3mi→shower→dress→breakfast→therapy); sleep log running (lever = brush by 8:40). PROPOSED: evening shower 8:00 (absorbs PJs) + weights restart 5:30. LIVING ARTIFACT: near-daily feedback → dated #3528 comments, body = current schedule. NEXT: evening-chain yes/adjust + cadence → build calendar #3529
- [wed #844 cost-basis time-series + costing program](project_wed844_cost_basis_timeseries_dispatch.md) — 2026-07-14: M1 + presentation MERGED (#1016/#1018); **#1017 = approval spine (A1–A4, gates #651)**; ✅ internal iteration MERGED (#1021/#1022/llm-wiki#838; 26 figures/$194bn). **2026-07-15: circulation DEFERRED — hardening EPIC #1023** (E1-E7 = #1024-#1030). ✅ E1+E4+E2+E5 MERGED (80 projects/$509bn; A1 evidence pack: priors corroborated where testable, contradicted nowhere). ✅✅✅ **HARDENING EPIC #1023 COMPLETE** — E1-E7 all merged except **E3 → PR #1037 OPEN** (award tranche 2: coverage on 28 projects, A1 pack now on 9 full-scope SURF tests, 0 above-band). 80 projects/$509bn, 4 cross-checked sourced views/project, priors hold. NEXT: merge #1037 → close #1023. Then ONLY deferred #1017 circulation remains (owner-gated: refresh email to $509bn/80, delete stale $177bn draft, send, collect A1). Detail in topic file
- [llm-wiki-acma OCR lane on gpu-claw (#267)](project_llm_wiki_acma_ocr_lane_gpu_claw.md) — 2026-07-13 ✅ SMOKE MERGED (PR #271); full-queue go = #272 (blocked on staging path); paddle version-skew trap banked
- [wed parametric economics sweep + HF refresh](project_wed_parametric_economics_sweep.md) — 2026-07-13 ✅ PR #1004 MERGED (`a26881d4`, content-verified); explorer dataset refreshed. NEXT: C9 website un-withhold decision. See [[project_wed_economics_c9_session_handoff]]
- [Fleet dispatch ecosystem (wh#3497)](project_fleet_dispatch_ecosystem_epic.md) — 2026-07-13: ✅ Phase-6 smoke rc 0 on gpu-claw; #561/#562/dm#1563 MERGED, #563 OPEN; twins dm#1564/dm#1565 filed. RULE: map detail PRIVATE-only. NEXT: merge #563; reboot+48h soak → VPN retire (deckhand#557). Detail in topic file
- [aceengineer.com redesign — Subsea7 theme](project_aceengineer_website_redesign_subsea7.md) — 2026-07-12: navy #0b3d5c/teal #2BB2A6, iceberg logo, no literal "AI". PR #59 OPEN (stacked #57→#58→#59; Vercel preview=review)
- [ace-win-1 batch mini-runs → operability (dm#1553)](project_ace_win1_batch_operability_program.md) — 2026-07-12: E/I/A/B/skill MERGED; F onboarding deckhand#556 + acma#237 await HUMAN merge. NEXT: D dm#1557 sweep catalog
- [dm#1528 sloshing fill/drain reduced-order](project_dm1528_sloshing_reduced_order.md) — 2026-07-12: coeff corrected 0.16·Π (GCI 9.5%); ITEM-4 handover dm#1562. REMAINING (blocked on user hull data): run #1562 → roll-reduction %
- [HF projection + staged promotion (wh#3433)](project_hf_projection_staged_promotion.md) — 2026-07-11: PR #3465 plan-approved; schema chain PR #3468; gated behind DRAFT #3452. Pilots blocked
- [World Energy Field Explorer program](project_world_energy_field_explorer_program.md) — 2026-07-10: wed EPIC #939 + #940-#951 + dm#1523. NEXT: #942 panel (dm#1519) or #945
- [Devakrishna passport renewal (DS-11)](project_devakrishna_passport_renewal.md) — 2026-07-18: DEFERRED until family returns from current trip (user decision; trip runs on existing passport, exp 22 Jun 2027, OK while travel ends before ~late Dec 2026). On return: SSN, height/hair/eye, ZIP, consent path → DS-11 + appointment
- [wed field-hub top-down IA](project_wed_field_hub_ia_epic.md) — 2026-07-07: #755/#756/#848-#850 LIVE; #757 plan-APPROVED; remaining #759/#761
- [International field-dev epic (wed #713)](project_wed_international_field_dev_epic.md) — 2026-07-13: 6 country chains MERGED + benchmark; #720 Mexico source recovered. NEXT: #720 DI-loader; #722
- [FDAS public tier + HSE finding](project_fdas_public_tier_dashboard_hse.md) — HSE does NOT favor dry-tree — don't pitch HSE. OPEN: dashboard + Roy email
- [wed economics C9 session handoff](project_wed_economics_c9_session_handoff.md) — 2026-07-13: PR #986 CLEAN/ready-merge; untracked C9 WIP on wed/main preserved to branch/PR

## Key Lessons (how to work)
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
- [Small calcs go into digitalmodel domain modules](feedback_small_calcs_into_digitalmodel_domains.md) — `src/digitalmodel/<domain>/` + tiny test
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
- [US↔India travel apps for the family](reference_us_india_travel_apps.md) — India e-Arrival Card MANDATORY since Apr 2026 (72h pre-arrival, OCI too, save the QR); MPC for US re-entry (12 family profiles); ATITHI 2.0 for India customs; H2O roaming needs credit top-up (silently fails at $0); Uber Reserve needs valid card (no cash, web can't add cards)
- [Family US passport scan locations](reference_family_us_passport_locations.md) — current scans in achantas-data (`va/`, `sd/ID/`, `da/`); Sabitha surname = DEEPTHIMAHANTI; Devakrishna expiry 22 Jun 2027 = travel constraint; numbers stay in scans (PII rule)
- [gpu-claw WireGuard flap → detached runs](reference_gpu_claw_wireguard_flap_detached_runs.md) — nohup + GitHub-as-progress-channel pattern
- [Vessel-fleet data locations](reference_vessel_fleet_data_locations.md) — rig-spec DB complete (epic wed #991); NEXT #997 onshore + #1006 equipment fields
- [ace-linux-1 display: NVIDIA Maxwell dead on kernel 7.0](reference_ace_linux_1_display_nvidia_maxwell_dead.md) — 2026-07-19: GTX 750 Ti fell to simpledrm 640×480 (no 535 modules for 7.0 kernel + nouveau blacklisted); fix = purge nvidia stack → nouveau; never reinstall nvidia-535
- [ace-linux-1 OOM hang 2026-07-12](reference_ace_linux_1_oom_hang_2026_07_12.md) — earlyoom installed; wedge RESOLVED. OPEN: #3504-#3506 fingerprint triage — detail in topic file
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
