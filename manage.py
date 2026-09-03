#!/usr/bin/env python3
"""
AISourceOfTruthBR Unified Management CLI.
Single entrypoint to manage MCP servers, Skills, Memory/Rules, and Setup.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

SCRIPTS = {
    "sync": REPO_ROOT / "sync.py",
    "mcp": REPO_ROOT / "mcp.py",
    "skills": REPO_ROOT / "skills.py",
    "skill": REPO_ROOT / "skills.py",
    "brain": REPO_ROOT / "brain.py",
    "memory": REPO_ROOT / "brain.py",
    "verify": REPO_ROOT / "verify.py",
    "setup": REPO_ROOT / "setup.py",
}


def print_help():
    print("""
AISourceOfTruthBR - Unified AI Configuration Tool

Usage:
  ./manage.py <command> [subcommand] [arguments...]

Available Commands:
  sync     Force sync components: ./manage.py sync [skill|brain|mcp|all]
  mcp      Manage MCP servers (add, remove, list, sync)
  skills   Manage Skills (list, add, new, remove, sync)
  brain    Manage Memory & Global Rules (status, edit, show, add, sync)
  verify   Run configuration parity audit across all assistants
  setup    Run complete setup or sync on this machine

Examples:
  ./manage.py sync skill
  ./manage.py sync brain
  ./manage.py sync mcp
  ./manage.py sync all
  ./manage.py mcp list
  ./manage.py skills list
  ./manage.py brain status
  ./manage.py verify
""")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    script = SCRIPTS.get(cmd)

    if not script or not script.exists():
        print(f"[ERROR] Unknown command: '{cmd}'")
        print_help()
        sys.exit(1)

    forward_args = [sys.executable, str(script)] + sys.argv[2:]
    res = subprocess.run(forward_args)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
