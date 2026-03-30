---
name: python-scientific-computing-1-use-vectorization
description: 'Sub-skill of python-scientific-computing: 1. Use Vectorization (+4).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Use Vectorization (+4)

## 1. Use Vectorization

```python
# ❌ Slow: Loop
result = []
for x in x_array:
    result.append(np.sin(x) * np.exp(-x))

# ✅ Fast: Vectorized
result = np.sin(x_array) * np.exp(-x_array)
```


## 2. Choose Right Data Type

```python
# Use appropriate precision
float32_array = np.array([1, 2, 3], dtype=np.float32)  # Less memory
float64_array = np.array([1, 2, 3], dtype=np.float64)  # More precision

# Use integer when possible
int_array = np.array([1, 2, 3], dtype=np.int32)
```


## 3. Avoid Matrix Inverse When Possible

```python
# ❌ Slower and less stable
x = np.linalg.inv(A) @ b

# ✅ Faster and more stable
x = np.linalg.solve(A, b)
```


## 4. Use Broadcasting

```python
# Broadcasting allows operations on arrays of different shapes
A = np.array([[1, 2, 3],
              [4, 5, 6]])  # Shape (2, 3)

b = np.array([10, 20, 30])  # Shape (3,)

# Broadcast adds b to each row of A
C = A + b  # Shape (2, 3)
```


## 5. Check Numerical Stability

```python
# Check condition number
cond = np.linalg.cond(A)
if cond > 1e10:
    print("Warning: Matrix is ill-conditioned")

# Use appropriate solver for symmetric positive definite
if np.allclose(A, A.T) and np.all(np.linalg.eigvals(A) > 0):
    x = np.linalg.solve(A, b)  # Can use Cholesky internally
```
