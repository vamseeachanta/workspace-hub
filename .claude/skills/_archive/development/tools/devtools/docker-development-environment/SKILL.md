---
name: devtools-docker-development-environment
description: 'Sub-skill of devtools: Docker Development Environment (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Docker Development Environment (+2)

## Docker Development Environment

```bash
# See docker for complete patterns

# Development Dockerfile with caching
cat > Dockerfile << 'EOF'
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

# Cache dependencies
COPY package*.json ./
RUN npm ci

# Build application
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "dist/server.js"]
EOF

# Docker Compose for local development
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  app:
    build:
      context: .
      target: builder
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    command: npm run dev

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
EOF

# Common commands
docker compose up -d
docker compose logs -f app
docker compose exec app sh
docker compose down -v
```


## CLI Productivity Setup

```bash
# See cli-productivity for complete patterns

# Essential aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias g='git'
alias d='docker'
alias dc='docker compose'
alias k='kubectl'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -20'
alias gd='git diff'
alias gb='git branch'
alias gco='git checkout'

# FZF integration
export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --exclude .git'

# Fuzzy file edit
fe() {
    local file=$(fzf --preview 'bat --color=always {}')
    [[ -n "$file" ]] && ${EDITOR:-vim} "$file"
}

# Fuzzy git branch checkout
fco() {
    local branch=$(git branch -a | fzf | sed 's/remotes\/origin\///' | xargs)
    [[ -n "$branch" ]] && git checkout "$branch"
}

# Fuzzy kill process
fkill() {
    local pid=$(ps aux | fzf | awk '{print $2}')
    [[ -n "$pid" ]] && kill -9 "$pid"
}

# Directory navigation with z
eval "$(zoxide init bash)"
```


## VS Code Configuration

```jsonc
// See vscode-extensions for complete patterns

// settings.json
{
  // Editor
  "editor.fontSize": 14,
  "editor.fontFamily": "'JetBrains Mono', 'Fira Code', monospace",
  "editor.fontLigatures": true,
  "editor.lineNumbers": "relative",
  "editor.minimap.enabled": false,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",

  // Files
  "files.autoSave": "onFocusChange",
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,

  // Terminal
  "terminal.integrated.fontSize": 13,
  "terminal.integrated.defaultProfile.osx": "zsh",

  // Git
  "git.autofetch": true,
  "git.confirmSync": false,

  // Language-specific
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript][typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

```jsonc
// keybindings.json
[
  { "key": "cmd+k cmd+e", "command": "workbench.view.explorer" },
  { "key": "cmd+k cmd+g", "command": "workbench.view.scm" },
  { "key": "cmd+k cmd+t", "command": "workbench.action.terminal.toggleTerminal" },
  { "key": "cmd+shift+d", "command": "editor.action.copyLinesDownAction" },
  { "key": "cmd+shift+k", "command": "editor.action.deleteLines" }
]
```
