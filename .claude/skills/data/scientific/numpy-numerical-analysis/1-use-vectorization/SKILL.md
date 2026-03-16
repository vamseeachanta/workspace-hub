---
name: numpy-numerical-analysis-1-use-vectorization
description: 'Sub-skill of numpy-numerical-analysis: 1. Use Vectorization (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Use Vectorization (+3)

## 1. Use Vectorization


```python
# ❌ Bad: Loop
result = np.zeros(len(x))
for i in range(len(x)):
    result[i] = x[i]**2 + y[i]**2

# ✅ Good: Vectorized
result = x**2 + y**2
```


## 2. Avoid Unnecessary Copies


```python
# ❌ Bad: Creates copies
a = np.array([1, 2, 3])
b = a
b[0] = 10  # Modifies original

# ✅ Good: Explicit copy when needed
a = np.array([1, 2, 3])
b = a.copy()
b[0] = 10  # Original unchanged
```


## 3. Use In-Place Operations


```python
# ❌ Bad: Creates new array
a = a + 1

# ✅ Good: In-place
a += 1
```


## 4. Choose Appropriate Data Types


```python
# Use float32 for large arrays when precision allows
large_array = np.zeros((10000, 10000), dtype=np.float32)  # 400 MB instead of 800 MB
```
