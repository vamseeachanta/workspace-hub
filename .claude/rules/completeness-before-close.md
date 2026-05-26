# Completeness-before-closure gate — agent rule (#2798)

**When closing an issue that OPTED IN (carries the `gate:completeness` label) and reached `status:plan-approved`, a test-/evidence-based completeness score (0–100%) must be computed, persisted, owner-reviewed, and ≥ its class threshold BEFORE `gh issue close`.**

> **Rollout (opt-in):** the gate enforces ONLY for issues explicitly labeled `gate:completeness`. The existing backlog and routine closes are untouched until opted in. An unconfigured gate (no `COMPLETENESS_OWNERS`) is inert for non-opted-in issues. Graduate to repo-wide enforcement only after the rollout is proven.

**Why:** closure should reflect verified completeness, not agent self-report. The user reviews an objective, test-grounded score before the issue is closed (per the 2026-05-25 requirement). Child of the enforced-gates epic [#1839](https://github.com/vamseeachanta/workspace-hub/issues/1839); reuses the module-status-matrix `quality_score`/`test_source_ratio` (#1629).

**How to apply:**

1. **Compute** the score with `scripts/workflow/completeness_score.py` (pure module):
   - `code` class (changed files map to a package) — reuses #1629 `quality_score` + `test_source_ratio` (fail-closed on stale snapshot), changed-code coverage, and an **evidence-linked** acceptance checklist. Threshold **90**.
   - `evidence` class (ops/docs/governance, no test surface) — weighted ratio of met evidence items. Threshold **80**.
   - Class is **auto-derived from changed files, not selectable** (no dodging code scoring via the ops path).
2. **Persist** the computed record to `hermes kanban complete --metadata '{"completeness_pct":N,...}'` AND stamp it on the issue body as a ```completeness {json}``` block.
3. **Render** the HTML artifact: `scripts/workflow/render_completeness_html.py` → `docs/reports/<date>-<issue>-completeness.html` (embeds the exact record; per `feedback_html_default_artifact`).
4. **Owner verifies** by applying the **owner-only `status:completeness-verified` label** (ruleset-restricted appliers). The agent records only the *computed* score; it cannot self-verify. The verified label must be applied **at or after** the issue body's last edit — editing the body after verification invalidates the label (anti-forgery). The closure threshold comes from **server-side class config**, never the body record. The gate only applies to issues closed as **`completed`** that carry **`status:plan-approved`** (un-planned/duplicate/won't-fix closes are not gated).
5. **Gate** (enforcement gradient per `.claude/rules/patterns.md`):
   - *Level 2 (advisory, local):* `scripts/enforcement/check-completeness-before-close.sh <issue>` — fast pre-flight; bypass `COMPLETENESS_ALLOW=1`.
   - *Level 3 (authoritative, server-side):* `.github/workflows/completeness-gate.yml` fires on `issues.closed`; if the record/label are missing/invalid or the verifier is the closer or pct<threshold, it **reopens the issue and comments**. A local git hook cannot intercept `gh issue close` (it is an API call) — this is why the gate is a GitHub Action.

**Position in the close flow (issue-planning-mode):** Issue → Plan → Approve → Implement → **Cross-review → [completeness gate] → Close** → (post-closure promotion #2236).

**Do NOT apply when:** the issue produced no work (duplicate, won't-fix, invalid) — close normally; the gate only fires when a completeness record is expected. Override the computed % **down only** (owner may judge it lower); never silently raise it.

**Related:** [`patterns.md`](patterns.md) (enforcement gradient), `feedback_completeness_score_before_closure`, `feedback_html_default_artifact`, [#1839](https://github.com/vamseeachanta/workspace-hub/issues/1839), [#1629]/#1663 (score substrate), [#2110](https://github.com/vamseeachanta/workspace-hub/issues/2110) (session-close report), [#2236](https://github.com/vamseeachanta/workspace-hub/issues/2236) (post-closure promotion).
