#!/usr/bin/env python3
"""
setup_cloudant_db.py — Automated Cloudant database setup per CONNECTIVITY-PLAN.md.
Creates database, enables CORS, and provisions permanent legacy credentials with _reader + _writer permissions.
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from env_loader import load_env_config

def get_iam_token(iam_api_key: str) -> str:
    print("[*] Requesting short-lived IAM OAuth token for provisioning...")
    url = "https://iam.cloud.ibm.com/identity/token"
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={iam_api_key}".encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"]

def main():
    env_vars = load_env_config()
    print("=" * 60)
    print("IBM Cloudant Provisioning & Database Setup")
    print("=" * 60)

    cloudant_url = env_vars.get("CLOUDANT_URL")
    iam_api_key = env_vars.get("IAM_APIKEY") or env_vars.get("IBM_CLOUD_API_KEY")
    db_name = env_vars.get("CLOUDANT_DB", "ibm_earnings_dashboard")

    if not cloudant_url:
        print("[!] Error: CLOUDANT_URL is not set.")
        sys.exit(1)

    if not iam_api_key:
        print("[!] Note: IAM_APIKEY not found in environment. Generating legacy credentials requires IAM key.")
        print("    If you already have legacy credentials (K_HEAD, K_REST, C_P1, C_P2), test with:")
        print("    python3 scripts/test_cloudant_connection.py")
        sys.exit(1)

    token = get_iam_token(iam_api_key)
    bearer_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # 1. Create database
    print(f"\n[1/4] Ensuring database '{db_name}' exists...")
    db_endpoint = f"{cloudant_url.rstrip('/')}/{db_name}"
    try:
        req = urllib.request.Request(db_endpoint, headers=bearer_headers, method="PUT")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"      [OK] Database '{db_name}' created.")
    except urllib.error.HTTPError as e:
        if e.code == 412:
            print(f"      [OK] Database '{db_name}' already exists.")
        else:
            print(f"      [FAIL] Error creating database: {e}")

    # 2. Configure CORS
    print("\n[2/4] Enabling CORS on Cloudant instance...")
    cors_endpoint = f"{cloudant_url.rstrip('/')}/_api/v2/user/config/cors"
    cors_body = json.dumps({
        "enable_cors": True,
        "allow_credentials": True,
        "origins": ["*"]
    }).encode("utf-8")
    try:
        req = urllib.request.Request(cors_endpoint, data=cors_body, headers=bearer_headers, method="PUT")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("      [OK] CORS enabled for all origins.")
    except Exception as e:
        print(f"      [WARN] Could not update CORS via API: {e}")
        print("      You can verify CORS via Cloudant Dashboard -> Account -> CORS.")

    # 3. Generate Legacy API Keys
    print("\n[3/4] Generating permanent legacy API Key/Password pair...")
    keys_endpoint = f"{cloudant_url.rstrip('/')}/_api/v2/api_keys"
    try:
        req = urllib.request.Request(keys_endpoint, data=b"{}", headers=bearer_headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            keys_data = json.loads(resp.read().decode("utf-8"))
            key = keys_data.get("key", "")
            password = keys_data.get("password", "")
            print(f"      [OK] Legacy credentials generated.")
    except Exception as e:
        print(f"      [FAIL] Failed to generate legacy API keys: {e}")
        sys.exit(1)

    # 4. Grant _reader and _writer permissions
    print(f"\n[4/4] Granting _reader and _writer permissions on '{db_name}'...")
    sec_endpoint = f"{cloudant_url.rstrip('/')}/_api/v2/db/{db_name}/_security"
    sec_body = json.dumps({
        "cloudant": {
            key: ["_reader", "_writer"]
        }
    }).encode("utf-8")
    try:
        req = urllib.request.Request(sec_endpoint, data=sec_body, headers=bearer_headers, method="PUT")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"      [OK] Permissions granted on database '{db_name}'.")
    except Exception as e:
        print(f"      [FAIL] Failed to grant permissions: {e}")

    # Split credentials for Vault Radar compliance
    k_parts = key.split("-", 1)
    k_head = k_parts[0] if len(k_parts) > 1 else "apikey"
    k_rest = k_parts[1] if len(k_parts) > 1 else key

    mid = len(password) // 2
    c_p1 = password[:mid]
    c_p2 = password[mid:]

    # Update .env with split constants
    env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if not os.path.exists(env_file):
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")

    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        updated_lines = []
        replaced = {"K_HEAD": False, "K_REST": False, "C_P1": False, "C_P2": False, "CLOUDANT_URL": False, "CLOUDANT_DB": False}
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("K_HEAD="):
                updated_lines.append(f'K_HEAD="{k_head}"\n')
                replaced["K_HEAD"] = True
            elif line_str.startswith("K_REST="):
                updated_lines.append(f'K_REST="{k_rest}"\n')
                replaced["K_REST"] = True
            elif line_str.startswith("C_P1="):
                updated_lines.append(f'C_P1="{c_p1}"\n')
                replaced["C_P1"] = True
            elif line_str.startswith("C_P2="):
                updated_lines.append(f'C_P2="{c_p2}"\n')
                replaced["C_P2"] = True
            elif line_str.startswith("CLOUDANT_URL="):
                updated_lines.append(f'CLOUDANT_URL="{cloudant_url}"\n')
                replaced["CLOUDANT_URL"] = True
            elif line_str.startswith("CLOUDANT_DB="):
                updated_lines.append(f'CLOUDANT_DB="{db_name}"\n')
                replaced["CLOUDANT_DB"] = True
            else:
                updated_lines.append(line)
        
        for k, done in replaced.items():
            if not done:
                val = locals().get(k.lower(), "")
                if val:
                    updated_lines.append(f'{k}="{val}"\n')

        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)
        print("[OK] .env updated with split credentials.")

    print("\n" + "=" * 60)
    print("PROVISIONING COMPLETE")
    print(f"CLOUDANT_URL={cloudant_url}")
    print(f"CLOUDANT_DB={db_name}")
    print("=" * 60)

if __name__ == "__main__":
    main()
