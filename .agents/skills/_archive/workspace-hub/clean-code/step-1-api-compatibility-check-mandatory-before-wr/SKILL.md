---
name: clean-code-step-1-api-compatibility-check-mandatory-before-wr
description: 'Sub-skill of clean-code: Step 1: API Compatibility Check (MANDATORY
  before writing shims) (+2).'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Step 1: API Compatibility Check (MANDATORY before writing shims) (+2)

## Step 1: API Compatibility Check (MANDATORY before writing shims)


```bash
# Compare __init__ signatures: old vs canonical
python3 -c "
import inspect
from old.module import OldClass
from canonical.module import CanonicalClass
print('OLD:', inspect.signature(OldClass.__init__))
print('NEW:', inspect.signature(CanonicalClass.__init__))
"
```

Checklist before shimming any class:
- [ ] `__init__` kwarg signatures match (no removed/renamed parameters)
- [ ] Factory classmethods match (`from_geojson(path)` vs `from_geojson(path, name)`)
- [ ] All module-level attributes that tests patch exist on canonical (`HAS_RASTERIO`, `HAS_FOLIUM`)


## Step 2: Diverged API — Use Relative Imports, Do NOT Shim


If `__init__` signatures differ between old and canonical:
- **Do NOT shim the base class** — any subclass calling `super().__init__(crs=crs)` with the
  old kwarg will crash at runtime with `TypeError: unexpected keyword argument`
- **Fix the subclass**: change its import to use a local relative import pointing to the
  compatible (old) class; shim only the unaffected modules (core/, io/, integrations/)

```python
# WRONG: shim breaks subclass calling super().__init__(crs=crs)
# specialized/gis/layers/feature_layer.py (shim)
from digitalmodel.gis.layers.feature_layer import FeatureLayer  # canonical dropped crs kwarg

# CORRECT: keep old feature_layer.py as-is; fix the subclass import
# specialized/gis/layers/well_layer.py
from .feature_layer import FeatureLayer   # relative → uses local compatible class
```


## Step 3: Re-export Patch-Target Attributes


Tests that use `unittest.mock.patch.object(module, "HAS_X", ...)` require `HAS_X` to exist
as a module-level attribute on the shim module. Shims must re-export these flags:

```python
# WRONG: shim omits the flag
from digitalmodel.gis.io.geotiff_handler import GeoTIFFHandler  # noqa: F401
# → patch.object(geotiff_handler, "HAS_RASTERIO", False) raises AttributeError

# CORRECT: re-export flag alongside the class
from digitalmodel.gis.io.geotiff_handler import GeoTIFFHandler, HAS_RASTERIO  # noqa: F401
__all__ = ['GeoTIFFHandler', 'HAS_RASTERIO']
```

---
