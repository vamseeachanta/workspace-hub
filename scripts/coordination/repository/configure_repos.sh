#!/bin/bash

# ABOUTME: Helper script to configure repository URLs in config/repos.conf
# ABOUTME: Provides interactive URL configuration with validation and bulk operations

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$WORKSPACE_ROOT/config/repos.conf"
GITIGNORE_FILE="$WORKSPACE_ROOT/.gitignore"

# Function to show header
show_header() {
    clear
    echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║           Repository URL Configuration Helper                 ║${NC}"
    echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to parse repositories from config
parse_config() {
    local -n repo_names=$1
    local -n repo_urls=$2
    local -n repo_categories=$3

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue

        # Extract repo name and URL
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local name="${BASH_REMATCH[1]}"
            local url="${BASH_REMATCH[2]}"
            repo_names+=("$name")
            repo_urls["$name"]="$url"
        fi
    done < "$CONFIG_FILE"

    # Parse categories from .gitignore
    while IFS= read -r line; do
        if [[ "$line" =~ ^([a-zA-Z0-9_-]+)/[[:space:]]*#[[:space:]]*(Personal|Work|Both|Personal,\ Work|Work,\ Personal)$ ]]; then
            local name="${BASH_REMATCH[1]}"
            local category="${BASH_REMATCH[2]}"
            repo_categories["$name"]="$category"
        fi
    done < "$GITIGNORE_FILE"
}

# Function to validate GitHub URL
validate_github_url() {
    local url="$1"

    # Allow empty URLs
    [[ -z "$url" ]] && return 0

    # Check if it's a valid GitHub URL format
    if [[ "$url" =~ ^git@github\.com:[^/]+/[^/]+\.git$ ]] || \
       [[ "$url" =~ ^https://github\.com/[^/]+/[^/]+(\.git)?$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to show repository list
show_repo_list() {
    local -n names=$1
    local -n urls=$2
    local -n categories=$3

    echo -e "${BOLD}Repository Configuration Status:${NC}"
    echo ""
    printf "%-4s %-30s %-12s %-10s\n" "No." "Repository" "Category" "Status"
    echo "────────────────────────────────────────────────────────────────"

    local i=1
    for repo in "${names[@]}"; do
        local category="${categories[$repo]:-Uncategorized}"
        local url="${urls[$repo]}"
        local status=""

        if [[ -z "$url" ]]; then
            status="${RED}Not configured${NC}"
        elif validate_github_url "$url"; then
            status="${GREEN}Configured${NC}"
        else
            status="${YELLOW}Invalid URL${NC}"
        fi

        printf "%-4s ${CYAN}%-30s${NC} %-12s %b\n" "$i" "$repo" "$category" "$status"
        ((i++))
    done
    echo ""
}

# Function to configure single repository
configure_single_repo() {
    local repo_name="$1"
    local current_url="$2"

    echo -e "${BOLD}Configuring: ${CYAN}$repo_name${NC}"
    echo ""

    if [[ -n "$current_url" ]]; then
        echo -e "Current URL: ${YELLOW}$current_url${NC}"
        echo ""
    fi

    echo "Enter GitHub URL (or press ENTER to skip):"
    echo "Formats:"
    echo "  - SSH: git@github.com:username/repo.git"
    echo "  - HTTPS: https://github.com/username/repo.git"
    echo ""

    read -e -p "URL: " new_url

    # Trim whitespace
    new_url=$(echo "$new_url" | xargs)

    # If empty, keep current URL
    if [[ -z "$new_url" ]]; then
        echo -e "${YELLOW}Skipped${NC}"
        return 0
    fi

    # Validate URL
    if ! validate_github_url "$new_url"; then
        echo -e "${RED}Invalid GitHub URL format${NC}"
        echo -e "${YELLOW}URL not updated${NC}"
        return 1
    fi

    # Update config file
    sed -i "s|^${repo_name}=.*$|${repo_name}=${new_url}|" "$CONFIG_FILE"
    echo -e "${GREEN}✓ URL updated${NC}"

    return 0
}

# Function to configure by category
configure_by_category() {
    local category="$1"
    local -n names=$2
    local -n urls=$3
    local -n categories=$4

    echo -e "${BOLD}Configuring ${category} repositories${NC}"
    echo ""

    local count=0
    for repo in "${names[@]}"; do
        local repo_category="${categories[$repo]}"

        # Check if repo matches category
        if [[ "$repo_category" == "$category" ]] || \
           [[ "$category" == "Both" && "$repo_category" =~ (Personal,\ Work|Work,\ Personal) ]]; then

            echo ""
            configure_single_repo "$repo" "${urls[$repo]}"
            ((count++))
            echo ""

            # Ask to continue after each repo
            read -p "Continue to next repository? (y/n): " continue
            [[ "$continue" != "y" ]] && break
        fi
    done

    echo ""
    echo -e "${GREEN}Configured $count repositories${NC}"
}

# Function to auto-generate URLs from username
auto_generate_urls() {
    local username="$1"
    local use_ssh="${2:-true}"
    local -n names=$3
    local -n categories=$4

    echo -e "${BOLD}Auto-generating URLs for username: ${CYAN}$username${NC}"
    echo ""

    local count=0
    for repo in "${names[@]}"; do
        # Skip uncategorized repos
        local category="${categories[$repo]}"
        [[ "$category" == "Uncategorized" ]] && continue

        # Generate URL
        local url=""
        if [[ "$use_ssh" == "true" ]]; then
            url="git@github.com:${username}/${repo}.git"
        else
            url="https://github.com/${username}/${repo}.git"
        fi

        # Update config
        sed -i "s|^${repo}=.*$|${repo}=${url}|" "$CONFIG_FILE"
        echo -e "${GREEN}✓${NC} $repo → $url"
        ((count++))
    done

    echo ""
    echo -e "${GREEN}Generated URLs for $count repositories${NC}"
}

# Function to show statistics
show_statistics() {
    local -n names=$1
    local -n urls=$2

    local total=${#names[@]}
    local configured=0
    local not_configured=0

    for repo in "${names[@]}"; do
        local url="${urls[$repo]}"
        if [[ -n "$url" ]]; then
            ((configured++))
        else
            ((not_configured++))
        fi
    done

    echo -e "${BOLD}Configuration Statistics:${NC}"
    echo ""
    echo -e "  Total repositories:       ${CYAN}$total${NC}"
    echo -e "  Configured:               ${GREEN}$configured${NC}"
    echo -e "  Not configured:           ${YELLOW}$not_configured${NC}"
    echo -e "  Completion:               $(( configured * 100 / total ))%"
    echo ""
}

# Main menu
show_main_menu() {
    declare -a REPO_NAMES=()
    declare -A REPO_URLS=()
    declare -A REPO_CATEGORIES=()

    # Parse configuration
    parse_config REPO_NAMES REPO_URLS REPO_CATEGORIES

    while true; do
        show_header
        show_statistics REPO_NAMES REPO_URLS
        show_repo_list REPO_NAMES REPO_URLS REPO_CATEGORIES

        echo -e "${BOLD}Configuration Options:${NC}"
        echo ""
        echo -e "  ${CYAN}1)${NC} Configure individual repository"
        echo -e "  ${CYAN}2)${NC} Configure Work repositories"
        echo -e "  ${CYAN}3)${NC} Configure Personal repositories"
        echo -e "  ${CYAN}4)${NC} Configure Both (Work & Personal) repositories"
        echo -e "  ${CYAN}5)${NC} Auto-generate URLs from GitHub username"
        echo -e "  ${CYAN}6)${NC} View current configuration"
        echo -e "  ${RED}0)${NC} Exit"
        echo ""

        read -p "Select option: " choice

        case "$choice" in
            1)
                echo ""
                read -p "Enter repository number: " repo_num

                if [[ "$repo_num" -ge 1 && "$repo_num" -le ${#REPO_NAMES[@]} ]]; then
                    local repo="${REPO_NAMES[$((repo_num-1))]}"
                    echo ""
                    configure_single_repo "$repo" "${REPO_URLS[$repo]}"

                    # Reload configuration
                    REPO_URLS=()
                    parse_config REPO_NAMES REPO_URLS REPO_CATEGORIES
                else
                    echo -e "${RED}Invalid repository number${NC}"
                fi

                echo ""
                read -p "Press ENTER to continue..."
                ;;

            2)
                echo ""
                configure_by_category "Work" REPO_NAMES REPO_URLS REPO_CATEGORIES

                # Reload configuration
                REPO_URLS=()
                parse_config REPO_NAMES REPO_URLS REPO_CATEGORIES

                read -p "Press ENTER to continue..."
                ;;

            3)
                echo ""
                configure_by_category "Personal" REPO_NAMES REPO_URLS REPO_CATEGORIES

                # Reload configuration
                REPO_URLS=()
                parse_config REPO_NAMES REPO_URLS REPO_CATEGORIES

                read -p "Press ENTER to continue..."
                ;;

            4)
                echo ""
                configure_by_category "Both" REPO_NAMES REPO_URLS REPO_CATEGORIES

                # Reload configuration
                REPO_URLS=()
                parse_config REPO_NAMES REPO_URLS REPO_CATEGORIES

                read -p "Press ENTER to continue..."
                ;;

            5)
                echo ""
                read -p "Enter GitHub username: " username
                echo ""
                echo "Choose URL format:"
                echo "  1) SSH (git@github.com:username/repo.git)"
                echo "  2) HTTPS (https://github.com/username/repo.git)"
                read -p "Select format (1/2): " format_choice

                local use_ssh="true"
                [[ "$format_choice" == "2" ]] && use_ssh="false"

                echo ""
                auto_generate_urls "$username" "$use_ssh" REPO_NAMES REPO_CATEGORIES

                # Reload configuration
                REPO_URLS=()
                parse_config REPO_NAMES REPO_URLS REPO_CATEGORIES

                echo ""
                read -p "Press ENTER to continue..."
                ;;

            6)
                echo ""
                cat "$CONFIG_FILE" | less
                ;;

            0)
                echo ""
                echo -e "${GREEN}Configuration saved to: $CONFIG_FILE${NC}"
                echo ""
                exit 0
                ;;

            *)
                echo -e "${RED}Invalid option${NC}"
                sleep 1
                ;;
        esac
    done
}

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}Error: Configuration file not found${NC}"
    echo "Expected: $CONFIG_FILE"
    exit 1
fi

# Check if .gitignore exists
if [[ ! -f "$GITIGNORE_FILE" ]]; then
    echo -e "${RED}Error: .gitignore file not found${NC}"
    echo "Expected: $GITIGNORE_FILE"
    exit 1
fi

# Run main menu
show_main_menu
