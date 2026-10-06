#!/usr/bin/env python3
"""
deploy.py — Deploy dist/ bundle to gh-pages branch on github.ibm.com.
Follows the deployment pattern in CONNECTIVITY-PLAN.md.
"""

import os
import sys
import subprocess
import shutil

sys.path.insert(0, os.path.dirname(__file__))
from env_loader import load_env_config

def run_cmd(cmd, cwd=None):
    print(f"[*] Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Info/Notice (code {res.returncode}): {res.stderr.strip()}")
        return False, res.stderr.strip()
    return True, res.stdout.strip()

def deploy():
    env_vars = load_env_config()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dist_dir = os.path.join(root_dir, "dist")

    print("=" * 60)
    print("IBM Earnings Dashboard Deployment Pipeline")
    print("=" * 60)

    # 1. Run build script with properly quoted executable and script path
    print("\n[1/3] Building production release bundle...")
    build_script = os.path.join(os.path.dirname(__file__), "build.py")
    ok, out = run_cmd(f'"{sys.executable}" "{build_script}"', cwd=root_dir)
    if not ok:
        print("[FAIL] Build step failed.")
        sys.exit(1)

    index_file = os.path.join(dist_dir, "index.html")
    if not os.path.exists(index_file):
        print(f"[!] Error: {index_file} not found.")
        sys.exit(1)

    print("\n[2/3] Checking Git repository in ibm-earnings-dashboard...")
    git_dir = os.path.join(root_dir, ".git")
    if not os.path.exists(git_dir):
        print("      Initializing local Git repository...")
        run_cmd("git init", cwd=root_dir)
        run_cmd("git branch -M main", cwd=root_dir)

    # Check git remote
    remote_url = "https://github.ibm.com/Julienne-Charles/ibm_earnings_dashboard.git"
    ok, remotes = run_cmd("git remote -v", cwd=root_dir)
    if "origin" not in remotes:
        run_cmd(f"git remote add origin {remote_url}", cwd=root_dir)
        print(f"      Remote 'origin' set to {remote_url}")

    print("\n[3/3] Deployment instructions for GitHub Pages:")
    print("=" * 60)
    print("To publish live on GitHub Pages (https://pages.github.ibm.com/Julienne-Charles/ibm_earnings_dashboard/):")
    print("\nOption A: Git CLI (Recommended)")
    print(f"  cd \"{root_dir}\"")
    print("  git add .")
    print('  git commit -m "Release v3: Cloudant Sync & SEC Compliance Engine"')
    print("  git push -u origin main")
    print("  git checkout -B gh-pages")
    print("  cp dist/index.html ./index.html")
    print("  git add index.html")
    print('  git commit -m "Deploy to GitHub Pages"')
    print("  git push -u origin gh-pages --force")
    print("  git checkout main")
    print("\nOption B: GitHub Enterprise Web Upload")
    print("  1. Navigate to https://github.ibm.com/Julienne-Charles/ibm_earnings_dashboard")
    print("  2. Switch to (or create) the `gh-pages` branch")
    print(f"  3. Upload the built file: {index_file} as `index.html` at repository root")
    print("  4. Enable GitHub Pages under Settings -> Pages -> Source: 'Deploy from branch (gh-pages / root)'")
    print("=" * 60)

if __name__ == "__main__":
    deploy()
