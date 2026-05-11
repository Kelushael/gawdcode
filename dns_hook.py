#!/usr/bin/env python3
"""
Gawdcode DNS Hook - Point domains to GPU inference node via Hostinger API
"""

import httpx
import json
from pathlib import Path

HOSTINGER_API = "https://api.hostinger.com"


def load_hostinger_creds():
    """Load credentials from ~/.gawdcode/hostinger.json"""
    cfg_path = Path.home() / ".gawdcode" / "hostinger.json"
    if cfg_path.exists():
        return json.loads(cfg_path.read_text())
    return None


def point_domain(domain: str, target_ip: str, creds: dict = None):
    """
    Point domain A record to target IP using Hostinger API
    cred format: {"api_key": "...", "client_id": "..."}
    """
    if not creds:
        creds = load_hostinger_creds()

    headers = {"Authorization": f"Bearer {creds['api_key']}"}

    # Get zone ID first
    resp = httpx.get(
        f"{HOSTINGER_API}/client/v1/zones/find",
        params={"domain": domain},
        headers=headers,
    )

    zone_id = resp.json().get("id")

    # Update A record
    record_data = {"type": "A", "name": "@", "content": target_ip, "ttl": 3600}

    return httpx.put(
        f"{HOSTINGER_API}/client/v1/zones/{zone_id}/records/@/A",
        json=record_data,
        headers=headers,
    )


def status():
    """Check current DNS pointing"""
    creds = load_hostinger_creds()
    if not creds:
        print("No Hostinger credentials found at ~/.gawdcode/hostinger.json")
        return

    domains = ["marcusx.fun", "markyninox.com"]
    for domain in domains:
        resp = httpx.get(
            f"{HOSTINGER_API}/client/v1/zones/find",
            params={"domain": domain},
            headers={"Authorization": f"Bearer {creds['api_key']}"},
        )
        data = resp.json()
        print(
            f"{domain} -> {data.get('records', {}).get('A', [{}])[0].get('content', 'unknown')}"
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        point_domain(sys.argv[1], sys.argv[2])
    else:
        status()
