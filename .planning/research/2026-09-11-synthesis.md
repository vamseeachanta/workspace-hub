# Weekly Research Synthesis — 2026-09-11

**Scope note:** this session has no `gh` or Bash tool available, matching every prior weekly synthesis in this chain. No issue in the table below has been filed or verified as filed; "Create GitHub issue" entries remain recommendations only. Prior weeks' carryover verification (whether 08-21→09-04 recommended issues were ever created) also remains unconfirmed.

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| Python-ecosystem (4th) and competitor-market (4th) research passes have now each returned confirmation-only results for three-to-four consecutive weeks, and both independently recommend quarterly cadence | High | Promote to PROJECT.md (research-cadence policy) + Create GitHub issue to formalize the schedule | Pending |
| Research keeps generating meta-infrastructure proposals for Phase 7 (SKILLCRAFT DAG contracts, unified trace-audit sidecar, IMDA identity cards, 128K-output/task-queue pattern) that have no anchor in Phase 7's actual remaining plan, which is 07-03 (smoke test execution + artifact commit) per ROADMAP.md | High | Create GitHub issue as a separate backlog item, distinct from Phase 7; do not fold into 07-03 | Pending |
| The skill-design report's "Unified Skill Evaluation Audit Trail Specification" citation is `arxiv.org/abs/2609.xxxxx` — a literal placeholder, not a resolvable identifier | Medium | Ignore/do not cite until a real identifier is located; flag as unverified in any downstream reference | Pending |
| Phase 999.2 design sketch remains unwritten; this week's standards report adds API 579 Part 16 (FRP) as a further scope-boundary question without resolving it | High | Create GitHub issue: force the Phase 999.2 sketch (6th consecutive week the gap has surfaced across research passes) | Pending |
| DNV July 2026 class edition (battery/shore-power notations) + OrcaWave <1% WAMIT validation study — both traceable to named, dated primary sources (DNV, Orcina/MDPI) | Medium | Promote to PROJECT.md v1.1 design-basis (normative stack + validation citation) | Pending |
| EU MED Regulation 2026/1434 (June 30, 2026) — relevant only if v1.1 clients are EU-flagged/EU-operational, which is currently undefined in PROJECT.md | Medium | Create GitHub issue: define v1.1 client geographic scope, then conditionally add the compliance note | Pending |
| Shopee/IMDA "94% mis-routing reduction" case study is a single vendor blog claim with no independent replication cited | Medium | Monitor — do not promote as a decision basis until a second, independent source confirms the figure | Pending |
| MCP "10,000+ servers / 97M SDK downloads/month" statistic is precise but unverified in this session; general MCP stability (July 28 stateless-core spec) is independently corroborated across multiple weeks | Low-Medium | Monitor — usable as qualitative "MCP is stable," not as a cited hard number in client-facing material | Pending |
| Constraint-repetition pattern (skill authoring) reported as validated against a Kaggle benchmark with an unusually specific discussion URL; cannot verify existence in this session | Low | Monitor — treat as a hypothesis pending independent confirmation before auditing 50+ skills against it | Pending |
| Sesam/SACS/OrcaFlex/Flexcom/ANSYS competitive landscape — 4th consecutive week, zero change | Low | Ignore this week; resume per the new quarterly cadence (next: Dec 10, 2026) | Pending |

## Top 3 Insights for PROJECT.md

1. **v1.1's design-basis can absorb three concretely sourced, low-risk additions this week: the DNV July 2026 battery/shore-power notation check against the L00–L06 example set, an OrcaWave-vs-WAMIT validation citation (<1% deviation across all six motion modes), and a conditional EU MED 2026/1434 compliance note gated on client geographic scope.** These trace to named regulatory and peer-reviewed sources rather than vendor blog posts, which distinguishes them from this week's less-verifiable claims (see item 3 below) and makes them safe to land in PROJECT.md without further verification.

2. **Research cadence should actually change this week, not merely be recommended again.** Python-ecosystem and competitor-market have each independently proposed quarterly monitoring after three-to-four consecutive confirmation-only passes; the 2026-09-04 synthesis made the same recommendation and it was not acted on. Two independent domains converging on the identical proposal for a second time is a stronger signal than either domain restating it alone — the corrective action (narrow weekly scope to standards + skill-design, park python-ecosystem/competitor-market to a quarterly calendar) should be applied to the *next* research cycle, not deferred to a fifth confirmation.

3. **The research pipeline is now proposing architecture (SKILLCRAFT DAGs, trace-audit sidecars, IMDA identity cards, task-queue read-only patterns) for a Phase 7 whose only remaining plan item is a smoke test (07-03).** None of these proposals derive from a stated Phase 7 requirement; they derive from external vendor/preprint activity that happens to be thematically adjacent. Before any of it lands in PROJECT.md, the underlying citations need a verification pass — one of them (`arxiv.org/abs/2609.xxxxx`) is not a resolvable reference at all. Recommend routing this material to a new backlog phase (adjacent to 999.4) rather than expanding Phase 7's scope while 07-03 is still open.

## Cross-Domain Connections

- **python-ecosystem ↔ competitor-market:** both reports this week independently reach the same conclusion — shift from weekly to quarterly research cadence — after three and four consecutive confirmation-only passes respectively. The redundant conclusion from two unrelated domains is itself the actionable signal.
- **skill-design ↔ ai-tooling:** both propose meta-infrastructure (composition-contract DAGs, unified trace schemas, identity cards, task-queue patterns) aimed at Phase 7/999.4, but neither report checked that proposal against ROADMAP.md's actual Phase 7 scope (07-03 smoke test only). The overlap compounds scope-creep risk rather than validating the proposals.
- **standards ↔ ai-tooling:** both produced small, additive, well-sourced documentation items this week (DNV/OrcaWave/EU citations; MCP maturity note) rather than decision-changing findings — consistent with the broader pattern that the substrate (standards, tooling) has stabilized and design/execution is now the constraint, not research.

## Detailed Action Items

- [ ] Promote: DNV July 2026 battery/shore-power notation check + OrcaWave <1% WAMIT validation citation → PROJECT.md v1.1 design-basis
- [ ] Issue: `workspace-hub#TBD` — "Define v1.1 client geographic scope (EU-flagged/operational?) → conditionally apply EU MED 2026/1434 compliance note"
- [ ] Issue: `workspace-hub#TBD` — "Formalize research cadence: python-ecosystem + competitor-market → quarterly (next: 2026-12-10); narrow weekly scope to standards + skill-design"
- [ ] Issue: `workspace-hub#TBD` — "Phase 999.2 scope sketch + WRK re-score — 6th consecutive research-cycle finding, now includes API 579 Part 16 FRP boundary question"
- [ ] Issue: `workspace-hub#TBD` — "Route SKILLCRAFT/trace-audit/IMDA-card/task-queue proposals to a new backlog phase (999.x) distinct from Phase 7; verify the `arxiv.org/abs/2609.xxxxx` citation before any adoption"
- [ ] Monitor: Shopee/IMDA "94% mis-routing reduction" claim — needs independent corroboration before use as a governance-decision basis
- [ ] Monitor: MCP "10,000+ servers / 97M downloads/month" figure — usable qualitatively, not as a cited hard number
- [ ] Monitor: Kaggle constraint-repetition benchmark — verify the discussion exists before auditing skills against it
- [ ] Carryover (still unresolved, now 4th+ week running): confirm whether any 08-21→09-10 recommended issues were actually filed — requires a `gh`-capable session
