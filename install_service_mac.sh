#!/bin/bash
# Install Thumbtack bot as a LaunchAgent on Mac (runs when user is logged in)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_NAME="com.thumbtack.autoresponder"
PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "🚀 Installing Thumbtack Auto-Responder as LaunchAgent..."
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup_mac.sh first"
    exit 1
fi

# Get Python path from venv
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
LOG_DIR="$SCRIPT_DIR/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

# Create LaunchAgent plist
echo "📝 Creating LaunchAgent configuration..."
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${MAIN_SCRIPT}</string>
    </array>

    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>${LOG_DIR}/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
EOF

echo "✅ LaunchAgent plist created at: $PLIST_FILE"
echo ""

# Load the LaunchAgent
echo "🔄 Loading LaunchAgent..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo ""
echo "✅ Installation complete!"
echo ""
echo "The bot will now:"
echo "  - Start automatically when you login"
echo "  - Restart automatically if it crashes"
echo "  - Run in the background"
echo ""
echo "Useful commands:"
echo "  Check status:   launchctl list | grep thumbtack"
echo "  View logs:      tail -f $LOG_DIR/bot.log"
echo "  Stop service:   launchctl unload $PLIST_FILE"
echo "  Start service:  launchctl load $PLIST_FILE"
echo "  Restart:        launchctl kickstart -k gui/\$(id -u)/${PLIST_NAME}"
echo ""
echo "To uninstall:"
echo "  ./uninstall_service_mac.sh"
