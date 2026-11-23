---
name: openfoam-19-blockmeshdict
description: 'Sub-skill of openfoam: 1.9 blockMeshDict (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1.9 blockMeshDict (+1)

## 1.9 blockMeshDict


```cpp
scale   1;
vertices
(
    (0 0 0)       // 0
    (1 0 0)       // 1
    (1 1 0)       // 2
    (0 1 0)       // 3
    (0 0 0.1)     // 4
    (1 0 0.1)     // 5
    (1 1 0.1)     // 6
    (0 1 0.1)     // 7
);
blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);
boundary
(
    movingWall { type wall; faces ((3 7 6 2)); }
    fixedWalls { type wall; faces ((0 4 7 3) (1 2 6 5) (0 1 5 4)); }
    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }
);
```


## 1.10 decomposeParDict


```cpp
numberOfSubdomains 4;
method          scotch;         // automatic graph-based partitioning
```

Methods: `scotch` (automatic, recommended), `simple`/`hierarchical` (geometric, need `n (nx ny nz)`), `metis` (external lib).

---
