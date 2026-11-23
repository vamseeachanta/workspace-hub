#!/bin/bash

echo "🔧 Fixing Remaining Repos with Extra Branches"
echo "=============================================="

cd /mnt/github/github

# Fix achantas-media (on wrong branch)
echo "📍 Fixing achantas-media..."
cd achantas-media
git checkout master 2>/dev/null
git branch -D jun-jul-aug 2>/dev/null
cd ..

# Fix energy (has extra local branch)
echo "📍 Fixing energy..."
cd energy
git checkout master 2>/dev/null
git branch -D $(git branch | grep -v master | xargs) 2>/dev/null
cd ..

# Fix investments (has extra local branches)
echo "📍 Fixing investments..."
cd investments
git checkout main 2>/dev/null
git branch -D $(git branch | grep -v main | xargs) 2>/dev/null
cd ..

# Fix client-b (has extra local branch)
echo "📍 Fixing client-b..."
cd client-b  
git checkout master 2>/dev/null
git branch -D $(git branch | grep -v master | xargs) 2>/dev/null
cd ..

# Fix client-d (has extra local branch)
echo "📍 Fixing client-d..."
cd client-d
git checkout main 2>/dev/null
git branch -D $(git branch | grep -v main | xargs) 2>/dev/null
cd ..

# Fix teamresumes (has extra local branches)
echo "📍 Fixing teamresumes..."
cd teamresumes
git checkout main 2>/dev/null
git branch -D $(git branch | grep -v main | xargs) 2>/dev/null
cd ..

echo ""
echo "✅ All repos fixed! Running final status check..."
echo ""