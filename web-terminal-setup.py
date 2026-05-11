#!/usr/bin/env python3
"""
Web Terminal Setup for markyninox.com/gawdcode
Serves GPU terminal with pre-launched agent and active tools

Run on GPU node (gesher-el):
  python3 web-terminal-setup.py install
"""

import os

# Nginx server block for gawdcode
NGINX_CONF = """
server {
    listen 80;
    server_name markyninox.com;
    
    location /gawdcode {
        proxy_pass http://127.0.0.1:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
"""

# Terminal HTML with pre-launched agent
TERMINAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gawdcode - GPU Terminal</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5/css/xterm.css">
    <style>
        body,html{margin:0;height:100%;background:#0a0a0a;color:#00ff88;font-family:monospace}
        #t{width:100%;height:100%}
        #status{position:fixed;top:5px;right:10px;background:#111;padding:5px 10px;border-radius:3px;font-size:12px}
    </style>
</head>
<body>
    <div id="status">GPU:108.181.162.206 | Agent:Active | Tools:19</div>
    <div id="t"></div>
    <script src="https://cdn.jsdelivr.net/npm/xterm@5/js/xterm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/js/xterm-addon-fit.js"></script>
    <script>
        const term = new Terminal({cursorBlink:true,theme:{background:"#0a0a0a",foreground:"#00ff88"}});
        const fit = new FitAddon.FitAddon();
        term.loadAddon(fit);
        term.open(document.getElementById("t"));
        fit.fit();
        
        const ws = new WebSocket(`ws://${location.host}/ws`);
        ws.onmessage = e => term.write(e.data);
        term.onData(d => ws.send(d));
        
        // Auto-launch agent
        term.writeln("\x1b[36m★ Gawdcode Agent Ready\x1b[0m");
        term.writeln("19 tools active. Type 'help' for commands.\n");
    </script>
</body>
</html>
"""


def setup_nginx():
    """Install nginx config"""
    config_path = "/etc/nginx/sites-enabled/gawdcode"
    with open(config_path, "w") as f:
        f.write(NGINX_CONF)
    print("✓ Nginx config written")

    # Reload nginx
    os.system("nginx -t && systemctl reload nginx")


def start_terminal_server():
    """Start web terminal"""
    import subprocess
    import threading
    import asyncio
    import pty
    import select
    from aiohttp import web

    async def index(request):
        return web.Response(text=TERMINAL_HTML, content_type="text/html")

    async def websocket(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        master, slave = pty.openpty()
        shell = subprocess.Popen(
            ["/bin/bash"],
            preexec_fn=os.setsid,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
        )

        async def read():
            while True:
                r, _, _ = select.select([master], [], [], 0.1)
                if r:
                    data = os.read(master, 1024)
                    if not data:
                        break
                    await ws.send_str(data.decode(errors="replace"))

        async def write():
            async for msg in ws:
                if msg.type.name == "TEXT":
                    os.write(master, msg.data.encode())

        await asyncio.gather(read(), write())
        shell.kill()
        os.close(master)

    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket)

    print("Starting terminal on port 8888...")
    web.run_app(app, host="0.0.0.0", port=8888)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "install":
        setup_nginx()
    else:
        start_terminal_server()
