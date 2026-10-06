#!/usr/bin/env python3
"""
test_cloudant_connection.py — Verify IBM Cloudant connectivity and database read/write.
Supports both IBM Cloud IAM authentication and legacy Basic Auth.
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from env_loader import load_env_config

def get_auth_header(url, cfg):
    iam_key = cfg.get("IAM_APIKEY") or cfg.get("CLOUDANT_APIKEY")
    p1 = cfg.get("C_P1", "")
    p2 = cfg.get("C_P2", "")
    k_head = cfg.get("K_HEAD", "apikey")
    k_rest = cfg.get("K_REST", "")

    # Try IAM OAuth Token
    raw_iam_key = iam_key or (f"{p1}{p2}" if len(f"{p1}{p2}") > 30 else None)
    if raw_iam_key:
        try:
            token_url = "https://iam.cloud.ibm.com/identity/token"
            data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={raw_iam_key}".encode("utf-8")
            req = urllib.request.Request(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                tok_data = json.loads(resp.read().decode("utf-8"))
                return f"Bearer {tok_data['access_token']}", "IBM Cloud IAM Bearer Token"
        except Exception as e:
            print(f"[!] IAM token request failed ({e}), falling back to Basic Auth...")

    # Fallback to Legacy Basic Auth
    legacy_key = f"{k_head}-{k_rest}" if k_rest else cfg.get("CLOUDANT_KEY", "")
    legacy_pass = f"{p1}{p2}" if (p1 or p2) else cfg.get("CLOUDANT_PASSWORD", "")
    if legacy_key and legacy_pass:
        auth_str = f"{legacy_key}:{legacy_pass}"
        auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")
        return f"Basic {auth_b64}", f"Legacy Basic Auth (Key: {legacy_key[:8]}...)"

    return None, "None"

def test_connection():
    cfg = load_env_config()
    url = cfg.get("CLOUDANT_URL")
    db = cfg.get("CLOUDANT_DB", "ibm_earnings_dashboard")

    print("=" * 60)
    print("IBM Cloudant Connectivity Verification")
    print("=" * 60)

    if not url:
        print("[!] CLOUDANT_URL not found in .env or environment.")
        return False

    auth_header, auth_desc = get_auth_header(url, cfg)
    if not auth_header:
        print("[!] No valid IAM API key or legacy Basic Auth credentials found.")
        return False

    print(f"[*] Cloudant URL : {url}")
    print(f"[*] Database     : {db}")
    print(f"[*] Auth Method  : {auth_desc}")

    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # 1. Ping Cloudant root
    print("\n[1/3] Pinging Cloudant instance root...")
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"      [OK] Connected! CouchDB/Cloudant version: {data.get('version', 'N/A')}")
    except Exception as e:
        print(f"      [FAIL] Root ping failed: {e}")
        return False

    # 2. Check / create database
    print(f"\n[2/3] Checking database '{db}'...")
    db_url = f"{url.rstrip('/')}/{db}"
    try:
        req = urllib.request.Request(db_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"      [OK] Database exists. Total documents: {data.get('doc_count', 0)}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"      [INFO] Database '{db}' does not exist yet. Attempting to create...")
            try:
                put_req = urllib.request.Request(db_url, headers=headers, method="PUT")
                with urllib.request.urlopen(put_req, timeout=10) as resp:
                    print(f"      [OK] Database '{db}' created successfully.")
            except Exception as create_err:
                print(f"      [FAIL] Could not create database: {create_err}")
                return False
        else:
            print(f"      [FAIL] HTTP error checking database: {e}")
            return False

    # 3. Test read / write doc
    print("\n[3/3] Testing document read and write...")
    test_doc_id = "test_connectivity_check"
    test_doc_url = f"{db_url}/{test_doc_id}"
    try:
        existing_rev = None
        try:
            req = urllib.request.Request(test_doc_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                doc = json.loads(resp.read().decode("utf-8"))
                existing_rev = doc.get("_rev")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise

        payload = {
            "type": "connectivity_test",
            "message": "Connection verified successfully by test_cloudant_connection.py",
            "timestamp": "UTC",
        }
        if existing_rev:
            payload["_rev"] = existing_rev

        body = json.dumps(payload).encode("utf-8")
        put_req = urllib.request.Request(test_doc_url, data=body, headers=headers, method="PUT")
        with urllib.request.urlopen(put_req, timeout=10) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            print(f"      [OK] Write successful! Document rev: {res_data.get('rev', 'ok')}")

        req = urllib.request.Request(test_doc_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            read_doc = json.loads(resp.read().decode("utf-8"))
            print(f"      [OK] Read-back verified! Message: '{read_doc.get('message')}'")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED: Cloudant connection and database sync are healthy.")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"      [FAIL] Read/write test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
