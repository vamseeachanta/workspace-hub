#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Repository Resolution Tool${NC}"
echo "=================================="
echo ""

# List of diverged repositories
diverged_repos=(
    "aceengineer-website"
    "ai-native-traditional-eng"
    "assethold"
    "assetutilities"
    "energy"
    "pyproject-starter"
    "rock-oil-field"
    "saipem"
)

# Arrays to track results
branches_needing_attention=()
push_results=()
cleanup_results=()

echo -e "${YELLOW}Processing ${#diverged_repos[@]} diverged repositories...${NC}"
echo ""

# Process each diverged repository
for repo in "${diverged_repos[@]}"; do
    echo -e "${BLUE}📦 Processing: $repo${NC}"
    
    if [ -d "$repo" ]; then
        cd "$repo"
        
        # 1. Push local commits to remote
        echo "  → Pushing local commits to remote..."
        current_branch=$(git branch --show-current)
        
        if git push origin "$current_branch" 2>/dev/null; then
            push_results+=("$repo: ✅ Pushed successfully")
            echo -e "  ${GREEN}✓ Pushed local commits${NC}"
        else
            # Try force push if regular push fails (in case of diverged history)
            echo "  → Regular push failed, attempting to pull and merge..."
            git pull origin "$current_branch" --no-edit 2>/dev/null
            if git push origin "$current_branch" 2>/dev/null; then
                push_results+=("$repo: ✅ Merged and pushed")
                echo -e "  ${GREEN}✓ Merged and pushed successfully${NC}"
            else
                push_results+=("$repo: ❌ Failed to push")
                echo -e "  ${RED}✗ Failed to push (may need manual resolution)${NC}"
            fi
        fi
        
        # 2. Check for branches other than main
        echo "  → Checking for non-main branches..."
        all_branches=$(git branch -a | grep -v 'HEAD\|main\|master' | sed 's/^[* ]*//' | sed 's/remotes\/origin\///' | sort -u)
        
        if [ ! -z "$all_branches" ]; then
            echo -e "  ${YELLOW}⚠ Found non-main branches:${NC}"
            echo "$all_branches" | while read branch; do
                echo "    - $branch"
            done
            
            # Store branches that need attention
            branches_needing_attention+=("$repo: $(echo $all_branches | tr '\n' ', ')")
            
            # Try to merge and delete local branches that are already merged
            local_branches=$(git branch | grep -v 'main\|master' | sed 's/^[* ]*//')
            if [ ! -z "$local_branches" ]; then
                echo "  → Cleaning up merged branches..."
                echo "$local_branches" | while read branch; do
                    # Check if branch is merged into main
                    if git branch --merged main | grep -q "$branch"; then
                        git branch -d "$branch" 2>/dev/null && \
                            echo -e "    ${GREEN}✓ Deleted merged branch: $branch${NC}" || \
                            echo -e "    ${YELLOW}⚠ Could not delete: $branch${NC}"
                        cleanup_results+=("$repo/$branch: Deleted (merged)")
                    else
                        echo -e "    ${YELLOW}⚠ Branch '$branch' has unmerged changes${NC}"
                        cleanup_results+=("$repo/$branch: Kept (unmerged)")
                    fi
                done
            fi
            
            # Clean up remote tracking branches
            echo "  → Pruning remote branches..."
            git remote prune origin 2>/dev/null
            
        else
            echo -e "  ${GREEN}✓ Only main/master branch exists${NC}"
        fi
        
        cd ..
    else
        echo -e "  ${RED}✗ Repository not found${NC}"
    fi
    
    echo ""
done

# Also check all other repositories for branches
echo -e "${BLUE}🔍 Checking all repositories for non-main branches...${NC}"
echo ""

all_repos=$(find . -type d -name ".git" 2>/dev/null | sed 's/\/.git$//' | sed 's/^\.\///' | sort)

for repo in $all_repos; do
    # Skip if already processed
    if [[ " ${diverged_repos[@]} " =~ " ${repo} " ]]; then
        continue
    fi
    
    if [ -d "$repo/.git" ]; then
        cd "$repo"
        branches=$(git branch -a 2>/dev/null | grep -v 'HEAD\|main\|master' | sed 's/^[* ]*//' | sed 's/remotes\/origin\///' | sort -u)
        
        if [ ! -z "$branches" ]; then
            echo -e "${YELLOW}📌 $repo has non-main branches:${NC}"
            echo "$branches" | while read branch; do
                echo "    - $branch"
            done
            branches_needing_attention+=("$repo: $(echo $branches | tr '\n' ', ')")
            echo ""
        fi
        cd ..
    fi
done

# Summary Report
echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}📊 Resolution Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

echo -e "${GREEN}Push Results:${NC}"
for result in "${push_results[@]}"; do
    echo "  $result"
done

echo ""
if [ ${#branches_needing_attention[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Repositories with non-main branches (need attention):${NC}"
    for branch_info in "${branches_needing_attention[@]}"; do
        echo "  $branch_info"
    done
else
    echo -e "${GREEN}✅ All repositories only have main/master branches${NC}"
fi

echo ""
if [ ${#cleanup_results[@]} -gt 0 ]; then
    echo -e "${BLUE}Branch Cleanup Results:${NC}"
    for result in "${cleanup_results[@]}"; do
        echo "  $result"
    done
fi

echo ""
echo -e "${GREEN}✅ Resolution process completed!${NC}"