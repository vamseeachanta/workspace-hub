---
name: pyproject-toml-pytest
description: 'Sub-skill of pyproject-toml: pytest (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# pytest (+2)

## pytest


```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = [
    "-v",                    # Verbose
    "--tb=short",           # Short traceback
    "-ra",                  # Show extra summary
    "--strict-markers",     # Error on unknown markers
    "--cov=src",           # Coverage

*See sub-skills for full details.*

## ruff (Modern Linter)


```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
```

## mypy (Type Checker)


```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true

[[tool.mypy.overrides]]
module = ["pandas.*", "numpy.*"]
ignore_missing_imports = true
```
