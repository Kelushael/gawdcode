# Gawdcode

Conversational CLI agent for controlling GPU inference nodes.

## Install

```bash
curl -fsSL https://github.com/Kelushael/gawdcode/raw/main/install.sh | sudo bash
```

## Quick Start

```bash
# Interactive setup (guarantees access)
gawdcode-setup

# Launch cloud terminal
gawdcode terminal

# Chat mode
gawdcode
```

## Architecture

```
User → gawdcode-setup → Select agents → Configure providers → Save config
                              ↓
                        gawdcode-mini (CLI)
                              ↓
                    Local LLM + Cloud APIs in tandem
```

### Agents

1. **Helper** (small/reactive) - Fast responses, status checks, simple tasks
2. **Worker** (large) - Complex reasoning, code generation, planning

### Providers

- Local Ollama models (gemma4, qwen2.5-coder, etc.)
- Cloud APIs (Claude, OpenAI)
- OpenRouter unified access

## Files

- `gawdcode-setup.py` - Interactive configuration (never locks you out)
- `gawdcode-mini.py` - CLI agent with cloud terminal
- `terminal.py` - Web terminal server
- `dns_hook.py` - Hostinger DNS integration

## Usage

```bash
# Setup
gawdcode-setup

# Start terminal server
gawdcode terminal

# Or chat mode
gawdcode
```

Open browser to: http://localhost:8888

## Configuration

Saved at `~/.gawdcode/config.json`:

```json
{
  "gpus": [{"gpu_ip": "108.181.162.206", "ssh_key": "~/.ssh/id_ollama"}],
  "agents": [
    {"name": "helper", "model": "gemma4:latest"},
    {"name": "worker", "model": "claude-opus-4-7"}
  ],
  "providers": {
    "openrouter": {"api_key": "..."},
    "anthropic": {"api_key": "..."}
  },
  "mcp_token": "..."
}
```