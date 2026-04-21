# Review: #2417 — framing adversarial review (during active rewrite)

Reviewer: Claude (adversarial)
Date: 2026-04-21
Target: framing comment posted 2026-04-21T10:14:07Z on issue #2417 (`IC_kwDOP48Lhs7_kWRH`)
Related: umbrella #2425, plan `docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md`, reviews `scripts/review/results/2026-04-20-plan-2417-{claude,codex,gemini}.md`

## Verdict: **MAJOR**

The framing comment misreads the reusability of `skill-autoresearch-nightly.sh`, flags the wrong two Claude-CLI items versus the actual converged MAJOR findings, includes a target surface (`.claude/hooks/`) that is a category error for an autoresearch text-rewrite loop, and lands during an active fresh-MAJOR rewrite where it supplies no remediation signal on any of the four convergent blockers. It is not neutral noise — it asserts "low-novelty, high-leverage" while three reviewers said the plan was under-specified on core contracts.

---

## What I actually verified (checklist)

- [✓] Fetched live `gh issue view 2417` — confirmed `status:plan-review` label, confirmed 2026-04-21 rollback comment present, confirmed framing comment text verbatim.
- [✓] Fetched `gh issue view 2425` — confirmed framing comment content in umbrella body matches the per-issue framing ("wait for rewrite wave", "⭐⭐⭐ readiness in fresh-MAJOR rewrite").
- [✓] Read full `scripts/cron/skill-autoresearch-nightly.sh` (240 lines) — hard-coded skill-only assumptions catalogued (see finding 1).
- [✓] Read all three MAJOR review artifacts (`2026-04-20-plan-2417-{claude,codex,gemini}.md`) — extracted converged blocker list.
- [✓] Read full plan `docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md` — verified the 4 open questions in §Risks, §Open, §Adversarial Review Summary.
- [✓] Inspected `.claude/agents/`, `.claude/get-shit-done/templates/`, `.claude/hooks/`, `.claude/rules/` on disk — confirmed heterogeneity (markdown agent prompts, mixed templates including JSON + MD, **shell scripts** for hooks, short MD rules).
- [✗] Did NOT run `tests/cron/test_skill_autoresearch.sh` or any unit tests — review is document-only.
- [✗] Did NOT inspect `config/scheduled-tasks/schedule-tasks.yaml` to verify scheduled-task integration claims in the framing.

---

## Findings

### 1. **MAJOR — "reusable as claimed" overstates reuse; script is skill-specific in load-bearing ways.**

Framing claim: "`scripts/cron/skill-autoresearch-nightly.sh` already proves the `claude -p` + budget + rotation loop … mostly surface-area, not novel orchestration."

Actual script evidence (`scripts/cron/skill-autoresearch-nightly.sh`):
- Line 25: `RESULTS_FILE=".../.claude/state/skill-autoresearch/results.tsv"` — skill-specific state dir.
- Line 24: `BRANCH="autoresearch/skills-${DATE}"` — skill-branded branch naming.
- Line 29: `EVAL_SCRIPT=".../skill-eval/scripts/eval-skills.py"` — hard-wired to skill-eval Python script.
- Lines 82–101: ranking logic pipes JSON through Python that keys on `s['name']` (skill-eval schema) and counts `WARNING`-severity `issues` — not an abstract evaluator protocol.
- Lines 131–132: `find ".../.claude/skills" -path "*/${skill_name}/SKILL.md"` — target discovery literally greps SKILL.md.
- Lines 154–165: amendment prompt is skill-specific ("improving a SKILL.md file", "Keep the file under 150 lines") — not a target-type-aware template.
- Lines 186, 194–204: post-amendment eval again invokes skill-eval and reads skill-eval's summary schema.
- Line 51: TSV header is `date\tskill\twarnings_before\twarnings_after\tresult\tduration_s` — the exact schema migration flagged by all three reviewers.

The "reusable" portions are: `git_safe_init` / stashing / branch create/switch / timeout guard / keep-or-revert decision flow. Those are ~40 of the 240 lines. The other ~200 lines are skill-shaped. Calling this "surface-area, not novel orchestration" is wrong by line count and wrong by responsibility — the evaluator protocol, prompt synthesis, target discovery, and results schema are all parts the reviewers called under-specified, and all four live inside this script today as skill-hardcoded.

### 2. **MAJOR — The two flagged Claude-CLI items do not address any of the four converged MAJOR findings.**

Framing flags two items for the rewrite:
1. "Per-surface prompt file versioning"
2. "Output-location isolation so `.claude/agents/` research doesn't overwrite `.claude/skills/` research artifacts"

Converged MAJOR findings across all three reviewers (from the three review files and the 2026-04-20 rollback comment):
- (A) Evaluator contract under-specified (all 3).
- (B) Results-schema migration / backward-compat unresolved (all 3).
- (C) `workflow-config` has no explicit v1 allowlist (all 3).
- (D) Wrapper/core integration architecture ambiguous (Claude + Codex; Gemini adjacent).

The framing's item (1) "prompt-file versioning" is a net-new nice-to-have not raised by any reviewer. The framing's item (2) "output-location isolation" is tangential to (B) at best — "isolation" is a path-namespacing concern, while the actual blocker is additive-vs-in-place schema migration + downstream consumers of `results.tsv` (called out explicitly by Gemini: `skill-health-dashboard.sh`). Neither flagged item touches (A), (C), or (D). The framing is flagging cosmetic polish while the rewrite is stuck on contract definition.

### 3. **MAJOR — `.claude/hooks/` listed as a target surface is a category error.**

Framing comment: "Generalizing to `.claude/agents/`, `.claude/get-shit-done/`, `.claude/rules/`, and `.claude/hooks/` is mostly surface-area, not novel orchestration."

Verified on-disk: `.claude/hooks/` contains executable shell scripts (`capture-corrections.sh`, `check-claude-md-limits.sh`, `check-encoding.sh`, `check-js-lockfiles.sh`, `config-protection-pretooluse.sh`, etc.). Hooks are not prompt-bearing text that an `claude -p` rewrite loop can edit safely. They are behavioral enforcement code — regressions here would alter commit gating, state-file sizing, and tool-use protection. The autoresearch keep/revert loop uses warning counts as an improvement predicate; hooks have no such evaluator and their "warnings" surface is a lint pass on shell, which is unrelated to autoresearch's improvement thesis.

Also: the **issue body** lists the in-scope target types as `skill`, `agent`, `template`, `workflow-config` — hooks are NOT in the issue's scope. The framing is expanding scope beyond what the plan and the issue cover, during an active rewrite, which adds noise rather than clarifying direction.

### 4. **MAJOR — "Minor tweaks per surface" understates per-surface evaluator work.**

On-disk heterogeneity of the listed target surfaces:
- `.claude/agents/` — markdown agent definitions (e.g. `code-reviewer.md`, `gsd-*.md`). No existing evaluator. Improvement predicate undefined.
- `.claude/get-shit-done/templates/` — mixed: markdown (`AI-SPEC.md`, `claude-md.md`, `continue-here.md`) AND `config.json` AND a subdirectory `codebase/`. No uniform evaluator. Some files are prompt-bearing markdown, one is JSON config — different parse/validate paths.
- `.claude/rules/` — terse markdown (`coding-style.md`, `patterns.md`, `README.md`), each ≤ ~30 lines by convention. No evaluator; "warnings" here would have to be defined from scratch.
- `.claude/hooks/` — shell (see finding 3).

Each surface needs its own evaluator implementation, its own prompt contract, its own keep/revert predicate. The framing's "surface-area, not novel orchestration" collapses all of this into a flat claim. This is exactly the gap Claude/Codex/Gemini called out as "evaluator contract under-specified" — the framing reproduces the same blind spot at a higher level.

### 5. **MINOR — Timing conflicts with active rewrite stance.**

The framing comment says "Plan remains in rewrite" and "Framing only — no status label change," yet the issue was rolled back to `status:plan-review` only ~7 hours earlier. Posting framing that asserts "most direct extension of existing pattern" and "low-novelty, high-leverage" during an active rewrite cycle biases the rewriter toward "small change" when three independent reviewers just said the plan's contracts are missing. Either (a) contribute concrete remediation on (A)–(D), or (b) stay silent until the v2 plan exists. The current middle-ground framing is the noise case described in the adversarial angle.

### 6. **MINOR — Framing contradicts its own premise on readiness.**

Umbrella #2425 table marks #2417 as "⭐⭐⭐" and "wait for rewrite wave." The per-issue framing argues it is the **most direct extension** of an existing pattern — which should read as ⭐⭐⭐⭐ or ⭐⭐⭐⭐⭐ if true. Either the "most direct extension" claim is overstated, or the umbrella's ⭐⭐⭐ / wait posture is wrong. One of them has to give; right now the framing sends a mixed signal ("simplest rollout candidate, but also not ready").

### 7. **MINOR — "Lower risk than #2413 / #2424" is asserted, not evidenced.**

Framing: "Risk profile is lower than #2413 (no external scope constraints) and #2424 (no cross-repo auth)."

#2417's actual risk profile, per its own plan §Risks (lines 180–184): `workflow-config` sprawl, weak non-skill evaluator quality, `results.tsv` consumer breakage, open question of whether to mutate the schema in place. These are internal-design risks, not external-auth risks, but they are not "lower" — they are the exact class that generated three MAJOR verdicts. Comparing across risk categories without normalization is unsupported.

---

## Required changes before proceeding

1. **Retract or revise the two flagged items**: replace "prompt-file versioning" and "output-location isolation" with the four converged blockers (A) evaluator contract, (B) results-schema migration, (C) workflow-config allowlist, (D) wrapper/core integration. If Claude-CLI framing adds value, it adds it on these.
2. **Drop `.claude/hooks/` from the target list** in the comment — it is shell code, not prompt-bearing text, and it is not in the issue scope. If hooks are genuinely a target, that requires a new issue and a new evaluator class (lint-on-shell, not autoresearch-rewrite).
3. **Remove the "low-novelty" framing** OR qualify it: acknowledge that target discovery, evaluator protocol, prompt synthesis, and results schema are all currently skill-hardcoded in the existing script (findings 1 + 4), so the rewrite is medium-novelty on each of four axes, not low-novelty.
4. **Reconcile with umbrella #2425's ⭐⭐⭐ / wait posture** — either upgrade the rank or remove the "most direct extension" claim.
5. **If the intent is to help the rewrite, contribute a concrete evaluator-protocol sketch or a workflow-config allowlist** — those are what's actually blocking approval. A comment that neither unblocks nor scopes-down has no useful role during `status:plan-review`.

---

## What I did NOT check (honesty declaration)

- Did not execute `tests/cron/test_skill_autoresearch.sh` to verify the "10 passed" claim from the issue body.
- Did not read `config/scheduled-tasks/schedule-tasks.yaml` to verify scheduled-task integration scope.
- Did not inspect `skill-health-dashboard.sh` to confirm its `results.tsv` consumption pattern (Gemini asserted it; I took Gemini's word).
- Did not check whether a v2 plan file has been drafted since the 2026-04-21 rollback — this review is against the v1 plan + today's framing comment.
- Did not review #2418 (compounding loop) for scope-overlap, though the framing references budget-guard pairing.
- Did not verify other umbrella rollout candidates (#2347, #2424, #2413) to confirm the cross-issue ranking.
- Did not evaluate whether `.claude/get-shit-done/` (mentioned in framing) is the same path as `.claude/get-shit-done/templates/` (mentioned in the plan) — they may differ, and that's a scope ambiguity in the framing itself.
