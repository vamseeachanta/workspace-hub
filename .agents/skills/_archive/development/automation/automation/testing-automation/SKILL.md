---
name: automation-testing-automation
description: 'Sub-skill of automation: Testing Automation.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Testing Automation

## Testing Automation


```python
# Test workflow logic in isolation
def test_transform_step():
    input_data = {"raw": "value"}
    expected = {"processed": "VALUE"}

    result = transform_step(input_data)

    assert result == expected

# Integration tests with mocked services
def test_workflow_end_to_end(mock_api):
    mock_api.return_value = {"status": "ok"}

    result = run_workflow("test-workflow")

    assert result.success
    assert mock_api.called
```
