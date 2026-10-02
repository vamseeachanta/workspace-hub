# Physical realism before a mechanism enters a report — agent rule

**When to apply:** in any engineering work, any time an analysis result, a failure, or an explanation depends on a physical mechanism. This covers solver instability, a load peak, a slack/snap event, a resonance or an unexpected response. It applies whatever the tool (OrcaFlex, Ansys, OpenFOAM, a spreadsheet, hand calculation) and whatever the deliverable (report, issue, board card, email).

**Rule:** a mechanism is stated as a finding only when its realism verdict is `not_implausible`. When the verdict is `implausible` or `not established`, the mechanism is **not** reported as a finding. It is flagged for human review in a standalone HTML page, ready for that review, and the report states the cause as not established until the owner decides.

**Why:** a model can be numerically correct and physically wrong. Examples are a sling carrying compression, a line snapping from a slack state the rigging cannot reach, energy growing without a source, and a response driven by an idealisation (rigid body, massless line, point load). Once such a mechanism reaches a report it reads as understanding and stops the investigation. The same treatment applies to every piece of engineering work, so that realism is judged by a person looking at the evidence, not by the agent that produced it. (Owner instruction, 2026-09-25.)

**How to apply:**

1. **Reach a realism verdict against a named expectation.** State the physical expectation for the real system, for example a component capacity, a possible state (slack, contact, separation), an energy source or a typical magnitude. Bind it to:
   - a comparator the model did not produce, with its class per [`reproducibility-is-not-correctness.md`](reproducibility-is-not-correctness.md);
   - the criterion or limit;
   - the governing case.

   The verdict vocabulary follows [`report-audience-and-surface.md`](report-audience-and-surface.md) item 5:
   - `not_implausible`: the modelled behaviour falls within the expectation;
   - `implausible`: it contradicts the expectation;
   - `not established`: the comparator or the evidence is missing.

   A plausibility check cannot confirm a mechanism; it can only fail to contradict it.
2. **`not_implausible`:** state the mechanism with its evidence. [`mechanism-before-publication.md`](mechanism-before-publication.md) still applies: read the source or output that settles it, and label hypotheses as hypotheses.
3. **`implausible` or `not established`:** build the review page. It is a standalone HTML page with one section per affected case or result, each containing:
   - **screenshots** of the model or result at the relevant times (for example the model view just before an instability), so the reviewer sees the physical configuration;
   - **the simulated response beside the physical expectation**: time histories or plots of the governing quantities, with the expected range, limit or behaviour drawn on the same axes;
   - **the verdict and its basis**: what the model shows, what the real system would do, the comparator used, and why they differ, in two or three sentences;
   - **the evidence still missing**, and what would settle it (a rerun, a refined model, test data, a drawing);
   - a status line: *Ready for human review — mechanism not established.*
4. **Name the surface before building the page.**
   - The review page is an **internal** surface by default. It lives in the owning private repository or local output, and is linked from the project's decision board or equivalent gate record.
   - Publishing it to any URL makes it a **hosted** surface under [`report-audience-and-surface.md`](report-audience-and-surface.md). Every screenshot and plot must then be checked and redacted for client identifiers (vessel names, drawing references, coordinates, project IDs) before publication.
   - Nothing from the page is written into a public repository.
5. **Route it as a human gate.** The board card links the page and offers the reviewer's options. The report keeps the cause *not established* and references the review until the owner decides.
6. **Do not rewrite the result to look realistic.** Filtering, clipping or re-labelling a non-physical response to hide it is not allowed; the review page shows the response as produced.

**Do NOT apply when:** the result makes no mechanistic claim, i.e. it is a plain observation with no "because". "The run stopped at 355 s" needs no review page; "the run stopped because the sling snapped" does.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 0 prose now. Level 2 candidate: a report check that fails when a mechanism statement carries neither a `not_implausible` verdict with its comparator nor a link to a human-review page.

**Related:** [`mechanism-before-publication.md`](mechanism-before-publication.md) (verify a cause before publishing it), [`reproducibility-is-not-correctness.md`](reproducibility-is-not-correctness.md) (comparator classes), [`report-audience-and-surface.md`](report-audience-and-surface.md) (surfaces, redaction and verdict vocabulary), [`engineering-register.md`](engineering-register.md).
