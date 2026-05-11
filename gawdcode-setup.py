#!/usr/bin/env python3
"""
Gawdcode Setup Helper - Interactive configuration
Guarantees access - always asks until valid config achieved
"""

import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".gawdcode"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_MODELS = {
    "local": ["gemma4:latest", "qwen2.5-coder:14b", "phi4:latest"],
    "cloud": ["claude-opus-4-7", "claude-sonnet-4-0", "gpt-4-turbo"],
    "openrouter": [
        "google/gemini-pro-1.5",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
    ],
}


def prompt(message, default=None, required=True):
    while True:
        if default:
            resp = input(f"{message} [{default}]: ").strip()
            resp = resp or default
        else:
            resp = input(f"{message}: ").strip()

        if resp or not required:
            return resp
        print("Required - please enter a value")


def select_from_list(items, prompt_msg="Select"):
    print(f"\n{prompt_msg}:")
    for i, item in enumerate(items):
        print(f"  {i + 1}. {item}")

    while True:
        try:
            choice = int(input("> ")) - 1
            if 0 <= choice < len(items):
                return items[choice]
        except (ValueError, IndexError):
            pass
        print("Invalid selection")


def setup_gpu_node():
    print("\n=== GPU Node Configuration ===")
    gpu_ip = prompt("GPU node IP/hostname", "108.181.162.206")
    ssh_key = prompt("SSH key path", "~/.ssh/id_ollama")
    ssh_key = os.path.expanduser(ssh_key)

    # Test connection
    print(f"Testing connection to {gpu_ip}...")
    result = os.system(
        f"ssh -o ConnectTimeout=3 -i {ssh_key} administrator@{gpu_ip} 'echo OK' 2>/dev/null"
    )

    if result == 0:
        print("✓ Connected!")
        return {"gpu_ip": gpu_ip, "ssh_key": ssh_key}
    else:
        print("⚠ Could not connect, but saving config anyway")
        return {"gpu_ip": gpu_ip, "ssh_key": ssh_key, "status": "unverified"}


def select_agents():
    print("\n=== Agent Selection ===")
    print("Choose your agents (smaller for reactive, larger for complex)")

    agents = []

    # Default helper agent
    helper = select_from_list(
        DEFAULT_MODELS["local"] + DEFAULT_MODELS["cloud"][:2],
        "Default helper agent (small & reactive)",
    )
    agents.append({"name": "helper", "model": helper, "size": "small"})

    # Worker agent
    worker = select_from_list(
        DEFAULT_MODELS["cloud"] + DEFAULT_MODELS["openrouter"],
        "Worker agent (larger for complex tasks)",
    )
    agents.append({"name": "worker", "model": worker, "size": "large"})

    return agents


def setup_providers():
    print("\n=== Cloud Provider Setup (optional) ===")
    providers = {}

    openrouter = prompt("OpenRouter API key", required=False)
    if openrouter:
        providers["openrouter"] = {"api_key": openrouter}

    anthropic = prompt("Anthropic API key", required=False)
    if anthropic:
        providers["anthropic"] = {"api_key": anthropic}

    return providers


def save_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    print(f"\n✓ Config saved to {CONFIG_FILE}")


def main():
    print("=== Gawdcode Setup ===")
    print("This will configure your CLI agent experience\n")

    config = {}

    # GPU node
    config["gpus"] = [setup_gpu_node()]

    # Agent selection
    config["agents"] = select_agents()

    # Cloud providers
    config["providers"] = setup_providers()

    # Token for MCP
    token = prompt(
        "MCP bearer token", "V3AeNFVJrwo4CaAwYy3u1DwGeMCml50KydxIXBJlc1f884e8"
    )
    config["mcp_token"] = token

    # Save
    save_config(config)

    print("\n=== Setup Complete ===")
    print("Run: gawdcode-mini start")
    print("Or:  gawdcode-mini terminal")


if __name__ == "__main__":
    main()
