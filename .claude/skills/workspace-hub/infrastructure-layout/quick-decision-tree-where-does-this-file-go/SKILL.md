---
name: infrastructure-layout-quick-decision-tree-where-does-this-file-go
description: "Sub-skill of infrastructure-layout: Quick Decision Tree \u2014 \"Where\
  \ does this file go?\"."
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Quick Decision Tree — "Where does this file go?"

## Quick Decision Tree — "Where does this file go?"


```
Is it shared across multiple domains in the same package?
│
├─ YES → Is it configuration loading / schema validation?
│        └─ YES → infrastructure/config/
│
├─ YES → Is it a database connection, cache, or audit trail?
│        └─ YES → infrastructure/persistence/
│
├─ YES → Is it a data validation pipeline or validator class?
│        └─ YES → infrastructure/validation/
│
├─ YES → Is it a numerical solver BASE CLASS or FRAMEWORK?
│        └─ YES → infrastructure/solvers/ (or base_solvers/)
│            Note: domain-specific implementations → domain package
│
├─ YES → Is it data I/O, ETL, visualization, or a utility function?
│        └─ YES → infrastructure/utils/
│
└─ NO  → It belongs in the DOMAIN package (structural/, subsea/, well/, etc.)

Is it a Flask/Dash app, blueprint, or web route?
└─ YES → src/<pkg>/web/   (NOT in infrastructure/)

Is it a test?
└─ YES → tests/infrastructure/<domain>/  (NOT in src/)
```

---
