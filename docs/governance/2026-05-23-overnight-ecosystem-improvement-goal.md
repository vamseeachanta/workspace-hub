# Overnight Ecosystem Improvement Goal — "Deepening Sweep"

> **Purpose:** A copy-pasteable, ecosystem-tuned prompt for an overnight autonomous run that
> *enhances* the repo ecosystem — surfacing and landing safe, high-value, low-risk improvements
> across repos, gated by adversarial cross-review and a human morning-merge.
>
> **Default posture: PROPOSE, do not auto-merge.** Overnight work lands as *draft PRs* + GitHub
> issues, never merged unattended. This is deliberate — it respects the load-bearing human-in-loop
> gate (`feedback_never_offer_to_self_label_plan_approved`).
>
> **Status:** candidate `/goal` catalog entry (ecosystem-tuned, slot #31). Before first use, add it
> to catalog [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) so the weekly
> picklist can allocate it a runner + token budget.

---

## THE PROMPT (paste below this line into the overnight session)

```
GOAL: Overnight Ecosystem "Deepening Sweep" — propose safe, high-value improvements across the
repo ecosystem, one repo per runner, landing as adversarially-reviewed DRAFT PRs + tracking issues
for human morning-merge. Improve testability, AI-navigability, doc freshness, and CI health.
Do NOT merge anything. Do NOT touch published-repo licensing/branding.

═══════════════════════════════════════════════════════════════════════════
PHASE 0 — CONTRACT & SAFETY PREFLIGHT  (abort the run if any check fails)
═══════════════════════════════════════════════════════════════════════════
1. Fetch the /goal catalog + weekly picklist (REQUIRED by .claude/rules/goal-invocation.md):
     gh issue view 2695 --repo vamseeachanta/workspace-hub --json body
     gh issue view 2695 --repo vamseeachanta/workspace-hub --comments | tail -200
   - Confirm this entry (Deepening Sweep) is on this week's picklist and which RUNNER it is
     allocated to (claude / codex / hermes / gemini). If THIS runner ≠ allocated runner, STOP
     and surface the mismatch (feedback_multi_agent_commit_serialization).
2. Verify the plan-approved gate: this run requires status:plan-approved on its tracking issue.
   NEVER self-approve and NEVER self-label. If unset, STOP and ask a human.
3. Parallel-work check (feedback_check_parallel_work): scan in-flight sessions + wip-labelled
   issues. For each candidate repo, `git fetch --all` and grep open PRs/issues so you don't
   re-solve work another machine already pushed (feedback_fetch_remote_before_resolving_issue).
4. Hermes preflight (feedback_hermes_active_preflight_check): pgrep for active Hermes workers on
   any repo you intend to touch; if active, use a feature branch + (for large repos) skip worktree
   isolation — do not race its cleanup loop.

═══════════════════════════════════════════════════════════════════════════
PHASE 1 — REPO SELECTION  (one repo per runner; size-aware)
═══════════════════════════════════════════════════════════════════════════
Eligible repos (pick per weekly allocation; default rotation): digitalmodel, assethold,
worldenergydata, llm-wiki, aceengineer-website, achantas-data, workspace-hub.

Selection rules:
- GREEN BASELINE ONLY: `gh run list --branch main --limit 5` must not be already-red
  (feedback_ci_baseline_red_not_pr_broken). If main CI is red, the ONLY allowed work is a
  diagnostic issue documenting the red baseline — no feature changes on top of red.
- SIZE GUARD: digitalmodel & workspace-hub are 19K–33K files — do NOT use worktree isolation
  (feedback_worktree_isolation_large_repo_cost / _materialization_variance). Work on a feature
  branch in place; serialize commits.
- PUBLISHED-REPO GUARD: never touch LICENSE / branding / per-repo .claude
  (feedback_per_repo_metadata_is_firewall). Off-repo intel goes to /mnt/ace/<repo>/docs, never
  in-repo (feedback_offrepo_intel_routing).

═══════════════════════════════════════════════════════════════════════════
PHASE 2 — IMPROVEMENT LOOP  (per repo; use the installed skills as the engine)
═══════════════════════════════════════════════════════════════════════════
For the selected repo, on a fresh feature branch `overnight/deepening-YYYY-MM-DD`:

  A. MAP — invoke `zoom-out` to build a module/caller map in the repo's own vocabulary.
  B. FIND — invoke `improve-codebase-architecture` to surface *deepening opportunities*
     (shallow→deep modules, tight coupling, low testability/AI-navigability). Read the repo's
     CONTEXT.md / docs/adr/ first if present; if absent, note that as a finding (a missing shared
     language is itself an improvement opportunity).
  C. TRIAGE — rank findings by (value ÷ blast-radius). Pick only SMALL, independently-reviewable
     vertical slices ("tracer bullets"). HARD CAP: ≤3 slices per repo per night. Anything bigger
     becomes a GitHub issue describing the work, not a code change.
  D. FIX FAILING TESTS — if the repo has failing-but-not-baseline tests, invoke `diagnose`
     (reproduce→minimise→hypothesise→instrument→fix→regression-test). Scope the regression test
     to the defect CLASS, not just the named file (feedback_regression_test_broader_than_issue_scope).
  E. IMPLEMENT — for each accepted slice use `tdd` (red-green-refactor). Python repos: `uv run`
     for everything (feedback uv_run_isolation); never bare `python`/`pytest`. Local pytest in
     digitalmodel/.venv hangs >30s — rely on CI, verify syntax via `py_compile`
     (feedback_local_venv_pytest_import_hang).

═══════════════════════════════════════════════════════════════════════════
PHASE 3 — REVIEW  (adversarial, always; scale depth to blast-radius)
═══════════════════════════════════════════════════════════════════════════
- Run an ADVERSARIAL review on every diff (feedback_adversarial_review_stance,
  feedback_always_adversarial_review_scale_depth): T1=1 / T2=2 / T3=3 providers by scope.
- Refetch the live issue/PR body before each review dispatch — never reuse cached prompts
  (feedback_reviewer_dispatch_refetch_live_body).
- If Codex is in the loop: push the artifact to GitHub BEFORE `codex exec`
  (feedback_codex_needs_pushed_artifact); verify any Codex/Gemini "file missing" claim locally
  with `git ls-files` (sandbox overlay blindness).

═══════════════════════════════════════════════════════════════════════════
PHASE 4 — LAND AS DRAFT  (commit discipline; NO merge)
═══════════════════════════════════════════════════════════════════════════
- COMMIT SERIALIZATION (feedback_multi_agent_commit_serialization): if multiple runners share a
  repo, agents WRITE FILES ONLY; one runner serializes commits. Before each commit:
  `git diff --cached --name-only` to confirm you're not sweeping a parallel session's staged files
  (feedback_retry_loop_sweep_contamination). Use atomic per-file commits separated by `;` under
  heavy git load (feedback_chained_git_op_under_heavy_load).
- Commit the INDEX, not pathspec-mode, when a staged deletion is involved
  (feedback_git_commit_pathspec_ignores_staged_deletion).
- Iron Law: never `commit --no-verify`. `push --no-verify` is allowed only for branch preservation.
- If a phase test-gates a commit, use SKIP_PUSH=1 so the post-commit autosync hook can't bypass the
  gate (feedback_post_commit_autosync_defeats_test_gate). After any `[rejected]` push, check reflog
  + status before retrying (feedback_reflog_as_ground_truth, feedback_autosync_silent_pusher).
- Open a DRAFT PR per slice. Use line-separated `Closes #X` trailers (one per line) so all refs
  fire on squash (feedback_closes_trailer_fires_once). Title prefix: `[overnight-draft]`.

═══════════════════════════════════════════════════════════════════════════
PHASE 5 — REPORT  (issue per repo + morning digest)
═══════════════════════════════════════════════════════════════════════════
- Comment a summary on every issue you touched (feedback_gh_issue_comment); render #NNNN as
  Markdown links (feedback_inline_gh_issue_url). If an issue is CLOSED, reopen→comment→close
  (feedback_gh_issue_close_silent_comment_drop). Throttle bulk comments: ≤200/batch, watch for
  "was submitted too quickly" (feedback_bulk_comment_cumulative_volume_threshold).
- Write a HUMAN-FACING morning digest as HTML (feedback_html_default_artifact) to
  docs/sessions/YYYY-MM-DD-overnight-deepening-digest.html: per repo → findings, slices landed as
  draft PRs (with links), slices deferred to issues, CI status, and the single highest-value
  follow-up. Include an explicit "NEEDS HUMAN MERGE" list.
- Post-run, comment on catalog #2695 noting this entry was used + any catalog-vs-reality divergence
  (goal-invocation.md step 5).
- PRE-COMPLETION CLEANUP AUDIT (feedback_pre_completion_cleanup_audit_gate): run the audit skill;
  bucket residue CLEAN/EXPECTED/UNEXPECTED; never report "done" with UNEXPECTED residue. Leave a
  `handoff` document (invoke the handoff skill) for the morning session.

═══════════════════════════════════════════════════════════════════════════
HARD STOPS  (abort + surface, do not improvise)
═══════════════════════════════════════════════════════════════════════════
- Any destructive op (rm, reset --hard, force-push) — STOP, never overnight.
- main CI baseline already red on a target repo — diagnostic issue only, no feature work.
- Runner ≠ weekly allocation, or plan-approved gate unset — STOP.
- A slice exceeds 3-per-repo cap or stops being independently reviewable — convert to an issue.
- Worktree dir absent after 5 min on a large repo — kill + pivot to in-place branch
  (feedback_worktree_materialization_variance).
```

---

## Why this shape (rationale for the human reviewer)

- **Propose-not-merge** is the core safety property. Autonomous overnight code *landing* (merge)
  would collide with your never-self-approve gate; draft PRs + morning human-merge keep the gate intact.
- **`improve-codebase-architecture` is the engine** — it's exactly what you just installed, and its
  "deepening opportunities" framing (shallow→deep modules, testability, AI-navigability) is the
  highest-leverage *ecosystem-enhancing* lens, not just bug-fixing.
- **Every guardrail traces to a real scar** in `MEMORY.md` — CI baseline, worktree cost on large
  repos, commit serialization, autosync defeating test gates, published-repo firewall, Hermes
  preflight. The prompt is essentially your hard-won lessons compiled into one runbook.
- **Caps + tracer-bullet slicing** keep blast-radius small: ≤3 independently-reviewable slices per
  repo; anything bigger becomes an issue, not an overnight diff.

## Wiring options (pick when ready)
1. **Add to `/goal` catalog #2695** as ecosystem entry #31 so the weekly picklist allocates it.
2. **Schedule it** via the `schedule` skill (cron remote agent) once it's catalog-listed and a
   `status:plan-approved` tracking issue exists.
3. **Dry-run first**: run Phases 0–3 on ONE green repo with the 3-slice cap, review the draft PRs,
   then enable the rotation.
