#!/usr/bin/env python3
"""
AISourceOfTruthBR MCP Management Engine.
Manages MCP servers centrally and synchronizes them to AGY CLI and Claude Code CLI.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
MCP_CONFIG_FILE = REPO_ROOT / "mcp" / "mcp_config.json"

HOME = Path.home()
CLAUDE_JSON = HOME / ".claude.json"
GEMINI_CONFIG_DIR = HOME / ".gemini" / "config"
GEMINI_MCP_FILE = GEMINI_CONFIG_DIR / "mcp_config.json"
COPILOT_DIR = HOME / ".copilot"
COPILOT_MCP_FILE = COPILOT_DIR / "mcp-config.json"


def load_mcp_config():
    """Load the central mcp_config.json file."""
    if not MCP_CONFIG_FILE.exists():
        return {"mcpServers": {}}
    try:
        with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read {MCP_CONFIG_FILE}: {e}")
        return {"mcpServers": {}}


def save_mcp_config(data):
    """Save the central mcp_config.json file with clean formatting."""
    MCP_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MCP_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def sync_to_clis():
    """Synchronize central MCP servers to AGY, Claude Code, and Copilot."""
    data = load_mcp_config()
    servers = data.get("mcpServers", {})

    # 1. Antigravity (AGY) - Ensure symlink to central config
    GEMINI_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if GEMINI_MCP_FILE.is_symlink():
        if GEMINI_MCP_FILE.resolve() != MCP_CONFIG_FILE.resolve():
            GEMINI_MCP_FILE.unlink()
            GEMINI_MCP_FILE.symlink_to(MCP_CONFIG_FILE)
    elif GEMINI_MCP_FILE.exists():
        backup = GEMINI_MCP_FILE.with_suffix(".backup")
        GEMINI_MCP_FILE.rename(backup)
        GEMINI_MCP_FILE.symlink_to(MCP_CONFIG_FILE)
    else:
        GEMINI_MCP_FILE.symlink_to(MCP_CONFIG_FILE)

    # 2. GitHub Copilot - Ensure symlink to central config
    COPILOT_DIR.mkdir(parents=True, exist_ok=True)
    if COPILOT_MCP_FILE.is_symlink():
        if COPILOT_MCP_FILE.resolve() != MCP_CONFIG_FILE.resolve():
            COPILOT_MCP_FILE.unlink()
            COPILOT_MCP_FILE.symlink_to(MCP_CONFIG_FILE)
    elif COPILOT_MCP_FILE.exists():
        backup = COPILOT_MCP_FILE.with_suffix(".backup")
        COPILOT_MCP_FILE.rename(backup)
        COPILOT_MCP_FILE.symlink_to(MCP_CONFIG_FILE)
    else:
        COPILOT_MCP_FILE.symlink_to(MCP_CONFIG_FILE)

    # 3. Claude Code - Update ~/.claude.json mcpServers
    if CLAUDE_JSON.exists():
        try:
            with open(CLAUDE_JSON, "r", encoding="utf-8") as f:
                cdata = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to read ~/.claude.json: {e}")
            cdata = {}
    else:
        cdata = {}

    if "mcpServers" not in cdata or not isinstance(cdata["mcpServers"], dict):
        cdata["mcpServers"] = {}

    # Mirror active servers from central config
    for name, config in servers.items():
        cdata["mcpServers"][name] = config

    # Remove servers that were deleted from central config
    for name in list(cdata["mcpServers"].keys()):
        if name not in servers:
            del cdata["mcpServers"][name]

    # Save ~/.claude.json
    try:
        backup = CLAUDE_JSON.with_suffix(".json.bak")
        if CLAUDE_JSON.exists():
            shutil.copy2(CLAUDE_JSON, backup)
        with open(CLAUDE_JSON, "w", encoding="utf-8") as f:
            json.dump(cdata, f, indent=2)
            f.write("\n")
    except Exception as e:
        print(f"[ERROR] Failed to update ~/.claude.json: {e}")
        return False

    return True


def add_server(name: str, command: str, args: list = None, env: dict = None):
    """Add or update an MCP server and sync automatically."""
    data = load_mcp_config()
    if "mcpServers" not in data:
        data["mcpServers"] = {}

    server_def = {
        "command": command,
        "args": args if args is not None else [],
    }
    if env:
        server_def["env"] = env

    data["mcpServers"][name] = server_def
    save_mcp_config(data)
    print(f"[OK] Added '{name}' to {MCP_CONFIG_FILE}")

    if sync_to_clis():
        print(f"[SUCCESS] Synced '{name}' to Antigravity (AGY) and Claude Code.")
    else:
        print(f"[WARN] Failed to sync to one or more CLI tools.")


def remove_server(name: str):
    """Remove an MCP server and sync automatically."""
    data = load_mcp_config()
    if "mcpServers" not in data or name not in data["mcpServers"]:
        print(f"[WARN] Server '{name}' not found in {MCP_CONFIG_FILE}")
        return

    del data["mcpServers"][name]
    save_mcp_config(data)
    print(f"[OK] Removed '{name}' from {MCP_CONFIG_FILE}")

    if sync_to_clis():
        print(f"[SUCCESS] Removed '{name}' from Antigravity (AGY) and Claude Code.")
    else:
        print(f"[WARN] Failed to sync changes.")


def list_servers():
    """List all registered MCP servers and their synchronization status."""
    data = load_mcp_config()
    servers = data.get("mcpServers", {})

    claude_servers = {}
    if CLAUDE_JSON.exists():
        try:
            with open(CLAUDE_JSON, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                claude_servers = cdata.get("mcpServers", {})
        except Exception:
            pass

    print("\n" + "=" * 80)
    print("  AISourceOfTruthBR - Registered MCP Servers")
    print("=" * 80)
    fmt = "{:<16} | {:<25} | {:<10} | {:<10} | {}"
    print(fmt.format("Server Name", "Command", "AGY Sync", "Claude Sync", "Arguments"))
    print("-" * 80)

    for name, cfg in servers.items():
        cmd = cfg.get("command", "")
        args = " ".join(cfg.get("args", []))
        agy_ok = "YES" if GEMINI_MCP_FILE.is_symlink() else "CHECK"
        claude_ok = "YES" if name in claude_servers else "NO"
        print(fmt.format(name, cmd[-25:], agy_ok, claude_ok, args[:30]))

    print("=" * 80)
    print(f"Total Servers: {len(servers)}\n")


def interactive_add():
    """Prompt user interactively for MCP server details."""
    print("\n--- Add New MCP Server ---")
    name = input("Server Name (e.g. fetch, github): ").strip()
    if not name:
        print("[ERROR] Server name is required.")
        return

    command = input("Command executable (e.g. npx, uvx, /path/to/binary): ").strip()
    if not command:
        print("[ERROR] Command is required.")
        return

    raw_args = input("Arguments (space-separated, optional): ").strip()
    args = raw_args.split() if raw_args else []

    add_server(name, command, args)


def main():
    parser = argparse.ArgumentParser(description="AISourceOfTruthBR MCP Manager")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # add
    p_add = subparsers.add_parser("add", help="Add or update an MCP server")
    p_add.add_argument("name", nargs="?", help="Server name")
    p_add.add_argument("command", nargs="?", help="Executable command")
    p_add.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to command")

    # remove
    p_rm = subparsers.add_parser("remove", aliases=["rm"], help="Remove an MCP server")
    p_rm.add_argument("name", help="Server name to remove")

    # list
    subparsers.add_parser("list", aliases=["ls"], help="List all registered MCP servers")

    # sync
    subparsers.add_parser("sync", help="Synchronize all MCP servers to installed CLIs")

    args = parser.parse_args()

    if args.action == "add":
        if args.name and args.command:
            add_server(args.name, args.command, args.args)
        elif not args.name:
            interactive_add()
        else:
            print("[ERROR] Must provide command or run interactively.")
    elif args.action in ("remove", "rm"):
        remove_server(args.name)
    elif args.action in ("list", "ls"):
        list_servers()
    elif args.action == "sync":
        if sync_to_clis():
            print("[SUCCESS] Synchronized all MCP servers.")
    else:
        list_servers()


if __name__ == "__main__":
    main()
