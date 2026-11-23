# Session Hand-off — GTM Plan Review + Implementation v2 (2026-04-21)

Copy the block below into the next session's opening prompt. Works for either Claude Code or Hermes (agent-agnostic — uses only shell/gh/git + file paths, no agent-specific tooling).

---

## Hand-off prompt (paste-ready)

We are resuming a multi-wave GTM planning + implementation workstream. The preceding session shipped **2 more user-visible fixes** to production on top of the 2026-04-20 session's 3 shipped features. Two issues closed end-to-end (#2367, #2391) through full plan → adversarial review → user-approve → implement → verify → close cycles.

### What's shipped to production (aceengineer-website)

New since prior handoff (2026-04-20 → 2026-04-21):

- **#2367** — Download-Capability-Summary CTA wired on 5 pages (demos gallery hero + 4 methodology `.method-cta` blocks), class `btn-info btn-lg`, `download` attribute. Commit `3d21b8e` on aceengineer-website main.
- **#2391** — `sitemap.xml` + `robots.txt` now serving at HTTP 200 (were both 404). `build.js` extended with `copySitemap()` and `copyRobotsTxt()` functions that copy from repo root to `dist/` on every build. `robots.txt` advertises the `www.` host instead of apex (removes an unnecessary 301 hop for crawlers). Commit `4c74e7b` on aceengineer-website main. **Scope-patch note:** plan v5 only specified `copySitemap()`; implementation discovered `robots.txt` had the same 404 root cause and added `copyRobotsTxt()` inline — `feedback_attestation_enables_contradiction_detection` pattern.

Still live from the 2026-04-20 session (trust the committed state, do not re-verify):
- 5 demo detail pages at `/demos/{freespan,wall-thickness,mudmat,pipelay,jumper-installation}.html`
- Vendored Plotly 2.32.0 + Inter fonts
- Capability-summary PDF at `/assets/capability-summary-v1.pdf` (314 972 B, SHA256 `84b3febd2b…`, 1 page Letter)
- Jest link-check CI gate (137 → 141 tests after this session)

### Issues closed this session

- **#2367** CTA wiring (plan v4 → round-4 review 2 APPROVE / 1 MINOR → plan-approved → implemented → 21 pre-commit + 13 post-deploy gates green)
- **#2391** sitemap + robots.txt fix (plan v3 → v4 → v5 → round-5 review 2 APPROVE / 1 MAJOR-with-false-positive → user-approved → implemented + bonus robots.txt patch → 141 Jest tests + 5 post-deploy gates, 4/5 pass + 1 plan-spec-error)

### Issues still closed from prior arc
- **#2342, #2343** demo detail pages
- **#2344** capability-summary PDF
- **#2407** dependabot alerts dismissed
- **#1708, #1709** already-implemented follow-ups

### Open priorities (ordered)

1. **#2357** apex→www sitemap backfill — **now critical** (bumped up from low-priority after #2391 landed). With sitemap.xml now serving, the 34 apex-host `<loc>` entries are crawler-visible and each induces a 301 (technically 307 — see note below) hop. Shipping #2357 closes the canonicalization-hop window. Currently `status:plan-review`.
2. **#2346** prospect-data pipeline — scaffolding landed last session (commit `d31bcdc29`); 8 items enumerated in `docs/gtm/intake/IMPLEMENTATION-STATUS.md`. Next logical step: 2nd canonical vessel (Allseas Lorelay pipelay barge) + `materialize_demo_inputs` for demo_04. Biggest remaining work.
3. **#2348** scanner ToS triage — plan v3 `status:plan-approved`; implementation not started. Cron `gtm-job-market-scan` is **PAUSED** since commit `a9a2a922b`; stays paused until U1-U5 unpause checklist completes during implementation.
4. **#2422** (new) detail-page CTA extension — low priority follow-up from #2367 Q3; 5 demo detail pages need the same Download-PDF anchor pattern.

### Low-priority backlog (carried from prior handoff)
- **#2349** plan-doc refresh
- **#2350** mooring animation verify
- **#2351** checkpoint dashboard
- **#2355** Node engine pin
- **#2356** GH Actions for npm test

### Open cosmetic concern (file only if you care)

Vercel returns **307** (not 301) for apex-to-www redirects across ALL paths on this project, despite `vercel.json` having `"permanent": true` on the redirect rule. Verified on `/`, `/demos/`, `/methodology/*/`, `/robots.txt`, `/sitemap.xml`. No-one has noticed for months. Cosmetic SEO implication: 307 is temporary, crawlers don't update their index to canonical `www.` as aggressively as they would with 301/308. If SEO is important, investigate whether `vercel.json` needs migration to `headers` rule, or whether a platform bug is worth filing with Vercel.

### Cross-repo + parallel-agent awareness

- **`aceengineer-website`** is a nested separate git repo (its own remote, deploys via Vercel). Commits there land separately from workspace-hub. Vercel rebuild typical latency: 30-60s post-push on small changes.
- **Parallel agent active** during both sessions — shipped #2017 plans v3 → v7 and #2405 cross-review sandbox attestation work. This causes git push races on workspace-hub main (auto-sync recovers, your commits land, but `git push` may return "rejected" initially). Pattern: push → if rejected, fetch + check if your commit is on origin via `git branch -r --contains <sha>` before retrying. Don't `git reset HEAD` in retry loops (hazard per `feedback_retry_loop_reset_hazard`).
- **Both sessions** touched `docs/plans/README.md` (shared index file). Multi-agent commit serialization hazard applies per `feedback_multi_agent_commit_serialization`.

### Critical workflow discipline — load before dispatching parallel agents

Memory files at `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/` (Claude auto-memory — if running Hermes, the substance is captured below for cross-agent portability):

1. **Never self-approve `status:plan-approved`.** User-in-the-loop at plan-approval is load-bearing, not friction to route around. Present links + CLI commands only — never offer "just tell me and I'll do it" shortcuts. (`feedback_never_offer_to_self_label_plan_approved.md`, added 2026-04-21.)
2. **Codex sandbox blocks filesystem writes and shell exec.** Never delegate implementation/build/commit to Codex. If Codex review is dispatched and no artifact file is produced ("silent-drop"), capture findings inline and reconstruct the artifact file yourself post-hoc. Cite `feedback_codex_sandbox_write_blocked.md` in the reconstructed header.
3. **Plan prose must be future/imperative tense** until the artifact is actually in git. Plans describing proposed work as "committed"/"vendored"/"added" trick reviewers. (`feedback_plan_past_tense_artifact_claims.md`)
4. **Plan-text review and live-state verification are complementary.** Five rounds of adversarial review on #2391 missed that `robots.txt` was also 404 — one `curl` caught it in implementation. When live-state checks are cheap, run them before committing to the plan. (`feedback_attestation_enables_contradiction_detection`, added 2026-04-20 by parallel agent.)
5. **Cross-provider review payoff:** Codex finds non-overlapping defects vs. Claude + Gemini; always verify Codex's GitHub-connector evidence locally (Codex's sandbox-visibility blind spots can produce false-positive "MISSING" claims — `cross-review.sh` was flagged MISSING in round-5 when the file is demonstrably in git). (`feedback_cross_provider_review_payoff.md`)
6. **Parallel agents racing on shared index files.** Serialize commit phases or use per-agent worktrees when touching `docs/plans/README.md`, `MEMORY.md`, or other shared-index files. (`feedback_multi_agent_commit_serialization.md`)

### Workflow summary (mandatory per `.claude/CLAUDE.md` and `.claude/rules/`)

Issue → Resource Intel → Plan → Adversarial Review (Claude + Codex + Gemini via `scripts/review/cross-review.sh <plan> all --type plan`) → `status:plan-review` → **USER APPROVES** → `status:plan-approved` → Implement → Post-deploy verify → Close.

User approval is a discrete user action (CLI label transition, web UI click, or explicit chat instruction they author). Never self-transition.

### Suggested first actions for new session

1. `cd /mnt/local-analysis/workspace-hub && git status && git log --oneline -5 && cd aceengineer-website && git status && git log --oneline -3` — confirm clean state on both repos.
2. `gh issue list --state open --label "status:plan-approved" --repo vamseeachanta/workspace-hub` — surface ready-to-implement plans.
3. Pick one:
   - **Fast + high-value:** work #2357 (apex→www sitemap backfill). Currently `status:plan-review`. Read plan, run adversarial review if needed, self-approve by the user, implement. This closes the canonicalization-hop window that #2391's v5 decoupling left open.
   - **Deep:** resume #2346 implementation. Read `docs/gtm/intake/IMPLEMENTATION-STATUS.md`, pick next unchecked item. The two lowest-hanging are the 2nd canonical vessel (Allseas Lorelay — OTC paper cited in plan) and `materialize_demo_inputs` for demo_04 (pipelay).
   - **Governance:** drive #2348 implementation — robots.txt parser + `TOS_REVIEW.md` + U1-U5 unpause checklist; unpause the `gtm-job-market-scan` cron.

### Context-loading paths (cold-start)

- This hand-off: `docs/session-handoffs/2026-04-21-gtm-plan-review-implementation-v2.md`
- Prior hand-off: `docs/session-handoffs/2026-04-20-gtm-plan-review-implementation.md`
- Plan files: `docs/plans/2026-04-*.md`
- Review artifacts: `scripts/review/results/2026-04-*.md` (every round of every plan is kept; naming convention `<date>[-v<N>]-plan-<issue>-<reviewer>.md`)
- Implementation evidence: each closed issue's final comment on GitHub contains the full pre/post-commit gate results
- Scaffolding status (for #2346): `docs/gtm/intake/IMPLEMENTATION-STATUS.md`
- Cross-review harness: `scripts/review/cross-review.sh`

Trust the committed state. If anything looks off, grep for the commit SHA listed above to verify. Don't re-review shipped work.

---

**End hand-off prompt.**
