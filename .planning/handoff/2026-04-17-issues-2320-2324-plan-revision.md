# Handoff — GH #2320-#2324 plan revisions (post-v2 adversarial wave)

**Created:** 2026-04-17
**Repo:** `/mnt/local-analysis/workspace-hub` (branch: `main`)
**Source session:** created the 5 issues, drafted 5 plans, ran 2 adversarial review waves, added stance-contract across skills + memory.

---

## TL;DR for fresh session

Five GH issues (#2320–#2324) have plans labeled `status:plan-review`. All five plans got MAJOR from Claude + Codex + Gemini in wave v2 (stance-contract applied). Plans need revision before user approval. User's verdict pending on revise / split / approve-with-debt per plan. **Do not implement any of these issues yet — none are `status:plan-approved`.**

## What exists now

| Artifact | Path |
|---|---|
| 5 GH issues | https://github.com/vamseeachanta/workspace-hub/issues/{2320,2321,2322,2323,2324} |
| 5 plan files | `docs/plans/2026-04-17-issue-232{0,1,2,3,4}-*.md` |
| 15 review artifacts | `scripts/review/results/2026-04-17-plan-232{0..4}-{claude,codex,gemini}.md` |
| Plan index rows | `docs/plans/README.md` (search for 2320-2324) |
| Stance contract (plan-review) | `.claude/skills/coordination/issue-planning-mode/SKILL.md` Step 3 |
| Stance contract (cross-review) | `.claude/skills/coordination/cross-review-policy/SKILL.md` "Reviewer Stance" |
| Feedback memory | `feedback_adversarial_review_stance.md` in auto-memory dir |
| v2 prompt template | `/tmp/plan-review-prompt-v2.md` (ephemeral — re-derive from stance contract sections if missing) |

## Wave v2 verdicts (all MAJOR)

| Issue | Claude v2 | Codex v2 | Gemini v2 | Core blocker |
|---|---|---|---|---|
| #2320 skill-usage-audit | MAJOR | MAJOR | MAJOR | Pseudocode JSON schema doesn't match real Claude Code session jsonl; 90d promise vs 15d log retention; PII unaddressed |
| #2321 plugin-consolidation | MAJOR | MAJOR | MAJOR | Mechanism (`git mv`) likely doesn't apply to plugin-owned skills; plugin config location still "TBD" |
| #2322 rule-promotion | MAJOR | MAJOR | MAJOR | `.bats` vs repo's `test_*.sh` precedent; abs-path allowlist requires AST parsing; `.claude/work-queue/` schema was invented (no top-level yamls) |
| #2323 cross-ai-review-fanout | MAJOR | MAJOR | MAJOR | Pseudocode provider invocations broken for Codex/Gemini (both need INLINE content, empirically verified this session); circular self-test; no offline/mock path |
| #2324 memory-md-curation | MAJOR | MAJOR | MAJOR | Memory-system conflation: target dir NOT git-tracked but plan proposes `git mv`; false cross-machine-sync premise |

Full findings in each plan's **Adversarial Review Summary** section and the 15 per-provider artifacts.

## User's decision framework (pending)

Three options per plan — user will decide:
1. **Revise** — rewrite plan addressing blockers, re-run wave v2. Best for durable work. Lean: #2320, #2324 (premise-level issues).
2. **Split** — break into narrower children. Lean: #2321 (plugin-owned-skill mechanism needs separate resolution first).
3. **Approve with debt** — label `status:plan-approved`, treat blockers as follow-ups during implementation. Fastest. Acceptable for #2322, #2323 if user chooses.

## Standards to apply in this session (non-negotiable)

1. **Adversarial stance contract** — every review prompt must force defect-hunting per `.claude/skills/coordination/cross-review-policy/SKILL.md` "Reviewer Stance" section. 6 clauses: adversarial framing, no praise, bias toward non-approval, evidence per finding, source skepticism, empty-review-is-failure.
2. **File-path based review prompts fail for Codex/Gemini** — must pass plan content INLINE in the prompt. Verified empirically this session.
3. **Plan-approval gate** — do NOT modify implementation code for these issues until the issue has `status:plan-approved` label AND `.planning/plan-approved/NNNN.md` marker exists.
4. **GitHub-issues-only** — do not create local task IDs / WRK numbers. Every unit of work = a GH issue.
5. **User feedback 2026-04-17** — "Make all the reviews adversarial in nature. Helps maximize productivity." — applies to every review surface.

## Bootstrap commands

```bash
cd /mnt/local-analysis/workspace-hub

# Verify state
git status
git log --oneline -5

# See the 5 issues
for n in 2320 2321 2322 2323 2324; do
  echo "=== #$n ==="
  gh issue view $n --repo vamseeachanta/workspace-hub --json title,labels,state --jq '{title, state, labels: [.labels[].name]}'
done

# Read plan files
ls docs/plans/2026-04-17-issue-232*.md

# Read v2 review artifacts
ls scripts/review/results/2026-04-17-plan-232*.md

# Check stance contract is live in skills
grep -A5 "Reviewer Stance\|Reviewer-stance" .claude/skills/coordination/{issue-planning-mode,cross-review-policy}/SKILL.md
```

## What the user will likely ask next

Probable prompts:
- "Revise plan #2320 against its blockers"
- "Split #2321 into smaller issues"
- "Approve #2322 and #2323 with known debt — create the plan-approved markers"
- "Run wave v3 after I've revised plan X"

## Start-of-session checklist for fresh session

- [ ] Read this handoff file first.
- [ ] Invoke `issue-planning-mode` skill if about to touch any of the 5 plans.
- [ ] Do NOT assume any plan is approval-ready; verify via `gh issue view <n> --json labels` → expect `status:plan-review`, not `status:plan-approved`.
- [ ] If user asks to revise a plan: read the current plan file AND the 3 per-provider review artifacts before rewriting.
- [ ] If user asks to re-run the adversarial wave: use INLINE plan content in prompts for Codex/Gemini, not file paths; apply the 6-clause stance contract from `plan-review-prompt-v2.md` (or re-derive from the skill files).
- [ ] If provider returns an empty review or just permission warnings — retry from `/tmp` cwd to escape the local `.gemini/agents/*.md` validation issues.

## Known quirks to carry forward

- `.gemini/agents/*.md` under repo root have a `permissionMode` validation error that aborts Gemini in the repo cwd; running `cd /tmp && gemini -p ...` works.
- Gemini occasionally hits `429 No capacity for model gemini-3.1-pro-preview` — retry with backoff works; inline-content prompts consume more tokens but succeed more reliably.
- Codex without inline content falls back to GitHub MCP lookups and returns false MAJOR ("file inaccessible"). Always inline plan content for Codex.
- Memory dir at `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/` is NOT git-tracked (surprised #2324's plan). Repo's `.claude/memory/` IS git-tracked. Two different systems.

## Do-not-do list

- Do not rerun the adversarial wave without user asking — it burns provider quota.
- Do not relabel `status:plan-review` → `status:plan-approved` — only the user approves.
- Do not create new GH issues for the same scope — 5 already exist.
- Do not modify `MEMORY.md` as a way to change user preferences — the contract is in the skills + feedback memory file.
