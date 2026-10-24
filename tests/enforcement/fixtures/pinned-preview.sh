#!/bin/sh
set -eu
mode=preview
target=local
if [ "$mode" = apply ]; then
  printf '%s\n' "$target"
fi
printf '%s\n' "$mode"
# no external effects
exit 0
