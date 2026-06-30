#!/bin/bash
# Install caffeine-menubar as a background menu-bar app that starts at login.
#
# Uses a LaunchAgent (the reliable way to run a menu-bar / LSUIElement app) instead
# of a double-clickable .app — a bare-script .app doesn't always register as a GUI
# app, so its menu-bar icon never appears.
#
#   ./install.sh      install + start now + start at login
#   ./uninstall.sh    stop + remove
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.elaine.caffeine-menubar"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
PY="$DIR/.venv/bin/python"

echo "→ venv + deps"
python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/pip" install -q --upgrade pip
"$DIR/.venv/bin/pip" install -q -r "$DIR/requirements.txt"

echo "→ icons"
"$PY" "$DIR/make_icons.py"

echo "→ LaunchAgent"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PY</string>
    <string>$DIR/app.py</string>
  </array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><false/>
  <key>ProcessType</key><string>UIElement</string>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/caffeine-menubar.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/caffeine-menubar.log</string>
</dict>
</plist>
PL

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "✓ Installed and started. Look for the ☕ in your menu bar (it'll start at login too)."
echo "  Logs: ~/Library/Logs/caffeine-menubar.log"
