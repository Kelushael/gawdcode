# Ollama Tools Extension

## Default Tool Access for Ollama Models

To give ollama models read/write/bash access automatically:

### Method 1: Environment Variables
```bash
export OLLAMA_TOOLKIT=1
export OLLAMA_TOOLS_PATH=/opt/gawdcode/tools.json
```

### Method 2: System Prompt Injection
Add to `~/.ollama/modelfile`:
```
FROM gemma4
SYSTEM """You have access to these tools:
- read_file(path)
- write_file(path, content)  
- bash_exec(command)
- list_files(path)

To use: {"tool": "bash_exec", "args": {"command": "ls -la"}}
"""
```

### Method 3: Runtime Wrapper
```bash
# /usr/local/bin/ollama
#!/bin/bash
# Wrap ollama to inject tools
exec /usr/bin/ollama "$@" | python3 /opt/gawdcode/tool-injector.py
```

### Installed Tools (19 total)
Available via MCP at markyninox.com/mcp:
- files.* (6 tools) - read/write/search filesystem
- shell.* (1 tool) - bash execution
- lab.* (4 tools) - desktop automation
- self_mod.* (3 tools) - self-modification
- gesher.* (5 tools) - stream governance