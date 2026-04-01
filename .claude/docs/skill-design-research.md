# Skill Design Research — Anthropic Official Guidance + Installed Plugin Patterns
*Issue: #93 | Created: 2026-04-01 | Umbrella: #1547*

---

## 1. Sources Reviewed

### Anthropic Official
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — canonical authoring guide
- [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — specification and structure
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — engineering blog post
- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — 32-page PDF playbook (Jan 2026)
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — agent architecture patterns
- [Introduction to Agent Skills course](https://anthropic.skilljar.com/introduction-to-agent-skills) — Anthropic Academy (free)
- [Claude Certified Architect, Foundations](https://anthropic.skilljar.com/) — launched 2026-03-12, 60-question proctored exam
- [agentskills.io](https://agentskills.io/specification) — open standard specification

### Installed Plugins Analyzed
- **Superpowers** (obra/superpowers): `writing-skills`, `verification-before-completion`, `systematic-debugging`, `executing-plans`, `brainstorming`
- **GSD** (workspace-hub native): `gsd-execute-phase`, `gsd-plan-phase`, `gsd-discuss-phase`

### Existing Workspace Docs
- `.claude/docs/plugins-vs-skills.md` — plugin vs skill trade-off (WRK-225)
- `.claude/docs/skill-metadata-schema.md` — frontmatter schema (#1481)

---

## 2. Key Patterns from Anthropic Official Guidance

### 2.1 Progressive Disclosure (Core Design Principle)

Anthropic's single most emphasized pattern. Skills load in layers:

1. **Description only** at startup — injected into system prompt (~2% of context budget)
2. **SKILL.md body** loaded on invocation — the "table of contents"
3. **Reference files** loaded on demand — heavy docs, examples, scripts

Implication: SKILL.md should be a concise router, not an encyclopedia. Keep body under 500 lines. Split into reference files when approaching that limit.

### 2.2 Description Is the Discovery Mechanism

The description field is the single most important line in any skill. It determines whether Claude selects the skill from 100+ candidates.

Rules from Anthropic:
- Write in **third person** (it is injected into the system prompt)
- Include **what it does AND when to use it**
- Be specific: include trigger terms, file types, error messages
- Max 1024 characters (but aim for under 500)
- Avoid vague descriptions ("helps with documents")

### 2.3 Degrees of Freedom

Match instruction specificity to task fragility:
- **High freedom** (text guidance): code reviews, analysis — multiple valid approaches
- **Medium freedom** (pseudocode/templates): preferred pattern exists but variation OK
- **Low freedom** (exact scripts): database migrations, deployments — one safe path

### 2.4 Conciseness as Context Stewardship

"The context window is a public good." Every token in a skill competes with conversation history, other skills, and the user's actual request.

Default assumption: Claude is already smart. Only add context Claude does not already have. Challenge each paragraph: "Does this justify its token cost?"

### 2.5 Scripts Execute, Not Load

When a SKILL.md references executable scripts, Claude runs them via bash and receives only the output. The script source code never enters context. This is a free way to add capability without burning tokens.

### 2.6 Test with All Target Models

Skills act as additions to models. What works for Opus may need more detail for Haiku. If a skill will be used across model tiers, test on each.

### 2.7 Open Standard (agentskills.io)

Agent Skills is published as an open standard. Skills should be portable across platforms. Two required frontmatter fields: `name` and `description`.

---

## 3. Patterns from Well-Designed Installed Skills

### 3.1 Superpowers: Writing-Skills

**Pattern: TDD for Documentation**

The writing-skills skill treats skill creation as test-driven development:
- RED: Run a pressure scenario without the skill, document agent failures
- GREEN: Write minimal skill addressing those specific failures
- REFACTOR: Find new rationalizations, add counters, re-test

This is the highest-quality skill authoring methodology observed. It produces skills that are battle-tested before deployment.

**Pattern: Claude Search Optimization (CSO)**

Superpowers coined "CSO" — optimizing skills for Claude's internal search:
- Description = triggering conditions only, never workflow summary
- If description summarizes workflow, Claude follows the description instead of reading the full skill (verified by testing)
- Include error messages, symptoms, and synonyms as keywords
- Use gerund naming (`creating-skills` not `skill-creation`)

**Pattern: Rationalization Tables**

For discipline-enforcing skills, include a table of excuses and rebuttals. Agents are sophisticated rationalizers under pressure. Explicit counters close loopholes.

**Pattern: Token Budget Awareness**

Concrete targets: getting-started skills < 150 words, frequently-loaded < 200 words, others < 500 words. Use cross-references instead of repeating content. Move flag documentation to `--help` output.

### 3.2 Superpowers: Verification-Before-Completion

**Pattern: Iron Law + Gate Function**

A single non-negotiable rule ("No completion claims without fresh verification evidence") enforced through a gate function checklist: IDENTIFY what command proves the claim, RUN it fresh, READ full output, VERIFY, THEN claim.

**Pattern: Red Flags List**

Concrete trigger phrases that signal rule violation: "should", "probably", "seems to", expressing satisfaction before running verification. Makes self-correction easy.

### 3.3 Superpowers: Systematic-Debugging

**Pattern: Phased Progression with Gates**

Four phases (Root Cause, Pattern Analysis, Hypothesis, Implementation), each gated — must complete current phase before proceeding. This prevents the common failure of jumping to fixes.

**Pattern: Escalation Threshold**

After 3+ failed fixes, the skill forces an architecture-level discussion instead of more patches. This breaks the "one more fix" loop.

**Pattern: Cross-Skill References**

Uses `REQUIRED BACKGROUND:` and `REQUIRED SUB-SKILL:` markers to link to related skills without force-loading them via `@` syntax (which would burn context).

### 3.4 GSD: Execute-Phase

**Pattern: Codex Adapter Layer**

The `<codex_skill_adapter>` block translates Claude Code primitives (AskUserQuestion, Task) to Codex equivalents (request_user_input, spawn_agent). This enables cross-provider skill reuse.

**Pattern: Flag Handling as Documentation**

Flags are documented but explicitly inactive unless their literal token appears in arguments. This prevents "implied active" behavior drift.

**Pattern: Context Budget Allocation**

Explicit budget: ~15% orchestrator, 100% fresh per subagent. Prevents orchestrator bloat in multi-agent workflows.

---

## 4. Concrete Recommendations for Workspace-Hub Skill Ecosystem

### 4.1 Description Quality Audit (High Impact, Low Effort)

Many workspace-hub skills have descriptions that are too terse or summarize workflow instead of triggering conditions. Audit the 479 skills for:
- Descriptions that start with "Use when..." and include specific triggers
- Third-person voice consistently
- No workflow summaries in descriptions (CSO anti-pattern)
- Keyword coverage for error messages, symptoms, tool names

### 4.2 Token Budget Enforcement

Establish word-count targets per skill tier:
- **Always-loaded skills** (getting-started, workspace context): < 150 words
- **Frequently-invoked skills** (daily workflow): < 300 words
- **On-demand skills** (specialized domains): < 500 words in SKILL.md, heavy reference in separate files

Script the check: `wc -w skills/*/SKILL.md | sort -n` as a periodic health metric.

### 4.3 Progressive Disclosure Adoption

For skills currently over 500 lines, split into:
- SKILL.md: overview + quick start + navigation links
- Reference files: API docs, detailed examples, templates
- Scripts: executable utilities (free — output only, no context cost)

### 4.4 Cross-Skill Reference Conventions

Standardize on the Superpowers pattern:
- `**REQUIRED BACKGROUND:** superpowers:skill-name` for prerequisites
- `**REQUIRED SUB-SKILL:** gsd-skill-name` for dependencies
- Never use `@` links to force-load other skills (burns 200k+ context)
- `related_skills` in frontmatter for soft associations

### 4.5 Degrees of Freedom Tagging

For each skill, decide and document the freedom level:
- High: guidance-only skills (code review, brainstorming)
- Medium: template-based skills (report generation, data processing)
- Low: exact-script skills (deployments, migrations, queue operations)

This helps Claude calibrate how strictly to follow instructions.

### 4.6 Rationalization Defense for Discipline Skills

Any skill that enforces a constraint (verification, TDD, review gates) should include:
- An Iron Law (one non-negotiable sentence)
- A rationalization table (excuse / reality pairs)
- A red flags list (trigger phrases that signal violation)
- A "no exceptions" block closing specific loopholes

### 4.7 Codex/Gemini Adapter Pattern

For skills that use Claude-specific primitives (Task, AskUserQuestion), include a `<codex_skill_adapter>` block mapping to Codex equivalents. This preserves cross-provider portability without duplicating the skill.

---

## 5. Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| **Workflow summary in description** | Claude follows description as shortcut, skips skill body | Description = triggering conditions only |
| **Monolithic SKILL.md (500+ lines)** | Burns context budget, Claude may skip sections | Split into SKILL.md overview + reference files |
| **Force-loading via `@` links** | Loads 200k+ tokens before needed | Use named references: "See skill-name" |
| **Multi-language examples** | Diluted quality, maintenance burden | One excellent example in most relevant language |
| **Narrative storytelling** | "In session 2025-10-03 we found..." is not reusable | Extract the pattern, discard the story |
| **Generic labels** | helper1, step3, pattern4 have no semantic meaning | Use descriptive names always |
| **First-person descriptions** | "I can help you..." breaks system prompt injection | Third person: "Processes X when Y" |
| **Skipping testing** | Untested skills have issues, always | RED-GREEN-REFACTOR, no exceptions |
| **Over-explaining what Claude already knows** | Wastes tokens on common knowledge | Only add context Claude lacks |
| **Flowcharts for linear sequences** | Adds visual noise without decision value | Use numbered lists for linear steps |
| **Implied-active flags** | Flags documented but treated as active by default | Flags active only when literal token present |

---

## 6. Claude Certified Architect Program — Relevance

The Claude Certified Architect (CCA) Foundations exam, launched 2026-03-12, tests five competency domains across 60 questions. While primarily aimed at production API/application architects, the exam content overlaps with skill design in these areas:

- **Prompt engineering**: Skills are specialized prompts; the same principles of clarity, structure, and testing apply
- **Agent architecture**: Understanding orchestrator-worker patterns, progressive disclosure, and context management
- **MCP integration**: Skills that bundle MCP server references benefit from understanding the protocol

The Anthropic Academy courses (13 free, self-paced) are the best preparation path and directly applicable to skill authoring quality.

---

## 7. Summary

The three highest-leverage improvements for the workspace-hub skill ecosystem:

1. **Description quality**: Audit all 479 skill descriptions for CSO compliance (triggering conditions only, third-person, keyword-rich, no workflow summaries)
2. **Progressive disclosure**: Split oversized skills into SKILL.md overview + reference files; enforce 500-line limit on SKILL.md body
3. **Discipline skill hardening**: Add rationalization tables, red flags lists, and iron laws to any skill that enforces constraints

---

## 8. Cross-Skill Reference Convention

Standard patterns for referencing other skills:
- **Frontmatter**: `related_skills: [skill-a, skill-b]` for soft associations
- **Prerequisites**: `**REQUIRED BACKGROUND:** skill-name` in body
- **Dependencies**: `**REQUIRED SUB-SKILL:** skill-name` in body
- **Never**: `@skill-name` force-loading (burns context)
