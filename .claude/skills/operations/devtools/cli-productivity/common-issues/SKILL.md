---
name: cli-productivity-common-issues
description: 'Sub-skill of cli-productivity: Common Issues.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**fzf not finding files:**
```bash
# Check FZF_DEFAULT_COMMAND
echo $FZF_DEFAULT_COMMAND

# Test fd directly
fd --type f

# Check for hidden files
fd -H
```

**Colors not working:**
```bash
# Check terminal capabilities
echo $TERM

# Force color output
export CLICOLOR_FORCE=1
```

**Slow shell startup:**
```bash
# Profile startup time
time bash -i -c exit

# Identify slow sources
for f in ~/.bashrc ~/.bash_profile; do
    echo "--- $f ---"
    time source "$f"
done
```

**zoxide not working:**
```bash
# Check initialization
type z

# Rebuild database
zoxide import --from=z
```
