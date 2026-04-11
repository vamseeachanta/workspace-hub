# Weekly Ecosystem Execution and Intelligence Review

Status: draft
Parent issue: #2089

## Purpose

This weekly review exists to keep the workspace-hub repo ecosystem:
- executable across the machines where work actually happens
- aligned across Hermes and AI provider settings
- current in its knowledge systems
- accessible at the point of use for both humans and agents

This is not a static config audit. It is an operational readiness review covering settings, machines, execution paths, intelligence freshness, and intelligence accessibility.

## Review Outcomes

Each weekly run should answer five questions:
1. Can the primary machines still execute the expected classes of work?
2. Are Hermes and provider settings still aligned with the intended routing, quota, and cost strategy?
3. Are the machine-local prerequisites, auth states, and repo-linked skills still usable?
4. Are llm-wikis, resource intelligence, and document intelligence being kept current?
5. Is the accumulated intelligence actually discoverable and accessible in the contexts where work is performed?

## Scope

### 1. Hermes and Provider Settings
- Hermes config defaults and overrides
- provider/model routing choices
- fallback behavior
- auth mode and credential handling
- skill path and `external_dirs` parity
- workflow-enforcement settings affecting planning, TDD, and review gates

### 2. Multi-Machine Execution Readiness
- machine inventory and intended role
- key paths, shells, and environment assumptions
- auth state and credential availability
- required CLIs and tool availability
- repo access and working-copy assumptions
- machine-specific blockers, drift, or brittle dependencies

### 3. Knowledge Freshness
- llm-wiki upkeep
- resource intelligence upkeep
- document intelligence upkeep
- stale indexes, stale corpora, or missing refresh cycles
- broken or abandoned pipelines that should be producing new intelligence

### 4. Intelligence Accessibility
- whether key knowledge is discoverable from repo docs, skills, and operating workflows
- whether links, indexes, and entry points still work
- whether the relevant machine/agent can access the files and tools needed to use the intelligence
- whether important intelligence is trapped in one machine, one repo, one transcript, or one local path
- whether the current structure supports fast retrieval during real execution

## Suggested Weekly Checklist

### A. Settings and Routing
- [ ] Review Hermes default model and route mapping
- [ ] Review provider fallbacks and quota-sensitive paths
- [ ] Review auth modes and any machine-specific breakage
- [ ] Review skill-path/external-dir assumptions
- [ ] Review workflow hard-stop and enforcement settings

### B. Machine Readiness
- [ ] Confirm current machine list and intended responsibilities
- [ ] Check machine-specific config drift
- [ ] Check tool/CLI availability for primary workflows
- [ ] Check auth readiness for GitHub, Claude, Gemini, Gmail, and other critical systems
- [ ] Record any blockers preventing execution on a given machine

### C. Knowledge Freshness
- [ ] Check whether llm-wikis were updated on the expected cadence
- [ ] Check whether resource intelligence pipelines ran and produced usable outputs
- [ ] Check whether document intelligence pipelines/indexes are current
- [ ] Identify stale corpora, stale indexes, or missing refreshes

### D. Intelligence Accessibility
- [ ] Check whether the key intelligence has canonical entry points
- [ ] Check whether docs/skills reference the right locations
- [ ] Check whether the intelligence is accessible from the machines that need it
- [ ] Check whether retrieval is fast and obvious for agents and humans
- [ ] Identify broken links, path drift, missing syncs, or discoverability gaps

### E. Output and Follow-Through
- [ ] Write a short weekly findings summary
- [ ] Record machine-by-machine notes
- [ ] Record intelligence freshness/accessibility notes
- [ ] Capture recommended changes
- [ ] Open follow-on issues for anything that requires implementation

## Deliverable Format

Each review should produce:
- summary of overall ecosystem health
- machine-by-machine readiness notes
- settings/routing changes or risks
- knowledge freshness notes
- intelligence accessibility notes
- follow-on issues with owners/scope where needed

## Planned Follow-On Work

The weekly review is broad enough that it should be split into focused follow-on work items:
- checklist + reporting template
- multi-machine readiness matrix
- intelligence accessibility map
- automation/scheduled execution path
- canonical entry points for ecosystem intelligence
- freshness cadences and staleness signals for intelligence assets
- canonical artifact model for weekly findings/history
- machine dispatch/routing contract
- fleet heartbeat evidence feed
- weekly-review query packs and verification fixtures
- weekly ecosystem scorecard

## Related Issues
- Parent: #2089
- Checklist/template: #2092
- Machine readiness matrix: #2094
- Intelligence accessibility map: #2096
- Automation/scheduled run: #2097
- Canonical intelligence entry points: #2104
- Freshness cadence + staleness thresholds: #2105
- Findings artifact/history model: #2106
- Machine dispatch/routing contract: #2119
- Fleet heartbeat evidence feed: #2120
- Weekly-review query packs + fixtures: #2121
- Weekly ecosystem scorecard: #2122
- Machine readiness schema + generated view: #2134
- Per-machine readiness evidence bundles: #2135
- Intelligence accessibility registry: #2136
- Intelligence Entry Points page + backlink test: #2137
- Scheduled weekly review runner + task registration: #2138
- Weekly review artifact schema + canonical output layout: #2139
- Weekly review runner wrapper + CLI entrypoint: #2144
- Weekly review schedule registration + cron installer wiring: #2145
- Weekly review run-artifact schema spec: #2146
- Weekly review artifact validator CLI + CI checks: #2147
- Linux readiness evidence bundle writer: #2148
- Seeded intelligence accessibility registry generator: #2149
- Windows no-SSH readiness evidence writer + local drop path: #2150
- Per-machine readiness evidence bundle schema + status vocabulary: #2151
- Golden fixture corpus for weekly review run artifacts: #2152
- Weekly review history index + latest manifest writer: #2153
- Markdown/HTML publication layout renderer: #2154
- Shared machine/path resolver library: #2155
- Accessibility registry coherence validator: #2156
- Native PowerShell probe collector for Windows readiness bundles: #2157
- Git Bash launcher + path-normalization bridge for Windows evidence writer: #2158
- Publication bundle assembler for weekly review outputs: #2159
- Latest/history navigation + relative-link contract tests: #2160
- Ingest provider-session ecosystem audit reads into seeded accessibility registry: #2161
- Machine/path alias schema for seeded accessibility registry entries: #2162
- Windows Task Scheduler invocation harness for readiness evidence runs: #2163
- Cygpath/native-path fixture suite for Windows launcher bridge: #2164
- Publication asset/path integrity validator for assembled bundles: #2165
- Renderer golden snapshots for weekly publication outputs: #2166
- Session-read coherence golden fixture suite: #2167
- Cross-registry coverage/drift report for accessibility registry + provider-session reads: #2168
- Windows licensed-tool probe adapter contract: #2169
- OrcaFlex/OrcaWave/ANSYS-AQWA Windows probe adapters: #2170
- End-to-end weekly publication smoke scenarios: #2171
- Weekly publication rerun/idempotence verification: #2172
- Provider-session audit wiring into weekly registry build/publication bundle: #2173
- Unresolved session-read triage report + historical alias-normalized backfill: #2174
