---
name: cli-productivity-1-jq-json-processing
description: 'Sub-skill of cli-productivity: 1. jq - JSON Processing (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. jq - JSON Processing (+1)

## 1. jq - JSON Processing


**Basic Operations:**
```bash
# Pretty print JSON
echo '{"name":"John","age":30}' | jq '.'

# Extract field
curl -s https://api.github.com/repos/nodejs/node | jq '.stargazers_count'

# Filter arrays
echo '[1,2,3,4,5]' | jq '.[] | select(. > 2)'

# Transform data
echo '{"first":"John","last":"Doe"}' | jq '{fullName: (.first + " " + .last)}'
```

**Common jq Patterns:**
```bash
# Extract multiple fields
jq '{name: .name, stars: .stargazers_count}'

# Array operations
jq '.items | length'                    # Count items
jq '.items | first'                     # First item
jq '.items | last'                      # Last item
jq '.items[0:5]'                        # Slice first 5

# Filtering
jq '.[] | select(.status == "active")'
jq '.[] | select(.count > 100)'
jq '.[] | select(.name | contains("test"))'

# Sorting
jq 'sort_by(.date)'
jq 'sort_by(.date) | reverse'

# Grouping
jq 'group_by(.category)'
jq 'group_by(.category) | map({key: .[0].category, count: length})'

# Mapping
jq '.[] | {id, name}'
jq 'map({id: .id, upper_name: (.name | ascii_upcase)})'
```

**Shell Functions for jq:**
```bash
# Pretty print JSON file
jqp() {
    jq '.' "$1" | bat --language json
}

# Extract field from JSON file
jqf() {
    local file="$1"
    local field="$2"
    jq -r ".$field" "$file"
}

# Count items in JSON array
jqcount() {
    jq 'if type == "array" then length else 1 end' "$1"
}

# Filter JSON by field value
jqfilter() {
    local file="$1"
    local field="$2"
    local value="$3"
    jq --arg val "$value" ".[] | select(.$field == \$val)" "$file"
}
```


## 2. fzf - Fuzzy Finder


**Basic Usage:**
```bash
# Find and edit file
vim $(fzf)

# Find with preview
fzf --preview 'bat --color=always {}'

# Multi-select
fzf --multi

# Filter with query
echo -e "apple\nbanana\norange" | fzf --query "an"
```

**fzf Configuration:**
```bash
# Add to ~/.bashrc or ~/.zshrc

# Default options
export FZF_DEFAULT_OPTS='
    --height 40%
    --layout=reverse
    --border
    --preview-window=right:50%:wrap
    --bind=ctrl-d:preview-page-down
    --bind=ctrl-u:preview-page-up
'

# Use fd for faster file finding
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

# Preview settings
export FZF_CTRL_T_OPTS='--preview "bat --color=always --style=numbers --line-range=:500 {}"'
export FZF_ALT_C_OPTS='--preview "exa --tree --level=2 --color=always {}"'
```

**Powerful fzf Functions:**
```bash
# Fuzzy edit file
fe() {
    local file
    file=$(fzf --preview 'bat --color=always --style=numbers --line-range=:500 {}')
    [[ -n "$file" ]] && ${EDITOR:-vim} "$file"
}

# Fuzzy cd into directory
fcd() {
    local dir
    dir=$(fd --type d --hidden --follow --exclude .git | fzf --preview 'exa --tree --level=2 --color=always {}')
    [[ -n "$dir" ]] && cd "$dir"
}

# Fuzzy kill process
fkill() {
    local pid
    pid=$(ps aux | sed 1d | fzf --multi | awk '{print $2}')
    [[ -n "$pid" ]] && echo "$pid" | xargs kill -9
}

# Fuzzy git checkout branch
fco() {
    local branch
    branch=$(git branch -a --color=always | grep -v '/HEAD' | fzf --ansi | sed 's/^[* ]*//' | sed 's#remotes/origin/##')
    [[ -n "$branch" ]] && git checkout "$branch"
}

# Fuzzy git log
flog() {
    git log --oneline --color=always | fzf --ansi --preview 'git show --color=always {1}' | awk '{print $1}'
}

# Fuzzy history search
fh() {
    local cmd
    cmd=$(history | fzf --tac | sed 's/^[ ]*[0-9]*[ ]*//')
    [[ -n "$cmd" ]] && eval "$cmd"
}

# Fuzzy environment variable
fenv() {
    local var
    var=$(env | fzf | cut -d= -f1)
    [[ -n "$var" ]] && echo "${!var}"
}

# Fuzzy docker container
fdocker() {
    local container
    container=$(docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' | fzf | awk '{print $1}')
    [[ -n "$container" ]] && docker exec -it "$container" sh
}
```
