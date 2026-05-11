#!/usr/bin/env python3
"""
Gawdcode Bridge - Direct AI command execution
No prefixes - just ask and it runs
"""

import os
import sys
import json
import subprocess
from pathlib import Path

CONFIG = Path.home() / ".gawdcode" / "config.json"


def load_config():
    return json.loads(CONFIG.read_text()) if CONFIG.exists() else {}


def execute_tool(tool_name, args):
    """Execute any registered tool directly"""
    cfg = load_config()
    gpu_ip = cfg.get("gpus", [{}])[0].get("gpu_ip", "108.181.162.206")
    token = cfg.get("mcp_token", "")

    # Direct MCP execution
    mcp_url = f"http://{gpu_ip}:8091/mcp"
    headers = {
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": args},
        "id": 1,
    }

    result = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "POST",
            "-H",
            f"content-type: application/json",
            "-H",
            f"accept: application/json, text/event-stream",
            "-H",
            f"Authorization: Bearer {token}",
            "-d",
            json.dumps(payload),
            mcp_url,
        ],
        capture_output=True,
        text=True,
    )
    return result.stdout


def bash_exec(cmd):
    """Execute bash directly - full permissions"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr


def ai_loop():
    """Simple prompt -> execute loop"""
    print("=== Gawdcode Bridge ===")
    print("Direct execution - no prefixes needed\n")

    while True:
        try:
            prompt = input("> ").strip()
            if not prompt:
                continue

            # Natural language detection
            if "run" in prompt.lower() and any(
                kw in prompt for kw in ["bash", "shell", "command"]
            ):
                # Extract command after "run"
                cmd = prompt.split("run", 1)[-1].strip()
                if cmd.startswith("`") and cmd.endswith("`"):
                    cmd = cmd[1:-1]
                print(f"$ {cmd}")
                print(bash_exec(cmd))
            elif "file" in prompt.lower() or "read" in prompt.lower():
                # File operations
                import re

                path_match = re.search(
                    r'["\']?(/[^\s"\']+)["\']?|["\']([^\s"\']+)["\']', prompt
                )
                if path_match:
                    path = path_match.group(1) or path_match.group(2)
                    print(
                        open(path).read() if os.path.exists(path) else "File not found"
                    )
            else:
                # Try tool execution
                print(f"[executing] {prompt}")
                print(execute_tool("bash_exec", {"command": prompt}) if prompt else "")

        except KeyboardInterrupt:
            print("\n")
            break


if __name__ == "__main__":
    ai_loop()
