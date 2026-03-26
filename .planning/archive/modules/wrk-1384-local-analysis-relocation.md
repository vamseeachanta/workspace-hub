confirmed_by: user
confirmed_at: 2026-03-24T23:30:00Z
decision: passed

# WRK-1384: Review local-analysis folders for relocation to knowledge center

## Summary

Inventory all folders/files in `/mnt/remote/ace-linux-2/local-analysis` (excluding workspace-hub), classify by type, and produce a relocation plan mapping items to `/mnt/ace/` knowledge center.

## Acceptance Criteria

1. Complete inventory table with folder name, size, category, and recommended action
2. Each item classified as: RELOCATE (with destination), KEEP-IN-PLACE, DELETE, or REVIEW-MANUALLY
3. Relocation script generated for approved moves
4. No data loss — moves use `rsync` with verification, not destructive `mv`

## Relocation Plan

### Category 1: Engineering Projects → `/mnt/ace/client_projects/`

| Source | Size | Destination |
|--------|------|-------------|
| 0111 RII | 2.8G | client_projects/0111-RII/ |
| 0112 CN Adapter | 6.3M | client_projects/0112-CN-Adapter/ |
| 0116 Thinwall Pipe FEA | 15G | client_projects/0116-Thinwall-Pipe-FEA/ |
| 0119 Programming | 26M | client_projects/0119-Programming/ |
| 0127 Mooring | 9.8M | client_projects/0127-Mooring/ |
| 0132 | 428M | client_projects/0132/ |
| 0154 TVO | 24G | client_projects/0154-TVO/ |
| 0159 Anchor FEA | 276M | client_projects/0159-Anchor-FEA/ |
| 0162-001 | 455M | client_projects/0162-001/ |
| 0163-FDAS | 4.9G | client_projects/0163-FDAS/ |
| 0182 | 8.3G | client_projects/0182/ |
| 0190 | 66M | client_projects/0190/ |
| 0198 | 49G | client_projects/0198/ |
| Sewol | 128G | client_projects/Sewol/ |
| 0000 Completed | 13G | client_projects/0000-Completed/ |

### Category 2: Conference Literature → `/mnt/ace/docs/conferences/`

| Source | Size | Destination |
|--------|------|-------------|
| 0000 Conferences | 28G | docs/conferences/ |

### Category 3: Business/Admin → `/mnt/ace/aceengineer-admin/`

| Source | Size | Destination |
|--------|------|-------------|
| 0000 GDrive | 6.9G | aceengineer-admin/gdrive-export/ |
| 0000 www | 1.4G | aceengineer-admin/www-archive/ |

### Category 4: Data/Research → `/mnt/ace/data/`

| Source | Size | Destination |
|--------|------|-------------|
| OSI | 2.5G | data/osi-datasets/ |
| OrcFxAPIConfig.py | 1.7K | digitalmodel/ (config reference) |

### Category 5: Reference → `/mnt/ace/docs/`

| Source | Size | Destination |
|--------|------|-------------|
| repo | 540M | docs/engineering-drawings/ |
| github_ref | 1.7M | docs/github-references/ |

### Category 6: DELETE (no knowledge value)

| Source | Size | Reason |
|--------|------|--------|
| $RECYCLE.BIN | 3.6M | Windows system artifact |
| System Volume Information | 1008K | Windows system artifact |
| DumpStack.log.tmp | 8K | Windows dump log |
| msdia80.dll | 905K | Visual Studio artifact |
| acma_wood.ps1 | 1K | Orphaned script |
| Dropbox | 8K | Empty directory |
| OneDrive | symlink | Broken symlink |
| Son_Server2 | 4.5M | Legacy server files |

### Category 7: REVIEW MANUALLY

| Source | Size | Reason |
|--------|------|--------|
| Temp | 77G | Mixed content - needs manual triage per subfolder |
| InstallationFiles | 18G | Software installers - keep only if not downloadable |
| itunes | 16G | Personal media - move to personal storage |
| 0000 BigData | 415M | Training materials - assess retention value |
| DataStax-Community Edition | 100M | Cassandra - assess retention value |
| HadoopCourse | 37M | Training - assess retention value |
| solidworks | 42M | CAD software - assess if needed |
| 0000 Tecplot | 5.4M | Tecplot config - assess if needed |

## Pseudocode

1. Generate inventory manifest (folder, size, file count, last-modified)
2. User reviews and approves/modifies relocation table above
3. Generate rsync script with:
   - `rsync -avh --progress` for each approved move
   - Verification checksums post-copy
   - Log file for audit trail
4. User runs rsync script (not automated - user controls execution)
5. After verification, user decides whether to delete originals

## Test Plan

1. Verify all source paths exist and are accessible
2. Verify all destination parent directories exist in /mnt/ace/
3. Dry-run rsync (`--dry-run`) to confirm no conflicts
4. Post-copy: compare file counts and sizes between source and destination

## Notes

- Total relocatable data: ~290GB (engineering + conferences + admin + data + reference)
- Manual review needed: ~112GB (Temp + InstallationFiles + itunes + training)
- Deletable: ~6MB (system artifacts)
- This is a non-destructive plan — originals stay until user confirms successful copy
