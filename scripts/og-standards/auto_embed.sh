#!/bin/bash
# Auto-embedding script that runs periodically to embed new OCR chunks
# Usage: nohup ./auto_embed.sh >> logs/auto_embed.log 2>&1 &

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Use symlink to avoid path issues with ampersand
OG_DIR="/tmp/og-standards"
LOG_FILE="$OG_DIR/logs/auto_embed.log"
DB_FILE="$OG_DIR/_inventory.db"

echo "=== Starting auto-embed at $(date) ===" >> "$LOG_FILE"

while true; do
    # Check if OCR is still running
    if ! pgrep -f "ocr_scanned_pdfs.py" > /dev/null; then
        echo "$(date) - OCR process complete, running final embedding..." >> "$LOG_FILE"
        CUDA_VISIBLE_DEVICES="" python embed.py --config config.yaml --batch-size 200 >> "$LOG_FILE" 2>&1
        echo "$(date) - Auto-embed complete, exiting" >> "$LOG_FILE"
        break
    fi

    # Get pending count
    pending=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM text_chunks WHERE embedding IS NULL;")

    if [ "$pending" -gt 50 ]; then
        echo "$(date) - Embedding $pending chunks..." >> "$LOG_FILE"
        CUDA_VISIBLE_DEVICES="" python embed.py --config config.yaml --batch-size 200 >> "$LOG_FILE" 2>&1
    else
        echo "$(date) - Only $pending pending, waiting..." >> "$LOG_FILE"
    fi

    # Wait 2 minutes before next check
    sleep 120
done

echo "=== Auto-embed finished at $(date) ===" >> "$LOG_FILE"
