---
name: engineering-solver-domain-recon
description: Deep reconnaissance of an engineering solver domain (OrcaWave, OrcaFlex, CalculiX, OpenFOAM, etc.) across a multi-repo ecosystem — map infrastructure, issues, skills, data artifacts, machine constraints, and solver queue state before planning work.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [engineering, solver, orcawave, orcaflex, recon, planning, multi-machine]
    related_skills: [issue-portfolio-triage, writing-plans, multi-machine-ai-readiness-and-issue-triage, github-issues]
---

# Engineering Solver Domain Reconnaissance

Use when the user wants to plan intensive work in a specific engineering solver domain (OrcaWave, OrcaFlex, CalculiX, ANSYS, OpenFOAM, etc.) and you need a complete picture of what exists, what's broken, and what to build next.

## When to Use

- User says "let's do intensive X work" where X is a solver/tool domain
- User wants to review features and issues for a specific engineering area
- Planning a multi-session sprint on a solver-related feature set
- Need to understand what can be done locally vs on a licensed machine

## Why This Exists

Generic issue triage misses the engineering solver context:
- Solver execution is often constrained to specific licensed machines
- A git-based job queue may bridge dev machines and solver machines
- Existing skills, agents, examples, and lessons-learned files contain critical domain knowledge
- The split between "what I can code/test here" vs "what must run there" shapes every plan

## Reconnaissance Checklist (do all of these)

### 1. Issue Discovery — Multi-Strategy

Don't rely only on title grep. Use layered search:

```bash
# Layer 1: Direct title match
gh issue list --state open --limit 500 --json number,title,labels \
  --jq '.[] | select(.title | test("KEYWORD1|KEYWORD2"; "i")) | ...'

# Layer 2: Broader domain match (related physics, methods, tools)
gh issue list --state open --limit 500 --json number,title,labels \
  --jq '.[] | select(.title | test("wave load|rao|hydro|BEM|diffraction|mooring|riser"; "i")) | ...'

# Layer 3: Label-based (domain:marine, cat:engineering, etc.)
gh issue list --state open --limit 500 --json number,title,labels \
  --jq '.[] | select(.labels | map(.name) | any(test("domain:marine|domain:pipeline"))) | ...'

# Layer 4: View key issue bodies for parent/child structure
gh issue view <num> --json number,title,body,labels,comments
```

### 2. Infrastructure Inventory

Map what already exists before planning new work:

```
Solver queue:     scripts/solver/, queue/pending/, queue/completed/, queue/failed/
Skills:           find .claude/skills -path '*KEYWORD*' -type f
Agents:           find . -path '*.claude/agents/KEYWORD*' -type d
Source modules:   find . -path '*src/*KEYWORD*' -type f
Scripts:          find . -path '*scripts/*KEYWORD*' -type f
Examples:         find . -path '*examples/*KEYWORD*' -type f
Docs/domains:     find . -path '*docs/domains/KEYWORD*' -type f
Lessons learned:  find . -path '*.claude/memory/*KEYWORD*'
Knowledge:        find . -path '*knowledge/seeds/*KEYWORD*'
Config:           search_files for KEYWORD in *.yaml files
```

This inventory often reveals 50-80% of the domain is already built — the user may not know.

### 3. Queue State Analysis

If a solver queue exists:

```bash
# What completed?
cat queue/completed/*/result.yaml

# What failed? (diagnose path/input errors)
cat queue/failed/*/result.yaml

# What's the queue schema?
cat queue/job-schema.yaml

# How does submission work?
cat scripts/solver/README.md
```

Failed jobs often reveal path resolution bugs or input format mistakes that are quick wins.

### 4. Machine Constraint Mapping

Create a clear split:

**CAN do on dev-primary (or current machine):**
- Write input generators, model builders, post-processors
- Write tests (TDD — mock solver output)
- Submit jobs to solver queue
- Post-process results after queue completion
- Build comparison/benchmarking frameworks
- Build reporting modules

**MUST do on licensed machine:**
- Actual solver execution (OrcFxAPI, ANSYS, etc.)
- Result file generation (.owr, .sim, .rst, etc.)
- License-dependent API calls

Structure every plan around this split. The queue is the bridge.

### 5. Skills and Lessons Audit

Read the domain skills and memory files — they contain hard-won API knowledge:

```bash
# List domain skills
find .claude/skills -path '*DOMAIN*' -name SKILL.md

# Read lessons learned (often has API gotchas, unit conversions, shape conventions)
cat .claude/memory/DOMAIN-lessons.md
```

These files prevent re-discovering known pitfalls (e.g., OrcaWave frequencies are Hz descending, not rad/s ascending).

### 6. Bulk Module Analysis — AST via Terminal (Preferred)

**Preferred approach:** Use Python AST via `uv run python3` heredoc in terminal. This is faster and more reliable than subagents or serial `read_file` for 20+ module audits:

```bash
uv run python3 << 'PYEOF'
import ast, os, json

def analyze_module(filepath):
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)
    classes = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append({'name': node.name, 'methods': methods})
    top_funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    return {
        'lines': len(source.split('\n')),
        'classes': classes,
        'top_funcs': top_funcs,
        'has_todo': 'TODO' in source or 'FIXME' in source,
        'has_not_impl': 'NotImplementedError' in source,
        'docstring': (ast.get_docstring(tree) or '')[:200]
    }

base = 'path/to/package'
results = {}
for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in sorted(files):
        if f.endswith('.py'):
            path = os.path.join(root, f)
            results[os.path.relpath(path, base)] = analyze_module(path)
print(json.dumps(results, indent=2))
PYEOF
```

**Why AST via terminal beats alternatives:**
- `execute_code` with `read_file` fails on bulk reads — `read_file` caches/deduplicates and returns "File unchanged since last read" on subsequent calls in the same script, breaking bulk analysis.
- Subagents work but are slower to set up and can't feed results back into a single document as easily.
- AST gives clean structured output (classes, methods, line counts) without regex on line-numbered text.

**Pitfalls:**
- Don't use bare `python3` — always `uv run python3`.
- Don't use regex on `read_file` output — line number prefixes (`  42|code`) break class/function detection.
- The heredoc `<< 'PYEOF'` approach avoids quoting issues.
- For very large packages (50+ modules), split into 2 terminal calls to stay under output buffer limits.

**Alternative — Subagent parallelization:** For richer qualitative analysis (reasoning about what code does, not just structure), use `delegate_task` with up to 3 parallel subagents, each reading a subset of files. Best when you need prose assessment, not just structural extraction.

## Output Structure — Two Deliverable Types

### Type A: Infrastructure Audit (docs/assessments/)

Use when asked to audit existing code before building new:

```markdown
# [Domain] Infrastructure Audit
## Executive Summary (implemented vs skeleton vs gap — one paragraph)
## Module Inventory (table: module | lines | classes | status | description)
## Data Inventory (what hull/mesh/config files exist, what's in them)
## Test Coverage (table: test file → module under test)
## Related GH Issues (read issue bodies, document status)
## Gap Analysis: Implemented vs Skeleton vs Gap
## Recommendation: extend or rebuild?
```

Key: every module gets a verdict (Implemented / Partial / Stub / Gap). Include line counts — "413 lines with 5 classes and 10 methods" is more convincing than "looks implemented."

### Type B: Capability Roadmap (docs/roadmaps/)

Use when mapping full domain capabilities across skills, code, tests, and issues:

```markdown
# [Domain] Capability Roadmap
## Scale Summary (table: domain | skills | modules | LOC | tests | open issues)
## Per-Domain Sections:
   ### Skills Inventory (table: skill name | type | description)
   ### Code Module Map (table per sub-package with purpose and test coverage)
   ### Core Pipeline Diagram (ASCII: input → transform → output)
   ### Skill → Code → Test → Issue Mapping (cross-reference table)
## All Open GH Issues (categorized tables)
## Gap Analysis: What's NOT Yet Automated
## Cross-Reference with Existing Plans
## Priority Recommendations
```

### Legacy format (for backward compat)

```
1. INFRASTRUCTURE YOU ALREADY HAVE
2. OPEN ISSUES — RANKED BY LEVERAGE
3. MACHINE CONSTRAINTS
4. RECOMMENDED PLAN
```

## Plan Structure for Solver Work

When writing the execution plan, use waves:

- **Wave 1: Queue/infrastructure hardening** — always first. Fix broken jobs, add batch capability, add result watchers. This unblocks everything else.
- **Wave 2: Input generation + frameworks** — build parametric input generators, post-processing pipelines, comparison frameworks. All testable locally.
- **Wave 3: Job submission + integration** — submit actual solver jobs, wire up post-processing, close issues with evidence.

Each wave should produce submittable solver jobs as its deliverable.

## Post-Recon: Issue Reconciliation Phase (BEFORE creating new issues)

After the recon inventory is complete but BEFORE creating new issues or planning implementation, reconcile every open domain issue against current repo reality. This phase consistently saves more time than any other step — in practice, 30-50% of open issues are stale, partially implemented, or reference non-existent code.

### Reconciliation categories
- **IMPLEMENTED**: issue intent already exists in code/docs. Close with evidence.
- **PARTIAL**: meaningful code exists; remaining work is validation, coverage, or hardening. Re-scope the issue body.
- **REAL GAP**: still needs substantive engineering work. Keep open, assign machine.
- **INVALID / STALE**: issue body references classes, modules, or infrastructure that does not exist in the repo. Close as "not planned" with explanation.
- **DOC/TRACKING**: governance or roadmap artifact, not a code gap. Keep open only if it serves as an umbrella.

### How to reconcile
For each issue:
1. Read the issue body carefully — note specific file paths, class names, or module references it claims exist or need to be created.
2. Search the repo for those exact names: `search_files` for class names, `find` for file paths.
3. If the issue says "write tests for ExistingClass" but ExistingClass doesn't exist → INVALID.
4. If the issue says "build submit-batch.sh" but `scripts/solver/submit-batch.sh` already exists → PARTIAL or IMPLEMENTED.
5. Comment on the issue with your finding and updated status.

### Machine assignment during reconciliation
For each non-closed issue, assign:
- **Primary machine**: where the code/test work happens (usually dev-primary)
- **Required machine**: where licensed solver validation happens (e.g., licensed-win-1)
- **Dependencies**: which issues must complete first
- Apply `machine:dev-primary` or `machine:licensed-win-1` labels

### Output: reconciliation report
Write `docs/reports/<domain>-issue-reconciliation.md` with a table:
```
| Issue | Title | Status | Machine | Depends on | Evidence | Next action |
```

This report becomes the execution priority list, replacing the older roadmap's issue ordering.

## Post-Recon: Licensed-Machine Prompt Generation

When issues require a licensed machine (OrcFxAPI, ANSYS, etc.) that you cannot access from the current session, the best deliverable is a set of self-contained execution prompts.

### Prompt structure
Each prompt should include:
1. **Machine context** — hostname, workspace path, available tools, shell type
2. **Prerequisites** — git pull, pip install, version verification commands
3. **Numbered steps** with exact commands (not pseudocode)
4. **Verification after each step** — how to confirm it worked
5. **Commit and push instructions** — exact git commands including message
6. **GH issue comment** — exact gh command to post completion evidence
7. **Completion criteria** — measurable success conditions

### Key design rules
- Use `python` not `uv run` on Windows machines (no uv expected)
- Include exact file paths relative to the workspace root
- Reference specific input files that exist in the repo (verify paths during prompt generation)
- Structure prompts so each is independently executable — don't require prompt N to succeed before prompt N+1 starts (unless there's a real data dependency)
- Keep solver runs short (10-30s simulation) for fixture generation — the goal is evidence, not production analysis

### Typical prompt set after domain recon
1. Queue validation prompt — proves the solver queue infrastructure works end-to-end
2. Minimal fixture prompt — generates the smallest valid .sim or .owr file for test evidence
3. Result fixture prompt — runs a known test case and commits the output for dev-primary post-processing
4. Integration fixture prompt — runs a model that exercises a cross-tool pathway (e.g., imported RAOs)

Save prompts to `docs/plans/<machine>-<domain>-prompts.md` and commit immediately.

## Post-Recon: Follow-Up Issue Creation

After producing audit/roadmap documents AND completing reconciliation, create follow-up GH issues only for confirmed REAL GAP items. This closes the loop — the docs become actionable without inflating the backlog with duplicates of already-implemented work.

### Issue Creation Pattern

1. **Extract gaps from your audit** — each "Gap" item in the gap analysis section becomes a candidate issue.
2. **Chain dependencies** — issues should reference what they depend on and what they unblock:
   ```
   #1586 (queue) → #1588 (parametric gen) → #1591 (hull data)
                 → #1592 (handoff) → #1264/#1292 (downstream)
   ```
3. **Issue body template:**
   ```markdown
   ## Context
   Identified in docs/assessments/[audit].md (gap #N) and docs/roadmaps/[roadmap].md (section X gap #M).
   [One-sentence current state description]

   ## Deliverables
   1. [Specific file/script with path]
   2. [Tests]
   3. [Integration point]

   ## Related
   - Parent: #NNN (roadmap/audit issue)
   - Depends on: #NNN
   - Unblocks: #NNN, #NNN
   ```
4. **Priority tiering:** HIGH for critical-path blockers (e.g., solver queue), MEDIUM for leverage multipliers (e.g., hull seed data), LOW for nice-to-haves (e.g., validation runner).
5. **Comment on tracking issue** — post a key findings summary on the parent/tracking issue with a link to the deliverable doc.

### Typical Issue Set After Domain Recon

For a solver domain recon, expect 4-8 follow-up issues:
- 1-2 HIGH: Infrastructure hardening (queue, pipeline glue)
- 2-3 MEDIUM: Data seeding, automation bridges, handoff automation
- 1-2 LOW: Validation, compliance tooling, nice-to-have automation

## Type C: Research & Document Intelligence Gap Analysis (docs/reports/)

Use when assessing knowledge coverage for a specific engineering domain — what standards/papers/tools exist vs what's needed.

### Data Sources to Cross-Reference

For workspace-hub document intelligence audits, cross-reference these 6 registries:

1. **standards-transfer-ledger.yaml** — Which standards are done/gap/reference/wrk_captured for this domain?
2. **enhancement-plan.yaml** — How many documents classified in this domain? (Note: items[] capped at 500 per domain; use the `count` field for true totals)
3. **Conference archives** (`/mnt/ace/docs/conferences/`) — OMAE, OTC, ISOPE, SNAME file counts. Are any indexed?
4. **oss-engineering-catalog.yaml** — Which OSS tools are cataloged? Which are cloned to /mnt/ace? Which are pip-installed?
5. **Research literature** (`/mnt/ace-data/digitalmodel/docs/domains/`) — What PDFs exist per sub-domain?
6. **online-resources catalog** (`.planning/archive/online-resources/catalog.yaml`) — Known web resources not yet downloaded

### YAML Registry Data Extraction Pattern

For large YAML registries (7K+ lines), use inline python via `terminal()` — not `execute_code` with yaml.safe_load on huge files (can timeout):

```bash
# Domain filter + status breakdown from standards-transfer-ledger
python3 -c "
import yaml
from collections import Counter
with open('data/document-index/standards-transfer-ledger.yaml') as f:
    data = yaml.safe_load(f)
domain_stds = [s for s in data['standards'] if s.get('domain') == 'marine']
statuses = Counter(s.get('status','unknown') for s in domain_stds)
print(f'Total: {len(domain_stds)}')
for status, count in statuses.most_common():
    print(f'  {status}: {count}')
"
```

For enhancement-plan.yaml (34K lines, 1.7MB), don't try to parse all items — read the header counts:

```bash
# Domain breakdown from enhancement plan  
python3 -c "
import yaml
with open('data/document-index/enhancement-plan.yaml') as f:
    data = yaml.safe_load(f)
for domain, info in data.get('by_domain', {}).items():
    if isinstance(info, dict):
        print(f'{domain}: count={info.get(\"count\",\"?\")}, items_listed={len(info.get(\"items\",[]))}')
"
```

### Report Structure

```markdown
# [Domain] Research Gap Analysis
## 1. Standards Tracked (done/gap/reference/wrk breakdown + table of each)
## 2. Enhancement Plan Coverage (domain doc count, items listed, status)
## 3. Conference Papers (file counts per conference, indexing status)
## 4. OSS Tools (cataloged vs cloned vs installed — table with action needed)
## 5. Research Literature on Disk (PDFs by sub-domain, key texts identified)
## 6. Web Resources to Prioritize (from online-resources catalog)
## 7. Top 10 Recommendations (ranked by domain impact, with effort estimates)
## 8. Summary Scorecard (current vs target for each dimension)
```

### Follow-Up Issues for Research Gaps

Typical issue set after a research gap analysis (distinct from solver recon):
- 1-2 HIGH: Batch-process reference standards, install critical OSS tools
- 2-3 MEDIUM: Add new sources to indexing pipeline, create sub-domain taxonomy, acquire reference texts
- 1-2 LOW: Download web resources, clone additional OSS repos

## Post-Recon: Parallel Execution of Dev-Primary Issues via Agent Teams

After reconciliation identifies dev-primary executable issues, use `delegate_task` with up to 3 parallel subagents to implement them simultaneously. This is the highest-leverage pattern when the recon phase reveals that multiple issues are PARTIAL or coverage-gap work rather than greenfield builds.

### When to use parallel agent teams
- 2+ dev-primary issues are independent (no shared files)
- Each issue is well-scoped: coverage uplift, bridge module, test writing, doc generation
- You have the recon findings to give each subagent full context without re-discovery

### Effective delegation pattern
Each subagent task should include:
1. **Exact file paths** to read (source modules, existing tests, schemas)
2. **What to produce** (new test files, new module, exact output paths)
3. **Constraints** (use `uv run`, mock OrcFxAPI, no loguru imports, etc.)
4. **Return format** (complete file contents + paths, not diffs)

Example from practice — 3 parallel teams:
- Team 1: Write 166 OrcaWave reporting section tests (read 10 source files, produce 11 test files)
- Team 2: Implement parametric spec bridge module (read 6 source files, produce 1 module + 1 test file)
- Team 3: Assess feasibility of a third issue (read-only analysis, return structured report)

### Post-delegation verification
After subagents return, always:
1. Run the tests locally: `uv run pytest <new_test_files> -q --tb=short`
2. Verify all pass before committing
3. Commit code changes to the correct repo (watch for nested gitignored repos like `digitalmodel/`)
4. Comment on GH issues with evidence (test counts, pass/fail, commit hash)

### Pitfall: nested repos
`digitalmodel/` is gitignored inside `workspace-hub`. Subagents write files correctly but `git add` from workspace-hub root silently ignores them. Always `cd` into the nested repo and commit from there.

## Post-Recon: No-Hermes Licensed Machine Execution

When the licensed machine has agent CLIs (Claude Code, Codex, Gemini) but NOT Hermes:

### Key differences from Hermes-based execution
- Use `python` not `uv run` (Windows machines typically lack uv)
- No persistent memory or skills — pass full context in each prompt
- No subagents or delegate_task — sequential execution only
- No background process manager — all foreground
- The prompts file in the repo IS the skill equivalent

### Recommended 3-terminal pattern on licensed machine
- Terminal 1 (Claude Code): run prompts sequentially — this is the executor
- Terminal 2 (Codex): verification after each prompt completes — read-only
- Terminal 3 (Gemini): adversarial review after all prompts complete — read-only

Only Terminal 1 commits. Terminals 2 and 3 only `git pull` and read.

### Save an execution guide alongside prompts
Commit both files:
- `docs/plans/<machine>-<domain>-prompts.md` — the step-by-step prompts
- `docs/plans/<machine>-execution-guide.md` — which CLI to use, terminal layout, git contention avoidance, key differences from Hermes

## Pitfalls

- Don't assume you can run solvers locally — always check for license constraints
- Don't skip the infrastructure inventory — the user often has more built than they remember
- Don't plan only the solver execution — 70% of the work is input generation, post-processing, and comparison, all of which can be done locally with TDD
- Don't treat failed queue jobs as low priority — they're usually quick path-fix wins
- Don't forget submodules (digitalmodel/ etc.) — solver code often lives there, not in the hub repo
- For nested repos like `digitalmodel/`, check BOTH the nested repo and the workspace-hub root for roadmap/report/plan docs. In practice, the live domain roadmap may be in `workspace-hub/docs/...` while the code lives in `digitalmodel/src/...`.
- Treat README and local domain-index docs as potentially stale until verified against the actual tree. Example failure mode: README references `specs/module-registry.yaml` or old paths that no longer exist; `docs/domains/README.md` may describe a superseded layout.
- Reconcile issue statements against current code before accepting them as gaps. Some GH issues will still say queue/reporting utilities are missing even after `scripts/solver/submit-batch.sh`, `watch-results.sh`, or `post-process-hook.py` already exist.
- Read the lessons-learned file before writing any OrcFxAPI code — unit/shape conventions are non-obvious
- Don't use `read_file` for bulk module analysis — it caches/deduplicates, and the line-number prefixes break regex parsing. Use `uv run python3` with AST instead.
- When gathering data for audit/roadmap docs, maximize parallel calls — issue searches, file listings, module analysis can all happen concurrently
- Always commit+push audit docs immediately after writing them (before starting next task) to avoid git contention in multi-terminal setups
- **GH issue JSON truncation:** When `gh issue list --json` returns 200+ issues, the JSON output can exceed terminal buffer limits and contain control characters that break both `json.loads` and `json_parse`. Workaround: use plain `gh issue list` (tabular output) piped through `grep -iE \"(keyword1|keyword2)\"` instead. For individual issue details, use `gh issue view <num> --json` which is always small enough.
- **Subagent budget:** For hull_library-scale audits (25+ files), a single subagent with max_iterations=40 can read all files. For the full roadmap (3 parallel audits), budget ~3 minutes per subagent. Return structured text, not JSON — it's more resilient to large outputs.
- **GH issue creation with backticks in body:** When using `gh issue create --body` with markdown containing backticks or code blocks, the shell interprets them as command substitution. Use `execute_code` with `terminal()` calls for complex issue bodies — pass the body as a Python string to avoid shell escaping issues. Alternatively, write the body to a temp file and use `gh issue create --body-file`.
- **Enriching stub issues:** Auto-created issues (e.g., from backfill scripts) often have minimal bodies like "Auto-created by backfill-github-refs.sh". After a recon audit, comment on these with structured findings (current state, what's missing, recommended implementation) to make them actionable.
