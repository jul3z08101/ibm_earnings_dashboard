#!/usr/bin/env python3
"""
env_loader.py — Shared environment loader for Cloudant & GitHub configurations.
Handles key-value .env files and Cloudant Service Credentials JSON blocks safely.
"""

import os
import json
import re

def load_env_config():
    """Finds and parses .env file from workspace root or project subfolder."""
    possible_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env")
    ]
    
    env_file = None
    for p in possible_paths:
        p_abs = os.path.abspath(p)
        if os.path.exists(p_abs):
            env_file = p_abs
            break

    env_vars = dict(os.environ)

    if env_file:
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for JSON block in CLOUDANT_CREDENTIALS / CLOUDANT_CREDENTAILS
        json_match = re.search(r'CLOUDANT_CREDENT[A-Z]*\s*=\s*(\{[\s\S]*?\n\s*\})', content)
        if json_match:
            try:
                cloudant_data = json.loads(json_match.group(1))
                if isinstance(cloudant_data, dict):
                    if "url" in cloudant_data:
                        env_vars.setdefault("CLOUDANT_URL", cloudant_data["url"])
                    if "apikey" in cloudant_data:
                        env_vars.setdefault("IAM_APIKEY", cloudant_data["apikey"])
                        env_vars.setdefault("CLOUDANT_APIKEY", cloudant_data["apikey"])
                    if "username" in cloudant_data:
                        env_vars.setdefault("CLOUDANT_USERNAME", cloudant_data["username"])
                    if "password" in cloudant_data:
                        env_vars.setdefault("CLOUDANT_PASSWORD", cloudant_data["password"])
            except Exception:
                pass

        # Parse key=value lines
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                # Normalize common naming variations
                if k in ("CLOUDANT_CREDENTAILS", "CLOUDANT_CREDENTIALS"):
                    if v.startswith("{") and v.endswith("}"):
                        try:
                            d = json.loads(v)
                            if "url" in d: env_vars.setdefault("CLOUDANT_URL", d["url"])
                            if "apikey" in d: env_vars.setdefault("IAM_APIKEY", d["apikey"])
                        except Exception:
                            pass
                elif k in ("GITHUBPUBLIC_TOKEN", "GITHUB_PUBLIC_TOKEN"):
                    env_vars["GITHUB_TOKEN"] = v
                    env_vars["GITHUB_PUBLIC_TOKEN"] = v
                else:
                    if v:
                        env_vars[k] = v

    # Propagate back to os.environ
    for k, v in env_vars.items():
        if k not in os.environ and v:
            os.environ[k] = v

    return env_vars
