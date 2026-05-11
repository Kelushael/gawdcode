#!/usr/bin/env python3
"""
Gawdcode Mini - Small, fast, reactive CLI starter
One command setup for Claude/Litellm + GPU inference
"""

import json
import subprocess
import sys
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".gawdcode"
CONFIG_FILE = CONFIG_DIR / "config.json"


def quick_setup():
    """Minimal setup - ask once, save forever"""
    print("=== Gawdcode Mini Setup ===")

    gpu_ip = input("GPU node IP [107.181.162.206]: ").strip() or "107.181.162.206"
    token = input("MCP token: ").strip()

    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"gpu_ip": gpu_ip, "token": token}))

    print("\n✓ Configured! Run: gawdcode-mini start")


def start_agent():
    """Start preconfigured Claude agent"""
    if not CONFIG_FILE.exists():
        print("Run 'gawdcode-mini setup' first")
        return

    cfg = json.loads(CONFIG_FILE.read_text())

    # Start gawdcode terminal server
    print("Starting gawdcode terminal on port 8888...")
    subprocess.Popen(
        [sys.executable, __file__, "_server"],
        env={**os.environ, "GPU_IP": cfg["gpu_ip"]},
    )


def cloud_terminal():
    """Launch browser terminal"""
    import webbrowser
    import threading
    import time

    # Start server in background if not running
    start_agent()
    time.sleep(1)
    webbrowser.open("http://localhost:8888")


def _run_server():
    """Internal server"""
    os.system(f"python3 {__file__} --terminal 2>/dev/null || true")


def main():
    if len(sys.argv) < 2:
        print("Usage: gawdcode-mini <setup|start|terminal>")
        return

    cmd = sys.argv[1]
    if cmd == "setup":
        quick_setup()
    elif cmd == "start":
        start_agent()
    elif cmd == "terminal":
        cloud_terminal()
    elif cmd == "_server":
        _run_server()
    elif cmd == "--terminal":
        # Launch minimal terminal server
        os.system("uvicorn gawdcode-terminal:app --host 0.0.0.0 --port 8888 --quiet")
    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
