#!/bin/bash
# Gawdcode Installer - curl -fsSL https://github.com/Kelushael/gawdcode/raw/main/install.sh | sudo bash
set -e

REPO="https://github.com/Kelushael/gawdcode"
INSTALL_DIR="/opt/gawdcode"
BIN="/usr/local/bin"

echo "=== Gawdcode Installer ==="

# Install deps
apt-get update -qq && apt-get install -y -qq python3 python3-pip curl > /dev/null 2>&1 || true
pip3 install -q aiohttp httpx 2>/dev/null || true

# Get files
mkdir -p "$INSTALL_DIR"
curl -fsSL "$REPO/raw/main/gawdcode-setup.py" -o "$INSTALL_DIR/gawdcode-setup.py"
curl -fsSL "$REPO/raw/main/terminal.py" -o "$INSTALL_DIR/terminal.py"
curl -fsSL "$REPO/raw/main/gawdcode-mini.py" -o "$INSTALL_DIR/gawdcode-mini.py"

chmod +x "$INSTALL_DIR"/*.py

# Symlinks
ln -sf "$INSTALL_DIR/gawdcode-setup.py" "$BIN/gawdcode-setup"
ln -sf "$INSTALL_DIR/gawdcode-mini.py" "$BIN/gawdcode"

echo "✓ Installed! Run: gawdcode-setup"