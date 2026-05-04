---
name: discipline-refactor-python-package
description: 'Sub-skill of discipline-refactor: Python Package (+1).'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Python Package (+1)

## Python Package


**Before:**
```
mypackage/
├── src/mypackage/
│   ├── utils.py
│   ├── models.py
│   ├── api/
│   └── data/
├── tests/
│   ├── test_utils.py
│   └── test_api.py
└── docs/
    ├── api.md
    └── data.md
```

**After:**
```
mypackage/
├── src/mypackage/
│   └── modules/
│       ├── _core/
│       │   ├── __init__.py
│       │   └── utils.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       └── data/
│           ├── __init__.py
│           └── models.py
├── tests/
│   └── modules/
│       ├── _core/
│       │   └── test_utils.py
│       └── api/
│           └── test_routes.py
├── docs/
│   └── modules/
│       ├── api/
│       │   └── README.md
│       └── data/
│           └── README.md
└── specs/
    └── modules/
        └── api/
            └── api-spec.md
```


## Import Changes


```python
# Before
from mypackage.utils import helper
from mypackage.api.routes import router

# After
from mypackage.modules._core.utils import helper
from mypackage.modules.api.routes import router
```

---
