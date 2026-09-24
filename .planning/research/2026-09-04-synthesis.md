# Weekly Research Synthesis — 2026-09-04

Five research passes this week (2026-08-29 skill-design, 2026-08-31 standards, 2026-09-01 python-ecosystem, 2026-09-02 ai-tooling, 2026-09-03 competitor-market). No `gh`/Bash tool available in this session — issue titles below are **recommendations only**, same caveat as the 08-28 synthesis. This is now the **third consecutive weekly synthesis** unable to verify whether prior weeks' recommended issues were actually filed.

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| Phase 999.2 scope-sketch finding has now recurred in **5 consecutive research passes** (08-21→09-03) across three independent domains (standards, competitor-market ×2) with zero plan filed | **High** | Create GitHub issue: force Phase 999.2 design sketch this week — treat as blocking, not "monitor" | Pending |
| Anthropic Dreaming + Outcomes + Multi-agent Orchestration confirmed stable (May 6 GA, Harvey 6x pilot) — directly maps to Phase 7's reflection/rubric/parallel-validation needs | High | Promote to PROJECT.md — Phase 7 solver-verification architecture (plan→dream→validate→execute→reflect + 5-point Outcomes rubric) | Pending |
| MCP July 28 spec finalized (stateless core, header routing) removes session-affinity uncertainty from Phase 7's licensed-win-1 MCP tunnel | Medium-High | Promote to PROJECT.md — Phase 7 MCP tunnel design note | Pending |
| ISO 24656:2022 (wind CP) + ABS subsea cable standard (Mar 2026) complete the DNV/ABS/ISO normative stack — standards landscape now fully converged/locked | Medium | Promote to PROJECT.md — v1.1 normative standards list (single consolidated citation set) | Pending |
| Orchestrator-worker pattern (40-60% cost reduction, proven at scale) maps cleanly to Phase 7 (Opus orchestrator / Sonnet-Haiku solver worker) | Medium-High | Create GitHub issue: Phase 7/999.4 supervisor-pattern cost modeling | Pending |
| Claude Code Aug 29 (`/cost`, `/usage`, `/tasks`, Remote Control streaming) forms a complete observability layer | Medium | Promote to PROJECT.md — Phase 7 observability baseline section | Pending |
| Governance layer emerged as new domain: IMDA identity cards, Berkeley risk taxonomy, NIST interop profile (Q4 2026 target) | Medium (net-new domain) | Create GitHub issue: v1.1 skill-governance — adopt IMDA identity cards for Claude/Codex/Agy agents | Pending |
| Trace-based skill evaluation (Skill-Tester, SKILLCRAFT, SKILLLEARN-BENCH) replaces binary pass/fail with per-execution-step spans | Medium | Create GitHub issue: Phase 7 trace-span reporting schema | Pending |
| Gemini CLI formally retired June 18, 2026 → Antigravity CLI is the confirmed successor | Low-Medium | Create GitHub issue: audit SHARED_SOUL.md/model-routing.md for stale "Gemini CLI" references | Pending |
| PEP 808 formalizes static-dependency precedence; uv.lock now unambiguously authoritative | Low | Create GitHub issue: 15-min Phase 7 CI checklist note (PEP 808 compliance) | Pending |
| Python 3.15 final release confirmed Oct 1, 2026 (RC2 shipped 09-01) — frozendict, UTF-8 default | Low | Monitor — v1.2 CI matrix planning, revisit Oct 1 | Pending |
| Flexcom 2026.1.1 truss-element mooring-chain model now production-mature — directly bears on the Phase 999.2 scope question | Medium (folds into 999.2) | Fold into the forced Phase 999.2 sketch (do not track separately) | Pending |
| uv 0.12.1, coverage.py 2026 updates, PyYAML CVE isolated to Docling — all confirmation, no action | Low | No action | Pending |
| Progressive disclosure (98.7% context reduction, Pydantic AI 2.0) — concrete pattern for skill refactoring | Medium | Create GitHub issue: refactor 5 skill exemplars to Tier 1/Tier 2 structure | Pending |
| Competitor landscape (Sesam/SACS/OrcaFlex/ANSYS) — third consecutive confirmation pass, zero new entrants | Low | Ignore/monitor | Pending |

## Top 3 Insights for PROJECT.md

1. **Phase 999.2 is no longer a research finding — it is a process failure, and this synthesis should name it as such.** Five research passes across three independent domains (standards 08-24, standards 08-31, competitor-market 08-27, competitor-market 09-03, and skill-design's adjacent backlog-scope pattern) have now converged on the identical unaddressed gap. Each week's report explicitly states "research isn't the blocker, the design sketch is" — and each week the sketch still doesn't exist. PROJECT.md's own §Constraints says "Plan before acting"; a `0/4`-WRK backlog phase silently absorbing DNV seismic updates, ABS cables, ISO 24656, Flexcom truss elements, and MIM notation for five weeks running is exactly the failure mode that constraint exists to prevent. Recommend treating this as a hard stop: no sixth research pass touches Phase 999.2 scope until a sketch exists, regardless of what new standards land.

2. **Phase 7's architecture is now fully specified by external research, not internal design work — the gap between "research complete" and "design written" is now the critical path.** Three domains landed on the same shape this week: Anthropic's Dreaming/Outcomes/Multi-agent Orchestration (stable, GA, proven 6x at Harvey) gives the reflection+rubric+parallelism pattern; the orchestrator-worker cost data (40-60% savings, proven at scale) gives the role-separation model; and MCP's July 28 stateless-core spec removes the tunnel-design uncertainty. Unlike Phase 999.2, this is a genuinely converged, low-risk decision — every prerequisite fact needed to write the Phase 7 solver-verification design doc is now sitting across four weeks of ai-tooling research. This is the week to write it, not research it further.

3. **A new governance domain (IMDA/Berkeley/NIST) surfaced this week that PROJECT.md has no section for, and it has a hard external deadline.** Unlike prior weeks' incremental confirmations, skill-design's 08-29 report identified formal agentic-AI governance standards (Singapore IMDA Jan 2026, Berkeley CLTC Feb 2026, NIST targeting Q4 2026 for an interoperability profile) that did not exist in any prior research scope. workspace-hub's current governance is convention-based (SHARED_SOUL.md Hard Gates); the NIST profile lands in Q4 2026, which is now inside planning horizon. This doesn't block v1.1, but it's the one finding this week that isn't a confirmation of something already known — it deserves its own line in PROJECT.md rather than folding into the general skill-audit backlog.

## Cross-Domain Connections

- **Standards (08-31 ISO/ABS/DNV convergence) ↔ competitor-market (09-03 Flexcom truss elements):** both domains this week independently point at the exact same unresolved question — is mooring-chain/cable design in Phase 999.2's v1.0 scope? Standards supplies the normative stack (DNV-ST-0359, ABS cables, ISO 24656); competitor-market supplies the production-maturity signal (Flexcom's truss-element model, May 2026). Together they remove every remaining excuse to defer the design sketch.
- **ai-tooling (09-02 Dreaming/Outcomes) ↔ skill-design (08-29 trace-based eval, SkillRouter):** both domains describe the same underlying shift from binary pass/fail to structured, multi-step quality assessment for Phase 7 — Anthropic's Outcomes rubric and the four new academic eval frameworks (Skill-Tester, SKILLCRAFT, SKILLLEARN-BENCH, trace spans) are describing the same pattern from vendor and research-literature angles respectively. Write Phase 7's quality-scoring schema once, informed by both.
- **python-ecosystem (09-01 PEP 808) ↔ ai-tooling (09-02 MCP stateless spec):** both are "substrate has locked" findings — dependency reproducibility (uv.lock authoritative) and remote-execution architecture (no session affinity) are now settled, non-negotiable facts rather than open design questions for Phase 7. Neither needs further research; both need one-line documentation notes.
- **Process signal across all five reports:** every domain this week independently states some version of "no blocking changes, all facts in hand, execution is now the constraint" — standards, competitor-market, python-ecosystem, and ai-tooling all converge on this framing. The one exception is skill-design's governance finding, which is genuinely new. This is the first week where four of five domains explicitly recommend narrowing research scope rather than continuing full five-domain depth — worth acting on the 08-28 synthesis's suggestion to trim to 2-3 domains next week.

## Detailed Action Items

- [ ] Promote: Phase 7 solver-verification architecture (Dreaming reflection + Outcomes 5-point rubric + multi-agent orchestrator-worker fan-out) → PROJECT.md Phase 7 design
- [ ] Promote: Phase 7 MCP tunnel design note (stateless core, header routing, no session affinity, per July 28 spec) → PROJECT.md Phase 7 architecture
- [ ] Promote: Phase 7 observability baseline (`/cost`/`/usage`/`/tasks` + Remote Control streaming) → PROJECT.md Phase 7 design
- [ ] Promote: v1.1 normative standards list — consolidate ISO 19901-1:2026, ISO 19902, ISO 19905-1:2025/Amd1, DNV-ST-0359, ISO 24656:2022, DNV-ST-N001, DNV MIM notation into one citation block → PROJECT.md v1.1 definition-of-done
- [ ] Issue: `workspace-hub#TBD` — "Phase 999.2 scope sketch + WRK re-score — FORCE THIS WEEK (5th consecutive finding, includes Flexcom truss elements + full DNV/ABS/ISO cable+CP stack)"
- [ ] Issue: `workspace-hub#TBD` — "Phase 7/999.4 — orchestrator-worker cost modeling (Opus orchestrator / Sonnet-Haiku worker, target 40% cost reduction)"
- [ ] Issue: `workspace-hub#TBD` — "v1.1 skill-governance — adopt IMDA agent identity cards for Claude/Codex/Agy (new governance domain, NIST interop profile due Q4 2026)"
- [ ] Issue: `workspace-hub#TBD` — "Phase 7 — add trace-span quality schema (plan/dream/validate/execute/reflect) replacing binary pass/fail"
- [ ] Issue: `workspace-hub#TBD` — "Audit SHARED_SOUL.md + model-routing.md for stale 'Gemini CLI' references → Antigravity CLI/Agy (retired June 18, 2026)"
- [ ] Issue: `workspace-hub#TBD` — "Phase 7 CI checklist — 15-min PEP 808 declarative-dependency compliance note"
- [ ] Issue: `workspace-hub#TBD` — "Refactor 5 skill exemplars to progressive-disclosure Tier 1/Tier 2 structure (98.7% context-reduction pattern)"
- [ ] Monitor: Python 3.15 final release (Oct 1, 2026) — v1.2 CI matrix planning
- [ ] Monitor: NIST AI Agent Interoperability Profile — quarterly check, next Nov 1, 2026
- [ ] **Carryover confirmation still needed** (4th consecutive week): verify whether any 08-21 through 08-31 recommended issues were actually filed — no `gh`-capable session has run in this synthesis chain yet
- [ ] **Process decision for next week:** trim domain scope to 2-3 (standards + skill-design, where real scope changes still land) given four of five domains this week explicitly reported diminishing research returns
