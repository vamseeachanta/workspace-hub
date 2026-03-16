---
name: infrastructure-layout-compliance-checks
description: 'Sub-skill of infrastructure-layout: Compliance Checks.'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Compliance Checks

## Compliance Checks


Run after any structural change to `infrastructure/`:

```bash
pkg=your_package_name
infra=src/$pkg/infrastructure

# 1. Canonical dirs present
for d in config persistence validation utils solvers; do
  [ -d "$infra/$d" ] && echo "OK: $d" || echo "MISSING: $d"
done

# 2. No stale catch-all dirs (common/, core/, validators/ should be shims only)
for legacy in common core validators base_configs; do
  if [ -d "$infra/$legacy" ]; then
    real=$(find "$infra/$legacy" -name "*.py" | xargs grep -L "DeprecationWarning" 2>/dev/null | grep -v __init__ | wc -l)
    [ "$real" -gt 0 ] && echo "WARN: $legacy/ has $real non-shim files — migrate to canonical path"
  fi
done

# 3. Web layer not in infrastructure/
[ -d "$infra/services" ] && \
  find "$infra/services" -name "*.py" | xargs grep -L "DeprecationWarning" 2>/dev/null | \
  grep -v __init__ | grep -q . && \
  echo "WARN: real Flask/web code still in infrastructure/services/ — move to web/"

# 4. No domain logic embedded in infrastructure/domains/
[ -d "$infra/domains" ] && \
  find "$infra/domains" -name "*.py" | xargs grep -L "DeprecationWarning" 2>/dev/null | \
  grep -q . && echo "WARN: infrastructure/domains/ has non-shim files — move to domain packages"

# 5. External callers still using deprecated paths
for legacy_path in "infrastructure\.common\b" "infrastructure\.core\b" "infrastructure\.validators\b" "infrastructure\.base_configs\b"; do
  count=$(grep -r "$legacy_path" src/ --include="*.py" | grep -v "DeprecationWarning\|# " | wc -l)
  [ "$count" -gt 0 ] && echo "WARN: $count callers still using $legacy_path"
done

# 6. Run import smoke test
python3 -c "import $pkg.infrastructure.config; import $pkg.infrastructure.persistence; import $pkg.infrastructure.validation; import $pkg.infrastructure.utils; import $pkg.infrastructure.solvers; print('All 5 domains import OK')"
```

---
