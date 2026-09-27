import json
import os
import yaml
from pathlib import Path

# Default paths relative to workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
BATCH_FILE = WORKSPACE_ROOT / "data" / "document-index" / "conference-index-batch.jsonl"
CATALOG_FILE = WORKSPACE_ROOT / "data" / "document-index" / "conference-paper-catalog.yaml"
OUTPUT_FILE = WORKSPACE_ROOT / "data" / "document-index" / "conference-index-stats.yaml"

def create_stats():
    """
    Reads conference-index-batch.jsonl and creates summary statistics.
    """
    stats = {}
    total_count = 0
    total_size = 0

    with open(BATCH_FILE, 'r') as f:
        for line in f:
            entry = json.loads(line)
            conf_name = entry.get('conference')
            if conf_name not in stats:
                stats[conf_name] = {
                    'file_count': 0,
                    'pdf_count': 0,
                    'size_bytes': 0
                }
            
            stats[conf_name]['file_count'] += 1
            if entry.get('extension') == '.pdf':
                stats[conf_name]['pdf_count'] += 1
            
            try:
                file_size = os.path.getsize(entry['path'])
                stats[conf_name]['size_bytes'] += file_size
                total_size += file_size
            except FileNotFoundError:
                # Handle cases where the file might not be accessible
                pass

            total_count += 1

    # Load catalog to get priorities
    with open(CATALOG_FILE, 'r') as f:
        catalog = yaml.safe_load(f)
    
    conf_priorities = {conf['name']: conf.get('priority', 'medium') for conf in catalog['conferences']}

    # Prepare output data
    output_data = {
        'total_indexed_files': total_count,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'per_conference': []
    }

    # Sort by file count (descending)
    sorted_conferences = sorted(stats.items(), key=lambda item: item[1]['file_count'], reverse=True)

    for conf_name, conf_stats in sorted_conferences:
        output_data['per_conference'].append({
            'name': conf_name,
            'priority': conf_priorities.get(conf_name, 'unknown'),
            'file_count': conf_stats['file_count'],
            'pdf_count': conf_stats['pdf_count'],
            'size_mb': round(conf_stats['size_bytes'] / (1024 * 1024), 2)
        })

    # Write YAML output
    with open(OUTPUT_FILE, 'w') as f:
        yaml.dump(output_data, f, sort_keys=False)

    print(f"Stats written to {OUTPUT_FILE}")

if __name__ == '__main__':
    create_stats()
