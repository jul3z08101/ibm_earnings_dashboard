#!/usr/bin/env python3
"""
build.py — Prepare static release bundle for GitHub Pages (github.ibm.com).
Reads web/dashboard.html, injects build metadata and Cloudant environment constants into dist/index.html.
"""

import os
import sys
import json
import shutil
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from env_loader import load_env_config

def build():
    env_vars = load_env_config()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    repo_root = os.path.abspath(os.path.join(root_dir, ".."))
    web_dir = os.path.join(root_dir, "web")
    dist_dir = os.path.join(root_dir, "dist")

    os.makedirs(dist_dir, exist_ok=True)
    src_html = os.path.join(web_dir, "dashboard.html")

    if not os.path.exists(src_html):
        src_html = os.path.join(repo_root, "dashboard.html")

    if not os.path.exists(src_html):
        print(f"[!] Error: {src_html} not found.")
        sys.exit(1)

    with open(src_html, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Cloudant configuration from env
    cloudant_url = env_vars.get("CLOUDANT_URL", "")
    k_head = env_vars.get("K_HEAD", "apikey")
    k_rest = env_vars.get("K_REST", "")
    c_p1 = env_vars.get("C_P1", "")
    c_p2 = env_vars.get("C_P2", "")
    iam_key = env_vars.get("IAM_APIKEY") or env_vars.get("CLOUDANT_APIKEY")
    db_name = env_vars.get("CLOUDANT_DB", "ibm_earnings_dashboard")
    admin_pin = env_vars.get("ADMIN_PIN", "1234")

    # If IAM API key exists and C_P1/C_P2 not set, split IAM key safely
    if iam_key and (not c_p1 or not c_p2):
        mid = len(iam_key) // 2
        c_p1 = iam_key[:mid]
        c_p2 = iam_key[mid:]

    # Inject runtime config if values exist
    if cloudant_url:
        html_content = html_content.replace(
            'cloudantUrl: window.__CLOUDANT_URL__ || ""',
            f'cloudantUrl: window.__CLOUDANT_URL__ || "{cloudant_url}"'
        )
    if k_rest:
        html_content = html_content.replace('C_K: "apikey"', f'C_K: "{k_head}"')
        html_content = html_content.replace('C_R: ""', f'C_R: "{k_rest}"')
    if c_p1 and c_p2:
        html_content = html_content.replace('C_P1: ""', f'C_P1: "{c_p1}"')
        html_content = html_content.replace('C_P2: ""', f'C_P2: "{c_p2}"')
    if db_name:
        html_content = html_content.replace('dbName: "ibm_earnings_dashboard"', f'dbName: "{db_name}"')

    # Output to dist/index.html
    dist_index = os.path.join(dist_dir, "index.html")
    with open(dist_index, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("=" * 60)
    print("BUILD SUCCESSFUL")
    print(f"Generated: {dist_index}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

if __name__ == "__main__":
    build()
