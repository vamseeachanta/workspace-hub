#!/bin/bash

# ABOUTME: Bulk install data-validation-reporter to all repositories
# ABOUTME: Installs skill to all workspace-hub repositories

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_HUB:-D:/workspace-hub}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="$SKILL_DIR/install_to_repo.sh"

if [ ! -f "$INSTALLER" ]; then
    echo "Error: Installer script not found: $INSTALLER"
    exit 1
fi

# Make installer executable
chmod +x "$INSTALLER"

echo "========================================"
echo "Bulk Installation: data-validation-reporter"
echo "========================================"
echo "Workspace: $WORKSPACE_ROOT"
echo ""

# Target repositories (excluding digitalmodel - already installed)
REPOS=(
    "worldenergydata"
    "rock-oil-field"
    "assetutilities"
    "assethold"
    "saipem"
    "teamresumes"
    "acma-projects"
)

INSTALLED_COUNT=0
SKIPPED_COUNT=0
FAILED_COUNT=0

for repo in "${REPOS[@]}"; do
    repo_path="$WORKSPACE_ROOT/$repo"

    echo ""
    echo "========================================"
    echo "Repository: $repo"
    echo "========================================"

    if [ ! -d "$repo_path" ]; then
        echo "⊘ Repository not found, skipping"
        ((SKIPPED_COUNT++))
        continue
    fi

    # Check if already installed
    if [ -f "$repo_path/src/validators/data_validator.py" ]; then
        echo "⚠️  Already installed, skipping"
        ((SKIPPED_COUNT++))
        continue
    fi

    # Install
    if "$INSTALLER" "$repo_path"; then
        echo "✅ Installation successful"
        ((INSTALLED_COUNT++))

        # Commit changes
        cd "$repo_path"
        if git rev-parse --git-dir > /dev/null 2>&1; then
            echo "Committing changes..."
            git add src/validators/ config/validation/ examples/validation_examples.py 2>/dev/null || true

            if git diff --staged --quiet; then
                echo "No changes to commit"
            else
                git commit -m "feat(validators): Install data-validation-reporter skill

Install complete data validation and reporting system from workspace-hub skill library.

Components:
- src/validators/data_validator.py: Core validator with quality scoring
- src/validators/__init__.py: Package initialization
- src/validators/README.md: Module documentation
- config/validation/validation_config.yaml: Configuration template
- examples/validation_examples.py: Working examples

Features:
✅ Quality scoring (0-100 scale)
✅ Interactive Plotly reports
✅ Missing data analysis
✅ Type validation
✅ YAML configuration

Source: workspace-hub/skills/data-validation-reporter (v1.0.0)

Usage:
  from src.validators import DataValidator
  validator = DataValidator(config_path='config/validation/validation_config.yaml')
  results = validator.validate_dataframe(df, required_fields=['id'])
  validator.generate_interactive_report(results, Path('report.html'))"

                echo "✅ Changes committed"
            fi
        fi
    else
        echo "✗ Installation failed"
        ((FAILED_COUNT++))
    fi
done

echo ""
echo "========================================"
echo "Bulk Installation Summary"
echo "========================================"
echo "Total repositories: ${#REPOS[@]}"
echo "Successfully installed: $INSTALLED_COUNT"
echo "Skipped (already installed or not found): $SKIPPED_COUNT"
echo "Failed: $FAILED_COUNT"
echo ""

if [ $INSTALLED_COUNT -gt 0 ]; then
    echo "✅ Skill successfully installed to $INSTALLED_COUNT repositories"
    echo ""
    echo "Next steps:"
    echo "  1. Review and customize config files in each repository"
    echo "  2. Test installations: python examples/validation_examples.py"
    echo "  3. Push changes: cd <repo> && git push origin main"
    echo ""
fi
