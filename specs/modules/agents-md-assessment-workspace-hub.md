# Assessment: AGENTS.md Concepts for workspace-hub

## Source

Vercel blog: "agents.md outperforms skills in our agent evals"

## Key Article Findings

| Configuration | Pass Rate |
|---|---|
| Baseline (no docs) | 53% |
| Skills (default) | 53% |
| Skills + explicit instructions | 79% |
| **AGENTS.md (passive context)** | **100%** |

**Core insight**: Passive, always-available context (AGENTS.md) dramatically outperformed active retrieval (Skills). In 56% of eval cases, the skill was never invoked even though it was available. The agent simply didn't decide to use it.

**Why it works**: No decision point for agents to invoke resources. Consistent availability on every turn. Eliminates ordering/sequencing issues.

---

## Assessment: What Applies to workspace-hub

### 1. ALREADY STRONG - Passive Context via CLAUDE.md Hierarchy

workspace-hub already uses a tiered CLAUDE.md system (global 2KB + workspace 4KB + project 8KB + local 2KB = 16KB budget). This is architecturally aligned with the AGENTS.md pattern -- persistent context available on every turn.

**Verdict**: No structural change needed. The hierarchy is sound.

### 2. HIGH VALUE - Compressed Documentation Index in CLAUDE.md

**The article's most actionable technique.** Vercel compressed 40KB of Next.js docs into an 8KB pipe-delimited index inside AGENTS.md, pointing to retrievable files in `.next-docs/`.

**Current gap**: workspace-hub has `.claude/docs/` (8 reference docs), `.claude/rules/` (6 files), and `agent-library/` (87 agents) but CLAUDE.md does NOT contain a compressed index of these resources. Agents must know to look for them or be told.

**Recommendation**: Add a compressed index section to the root CLAUDE.md that maps available docs, rules, and key agents to their paths. Example:

```
## Resource Index
docs/|orchestrator-pattern.md:delegation,context-isolation|agent-composition.md:workflows,handoffs|command-registry.md:all-commands|mcp-tools.md:tool-integration
rules/|security.md:secrets,injection,auth|testing.md:tdd,coverage|coding-style.md:naming,size-limits|patterns.md:DI,factory,observer,SOLID|git-workflow.md:branches,commits,PRs
agents/core/|coder:implementation|tester:TDD-cycle|reviewer:code-review|planner:architecture
```

This gives the agent a map without consuming full context budget.

### 3. HIGH VALUE - "Retrieval-Led Reasoning" Directive

The article's key instruction: "Prefer retrieval-led reasoning over pre-training-led reasoning."

**Current gap**: No equivalent directive exists in workspace-hub CLAUDE.md files. Agents may rely on stale training data for domain-specific engineering tasks (OrcaFlex, hydrodynamics, mooring design) where project-specific docs should take precedence.

**Recommendation**: Add to root CLAUDE.md:
```
IMPORTANT: Prefer retrieval-led reasoning over training-led reasoning.
Always consult .claude/docs/, .claude/rules/, and project CLAUDE.md
before relying on general knowledge for domain-specific tasks.
```

### 4. MEDIUM VALUE - Evaluate Skill Invocation Rates

The article found skills went unused 56% of the time. workspace-hub has 77+ skills.

**Risk**: Many domain-specific skills (orcaflex-*, hydrodynamics, mooring-design) may never be invoked by agents who don't know they exist or don't decide to load them.

**Recommendation**:
- Audit which skills are actually invoked in practice
- For the most critical/frequently-needed skills, extract their core knowledge into passive context (CLAUDE.md or a compressed index)
- Keep skills for vertical, user-triggered workflows (the article confirms skills work well for explicit actions like `/create-spec`, `/execute-tasks`)

### 5. MEDIUM VALUE - Submodule-Level AGENTS.md / Documentation Indexes

Each of the 25 submodules has its own CLAUDE.md. The compression technique could be applied at the submodule level to index project-specific documentation.

**Recommendation**: For submodules with significant domain docs (e.g., digitalmodel, assetutilities, energy), add compressed doc indexes to their CLAUDE.md files pointing to local reference material.

### 6. LOW VALUE (Already Handled) - Context Budget Compression

The article's 80% compression (40KB to 8KB) aligns with workspace-hub's existing 16KB total context budget. The constraint is already enforced.

**Verdict**: No change needed. Budget discipline is already in place.

---

## Summary: Recommended Changes

| Priority | Change | Effort | Impact |
|----------|--------|--------|--------|
| **P0** | Add compressed resource index to root CLAUDE.md | Small | Agents discover docs/rules/agents without active search |
| **P0** | Add retrieval-led reasoning directive | Trivial | Prevents stale training data use for domain tasks |
| **P1** | Audit skill invocation rates | Medium | Identify unused skills, convert critical ones to passive context |
| **P1** | Add compressed doc indexes to key submodule CLAUDE.md files | Medium | Submodule agents find project docs faster |
| **P2** | Evaluate converting top engineering skills to passive doc snippets | Medium | Domain knowledge always available without skill invocation |

## Key Takeaway

workspace-hub's architecture is already well-aligned with the AGENTS.md philosophy through its CLAUDE.md hierarchy. The main gap is **discoverability** -- agents don't have a compressed map of available resources. Adding a resource index and retrieval-led reasoning directive are low-effort, high-impact improvements that directly apply the article's findings.

The article also validates the existing approach of keeping skills for user-triggered workflows (`/create-spec`, `/execute-tasks`, etc.) while making foundational knowledge passively available.
