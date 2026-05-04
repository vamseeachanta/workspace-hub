---
name: yaml-configuration-1-use-consistent-indentation
description: 'Sub-skill of yaml-configuration: 1. Use Consistent Indentation (+4).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Use Consistent Indentation (+4)

## 1. Use Consistent Indentation

```yaml
# ✅ Good: 2 spaces
vessel:
  dimensions:
    length: 320
    beam: 58

# ❌ Bad: Mixed indentation
vessel:
   dimensions:
     length: 320
   beam: 58
```


## 2. Quote Strings When Needed

```yaml
# Quote strings that could be interpreted as numbers or booleans
name: "12345"  # Without quotes, would be number
flag: "true"   # Without quotes, would be boolean

# Quote strings with special characters
description: "Wave height: 8.5m"
```


## 3. Use Anchors for Reusability

```yaml
# Define common material
steel: &steel
  density: 7850
  E: 200e9

# Reuse
chain_material: *steel
pipe_material: *steel
```


## 4. Add Comments for Clarity

```yaml
environment:
  water_depth: 1500  # meters, site-specific
  wave:
    Hs: 8.5  # 100-year return period
    Tp: 12.0  # Associated peak period
```


## 5. Organize Logically

```yaml
# Group related items
analysis:
  # ... analysis settings

environment:
  # ... environmental parameters

vessel:
  # ... vessel properties

mooring:
  # ... mooring system
```
