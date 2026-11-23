---
name: dash-common-issues
description: 'Sub-skill of dash: Common Issues.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Callback not firing**
```python
# Check component IDs match exactly
# Verify Input/Output/State decorators
# Check for circular dependencies
```

**Issue: Slow initial load**
```python
# Use loading states
dcc.Loading(
    children=[dcc.Graph(id="graph")],
    type="circle"
)
```

**Issue: Memory leaks**
```python
# Clear caches periodically
# Use background callbacks for long operations
# Limit data in client-side stores
```

**Issue: Multiple callback outputs**
```python
# Use allow_duplicate=True for same output
@callback(
    Output("output", "children", allow_duplicate=True),
    Input("button2", "n_clicks"),
    prevent_initial_call=True
)
```
