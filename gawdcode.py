#!/usr/bin/env python3
"""
Gawdcode CLI Agent - Conversational control of GPU inference nodes
Usage: gawdcode [command] [args]
"""

import argparse, json, os, sys, subprocess
from pathlib import Path

CONFIG_PATH = Path("/etc/gawdcode/config.json")


def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"gpu_node": "108.181.162.206", "mcp_token": None}


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def infer_target(natlang: str) -> dict:
    """
    Parse natural language to determine inference target.
    Returns: {"type": "local|remote|api", "target": "...", "model": "..."}
    """
    nl = natlang.lower()

    # API references (Anthropic, OpenAI)
    if any(kw in nl for kw in ["claude", "sonnet", "opus", "anthropic"]):
        return {"type": "api", "target": "anthropic", "model": "claude-opus-4-7"}
    if any(kw in nl for kw in ["gpt", "openai", "o3", "o4"]):
        return {"type": "api", "target": "openai", "model": "gpt-4"}

    # IP/hostname pattern
    import re

    ip_match = re.search(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b", natlang)
    if ip_match:
        return {"type": "remote", "target": ip_match.group(1), "model": "gemma4:latest"}

    host_match = re.search(r"@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", natlang)
    if host_match:
        return {
            "type": "remote",
            "target": host_match.group(1),
            "model": "gemma4:latest",
        }

    # SSH node reference
    if "ssh" in nl or "remote" in nl:
        return {
            "type": "remote",
            "target": load_config().get("gpu_node"),
            "model": "gemma4:latest",
        }

    # Local fallback
    return {"type": "local", "target": "gpu", "model": "gemma4:latest"}


def chat_mode():
    """Interactive chat mode with full tool access"""
    cfg = load_config()

    print("=== Gawdcode Chat Mode ===")
    print("Natural language control of GPU inference")
    print("Type 'exit' to quit, 'help' for commands\n")

    while True:
        try:
            prompt = input("gawdcode> ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit"]:
                break
            if prompt.lower() == "help":
                print("""
Commands:
  help         Show this help
  status       Check GPU node status
  shell <cmd>  Run command on GPU node
  chat <txt>   Send prompt to local LLM
  exit         Quit

Natural language:
  "run pwd on the gpu" → executes remotely
  "chat with gemma" → local inference
  "tell claude to..." → routes to Anthropic API
""")
                continue

            target = infer_target(prompt)

            if target["type"] == "local":
                print(f"[local] {target['model']}: Processing...")
            elif target["type"] == "remote":
                print(f"[remote] {target['target']}: {target['model']}")
            else:
                print(f"[api] {target['target']}: {target['model']}")

        except KeyboardInterrupt:
            print("\n")
            break
        except EOFError:
            break


def status_cmd():
    cfg = load_config()
    gpu = cfg.get("gpu_node")
    print(f"GPU Node: {gpu}")
    print(f"MCP Token: {'*' * 8 if cfg.get('mcp_token') else 'not configured'}")

    # Quick connectivity check
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            f"http://{gpu}:4100/health",
        ],
        capture_output=True,
    )
    print(f"Status: {'online' if result.stdout == b'200' else 'offline'}")


def main():
    parser = argparse.ArgumentParser(description="Gawdcode CLI Agent")
    parser.add_argument("command", nargs="?", default="chat", help="chat|status|shell")
    parser.add_argument("args", nargs="*", help="Command arguments")
    args = parser.parse_args()

    if args.command == "chat":
        chat_mode()
    elif args.command == "status":
        status_cmd()
    elif args.command == "shell":
        if len(args.args) < 1:
            print("Usage: gawdcode shell <command>")
            sys.exit(1)
        cmd = " ".join(args.args)
        print(f"Executing on GPU: {cmd}")
        # Would SSH to GPU node and run
    elif args.command == "configure":
        cfg = load_config()
        print("Configure Gawdcode:")
        gpu = input(f"GPU node [{cfg.get('gpu_node')}]: ") or cfg.get("gpu_node")
        token = input("MCP token: ")
        cfg = {"gpu_node": gpu, "mcp_token": token}
        save_config(cfg)
        print("Configuration saved")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
