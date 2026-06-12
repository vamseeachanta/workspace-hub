---
name: crossprovider hermes multi-repo-output-path-ambiguity-blocks-acceptan
description: Multi-repo output path ambiguity blocks acceptance
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-repo, output-management, scope-clarity]
---

When scope spans digitalmodel + workspace-hub + acma-projects, artifact types (markdown/HTML vs Word/PDF) route to different repos. Lack of explicit per-artifact routing causes outputs to land in wrong directories or duplicate/vanish. Acceptance criteria must specify: `markdown/HTML → digitalmodel/docs`, `Word/PDF → workspace-hub/acma-projects/B1528/output`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
