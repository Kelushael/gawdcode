#!/usr/bin/env python3
"""
Tool System for Ollama - Direct injection
Run: python3 toolsys.py <model> to chat with tools
"""

import json
import subprocess
import sys

SYSTEM_TOOLS = """
Available tools:
- read_file(path)
- write_file(path, content)  
- bash_exec(command)
- list_files(path)

Usage: {"tool": "bash_exec", "args": {"command": "ls -la"}}
Result will be returned directly.
"""


def run_ollama(model, prompt):
    """Run ollama with tools in system prompt"""
    full_prompt = f"{SYSTEM_TOOLS}\n\nUser: {prompt}"

    result = subprocess.run(
        ["ollama", "run", model], input=full_prompt, capture_output=True, text=True
    )

    # Check for tool call
    output = result.stdout
    try:
        data = json.loads(output.split("{")[1].split("}")[0] + "}")
        if "tool" in data:
            return execute_tool(data["tool"], data.get("args", {}))
    except:
        pass

    return output


def execute_tool(tool, args):
    """Execute tool directly"""
    if tool == "bash_exec":
        return subprocess.run(
            args["command"], shell=True, capture_output=True, text=True
        ).stdout
    if tool == "read_file":
        return (
            open(args["path"]).read()
            if __import__("os").path.exists(args["path"])
            else "Not found"
        )
    if tool == "write_file":
        open(args["path"], "w").write(args.get("content", ""))
        return f"Wrote {args['path']}"
    if tool == "list_files":
        return "\n".join(__import__("os").listdir(args.get("path", ".")))
    return "Unknown tool"


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "gemma4"
    while True:
        prompt = input("> ")
        if prompt.lower() in ["exit", "quit"]:
            break
        print(run_ollama(model, prompt))
