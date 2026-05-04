---
name: skill-chain-context-optimization
version: 1.0.0
category: coordination
description: Refactor large or frequently-run skills into context-efficient chains using isolated execution, file-backed handoffs, minimal summaries, and runtime-aware command substitution.
tags: [skills, context, optimization, chaining, subagents, token-efficiency]
---

# Skill Chain Context Optimization

Use this when reviewing or improving a skill that runs multiple steps, loops over many items, calls tools repeatedly, or returns large intermediate data. The goal is to keep the main agent context limited to decisions, summaries, and final artifacts rather than raw tool outputs.

## Source Pattern

This skill captures a 2026 skill-chaining pattern from the reviewed YouTube video `JdqJ2ekWt8M`:

1. Monolithic skill chaining bloats the working window because each step leaves bulky scrape/search/tool material in the active run.
2. The scalable pattern is: isolate execution, write minimal per-step artifacts to files, and feed only the next step's required fields forward.
3. The cited benchmark claimed roughly **51K tokens** added for the monolithic version versus **5-8K tokens** for the forked/file-backed version, about **85% lower context burn**.

Treat those numbers as directional evidence; verify against our own session/provider logs before making broad claims.

## When to Apply

Apply this pattern to skills that meet at least one of these conditions:

- `SKILL.md` is large (rough guide: >400 lines or >20 KB).
- The workflow loops over multiple records, issues, repos, documents, leads, files, or providers.
- The workflow has 3+ logically distinct stages where later stages only need a subset of earlier output.
- Tool outputs are large, repetitive, or mostly useful only for extraction.
- The skill is run frequently enough that token/context cost matters.

Do **not** apply this pattern mechanically to small one-shot skills. Extra orchestration can make simple skills harder to use.

## Three-Layer Refactor Pattern

### 1. Isolate heavy work from the orchestrator

Keep the orchestrator responsible for:

- loading the skill,
- deciding the stage order,
- checking gates,
- receiving compact status lines,
- producing the final user-facing result.

Move heavy tool use into isolated execution:

- Hermes: prefer `delegate_task` for reasoning-heavy isolated work, or `execute_code`/scripts for deterministic loops.
- Codex: use runtime-supported skill/agent forking if available in that environment.
- Codex/Gemini: use separate CLI invocations or file-based prompts when isolation is needed.

Subworkers should return compact status, not raw logs. For detailed evidence, they should write an artifact path and report that path.

### 2. Use file-backed handoffs between stages

Create a run-scoped artifact directory, for example:

```text
.Codex/tmp/skill-runs/<skill-name>/<YYYYMMDD-HHMMSS>-<short-id>/
  00-input.json
  10-profile.json
  20-company.md
  30-signals.json
  40-score.json
  90-final-summary.md
  errors.jsonl
```

Rules:

- Each stage writes only the fields needed by downstream stages.
- Prefer JSON for structured state and Markdown for human review artifacts.
- Include provenance fields: source path/URL, timestamp, command/script used, and confidence where applicable.
- Redact secrets and avoid writing sensitive raw payloads unless the skill explicitly requires it.
- Add cleanup guidance for high-volume temp directories; do not let `.Codex/tmp` grow indefinitely.

### 3. Feed forward only required context

For each stage, define an explicit input contract and output contract:

```markdown
## Stage: Score Candidate

Inputs:
- `10-profile.json`: `name`, `role`, `company`, `high_signal_facts[]`
- `20-company.md`: 5-10 line company brief
- `references/scoring-rubric.md`: static rubric

Output:
- `40-score.json`: `score`, `rationale[]`, `disqualifiers[]`, `next_action`

Return to orchestrator:
- one line: `score=<n>; next_action=<...>; artifact=40-score.json`
```

If the runtime supports parse-time command substitution such as ``!`cat artifact.json` ``, use it only for small, already-distilled artifacts. Otherwise use scripts or tool calls to read the artifact and pass the minimal content explicitly. Never substitute large raw scrape/search outputs.

## Refactor Procedure

1. **Inventory the current skill**
   - Count lines/chars and identify large sections.
   - Mark stage boundaries.
   - Identify repeated tool calls and raw-output handoffs.
   - Identify static references that belong in `references/`, templates, or scripts instead of inline prose.

2. **Split into orchestrator + stages**
   - Keep `SKILL.md` short enough to explain routing and gates.
   - Move reusable static examples into `references/` or `templates/`.
   - Move deterministic transformations into `scripts/`.
   - For complex reasoning stages, create sub-skills or explicit worker prompts.

3. **Define artifact contracts**
   - Write input/output schemas for every stage.
   - Include success and failure shapes.
   - Require workers to write detailed evidence to files and return only compact status.

4. **Add error propagation**
   - Each stage must report `status: ok|blocked|failed`.
   - Failures must include `reason`, `repro_or_source`, `artifact_path`, and `recommended_next_action`.
   - The orchestrator must stop or degrade explicitly rather than guessing.

5. **Measure before/after**
   - Capture approximate context/token burn before refactor where available.
   - Compare main-conversation output volume, artifact size, runtime, and user-visible quality.
   - Keep measured claims in reports; avoid unverified token savings claims in skill front matter.

## Runtime Compatibility Notes

- The YouTube pattern references Codex features such as skill forking and command substitution. Do not assume identical syntax works in Hermes, Codex, or Gemini.
- In Hermes, `delegate_task` already provides isolated child contexts, but only the final summary returns. If detailed work matters, instruct the subagent to write a named artifact in the repo/workdir and return the path.
- For deterministic extraction, prefer `execute_code` or checked-in scripts over LLM reasoning.
- For unattended cron jobs, prompts must be self-contained and cannot ask clarifying questions; use file contracts and explicit failure artifacts.

## Candidate Audit Heuristic

A quick filesystem-only first pass:

```bash
python - <<'PY'
from pathlib import Path
root = Path('.Codex/skills')
rows = []
for p in root.rglob('SKILL.md'):
    if '_archive' in p.parts:
        continue
    text = p.read_text(errors='ignore')
    lines = text.count('\n') + 1
    chars = len(text)
    signals = sum(s in text.lower() for s in ['loop', 'batch', 'parallel', 'search', 'scrape', 'research', 'review'])
    if lines > 400 or chars > 20000 or signals >= 3:
        rows.append((lines, chars, signals, p))
for lines, chars, signals, p in sorted(rows, reverse=True)[:30]:
    print(f'{lines:4d} {chars:6d} signals={signals} {p}')
PY
```

Use this as a triage list only. A large reference-heavy skill may be fine if it is rarely loaded or already file-backed.

## Validation Checklist

Before landing a context-optimization change:

- [ ] Orchestrator returns compact summaries and artifact paths only.
- [ ] Each stage has explicit input/output contracts.
- [ ] Raw tool outputs are not copied into downstream prompts unless required.
- [ ] Detailed evidence is written to files under a run-scoped artifact directory.
- [ ] Failure artifacts are machine-readable enough for reruns.
- [ ] Cleanup/retention guidance exists for temp artifacts.
- [ ] Runtime-specific features are labeled by provider/tool; no unsupported syntax is presented as universal.
- [ ] A before/after metric or at least a qualitative context-bloat rationale is recorded.

## Good Targets in workspace-hub

From a quick active skill inventory on 2026-04-26, no active skills used an explicit `context_fork`/`context fork` marker, while many large skills already mention temp/handoff artifacts. Prioritize optimization reviews for large, frequently loaded orchestration skills such as GitHub planning/execution, provider/session audits, research pipelines, and overnight batch workflows.
