# AC Test Matrix — WRK-1384

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC-1 | Complete inventory table | All folders enumerated in resource-intelligence.yaml | PASS |
| AC-2 | Each item classified | 7 categories with RELOCATE/KEEP/DELETE/REVIEW | PASS |
| AC-3 | Relocation script generated | relocate-to-ace.sh with rsync + verification | PASS |
| AC-4 | No data loss | rsync copy (non-destructive), originals preserved | PASS |
| AC-5 | Dry run validation | All source paths exist, destinations created | PASS |
| AC-6 | Disk space check | 2.7TB available, ~290GB needed | PASS |
| AC-7 | Post-copy verification | All 15 project folders + 5 categories confirmed on /mnt/ace/ | PASS |
