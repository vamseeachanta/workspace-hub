Governance cleanup:

- This issue currently carries the live label `status:plan-approved`, but there is no corresponding local approval marker `.planning/plan-approved/2271.md`.
- Per workflow governance, that is approval-state drift.
- Rolling the issue back to `status:plan-review` so GitHub state no longer implies local approval evidence that is absent.

If this issue was intentionally approved elsewhere, the approval marker should be recreated in a later controlled pass.
