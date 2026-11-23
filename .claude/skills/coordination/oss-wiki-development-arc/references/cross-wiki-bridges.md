# Cross-Wiki Bridges

A "bridge" is a substantive cross-wiki link: page A in wiki X links to page B in wiki Y in a way that adds engineering value, not just navigation. Bridges are the differentiator between "a collection of wikis" and "an interconnected wiki ecosystem."

## What Counts as a Bridge

**Substantive bridge** (counts):

> "...the 1980 Alexander L. Kielland capsize is analyzed in detail under [marine/incidents/kielland-1980] from a structural-fatigue perspective; the naval-architecture stability implications are covered separately at [naval/stability/post-kielland-stability-codes]."

The link tells the reader **why** to follow it and **what** they'll get on the other side.

**Non-substantive ("see also") link** (does NOT count):

> "See also: [naval/stability/post-kielland-stability-codes]"

The "see also" link gives the reader no reason to click and produces no compounding value. Phase-1 audits should not credit "see also" links toward bridge density.

## The Sister-Pair Pattern

The highest-value bridge structure is a **sister-pair**: two pages on related concepts, one in each wiki, that explicitly reference each other. The two pages frame the same underlying topic from different disciplinary angles.

### Examples (engineering ↔ marine)

| Engineering wiki | Marine wiki | Pair theme |
|------------------|-------------|------------|
| `engineering/fatigue/weld-fatigue-S-N-curves.md` | `marine/incidents/kielland-1980.md` | Theory ↔ named incident demonstrating theory |
| `engineering/codes/DNV-OS-E301.md` | `marine/operations/mooring-design.md` | Standard ↔ application of standard |
| `engineering/methods/spectral-fatigue-analysis.md` | `marine/loads/wave-spectra-jonswap.md` | Method ↔ input data for method |

### Pre-incident vs Post-incident sister-pair

A common engineering sister-pair is "design-prevention page" ↔ "diagnosis-from-failure page":

- **Design-prevention** (engineering wiki): how to avoid the failure mode in design. Forward-looking. Code-driven.
- **Post-incident diagnosis** (marine/operations wiki): how the failure manifested in a real case. Backward-looking. Evidence-driven.

These sister-pages cite each other because each grounds the other:

- The design-prevention page cites the post-incident diagnosis as the failure mode it prevents
- The post-incident diagnosis cites the design-prevention as the modern code that addresses the lesson

## Sibling-Template Recognition

Once one sister-pair exists, dozens of similar pairs follow the same template. Recognizing the template lets you bridge-construct faster:

**Template: "code ↔ application"**

- Engineering page: `engineering/codes/<code-id>.md` (the standard)
- Marine page: `marine/operations/<application>.md` (where the standard is applied)
- Bridge phrasing on engineering side: "Operational application is documented at [marine/operations/...]; failure modes addressed by this code are catalogued there."
- Bridge phrasing on marine side: "Compliance is governed by [engineering/codes/...]; required factors of safety derive from that document."

**Template: "method ↔ named example"**

- Engineering page: `engineering/methods/<method>.md`
- Marine/naval page: `<wiki>/incidents/<named-event>.md` or `<wiki>/projects/<named-project>.md`
- Bridge phrasing: explicit citation in both directions

**Template: "phenomenon ↔ measurement"**

- Engineering page: `engineering/concepts/<phenomenon>.md`
- Operations wiki: `<wiki>/instrumentation/<measurement-method>.md`

When iter-N+1 needs to construct bridges, scan each wiki's page list against these templates; matches are bridge-candidates.

## Bridge-Construction Iter-Lane (Phase 1, Lane D)

The bridge lane runs **after** content lanes B and C land in the same iter. Workflow:

1. Read iter-N audit doc's "recommended bridge targets" section
2. For each target pair, draft substantive bridge text on both sides
3. Verify the linked pages exist (substrate-saturation precondition)
4. Edit both pages with the substantive bridge text
5. Commit; verify with grep that both directions are present

**Why bridge-lane runs last:** content lanes may create new pages that bridge-lane wants to link. Running bridge-lane in parallel risks linking to pages that haven't landed yet.

## Bridge Validation (Phase 3)

The Phase-3 unidir-bridge audit (criterion 2) walks every cross-wiki link and verifies reciprocity. Process:

1. Build the cross-wiki link graph (only links where source-wiki ≠ target-wiki)
2. For each edge A→B, check if B→A also exists
3. Report all unidirectional edges

Phase-3 reciprocation lane reads this report and adds the missing reverse links. By Phase-3 exit, the count is 0.

## Bridge Density as a Phase-1 Metric

Phase-1 audit reports cross-wiki edge density:

```
edge_density = (cross_wiki_link_count) / (total_link_count)
```

Healthy ecosystems plateau at 5-15% edge density. Below 5% means the wikis are silos; above 20% suggests over-bridging (pages that should be in one wiki are being awkwardly split).

Track edge density across audit versions. Plateau signals Phase-1 bridge-saturation; combined with other Phase-1 saturation signals, it triggers transition to Phase 2.

## Common Bridge Anti-Patterns

- **"See also" bridges** — non-substantive; don't compound; should be replaced with substantive bridges in Phase 2 depth-expansion
- **One-way bridges** — added during Phase 1 without reciprocation; piles up as Phase-3 cleanup work
- **Bridges to stubs** — bridge lane links to a page that's a substrate-stub; reader follows and finds nothing. Substrate must be saturated on both sides before bridge-construction.
- **Over-bridging** — every paragraph has a cross-wiki link; reader experience degrades. Aim for 1-3 substantive bridges per page, not 10+.
- **Bridge-without-context** — link with no engineering reason given. Even "is governed by" is better than no context.

## Reference Exemplar

llm-wiki cross-wiki bridge structure between the engineering, marine, and naval-architecture wikis. V11 audit reports the substrate-saturation bridge density. V17 confirms bidirectional reciprocity.
