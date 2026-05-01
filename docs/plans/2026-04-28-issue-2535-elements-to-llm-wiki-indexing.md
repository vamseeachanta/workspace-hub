# Plan — workspace-hub#2535 Elements to LLM Wiki Indexing

## Status
Approved by user instruction in current Hermes session: "create gh issues appropriately and then perform the work".

## Deliverable
Metadata-first LLM-wiki indexing artifacts for all 8 Elements-ingested buckets, with source-of-record paths pointing to /mnt/ace parent destinations and no raw bulk data copied into git.

## Scope
- Create inventory/classification artifacts under .planning/intel/elements-to-llm-wiki/.
- Initialize missing wikis only as needed.
- Create metadata source pages and summary pages in knowledge/wikis/.
- Run status/lint checks and capture results.
- Commit/push artifacts and update #2535.

## Boundaries
- No deletion of /mnt/elements or _from_elements; #2534 remains retention-gated.
- No raw 1.9T+ data copied into workspace-hub.
- Deep extraction is deferred to #2536.

## Validation
- Inventory counts match Elements merge/readiness artifacts.
- Wiki pages exist and reference /mnt/ace parent paths.
- llm_wiki.py status/lint commands run for modified wikis.
- git diff confirms no raw binary bulk artifacts staged.
