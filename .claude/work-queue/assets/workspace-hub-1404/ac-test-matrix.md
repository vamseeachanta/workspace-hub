# WRK-1404 Acceptance Criteria Test Matrix

| # | Acceptance Criteria | Test | Result |
|---|---|---|---|
| 1 | rearrange-data/ emptied and removed | `rmdir` succeeds, dir absent | PASS |
| 2 | Personal files consolidated in admin/ | 6 subdirs + 5 files present | PASS |
| 3 | Books moved to books/ | 9 PDFs present in books/ | PASS |
| 4 | Duplicates removed | 1 OrcaFlexModelGen, 1 Selfish Gene | PASS |
| 5 | Misplaced folders archived | 3 _archive- prefixed dirs exist | PASS |
| 6 | No broken symlinks | find -xtype l returns 0 | PASS |
