# Overview: Engineering Wiki

> How the workspace-hub ecosystem is built and operated.

This wiki captures the **engineering methodology** behind the ACE Engineer workspace-hub — the patterns, tools, agents, and workflows that make 691+ skills, multiple AI agents, and multi-machine coordination work as a compound system.

## Scope

This wiki covers **how we engineer**, not **what we engineer**:

| This Wiki (Engineering) | Domain Wikis |
|------------------------|--------------|
| Compound engineering methodology | Marine engineering topics |
| Agent workflows and delegation | Maritime law cases |
| Testing and compliance enforcement | Naval architecture concepts |
| Tools: GSD, solver queue, skills system | OrcaFlex, AQWA, VIV analysis |

## Key Themes

### 1. Compound Engineering
Engineering work produces tools, tools produce better work. The [five lessons](concepts/compound-engineering.md) define the methodology.

### 2. Multi-Agent Coordination
Four agents ([Claude Code](entities/claude-code.md), [Codex](entities/codex-cli.md), [Gemini](entities/gemini-cli.md), [Hermes](entities/hermes.md)) share a [common skills system](entities/skills-system.md) and follow [parity rules](concepts/multi-agent-parity.md).

### 3. Enforcement Over Instruction
[Technical gates](concepts/enforcement-over-instruction.md) enforce what prose instructions cannot. The [compliance dashboard](entities/compliance-dashboard.md) monitors agent behavior.

### 4. Git as Infrastructure
Git serves as transport for the [solver queue](entities/solver-queue.md), message bus for [agent coordination](concepts/orchestrator-worker-separation.md), and persistence layer for [shared knowledge](entities/skills-system.md).

### 5. Domain Engineering Knowledge
Career expertise spanning pipeline integrity, VIV, FEA, CFD, cathodic protection, and energy economics is captured in [concept pages](index.md) alongside standards references ([DNV-RP-F101](standards/dnv-rp-f101.md), [API 579](standards/api-579-ffs.md), [DNV-RP-C203](standards/dnv-rp-c203.md), [DNV-RP-C205](standards/dnv-rp-c205.md)).

### 6. Software Engineering Patterns
Robust patterns for [shell scripting](concepts/shell-scripting-patterns.md), [Python type safety](concepts/python-type-safety.md), and [JSONL knowledge stores](concepts/jsonl-knowledge-stores.md) encode cross-cutting best practices.

## Statistics

| Category | Count |
|----------|-------|
| Concept pages | 25 |
| Entity pages | 13 |
| Source pages | 8 |
| Standards pages | 4 |
| Workflow pages | 2 |
| **Total content pages** | **52** |

## Source Classes

This wiki ingests from 5+ source classes documented in [SOURCE_INVENTORY.md](../SOURCE_INVENTORY.md):
1. Methodology docs (`docs/methodology/`) — 6 concept pages
2. Module documentation (`docs/modules/`) — entity + concept pages
3. Session learnings (`.claude/memory/`, solver lessons) — entity + workflow pages
4. Architecture docs (`docs/architecture/`) — entity pages
5. Knowledge seeds (`knowledge/seeds/career-learnings.yaml`) — 7 domain concept pages
6. Dark intelligence (`knowledge/dark-intelligence/`) — 2 calculation methodology pages

## Navigation

- **[Full Index](index.md)** — all pages with summaries
- **[Ingest Log](log.md)** — chronological operation history
- **[Source Inventory](../SOURCE_INVENTORY.md)** — what feeds this wiki
