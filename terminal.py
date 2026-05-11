#!/usr/bin/env python3
"""Gawdcode Cloud Terminal - Run: python terminal.py, open http://localhost:8888"""

import os
import asyncio
import pty
import subprocess
import select
from aiohttp import web

HTML = """<!DOCTYPE html><html><head><title>Gawdcode Terminal</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css">
<style>body,html{margin:0;height:100%;background:#1e1e1e}#t{width:100%;height:100%}</style>
</head><body><div id="t"></div>
<script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js"></script>
<script>const t=new Terminal({cursorBlink:true,theme:{background:"#1e1e1e"}});t.open(document.getElementById("t"));
const ws=new WebSocket(`ws://${location.host}/ws`);ws.onmessage=e=>t.write(e.data);t.onData(d=>ws.send(d));</script>
</body></html>"""


async def handle_index(request):
    return web.Response(text=HTML, content_type="text/html")


async def handle_ws(request):
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

    async def read_pty():
        while True:
            r, _, _ = select.select([master], [], [], 0.1)
            if r:
                data = os.read(master, 1024)
                if not data:
                    break
                await ws.send_str(data.decode(errors="replace"))

    async def write_ws():
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                os.write(master, msg.data.encode())

    await asyncio.gather(read_pty(), write_ws())
    shell.kill()
    os.close(master)
    return ws


def main():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/ws", handle_ws)
    web.run_app(app, host="0.0.0.0", port=8888)


if __name__ == "__main__":
    main()
