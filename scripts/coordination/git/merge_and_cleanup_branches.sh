#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔀 Branch Merge and Cleanup Tool${NC}"
echo "=================================="
echo ""

# Repositories with non-main branches that need attention. This repo->branch map
# carried client repo names (#3098), so it is no longer hardcoded. It is loaded
# from a gitignored per-host file ($BRANCH_CLEANUP_FILE or
# workspace-hub/config/.branch-cleanup.local), one entry per line:
#     <repo>:<space-separated branch list>
# ('#' comments and blank lines ignored). See config/.branch-cleanup.local.example.
# Absent file -> empty map -> the script processes nothing (safe no-op). The
# merge/delete/push logic below is unchanged.
declare -A repos_with_branches=()
_wh_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
_map_file="${BRANCH_CLEANUP_FILE:-$_wh_root/config/.branch-cleanup.local}"
if [[ -f "$_map_file" ]]; then
    while IFS=: read -r _repo _branches; do
        [[ -z "$_repo" || "$_repo" == \#* ]] && continue
        repos_with_branches["$_repo"]="${_branches# }"
    done < "$_map_file"
fi

# Track results
merged_branches=()
deleted_branches=()
manual_attention=()

echo -e "${YELLOW}Processing ${#repos_with_branches[@]} repositories with non-main branches...${NC}"
echo ""

for repo in "${!repos_with_branches[@]}"; do
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📦 Repository: $repo${NC}"
    branches="${repos_with_branches[$repo]}"
    
    if [ -d "$repo/.git" ]; then
        cd "$repo"
        
        # Ensure we're on main branch
        echo "  → Switching to main branch..."
        git checkout main 2>/dev/null || git checkout master 2>/dev/null
        
        # Pull latest main
        echo "  → Updating main branch..."
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
        
        # Process each branch
        for branch in $branches; do
            echo ""
            echo -e "  ${YELLOW}Branch: $branch${NC}"
            
            # Check if branch exists locally
            if git show-ref --verify --quiet "refs/heads/$branch"; then
                echo "    → Local branch exists"
                
                # Check if branch can be merged cleanly
                echo "    → Checking merge compatibility..."
                git checkout "$branch" 2>/dev/null
                
                # Get branch statistics
                commits_ahead=$(git rev-list --count main.."$branch" 2>/dev/null)
                commits_behind=$(git rev-list --count "$branch"..main 2>/dev/null)
                
                echo "    → Branch is $commits_ahead commits ahead, $commits_behind commits behind main"
                
                # Try to merge into main
                git checkout main 2>/dev/null
                
                if [ "$commits_ahead" -eq 0 ]; then
                    echo -e "    ${GREEN}✓ Branch fully merged, can be deleted${NC}"
                    git branch -d "$branch" 2>/dev/null && \
                        deleted_branches+=("$repo/$branch") && \
                        echo -e "    ${GREEN}✓ Deleted branch: $branch${NC}"
                else
                    echo "    → Attempting to merge branch into main..."
                    if git merge "$branch" --no-ff --no-edit 2>/dev/null; then
                        merged_branches+=("$repo/$branch")
                        echo -e "    ${GREEN}✓ Successfully merged $branch into main${NC}"
                        
                        # Push the merge
                        if git push origin main 2>/dev/null; then
                            echo -e "    ${GREEN}✓ Pushed merge to remote${NC}"
                            
                            # Delete the branch locally and remotely
                            git branch -d "$branch" 2>/dev/null && \
                                deleted_branches+=("$repo/$branch (local)") && \
                                echo -e "    ${GREEN}✓ Deleted local branch${NC}"
                            
                            git push origin --delete "$branch" 2>/dev/null && \
                                deleted_branches+=("$repo/$branch (remote)") && \
                                echo -e "    ${GREEN}✓ Deleted remote branch${NC}"
                        else
                            echo -e "    ${YELLOW}⚠ Could not push merge (may need manual push)${NC}"
                            manual_attention+=("$repo/$branch: Merged but needs manual push")
                        fi
                    else
                        # Abort the merge
                        git merge --abort 2>/dev/null
                        echo -e "    ${YELLOW}⚠ Cannot auto-merge (conflicts or diverged)${NC}"
                        manual_attention+=("$repo/$branch: Has $commits_ahead commits - needs manual review")
                    fi
                fi
                
            elif git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
                echo "    → Remote branch exists (no local copy)"
                
                # Check if remote branch is merged
                git fetch origin "$branch" 2>/dev/null
                if git branch -r --merged main | grep -q "origin/$branch"; then
                    echo -e "    ${GREEN}✓ Remote branch fully merged, deleting...${NC}"
                    git push origin --delete "$branch" 2>/dev/null && \
                        deleted_branches+=("$repo/$branch (remote only)") && \
                        echo -e "    ${GREEN}✓ Deleted remote branch${NC}"
                else
                    manual_attention+=("$repo/$branch: Remote branch needs manual review")
                fi
            else
                echo -e "    ${RED}✗ Branch not found (may be already deleted)${NC}"
            fi
        done
        
        # Return to main branch
        git checkout main 2>/dev/null || git checkout master 2>/dev/null
        
        cd ..
    else
        echo -e "  ${RED}✗ Repository not found${NC}"
    fi
done

# Final Summary
echo ""
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Final Summary${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ${#merged_branches[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Successfully Merged Branches:${NC}"
    for branch in "${merged_branches[@]}"; do
        echo "    • $branch"
    done
    echo ""
fi

if [ ${#deleted_branches[@]} -gt 0 ]; then
    echo -e "${GREEN}🗑️  Deleted Branches:${NC}"
    for branch in "${deleted_branches[@]}"; do
        echo "    • $branch"
    done
    echo ""
fi

if [ ${#manual_attention[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Branches Requiring Manual Attention:${NC}"
    for branch in "${manual_attention[@]}"; do
        echo "    • $branch"
    done
    echo ""
    echo -e "${YELLOW}For branches needing manual attention, you can:${NC}"
    echo "  1. Review the changes: git log main..branch-name"
    echo "  2. Merge manually: git merge branch-name"
    echo "  3. Rebase if needed: git rebase main branch-name"
    echo "  4. Force push if certain: git push -f origin branch-name"
else
    echo -e "${GREEN}✅ All branches processed successfully!${NC}"
fi

echo ""
echo -e "${BLUE}📝 Special Note:${NC}"
echo -e "${YELLOW}  • Some repositories may have workflow permission issues${NC}"
echo "    when pushing workflow files. Update GitHub OAuth permissions or use a"
echo "    Personal Access Token with 'workflow' scope."
echo ""
echo -e "${GREEN}✅ Branch cleanup process completed!${NC}"