#!/bin/bash
# Stop and remove the caffeine-menubar LaunchAgent.
set -euo pipefail
LABEL="com.elaine.caffeine-menubar"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
pkill -f "caffeine-menubar/app.py" 2>/dev/null || true
echo "✓ Removed. (Any active caffeinate from the app is also stopped.)"
