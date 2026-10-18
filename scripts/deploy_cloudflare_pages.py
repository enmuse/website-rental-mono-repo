#!/usr/bin/env python3
"""
deploy_cloudflare_pages.py — Programmatic Cloudflare Pages Deployer

Deploys the monorepo showcase and all 10 client websites to Cloudflare Pages.
Reads CLOUD_FLARE_PAGES_API_TOKEN or CLOUD_FLARE_API_TOKEN from .env.
"""

import os
import sys
import json
import subprocess
import argparse
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
DEFAULT_ACCOUNT_ID = "2bbe914ca4d82460c51d668407bb3dbd"
PROJECT_NAME = "wnc-client-sites"

def load_env_token():
    """Extracts Cloudflare API token from .env file."""
    if not ENV_FILE.exists():
        return ""
    tokens = {}
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("CLOUD_FLARE_PAGES_API_TOKEN="):
                tokens["pages"] = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("CLOUD_FLARE_API_TOKEN="):
                tokens["standard"] = line.split("=", 1)[1].strip().strip('"').strip("'")
    return tokens.get("pages") or tokens.get("standard") or ""

def cf_api_request(endpoint: str, token: str, method: str = "GET", data: dict = None) -> dict:
    url = f"https://api.cloudflare.com/client/v4{endpoint}"
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method=method
    )
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"success": False, "http_code": e.code, "error_body": body}
    except Exception as e:
        return {"success": False, "exception": str(e)}

def ensure_pages_project(account_id: str, token: str, project_name: str):
    """Ensures that the Pages project exists in the Cloudflare account."""
    res = cf_api_request(f"/accounts/{account_id}/pages/projects/{project_name}", token)
    if res.get("success"):
        print(f"✅ Cloudflare Pages project '{project_name}' exists (Subdomain: {res['result'].get('subdomain')})")
        return True
    
    print(f"🚀 Creating project '{project_name}'...")
    create_res = cf_api_request(
        f"/accounts/{account_id}/pages/projects",
        token,
        method="POST",
        data={"name": project_name, "production_branch": "main"}
    )
    if create_res.get("success"):
        print(f"✅ Created project '{project_name}' successfully!")
        return True
    else:
        print(f"⚠️ Project check note: {create_res.get('error_body') or create_res.get('exception')}")
        return False

def deploy_monorepo(account_id: str, token: str, project_name: str):
    """Deploys all files to Cloudflare Pages using wrangler."""
    print(f"\n📦 Deploying monorepo showcase and all 10 client sites to '{project_name}'...")
    env = os.environ.copy()
    env["CLOUDFLARE_API_TOKEN"] = token
    env["CLOUDFLARE_ACCOUNT_ID"] = account_id

    cmd = [
        "npx", "--yes", "wrangler", "pages", "deploy",
        str(REPO_ROOT),
        f"--project-name={project_name}",
        "--branch=main",
        "--commit-dirty=true"
    ]
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
        print(res.stdout)
        if res.returncode == 0:
            print(f"\n✨ Successfully deployed! Live at https://{project_name}.pages.dev")
            return True
        else:
            print(f"⚠️ Deploy error: {res.stderr}")
            return False
    except Exception as e:
        print(f"❌ Deploy subprocess exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Cloudflare Pages Deployer")
    parser.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID)
    parser.add_argument("--project", default=PROJECT_NAME)
    args = parser.parse_args()

    token = load_env_token()
    if not token:
        print("❌ Error: No Cloudflare API token found in .env")
        sys.exit(1)

    print("=========================================================")
    print("⛅ Cloudflare Pages Programmatic Deployer")
    print(f"Account ID: {args.account_id}")
    print(f"Target Project: {args.project}")
    print("=========================================================\n")

    ensure_pages_project(args.account_id, token, args.project)
    deploy_monorepo(args.account_id, token, args.project)

if __name__ == "__main__":
    main()
