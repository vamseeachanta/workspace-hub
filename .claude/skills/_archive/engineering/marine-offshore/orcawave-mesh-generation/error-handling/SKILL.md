---
name: orcawave-mesh-generation-error-handling
description: 'Sub-skill of orcawave-mesh-generation: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


```python
# Handle non-watertight geometry
try:
    mesh = generator.generate_mesh("geometry/hull.stl")
except MeshNotWatertightError as e:
    print(f"Geometry not watertight: {e}")
    # Attempt auto-heal
    mesh = generator.generate_mesh(
        "geometry/hull.stl",
        auto_heal=True,

*See sub-skills for full details.*
