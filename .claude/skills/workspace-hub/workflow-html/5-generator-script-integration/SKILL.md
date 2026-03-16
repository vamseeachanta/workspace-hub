---
name: workflow-html-5-generator-script-integration
description: 'Sub-skill of workflow-html: 5. Generator Script Integration.'
version: 2.3.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# 5. Generator Script Integration

## 5. Generator Script Integration


`scripts/work-queue/generate-html-review.py` — `--type` flags deprecated (WRK-1031). Use `--lifecycle`.

```python
def generate_lifecycle(wrk_id: str, output_file: str | None = None) -> None:
    """Generate WRK-NNN-lifecycle.html from evidence files on disk (stateless)."""
```

`detect_stage_statuses()` reads evidence files → `{stage_n: 'done'|'active'|'pending'|'na'}`.
Re-running `--lifecycle` is idempotent — safe at any stage gate.

---
