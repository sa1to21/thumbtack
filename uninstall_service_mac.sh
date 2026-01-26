#!/bin/bash
# Uninstall Thumbtack bot LaunchAgent from Mac

PLIST_NAME="com.thumbtack.autoresponder"
PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "🗑️  Uninstalling Thumbtack Auto-Responder LaunchAgent..."

if [ -f "$PLIST_FILE" ]; then
    # Unload the service
    launchctl unload "$PLIST_FILE" 2>/dev/null || true

    # Remove the plist file
    rm "$PLIST_FILE"

    echo "✅ Service uninstalled successfully"
    echo ""
    echo "The bot will no longer start automatically."
    echo "Your data (chrome_profile, logs, .env) are still intact."
else
    echo "❌ Service not found (not installed)"
fi
