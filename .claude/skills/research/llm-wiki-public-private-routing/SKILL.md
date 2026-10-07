---
name: llm-wiki-public-private-routing
description: Route wiki content using current source rights, ownership and destination authority. Apply project-name abstraction only after checking whether publication is permitted; private visibility and anonymization do not grant rights.
metadata:
  category: research
  related_skills:
    - research/llm-wiki
    - research/llm-wiki-page-shape-contract
    - research/llm-wiki-source-extraction-coverage
    - coordination/client-llm-wiki-factory
  related_issues:
    - vamseeachanta/workspace-hub#2727
    - vamseeachanta/workspace-hub#2746
    - vamseeachanta/workspace-hub#2374
  related_rules:
    - .claude/rules/codes-standards-data-routing.md
    - .legal-deny-list.yaml
  references:
    - references/abstraction-decision-tree.md
---

# Wiki public/private routing

This skill is the routing adapter used by `llm-wiki-page-shape-contract`.
Resolve repository-relative authority paths from the explicit workspace-hub
checkout, not an installed adapter directory.

## Canonical authority

Read `docs/architecture/agent-data-handling-contract.md` for ownership, original
retention, source-specific rights and publication boundaries. The residence/layer
policies and `.claude/rules/codes-standards-data-routing.md` complement that contract.
Do not infer destination visibility from a repository name or older public-wiki text.
Check the actual destination and current source rights for the proposed operation.

If the authority or rights evidence is missing or conflicting, identify the gap.
Metadata discovery may continue within existing access; copying and publication
must not proceed on an assumed entitlement. This skill grants no external action.

## Routing checks

- Keep exact client/project material in its authorized private owner. Public-bound
  derivatives require source-specific rights and applicable audience/action approval.
- Public promotion copies the permitted derivative; retain the private source page.
  Promotion does not authorize moving or deleting the private source.
- A public project name does not make private numerical results public. Check each
  material claim's source; preserve source references and extraction limitations.
- Removing names, aggregating ranges or labeling material synthetic does not establish
  redistribution rights. Mixed-source content retains every applicable restriction.
- Only after public use is permitted, apply the required project-name abstraction.
  An actual name may be retained when its public availability and the cited key
  data are evidenced and the governing source/destination contract permits use.
- Keep private locators, credentials and restricted source content out of public
  pages, filenames, commit messages and receipts. Use authorized opaque references.
- Vendor-licensed originals remain outside Git, including private Git. Permitted
  derivatives and private measured-original retention follow the canonical contract;
  a generic standards citation is not a publication license.

Record owner, intended destination/audience, source-rights evidence, remaining gaps
and any abstraction decision. A routing assessment is not publication approval.
Consult an existing private `public-name-exception-approved.yaml` decision ledger
before repeating a resolved question. Reuse a recorded decision only when current
source rights, destination and scope still match; the record grants no new authority.
Read [conditional examples](references/abstraction-decision-tree.md) when useful;
related maintenance skills do not activate automatically.
