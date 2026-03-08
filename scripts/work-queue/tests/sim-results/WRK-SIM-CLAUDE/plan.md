# WRK-SIM-CLAUDE Plan
## Mission
Add input validation to close-item.sh to block invalid WRK IDs.
## Steps
1. Validate WRK_ID format (WRK-NNN)
2. Check WRK exists in working/ or done/
3. Exit 1 with clear error if invalid
