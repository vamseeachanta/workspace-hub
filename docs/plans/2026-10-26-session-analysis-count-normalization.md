# Agent-candidate count normalization

## Plan-lite

The scope will remain agent-candidate count whitespace normalization. The count
pipeline will remove all whitespace with `tr -d '[:space:]'`, matching adjacent
pipelines and preventing carriage returns or embedded whitespace from reaching
arithmetic inputs.

The changed paths will be `scripts/analysis/session-analysis.sh`,
`tests/session-analysis/test_count_normalization.py` and this plan. The regression
module will run a copied script with synthetic records and restricted command
stubs; four records will yield four script candidates and two agent candidates.

Regression checks will cover embedded whitespace, CRLF counts, ordinary counts,
empty input and rejection of unexpected Git operations. Validation will run the
five pytest cases, Bash syntax checking, model-ID sourcing, whitespace checking,
engineering-register checking and a secret scan. The existing Bats suite will
run where its executable is available.

Stubbed CRLF coverage will establish normalization of those bytes, without
establishing native-platform behavior. The jq stub will cover only the exercised
queries with string-valued tool sequences.
