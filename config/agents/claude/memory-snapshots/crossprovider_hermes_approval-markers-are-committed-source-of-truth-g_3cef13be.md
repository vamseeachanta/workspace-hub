---
name: crossprovider hermes approval-markers-are-committed-source-of-truth-g
description: Approval markers are committed source-of-truth gates, not labels
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, github-workflow, file-markers]
---

Implementation can only proceed after `.planning/plan-approved/<issue>.md` file is committed to repo, synchronized with GitHub status label and approval comment. Label alone is insufficient; the file's presence and git history are the hard stop.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
