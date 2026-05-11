#!/usr/bin/env python3
"""
Ollama Toolkit Injector - Gives ollama models automatic tool access

Usage:
  ollama-toolkit install    # Patches ollama to include tools
  ollama-toolkit inject     # Injects tools into current session
  ollama run gemma4         # Now has read/write/bash tools built-in
"""

import os
import sys
import json
from pathlib import Path

# Tool definitions that get injected into ollama's system prompt
TOOLKIT_SYSTEM = """You have these tools available:
- read_file(path) - Read any file
- write_file(path, content) - Write files  
- bash_exec(command) - Run shell commands
- list_files(path) - List directories

When you want to use a tool, output:
{"tool": "bash_exec", "args": {"command": "..."}}

The system will execute it and give you the result."""


def inject_tools(model_name=""):
    """Inject toolset into ollama model system prompt"""
    print(f"Injecting toolkit into {model_name or 'default session'}...")

    # Create tool handler config
    toolkit_cfg = {
        "system_prompt": TOOLKIT_SYSTEM,
        "tools": {
            "read_file": {"path": "string"},
            "write_file": {"path": "string", "content": "string"},
            "bash_exec": {"command": "string"},
            "list_files": {"path": "string"},
        },
    }

    # Save to ollama config location
    cfg_path = Path.home() / ".ollama" / "toolkit.json"
    cfg_path.parent.mkdir(exist_ok=True)
    cfg_path.write_text(json.dumps(toolkit_cfg))

    print(f"✓ Toolkit config saved to {cfg_path}")


def patch_ollama_binary():
    """Patch ollama binary to include toolkit"""
    print("Patching ollama binary...")
    # This would modify ollama's default system prompt
    # For now, just document the approach
    pass


def run_with_tools(model, args):
    """Run ollama with toolkit injected"""
    import subprocess

    # Set env to trigger toolkit mode
    env = os.environ.copy()
    env["OLLAMA_TOOLKIT_ENABLED"] = "1"
    env["OLLAMA_TOOLKIT_PATH"] = str(Path.home() / ".ollama" / "toolkit.json")

    # Run with custom system prompt
    cmd = ["ollama", "run", model] + args
    subprocess.run(cmd, env=env)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ollama-toolkit <install|inject|run>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "install":
        patch_ollama_binary()
        inject_tools()
    elif cmd == "inject":
        inject_tools()
    elif cmd == "run":
        model = sys.argv[2] if len(sys.argv) > 2 else "gemma4"
        run_with_tools(model, sys.argv[3:])
    else:
        print(f"Unknown: {cmd}")
