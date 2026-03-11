# Test Results WRK-1018

| Test | Result |
|------|--------|
| scan --days 30 returns 6 unqueued items (captured:false) | PASS |
| --candidates-file appends well-formed MD block | PASS |
| malformed YAML file produces WARNING on stderr, continues | PASS |
| captured:true items with non-WRK capture_ref not surfaced | PASS |
| empty result exits 0 with summary message | PASS |
