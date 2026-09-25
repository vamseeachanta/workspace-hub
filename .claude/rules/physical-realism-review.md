# Physical realism before a mechanism enters a report — agent rule

**When to apply:** in any engineering work, any time an analysis result, a failure, or an explanation depends on a physical mechanism. This covers solver instability, a load peak, a slack/snap event, a resonance or an unexpected response. It applies whatever the tool (OrcaFlex, Ansys, OpenFOAM, a spreadsheet, hand calculation) and whatever the deliverable (report, issue, board card, email).

**Rule:** a mechanism is stated as a finding only when the evidence shows it is **physically realistic** for the real system. When the model's behaviour is not physically realistic, or realism cannot be judged from the evidence, the result is **not** reported as a finding. It is flagged for human review in a standalone HTML page that is ready for that review, and the report states the cause as not established until the owner decides.

**Why:** a model can be numerically correct and physically wrong. Examples are a sling carrying compression, a line snapping from a slack state the rigging cannot reach, energy growing without a source, and a response driven by an idealisation (rigid body, massless line, point load). Once such a mechanism reaches a report it reads as understanding and stops the investigation. The same treatment applies to every piece of engineering work, so that "unrealistic" is judged by a person looking at the evidence, not by the agent that produced it. (Owner instruction, 2026-09-25, raised on the mudmat vessel-capability study.)

**How to apply:**

1. **Judge realism against a stated expectation.** Write down what the real system would do: its component capacities, its possible states (slack, contact, separation), energy sources, and typical magnitudes from a comparator the model did not produce. Test the modelled behaviour against that.
2. **If it is realistic:** state the mechanism with its evidence. [`mechanism-before-publication.md`](mechanism-before-publication.md) still applies: read the source or output that settles it, and label hypotheses as hypotheses.
3. **If it is unrealistic or undetermined, build the review page.** A standalone HTML page, one section per affected case or result, each section containing:
   - **Screenshots** of the model or result at the relevant times (for example the model view just before an instability), so the reviewer sees the physical configuration;
   - **the simulated response beside the physical expectation**: time histories or plots of the governing quantities with the expected range, limit or behaviour drawn on the same axes;
   - **what the model shows, what the real system would do, and why they differ**, in two or three sentences;
   - **the evidence still missing** and what would settle it (a rerun, a refined model, test data, a drawing);
   - a clear status line: *Ready for human review — mechanism not established.*
4. **Route it as a human gate.** Link the page from the project's decision board (or equivalent gate record) with the options the reviewer can choose. The report keeps the cause *not established* and links the review page until the owner decides.
5. **Do not rewrite the result to look realistic.** Filtering, clipping or re-labelling a non-physical response to hide it is not allowed; the review page shows it as produced.

**Do NOT apply when:** the result makes no mechanistic claim, i.e. it is a plain observation with no "because". "The run stopped at 355 s" needs no review page; "the run stopped because the sling snapped" does.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 0 prose now. Level 2 candidate: a report check that fails when a mechanism statement carries neither an evidence reference nor a link to a human-review page.

**Related:** [`mechanism-before-publication.md`](mechanism-before-publication.md) (verify a cause before publishing it), [`reproducibility-is-not-correctness.md`](reproducibility-is-not-correctness.md) (a comparator outside the producing system), [`report-audience-and-surface.md`](report-audience-and-surface.md) (which surface the review page may live on), [`engineering-register.md`](engineering-register.md).
