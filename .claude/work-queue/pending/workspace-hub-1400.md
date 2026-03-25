---
id: WRK-1400
title: "Spot-check va-hdd-2 classification accuracy for engineering domains"
repo: workspace-hub
type: task
complexity: A
priority: medium
status: pending
created: 2026-03-25
depends_on: [WRK-1357]
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1400
---

# WRK-1400: Spot-check va-hdd-2 classification accuracy for engineering domains

## Description

Validate classification accuracy. WRK-1357 found 51.5% engineering rate -- anomalously high for personal HDD. Some misclassifications likely (e.g. "Microwave Engineering" is not O&G). Sample 50 files across engineering domains, manual review.

## Acceptance Criteria

- [ ] Random sample of 50 files across engineering domains
- [ ] Manual review: correct/wrong/ambiguous per file
- [ ] Accuracy report per domain
- [ ] Flag domains <80% accuracy for Phase E2 remap
- [ ] Report at data/document-index/summaries/va-hdd-2-accuracy-report.yaml

## Related

- Parent: WRK-1355
- Predecessor: WRK-1357
- Informs: WRK-1399
