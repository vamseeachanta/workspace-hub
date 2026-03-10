#!/usr/bin/env bash
echo "STDIN:" >&2
cat >&2
echo "ENV:" >&2
env | grep PRE_COMMIT >&2
