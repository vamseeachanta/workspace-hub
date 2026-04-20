# Session Hand-off — GTM Plan Review + Implementation (2026-04-20)

Copy the block below into the next session's opening prompt.

---

## Hand-off prompt (paste-ready)

We are resuming a multi-wave GTM planning + implementation workstream. The preceding session shipped 3 user-visible features to production, approved 3 plans, opened 10 new issues, dismissed 29 dependabot alerts, and left 2 plans at v3 with a single sequencing-update fix outstanding. Scaffolding for the biggest approved plan (#2346) is in place.

### What's shipped to production (aceengineer.com)

- 5 demo detail pages live at `/demos/{freespan,wall-thickness,mudmat,pipelay,jumper-installation}.html` — nav + footer + Google Analytics + vendored Plotly
- Vendored Plotly 2.32.0 (SHA256 `0a17719a...`) + BSD-3 LICENSE at `/assets/js/`
- Capability-summary PDF at `/assets/capability-summary-v1.pdf` (1 page, Letter, Inter embedded, SHA256 `84b3febd2b...`)
- Vendored Inter fonts at `/assets/fonts/inter/`
- Jest link-check CI gate + cache-control for `/demos/*.html`

### Issues closed this arc

- #2342, #2343 — demo detail pages (Commits 1 + 2)
- #2344 — capability-summary PDF rendered and live
- #2407 — 29 dependabot alerts dismissed (all orphan-path; `ref/py_react_sql/client/yarn.lock` deleted in `06f38714`)
- #1708, #1709 — already-implemented follow-ups closed with citations

### Plans approved and ready for implementation

- **#2346** prospect-data pipeline — `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` (v3.1, plan-approved). **Scaffolding landed** (commit `d31bcdc29`): intake schema, 1 canonical vessel (Seven Borealis, OTC-24523 + Bai&Bai ISBN), adapter skeleton, 6 passing tests, `docs/gtm/intake/IMPLEMENTATION-STATUS.md` enumerates what's deferred.
- **#2348** scanner ToS triage — `docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md` (v3, plan-approved). Implementation not started. **Cron `gtm-job-market-scan` is PAUSED** since commit `a9a2a922b`; stays paused until U1-U5 unpause checklist completes during implementation.

### Plans at v3 awaiting one small revision each

Both converged on the same class of issue — a single sequencing paragraph that treats #2344 as "not yet shipped" when the PDF is now live. Single-edit fix each.

- **#2367** CTA wiring (4 methodology pages + gallery download link) — `docs/plans/2026-04-20-issue-2367-pdf-cta-wiring.md` at `d77e106a3`. Reviews: Claude v3 MINOR, Codex v3 REQUEST-CHANGES. Both flag: `Sequencing predecessors` and Resource Intelligence still say "#2344 — will publish capability-summary-v1.pdf / Not yet cleared". Fix: rewrite those 4-5 lines to reflect that #2344 is live (commit `6f16cbd` on aceengineer-website, SHA256 `84b3febd2b...`), update Gaps/Acceptance to retain runtime verification gates.
- **#2391** sitemap 404 fix — `docs/plans/2026-04-20-issue-2391-sitemap-404-fix.md` at `931752fbd`. Reviews: Claude v3 MINOR (approve for implementation), Codex v3 silent-dropped. Only residuals are cosmetic traceability. Could self-approve without round 4; user's call.

### Outstanding implementation work (priority order)

1. **#2367 v4 sequencing update** — trivial; single-plan-paragraph edit. Then approve + implement + push to aceengineer-website.
2. **#2391 approval + implementation** — sitemap copy in build.js (~5-line patch). Bundled or back-to-back with #2357 (apex→www backfill).
3. **#2346 full implementation** — scaffolding done; 8 items enumerated in `docs/gtm/intake/IMPLEMENTATION-STATUS.md` (2 remaining canonical vessels, per-demo `materialize_demo_inputs` logic, `run_demo` subprocess dispatch, `branded_report.py` wrapper, dual-delivery state machine, SOP runbook, fallback sidecar, E2E across 5 demos). Biggest remaining work.
4. **#2348 implementation** — robots.txt parser wired into `safe_request()`, `TOS_REVIEW.md` with owner sign-off per source, LinkedIn `_OWNER_OVERRIDE_SOURCES` mechanism, remove dead sources (`google`/`google_direct`/`rigzone`) from `SOURCE_ALLOWLIST`, U1-U5 unpause checklist. **Cron stays paused until all 5 done.**

### Low-priority backlog

- #2357 (apex sitemap backfill — bundle with #2391), #2349 (plan-doc refresh), #2350 (mooring animation verify), #2351 (checkpoint dashboard), #2355 (Node engine pin), #2356 (GH Actions for npm test)

### Cross-repo note

`aceengineer-website` is a nested separate git repo (its own remote, its own deploys via Vercel). Commits there land separately from workspace-hub.

### Workflow discipline — read memory first

Before dispatching parallel agents, read these in `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`:

- `feedback_codex_sandbox_no_execution.md` — Codex cannot run shell commands; never delegate implementation/build/commit to Codex. Use Claude general-purpose instead.
- `feedback_codex_sandbox_write_blocked.md` — Codex cannot write files; capture review findings inline and transcribe manually.
- `feedback_plan_past_tense_artifact_claims.md` — plans describing prescribed work as "committed"/"vendored"/"added" trick reviewers; use future/imperative tense exclusively until the artifact is actually in git.
- `feedback_multi_agent_commit_serialization.md` — parallel agents touching shared index files (`docs/plans/README.md`, `MEMORY.md`) race on `.git/index.lock`. Either serialize the commit phase or use per-agent worktrees.
- `feedback_cross_provider_review_payoff.md` — Codex catches defects Claude misses (and vice versa) because Codex forces GitHub-state verification. Run both in every adversarial review.

### Recommended first actions for new session

1. `git status` in workspace-hub and aceengineer-website — confirm clean.
2. `gh issue list --state open --label "status:plan-approved"` — surface ready-to-implement plans.
3. Pick one:
   - **Fast path:** revise #2367 v4 sequencing (5-min edit) + self-approve #2391 → both move to plan-approved. Then implement whichever you want to ship first.
   - **Deep path:** resume #2346 implementation where scaffolding left off (see `docs/gtm/intake/IMPLEMENTATION-STATUS.md`). Next logical step: add 2nd canonical vessel (pipelay barge — Allseas Lorelay, OTC paper cited in plan) + flesh out `materialize_demo_inputs` for demo_04 (which the pipelay vessel targets).
   - **Governance path:** drive #2348 implementation; robots.txt parser + TOS_REVIEW.md authoring + U1-U5 checklist run; unpause the cron.

### Context loading

If you need the full prior-session arc:
- Plan artifacts: `docs/plans/2026-04-19-issue-2344-*.md`, `-2346-*.md`, `-2348-*.md`, `2026-04-20-issue-2367-*.md`, `2026-04-20-issue-2391-*.md`
- Review artifacts: `scripts/review/results/2026-04-*plan-234{4,6,8}-*.md`, `-2367-*.md`, `-2391-*.md`
- Implementation verification: `docs/security/aceengineer-website-orphan-path-verification-2026-04-20.md`
- Scaffolding: `docs/gtm/intake/IMPLEMENTATION-STATUS.md`
- This hand-off file: `docs/session-handoffs/2026-04-20-gtm-plan-review-implementation.md`

Do not re-review shipped work; trust the committed state. If anything looks off, grep for the commit SHA listed above to verify.

---

**End hand-off prompt.**
