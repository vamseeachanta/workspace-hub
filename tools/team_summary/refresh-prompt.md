Daily team-summary refresh for client wiki `llm-wiki-{{CLIENT}}` (workspace-hub#3967).

Edit exactly one file: `reports/team-summary/summary.yml`. Do not create, edit, move or delete any
other file. Do not commit; the calling script commits.

1. Read `reports/team-summary/summary.yml` and the wiki changes listed below (use `git show <sha>`).
2. Update the facts so they match the wiki as of today:
   - Set `as_of` to {{TODAY}}.
   - `priorities`: at most 3, each with owner, next action and due date (ISO date or `TBD`).
   - `issues`: status is one of open, investigating, awaiting-review, resolved. A resolved issue stays
     one refresh with status `resolved` (keep its owner; next_action names where the resolution is
     recorded), then is removed. Every item keeps all fields the schema requires.
   - `decisions`: add new dated decisions; keep the most recent 5.
   - `blockers`, `areas`, `deliverables`: current state only; drop items the wiki shows are finished.
3. Every item's `source` must be a path that exists in this wiki at HEAD. Prefer the primary record
   over dashboards or summaries.
4. Set an item's `review` when its next action asks a person for input, approval, a conclusion or
   comments on a document that exists in this wiki. Use `review.doc` for that wiki-relative path and
   `review.ask` as one of `input`, `approval`, `conclusion`, `comments`. Remove the item's `review`
   once the wiki records the response.
5. Facts only. Nothing that the wiki does not state. No forecasts or recommendations. The subject of a
   sentence is the work or document, not "we". State what is not established plainly.
6. If nothing material changed, leave the file unchanged.

Wiki changes since the last summary:
{{CHANGES}}
