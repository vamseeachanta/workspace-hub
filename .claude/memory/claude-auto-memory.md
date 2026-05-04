# Claude Code Auto-Memory Snapshot

> Git-tracked snapshot of Claude Code's auto-generated MEMORY.md index.
> Last captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md

# Workspace Hub Memory

## Feedback
> working-style.md, shell-git-patterns.md, engineering-modules.md
> feedback_*: html_refresh, skill_before_code, no_shortcuts_knowledge, dark_intelligence_excel
> repo_scope, research_skill_sources, specs_plans_location, uv_run_isolation, no_jargon
- [No local task IDs](feedback_no_reserved_wrk_ids.md) — GitHub issues only
- [Check parallel work](feedback_check_parallel_work.md) — scan in-flight sessions first
- [Comment on issues](feedback_gh_issue_comment.md) — post summary on every issue
- [Inline gh issue URLs](feedback_inline_gh_issue_url.md) — render `#NNNN` as Markdown hyperlink in chat output (not bare token)
- [Queue git-tracked](feedback_queue_git_tracked.md) — verify files in git before queue
- [Worktree gitlink pollution](feedback_worktree_gitlink_pollution.md) — add .claude/worktrees/ to .gitignore before parallel-agent runs
- [Adversarial review stance](feedback_adversarial_review_stance.md) — every review prompt must force defect-hunting, not charitable reading
- [Cross-provider review payoff](feedback_cross_provider_review_payoff.md) — Codex finds non-overlapping defects vs. Claude; verify Codex's GitHub-connector evidence locally
- [gh issue close drops comments](feedback_gh_issue_close_silent_comment_drop.md) — if issue already CLOSED, --comment is silently lost; reopen-comment-close to recover
- [Codex needs pushed artifact](feedback_codex_needs_pushed_artifact.md) — push plan to GitHub BEFORE dispatching `codex exec` review; sandbox can't read local files
- [Codex sandbox write blocked](feedback_codex_sandbox_write_blocked.md) — Codex sandbox blocks filesystem writes even for pushed artifacts; capture findings inline and write the review file yourself
- [Merge-race silent revert](feedback_merge_race_silent_revert.md) — auto-sync race during `git merge --no-ff` + `git commit --no-edit` can drop second-parent tree; always verify merged content matches branch tip
- [Data-format guidelines](data_format_guidelines.md) — default YAML for agent-facing structured data; JSON only when tool output is machine-consumed
- [Cross-machine execution](feedback_cross_machine_execution.md) — per-machine tasks via shared git repo, not SSH/rsync
- [Plugin cache ≠ repo tree](feedback_plugin_cache_not_repo_tracked.md) — `gsd:`/`sparc:`/`workflows:` skills live under `~/.claude/plugins/cache/`; `git mv` cannot operate on them
- [Retry-loop reset hazard](feedback_retry_loop_reset_hazard.md) — `git reset HEAD -- .` in a retry loop under auto-sync contention can strip staged edits and land mislabeled commits
- [Codex sandbox no execution](feedback_codex_sandbox_no_execution.md) — Codex sandbox blocks ALL shell exec (not just writes); never delegate implementation/build/commit to Codex
- [Plan past-tense drift](feedback_plan_past_tense_artifact_claims.md) — plans describing proposed work as committed artifacts trick reviewers; future tense only
- [Multi-agent commit serialization](feedback_multi_agent_commit_serialization.md) — parallel agents touching shared index files race on git lock; serialize the commit phase or use worktrees
- [Mock vs live invocation](feedback_mock_vs_live_invocation_divergence.md) — for external-CLI fixes, mock tests pass what live CLIs reject; always do a live repro before close
- [Attestation enables contradiction detection](feedback_attestation_enables_contradiction_detection.md) — #2405 unlocks plan-vs-live-state defect finding, not just Class-B silencing
- [Never offer self-label plan-approved](feedback_never_offer_to_self_label_plan_approved.md) — never self-approve in chat, never pre-authorize downstream agents via handoff-prompt language; user-in-loop gate is load-bearing across session boundaries
- [Recruiter engagement criteria](feedback_recruiter_engagement.md) — consulting-level + credible source only; do NOT draft replies to generic/drive-by recruiter outreach even in active job-search context
- [Email cross-noise](feedback_email_cross_noise.md) — third parties using user's Gmail by mistake; standard unsubscribe fails; mitigate with sender-domain DELETE in routing config
- [Codex sustained-MAJOR loop](feedback_codex_sustained_major_loop.md) — when Codex MAJOR 3+ rounds while Claude+Gemini MINOR by v3, surface consensus-vs-minority decision instead of auto-cycling (#2045, #2289 anti-pattern)
- [Parallel agent write-only pattern](feedback_parallel_agent_write_only_pattern.md) — agents write files only; main session serializes commits. Avoids git-lock races without needing worktrees for every agent
- [Permission gate blocks cross-review](feedback_permission_gate_blocks_cross_review.md) — planning-only sessions can't dispatch cross-review.sh; fallback is single-author r3 with transparent provenance
- [Commit attestation narrow scope](feedback_commit_attestation_narrow_scope.md) — commit "gates passed" covers only that commit's files; broader gate can regress; re-run live, don't infer from `git log A..B -- <fix files>`
- [Isolated-clone dispatch race](feedback_isolated_clone_dispatch_race.md) — subagent executing in exec-clone must check for parallel-session landing on main workspace before writing, since both lanes share the same GitHub issue
- [Codex sandbox fallback paths](feedback_codex_sandbox_fallback_paths.md) — when shell wrapper is blocked, Codex recovers via js_repl + GitHub connector; prompt must authorize these, and MAJOR verdicts lacking a fallback-read citation are weakly grounded
- [Gemini sandbox overlay blindness](feedback_gemini_sandbox_overlay_blindness.md) — Gemini cross-review sandbox can't see sparse-checkout overlay; 2026-04-23 batch had ~54 false-positive file-missing claims across 8 plans; always verify with `git ls-files` before accepting MAJOR
- [codex-cli 0.124.0 upstream stdin-hang](feedback_codex_cli_0_124_upstream_regression.md) — installed 2026-04-23; blocks ALL `codex exec` calls regardless of stdin redirection; reproduces on 90-byte plans; #2479 filed; workaround = downgrade to 0.123.0
- [Reflog as ground truth](feedback_reflog_as_ground_truth.md) — `[rejected]` pushes and "lock failed" rebase errors can mask successful operations; check reflog + `git status` before retrying
- [Stash `^3` for untracked extraction](feedback_stash_caret_3_for_untracked.md) — `git checkout stash@{0} -- <path>` silently fails for untracked-when-stashed files; use `stash@{0}^3` (third parent = untracked tree)
- [Auto-sync as silent pusher](feedback_autosync_silent_pusher.md) — auto-sync also resolves push contention by quietly pushing local-ahead commits; wait+verify after `[rejected]` instead of retrying
- [Gemini trust-env blocks reviews](feedback_gemini_trust_env_blocks_reviews.md) — Gemini CLI exits 55 in headless without `GEMINI_CLI_TRUST_WORKSPACE=true`; wrapper masked the real stderr; durable fix landed in submit-to-gemini.sh 2026-04-24
- [llm-wiki hyphen-path pattern](feedback_llm_wiki_hyphen_module_path_pattern.md) — `scripts/data/llm-wiki/` directory name poisons every Python dotted-path reference below it; recurred 3x in 2026-04-24 agent-drafted plans; grep plans for `llm-wiki\.` as a P1 smell *verified: 2026-05-03*
- [Gmail override-filters silent defeat](feedback_gmail_override_filters_silent_defeat.md) — Inbox "Override filters for important" silently nullifies Skip-Inbox; flip to "Don't override" before installing filters (2026-04-24 ace sweep)
- [Gmail filter-first over per-thread](feedback_gmail_filter_first_over_per_thread.md) — ingestion filters + "Apply to existing" handle ~80% of mail; reserve per-thread state machines for actionable ~20% residue
- [claude-in-chrome session-scoped](feedback_claude_in_chrome_session_scoped.md) — `mcp__claude-in-chrome__*` tools bind to main session; subagents can't drive Chrome; partition: main=browser, subagents=research
- [Gmail bulk archive dialog-free](feedback_gmail_bulk_archive_no_confirm.md) — archive (any volume) has no confirm dialog; delete/empty-trash/unsubscribe DO dialog and break claude-in-chrome; stay on archive+filter surface
- [gif_creator as proof pattern](feedback_gif_creator_as_proof_pattern.md) — `mcp__claude-in-chrome__gif_creator` captures up to 50 frames w/ click indicators; audit/skill-authoring/compliance artifact; start_recording → export to `docs/sessions/` *verified: 2026-05-04*
- [superpowers/specs gitignored](feedback_superpowers_specs_gitignored.md) — brainstorming skill's default `docs/superpowers/specs/` path is silently gitignored (workspace-hub `.gitignore:438`); write durable specs to `docs/governance/` instead
- [Hermes-active preflight check](feedback_hermes_active_preflight_check.md) — when Hermes runs "remove unrelated files" cleanup loops on main, parallel commits get reverted within minutes; preflight `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` and use a worktree+feature-branch if active
- [git switch --discard-changes](feedback_git_switch_discard_changes_pattern.md) — use `git switch --discard-changes` (not `git checkout`) when `.claude/state/` is dirty; plain checkout aborts silently and downstream cp+commit lands on the wrong branch (recurred 2x in 2026-04-25 wave-3/wave-5 contamination) *verified: 2026-05-03*
- [x11vnc vs TigerVNC for headless](feedback_x11vnc_vs_tigervnc_headless.md) — x11vnc is a screen mirror and crashloops on headless hosts (no GUI session to attach to); use TigerVNC `vncserver :N` instead — verified 2026-04-27 ace-linux-2 (67,189 crashloops in 4 days)
- [NTFS dirty-volume mount path](feedback_ntfs_dirty_volume_mount_path.md) — `ntfs3` (in-kernel) refuses dirty NTFS volumes; use `ntfs-3g` (FUSE) which auto-replays journal; drop `default_permissions` and pass explicit `uid`/`gid` for ownership
- [ntfs3 breaks IntxLNK symlinks](feedback_ntfs3_symlink_intxlnk.md) — in-kernel ntfs3 reads ntfs-3g-created symlinks as raw `IntxLNK` blobs; corrupts git type-tracked symlinks; verified 2026-05-01 on workspace-hub `/dev/sdc1`; stay on ntfs-3g for any volume hosting a git repo
- [Wikimedia thumb width quirk](feedback_wikimedia_thumb_width_quirk.md) — query `imageinfo` API for canonical `thumburl`; never hand-construct width segment; main-session re-verify (subagent verification was wrong twice on 2026-04-27)
- [Lane result path outside sandbox](feedback_lane_result_path_outside_sandbox.md) — provider-autofeed lanes prescribe `agent-logs/...` paths outside the workspace-hub sandbox; Read/Write/stat blocked, Glob enumeration only; fall back to `docs/sessions/` and emit ENV-MISMATCH banner *verified: 2026-05-04*
- [Sparse-checkout: add not disable](feedback_sparse_checkout_add_not_disable.md) — acma-projects only sparse repo (368K tracked, ~6% on disk); `git sparse-checkout add <path>` for missing files, never `disable` (hung 22min on 2026-04-30 materializing ~329K files)
- [Naive secret-scan FP cascade](feedback_naive_secret_scan_false_positive_cascade.md) — agent regex matches `secrets-scan.sh` paths, "tokens used" prose, argon2 password-hashing comments; for workspace-hub paths, trust the hardened pre-commit hook
- [Origin committed with unresolved markers](feedback_origin_committed_with_unresolved_markers.md) — parallel sessions can land half-resolved files; pull produces double-nested conflict markers; `git checkout --ours` if HEAD is clean
- [Emergency-stop recovery](feedback_emergency_stop_recovery_pattern.md) — kill -P stops next iteration; partial-deleted worktree's `.git` gitlink loss is recoverable via parent-repo `.git/worktrees/<name>/HEAD` registry entry *stale: 2026-05-03*
- [Bundle orphan SHAs from worktree](feedback_bundle_orphan_sha_from_worktree.md) — `git bundle create` from parent repo fails on unreachable orphans; bundle from inside worktree where HEAD points at the SHA; tag-on-origin for cross-machine durability
- [push --no-verify for preservation](feedback_pre_push_hook_no_verify_for_preservation.md) — Iron Law bans only `commit --no-verify`; push --no-verify allowed for codex-branch preservation pushes when tier-1 hook blocks

## Project
> project_ecosystem_theme.md, project_github_workflow.md, project_2025_taxes.md
> project_cfd_openfoam_storage.md
- [Doc-intel operating model](project_doc_intel_operating_model.md) — #2205 parent + #2206/#2207/#2209 children; 2026-04-19 amendments landed; follow-ons #2360/#2361/#2362
- [GSD](project_gsd_migration.md) — sole workflow, v1.38.1, Node 24+
- [Cross-review](project_cross_review_policy.md) — gate scripts + pre-push hook + audit cron
- [Mooring knowledge](project_mooring_failures_knowledge.md) — 40 entries at knowledge/seeds/
- [Nightly researchers](project_nightly_researchers.md) — LIVE, rotating Mon-Fri
- [Harness evals](project_ai_harness_evaluations.md) — #1466-1470
- [Hermes](project_hermes_installation.md) — v0.4.0, shebang reverts (3x)
- [Hermes Codex quota](project_hermes_codex_quota.md) — #6551, follow-ups #6564-6567
- [/today tips](project_workflow_tips_today.md) — tip-of-the-day, YAML catalog
- [Solver queue](project_solver_queue_architecture.md) — PRODUCTION, batch+retry+dashboard
- [Overnight batch](project_overnight_batch_runs.md) — 5 parallel terminals nightly
- [Tier-1 refactor](project_tier1_refactor.md) — Ph1 DONE; Ph2A/2B ready
- [Field-dev econ](project_field_dev_economics.md) — DONE; follow-ups #2076,#2079,#2081
- [Field-dev arch](project_field_dev_arch_patterns.md) — DONE; follow-ups #2082,#2084,#2086
- [assethold specs](project_assethold_spec_location.md) — design docs go in docs/reports/ (specs/ gitignored)
- [assethold ownership](project_assethold_ownership_transfer.md) — transferred samdansk2 → vamseeachanta; local origin may be stale
- [TX Franchise 2026](project_tx_franchise_2026.md) — DONE; both C-Corps filed, C-Corps ineligible for passive entity
- [Daily readiness cron](project_daily_readiness_cron.md) — trig_019GWtRosbZ9rw1HxrGpsvy9, 6am CT daily, posts to repo-readiness issue
- [CAD tooling review](project_cad_tooling_review.md) — PAUSED; #2327/#2328/#2329 await doc/resource intel (#2205) review
- [Claude Design adoption](project_claude_design_adoption.md) — epic #2426, trial #2435 in-flight (10 cards pending), brand hierarchy + visual-DNA locked 2026-04-21
- [AceEngineer copy canonical sources](project_aceengineer_copy_canonical_sources.md) — llm-wiki OUT OF SCOPE for firm copy; real canonical = live site + aceengineer-strategy (private); skill at `.claude/skills/coordination/aceengineer-website-copy-alignment/`; first execution issue #6 on 2026-04-24
- [Gmail MCP scope bump](project_gmail_mcp_scope_bump_decision.md) — #2423 mutation path is OAuth `gmail.modify` on claude_ai_Gmail MCP; browser automation only for interactive UI tasks
- [Issue #2460 approval binding](project_issue_2460_approval_binding.md) — CLOSED 2026-04-23; approval markers must be revision-bound (SHA + review artifact paths + storage surface), not mutable file-path refs; follow-ups #2467/#2468/#2469 (worldenergydata flake8 lanes)
- [Wiki standards/ path decision](project_wiki_standards_path_decision.md) — `wiki/standards/<code-id>.md` routing principle sanctioned across eng/marine/naval wikis; **#2471 is CSA-Z276-only** (verified 2026-04-25), referenced codification plan does not exist; general offshore/marine substrate now scoped to aceengineer-strategy aces-#4
- [llm-wiki stays embedded](project_llm_wiki_stays_embedded.md) — 2026-04-23 #2398 CLOSED; no spinout; triggers: 200MB, external consumer, cadence conflict, CI >5min, date 2026-10-23
- [ace-linux-2 VNC](project_ace_linux_2_vnc.md) — TigerVNC `vncserver@:1` user-systemd, 127.0.0.1:5901, SecurityTypes=None gated by SSH; replaces broken x11vnc.service; runbook in `.claude/skills/operations/devops/remote-desktop-headless-ubuntu/`
- [Elements drive identity](project_elements_drive_identity.md) — WD Elements 4 TB, NTFS UUID `94183792183771FA`, mounts at `/mnt/elements` on ace-linux-1; ingest into `/mnt/ace` planned per `docs/sessions/2026-04-27-elements-drive-ingest-handoff.md`; mount RO only; dirty-bit chkdsk pending

## Tips
- [Voice prompts](user_voice_prompt_tips.md) — Linux shortcuts for voice-dictated editing

## References
> ai-orchestration.md, network_machines.md
- [achantas-data](reference_achantas_data.md) — personal data + travel as GitHub issues
- [Google CLI](reference_google_cli_paid.md) — paid GWS API access
- [Gmail MCP scope](reference_gmail_mcp_scope.md) — read+compose only, no modify; archive/label/delete require browser or user UI
- [Travel skill family](reference_travel_skill_family.md) — `.claude/skills/travel/` (workspace-hub, SHA `0722fa994`); entry = `trip-planner`; calibration trips #41/#67/#68 in achantas-data
