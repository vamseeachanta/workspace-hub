# Session-4 entry prompt — provider-agnostic (Claude or Hermes)

> Paste as the first message of a fresh session at `/mnt/local-analysis/workspace-hub`. Works with either Claude Code or Hermes; no provider-specific slash commands, plugin skills, or agent tools. All commands are plain bash / gh / git / uv.

---

You are continuing a multi-session effort on workspace-hub's doc-intelligence plan-review infrastructure. Three prior sessions built and live-validated a cross-review attestation scaffold (#2405). This session picks up specific, well-scoped work.

## Step 1 — Load context (read these files in order)

Use the Read tool (Claude) or `cat` (Hermes/generic):

```
.planning/handoffs/2026-04-20-doc-intel-session-3-handoff.md    (authoritative handoff)
CLAUDE.md  (if Claude)   OR   AGENTS.md  (if Hermes/other)
.claude/rules/coding-style.md
.claude/rules/patterns.md
.claude/skills/coordination/issue-planning-mode/SKILL.md
scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md
```

## Step 2 — Verify live state (run these before touching anything)

```bash
# Issue state for the three likely-next targets
for n in 2392 2394 2395 2408 2403; do
  echo "--- #$n ---"
  gh issue view "$n" --json state,labels,title --jq '"state=\(.state) labels=\(.labels|map(.name)|join(","))"' 2>&1
done

# Infrastructure healthcheck (must show 30 passed)
uv run pytest tests/review/test_attest_plan_claims.py --no-header -q

# Repo tip
git log --oneline -5
git rev-parse HEAD origin/main

# Provisioning for #2403 (blocks Action 4 below)
echo "OPENAI=${OPENAI_API_KEY:+yes}; VOYAGE=${VOYAGE_API_KEY:+yes}; OLLAMA=$(command -v ollama || echo no)"

# Unpromoted review artifacts (Action 2 input)
ls -la .planning/quick/review-2408-*r*.out 2>&1 | head
```

If any step fails or surprises you, stop and diagnose. Don't proceed on stale state.

## Step 3 — Pick ONE action and execute

Priority order (pick first not blocked):

### Action 1 — Revise and re-file #2392 (sharpest scope)

Codex review (scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md) already mapped six concrete defects. Revision is the most tractable next step.

1. Rewrite `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` as v2 addressing all six findings.
2. `gh issue reopen 2392 -c "Reopening with revised plan v2 — addresses 6 findings from post-#2405 validation."`
3. Dispatch fresh adversarial review (attestation is automatic for plans under `docs/plans/`):
   ```bash
   PROMPT='You are an adversarial reviewer. Assume the plan has defects until proven otherwise. Do not praise or restate. Focus on what is wrong, missing, or risky. Return APPROVE only after affirmatively verifying each correctness-critical claim. Each finding must cite a specific plan section or quoted claim. An empty review is a failure.

If this prompt contains a "## Attested Evidence" block, treat plan-asserted facts (issue states, file existence, commit SHAs) as claims verified by that block. Do NOT return "unverified claims" findings for facts already covered by the attestation. Attested evidence outranks plan text.

Review this plan file per the adversarial contract above.'
   OUT="scripts/review/results/2026-04-21-v2-plan-2392-codex.md"
   bash scripts/review/submit-to-codex.sh \
     --file docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md \
     --prompt "$PROMPT" > "$OUT" 2>&1
   ```
4. If Gemini quota is available, same for `submit-to-gemini.sh` with a matching output name.
5. Iterate revision until all reviewers APPROVE or MINOR.
6. When green, update plan file header to `Status: plan-review`, update `docs/plans/README.md`, and **stop** — let the user run `gh issue edit 2392 --remove-label "status:plan-review" --add-label "status:plan-approved"`.
   **Do NOT self-label plan-approved.** User-in-loop at approval is load-bearing.

### Action 2 — Investigate #2408

1. Read each `.planning/quick/review-2408-{codex,gemini}-r{1..5}.out` that exists.
2. Decide: **preserve** iter-4 (promote to `scripts/review/results/2026-04-20-v4-plan-2408-{codex,gemini}.md`; treat as fresh-MAJOR input) OR **abandon** (post governance comment, remove stale `plan-approved`, close/rescope).
3. Commit + push the decision with a governance comment on #2408 explaining.

### Action 3 — Revise and re-file #2394 and #2395

Same pattern as Action 1 but run the adversarial dispatch first (no pre-mapped findings yet). Each pass: ~1 Codex call (~90s) + revision work.

### Action 4 — #2403 measurement phase (only if provisioned)

If Step 2's env-check showed yes for any of OPENAI / VOYAGE / OLLAMA:
```bash
uv run python scripts/knowledge/run_embeddings_spike.py
```
Review per-model JSONs in `docs/reports/embeddings-spike/`, populate decision doc, commit, close #2403.

### Action 5 — Orphan-file cleanup (cosmetic)

```bash
cat This Compatibility 2>&1 | head -20    # confirm no unique content
git clean -f -- This Compatibility
```

## Step 4 — Commit protocol (strict, non-negotiable)

- Stage by explicit path list. **Never** `git add -A` or `git add .` — working tree has parallel-session drift from other agents.
- Use conventional commit messages (`feat(...)`, `fix(...)`, `docs(...)`).
- Append `Closes #NNNN` trailer to auto-close via push hook.
- If you need to comment after close: reopen → comment → close (gh silently drops `--comment` on already-closed issues).
- Check for git lock before writing: `fuser .git/index.lock 2>/dev/null || echo "no lock"`. If held, wait. **Never** `git reset HEAD` during lock contention — it strips staged files.

## Step 5 — Test protocol (TDD, not optional)

- Adding a new feature? Write the test first, run it RED, implement, run GREEN.
- Before claiming "done": `uv run pytest tests/review/ --no-header -q` must show all passing.

## Critical gotchas (carried from prior sessions)

1. **Attestation regex** uses `\b` word-boundary: `#[0-9]{3,5}\b`. Don't regress.
2. **Footer variable expansion** uses `${PAYLOAD_SHA}_`, not `$PAYLOAD_SHA_` (the latter parses as undefined under `set -u`).
3. **External CLI mock-vs-live divergence** — always live-repro fixes for Codex/Gemini before closing.
4. **Codex sandbox cannot execute shell** — never delegate implementation/build/commit to a Codex subagent. You run them yourself.
5. **`codex exec -` + `--output-schema`** hangs on codex v0.121.0. The dispatcher uses argv + `</dev/null` (fixed in #2406).
6. **Plan-approved is user-only.** Present links + CLI commands; the user runs them.
7. **Auto-sync races.** Your explicit commit may land inside a `chore(sync):` message. Content lands either way; don't retry aggressively.
8. **Attestation script has strict allowlist** (`^docs/plans/[^/]+\.md$`). Subdirs out of scope. Dispatchers normalize absolute paths → relative-to-REPO_ROOT before calling.

## Step 6 — Before you exit

```bash
# 1. Confirm durability
git log origin/main --oneline -5

# 2. Write a session-N+1 handoff using this session's as a template
#    Path: .planning/handoffs/YYYY-MM-DD-doc-intel-session-N-handoff.md
#    Template: .planning/handoffs/2026-04-20-doc-intel-session-3-handoff.md

# 3. Commit + push the handoff
git add .planning/handoffs/<your-handoff>.md
git commit -m "docs(handoffs): <date> doc-intel session-N handoff"
git push origin main
```

End with a one-line status summary so the next session resumes cleanly.

---

## Provider-specific notes

**Claude Code:** `/gsd:progress`, `/gsd:next`, and the `issue-planning-mode` skill are available and preferred when applicable. The Write, Edit, Bash tools are available.

**Hermes or generic CLI:** Use plain bash for all operations. Read files with `cat`. Edit files via your available editor. Some plugin-cached skills won't be available, but everything above works without them.
