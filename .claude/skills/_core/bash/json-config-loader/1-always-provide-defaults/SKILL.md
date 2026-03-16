---
name: json-config-loader-1-always-provide-defaults
description: 'Sub-skill of json-config-loader: 1. Always Provide Defaults (+4).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Always Provide Defaults (+4)

## 1. Always Provide Defaults

```bash
value=$(config_get "key" "default_value")
```


## 2. Validate Early

```bash
config_require "api_key" "database_url" || exit 1
```


## 3. Use Environment Overrides for Secrets

```bash
# Don't store secrets in files
API_KEY="${API_KEY:-$(config_get 'api_key')}"
```


## 4. Validate JSON with jq

```bash
if ! jq empty "$file" 2>/dev/null; then
    echo "Invalid JSON" >&2
    exit 1
fi
```


## 5. Handle Missing Files Gracefully

```bash
if [[ -f "$config_file" ]]; then
    load_config "$config_file"
else
    echo "Warning: Config not found, using defaults" >&2
fi
```
