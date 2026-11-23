Integrated the Gemini review findings from the completed `review-2399-gemini-r3.out` run into the local #2399 draft.

Applied changes in the draft:
- added explicit discoverability-anchor requirement through `AGENTS.md`, `CLAUDE.md`, `.gemini/GEMINI.md`, and `docs/standards/CONTROL_PLANE_CONTRACT.md`
- upgraded the battery from a bare YAML artifact to a spec + runner-contract pair
- added a separate upgrade playbook artifact
- strengthened acceptance criteria around discoverability, runner-consumability, and ecosystem-wide scope

Also noted that the Gemini CLI run later hit provider capacity exhaustion (429 / MODEL_CAPACITY_EXHAUSTED), so future Gemini evidence should be treated carefully if retries are incomplete.

Status remains: NOT approval-ready yet.
A fresh re-review is still needed on the newly updated draft text.
