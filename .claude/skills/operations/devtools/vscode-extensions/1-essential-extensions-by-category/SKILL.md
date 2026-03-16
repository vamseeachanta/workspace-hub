---
name: vscode-extensions-1-essential-extensions-by-category
description: 'Sub-skill of vscode-extensions: 1. Essential Extensions by Category.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Essential Extensions by Category

## 1. Essential Extensions by Category


```bash
# Create extensions installation script
cat > install-extensions.sh << 'EOF'
#!/bin/bash
# ABOUTME: Install curated VS Code extensions by category
# ABOUTME: Run with category argument: ./install-extensions.sh python

install_base() {
    # Core productivity
    code --install-extension esbenp.prettier-vscode
    code --install-extension dbaeumer.vscode-eslint
    code --install-extension editorconfig.editorconfig
    code --install-extension streetsidesoftware.code-spell-checker
    code --install-extension usernamehw.errorlens
    code --install-extension gruntfuggly.todo-tree
    code --install-extension aaron-bond.better-comments
    code --install-extension christian-kohler.path-intellisense

    # Git
    code --install-extension eamodio.gitlens
    code --install-extension mhutchie.git-graph

    # Theme and icons
    code --install-extension pkief.material-icon-theme
    code --install-extension github.github-vscode-theme
}

install_python() {
    code --install-extension ms-python.python
    code --install-extension ms-python.vscode-pylance
    code --install-extension ms-python.black-formatter
    code --install-extension charliermarsh.ruff
    code --install-extension ms-python.debugpy
    code --install-extension njpwerner.autodocstring
    code --install-extension littlefoxteam.vscode-python-test-adapter
}

install_javascript() {
    code --install-extension esbenp.prettier-vscode
    code --install-extension dbaeumer.vscode-eslint
    code --install-extension dsznajder.es7-react-js-snippets
    code --install-extension bradlc.vscode-tailwindcss
    code --install-extension prisma.prisma
    code --install-extension wallabyjs.quokka-vscode
}

install_typescript() {
    install_javascript
    code --install-extension ms-vscode.vscode-typescript-next
    code --install-extension pmneo.tsimporter
    code --install-extension stringham.move-ts
}

install_rust() {
    code --install-extension rust-lang.rust-analyzer
    code --install-extension serayuzgur.crates
    code --install-extension tamasfe.even-better-toml
    code --install-extension vadimcn.vscode-lldb
}

install_go() {
    code --install-extension golang.go
    code --install-extension zxh404.vscode-proto3
}

install_docker() {
    code --install-extension ms-azuretools.vscode-docker
    code --install-extension ms-vscode-remote.remote-containers
    code --install-extension ms-kubernetes-tools.vscode-kubernetes-tools
    code --install-extension redhat.vscode-yaml
}

install_web() {
    code --install-extension ritwickdey.liveserver
    code --install-extension formulahendry.auto-rename-tag
    code --install-extension pranaygp.vscode-css-peek
    code --install-extension zignd.html-css-class-completion
    code --install-extension ecmel.vscode-html-css
}

install_data() {
    code --install-extension ms-toolsai.jupyter
    code --install-extension mechatroner.rainbow-csv
    code --install-extension randomfractalsinc.vscode-data-preview
    code --install-extension mtxr.sqltools
    code --install-extension cweijan.vscode-database-client2
}

install_remote() {
    code --install-extension ms-vscode-remote.remote-ssh
    code --install-extension ms-vscode-remote.remote-containers
    code --install-extension ms-vscode-remote.remote-wsl
    code --install-extension ms-vscode.remote-explorer
}

install_ai() {
    code --install-extension github.copilot
    code --install-extension github.copilot-chat
    code --install-extension continue.continue
}

# Main
case "$1" in
    base) install_base ;;
    python) install_base && install_python ;;
    javascript|js) install_base && install_javascript ;;
    typescript|ts) install_base && install_typescript ;;
    rust) install_base && install_rust ;;
    go) install_base && install_go ;;
    docker) install_base && install_docker ;;
    web) install_base && install_web ;;
    data) install_base && install_data ;;
    remote) install_remote ;;
    ai) install_ai ;;
    all) install_base && install_python && install_typescript && install_docker && install_remote ;;
    *)
        echo "Usage: $0 {base|python|javascript|typescript|rust|go|docker|web|data|remote|ai|all}"
        exit 1
        ;;
esac

echo "Extensions installed successfully!"
EOF
chmod +x install-extensions.sh
```
