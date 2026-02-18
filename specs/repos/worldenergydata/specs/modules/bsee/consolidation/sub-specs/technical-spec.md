# Technical Specification

This is the technical specification for the BSEE data consolidation detailed in @specs/modules/bsee/consolidation/spec.md

> Created: 2025-08-21
> Version: 1.0.0
> Module: BSEE

## Technical Requirements

### Data Analysis Requirements
- Ability to process 666 files totaling 369MB
- Support for multiple formats: CSV, Excel (.xlsx), Binary (.bin), Zip archives
- Checksum calculation for duplicate detection (MD5 or SHA256)
- Content comparison for similar but not identical files
- Memory-efficient processing for large datasets

### File Processing Capabilities
- Read CSV files with various delimiters and encodings
- Parse Excel files with multiple sheets
- Handle Git LFS binary files
- Extract and analyze zip archives
- Process files with different date formats

### Performance Requirements
- Complete inventory scan in < 10 minutes
- Checksum calculation for all files in < 5 minutes
- File operations should be atomic (all-or-nothing)
- Maintain audit trail of all changes

## Technical Approach

### Phase 1: Inventory Generation
```python
# Pseudocode for inventory generation
for file in walk('data/modules/bsee/'):
    metadata = {
        'path': file.path,
        'size': file.size,
        'type': file.extension,
        'modified': file.mtime,
        'checksum': calculate_md5(file),
        'row_count': get_row_count(file) if csv/excel,
        'columns': get_columns(file) if csv/excel
    }
    inventory.append(metadata)
```

### Phase 2: Duplicate Detection
```python
# Group files by checksum
duplicates = defaultdict(list)
for file in inventory:
    duplicates[file['checksum']].append(file['path'])

# Find content-similar files
for csv_file in csv_files:
    headers = get_headers(csv_file)
    similar_files = find_files_with_similar_headers(headers)
```

### Phase 3: Consolidation Strategy
```
Proposed Structure:
data/modules/bsee/
├── current/           # Latest, authoritative data
│   ├── production/    # Production data files
│   ├── wells/         # Well data files
│   ├── leases/        # Lease data files
│   └── surveys/       # Directional surveys
├── archive/           # Historical/legacy data
│   └── [date]/        # Archived by date
├── raw/               # Original downloads
│   ├── binary/        # Git LFS tracked
│   └── compressed/    # Zip files
└── README.md          # Data catalog and guide
```

## Implementation Details

### Duplicate Detection Algorithm
1. **Exact Duplicates**: Compare MD5 checksums
2. **Content Duplicates**: Compare after normalizing (trim whitespace, sort columns)
3. **Subset Detection**: Check if one file's data is contained in another
4. **Version Detection**: Identify files that are different versions of same data

### File Migration Strategy
1. Create destination directories
2. Copy (not move) files initially
3. Verify integrity with checksums
4. Update references in code
5. Delete source only after validation

### Data Validation Methods
```python
def validate_migration(old_path, new_path):
    # Check file exists
    assert os.path.exists(new_path)
    
    # Check size matches
    assert os.path.getsize(old_path) == os.path.getsize(new_path)
    
    # Check checksum matches
    assert get_md5(old_path) == get_md5(new_path)
    
    # For data files, check content
    if is_data_file(old_path):
        old_data = load_data(old_path)
        new_data = load_data(new_path)
        assert_data_equal(old_data, new_data)
```

## Tools and Libraries

### Required Python Libraries
- `pandas`: For CSV/Excel file analysis
- `hashlib`: For checksum calculation
- `pathlib`: For file system operations
- `shutil`: For file operations
- `zipfile`: For zip archive handling
- `openpyxl`: For Excel file processing

### Utility Scripts
```python
# inventory_generator.py - Creates file inventory
# duplicate_detector.py - Finds duplicate files
# migration_executor.py - Executes approved changes
# validator.py - Validates migration success
```

## Performance Optimizations

1. **Parallel Processing**: Use multiprocessing for checksum calculation
2. **Lazy Loading**: Don't load full file content unless necessary
3. **Incremental Processing**: Process files in batches
4. **Caching**: Cache checksums and metadata for reuse

## Error Handling

1. **File Access Errors**: Skip and log inaccessible files
2. **Corrupt Files**: Identify and quarantine corrupt data files
3. **Space Issues**: Check available disk space before operations
4. **Permission Errors**: Ensure write permissions before changes

## Rollback Strategy

1. Keep full backup in `data/modules/bsee.backup/`
2. Maintain operation log with all changes
3. Create rollback script that reverses operations
4. Test rollback on subset before full execution

## Security Considerations

1. **Data Integrity**: Use checksums to verify no data corruption
2. **Access Control**: Maintain current file permissions
3. **Audit Trail**: Log all operations with timestamps
4. **Sensitive Data**: Identify and handle any sensitive information

## Dependencies

- Python 3.9+ with required libraries
- Sufficient disk space (2x current size for safety)
- Git with LFS support for binary files
- Read/write permissions on data directory