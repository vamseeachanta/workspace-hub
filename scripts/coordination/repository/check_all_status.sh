#!/bin/bash
for dir in */; do
  if [ -d "${dir}.git" ]; then
    repo="${dir%/}"
    echo "=== $repo ==="
    cd "$dir"
    git status -sb
    cd ..
  fi
done
