#!/usr/bin/env python3
"""
AISourceOfTruthBR Setup and Synchronization Engine.
Unified configuration installer for AGY CLI, Claude Code CLI, and GitHub Copilot CLI.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BRAIN_FILE = REPO_ROOT / "AIBrain.md"
SKILLS_DIR = REPO_ROOT / "skills"
MCP_CONFIG_FILE = REPO_ROOT / "mcp" / "mcp_config.json"

HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
CLAUDE_JSON = HOME / ".claude.json"
GEMINI_CONFIG_DIR = HOME / ".gemini" / "config"
COPILOT_CONFIG_DIR = HOME / ".config" / "github-copilot"
COPILOT_DIR = HOME / ".copilot"
GITHUB_GLOBAL_DIR = HOME / ".github"


def run_command(cmd, shell=True, check=False):
    """Run a shell command safely."""
    try:
        res = subprocess.run(cmd, shell=shell, check=check, capture_output=True, text=True)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def is_tool_installed(name):
    """Check if a binary exists in system PATH."""
    return shutil.which(name) is not None


def ensure_symlink(source: Path, target: Path):
    """Create a symbolic link safely with automatic backup."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        if target.resolve() == source.resolve():
            print(f"  [OK] Link already valid: {target} -> {source}")
            return
        target.unlink()
    elif target.exists():
        backup_path = target.with_suffix(f"{target.suffix}.backup")
        print(f"  [INFO] Backing up existing {target} to {backup_path}")
        if backup_path.exists():
            if backup_path.is_dir():
                shutil.rmtree(backup_path)
            else:
                backup_path.unlink()
        target.rename(backup_path)

    os.symlink(source, target)
    print(f"  [CREATED] Symlink: {target} -> {source}")


def install_tools(interactive=True, install_copilot_flag=False):
    """Check and install CLI assistants if missing."""
    print("\n==> Checking AI CLI Tools...")

    # 1. Claude Code CLI
    if is_tool_installed("claude"):
        print("  [OK] Claude Code CLI is installed.")
    else:
        print("  [INSTALL] Installing Claude Code CLI...")
        code, out, err = run_command("curl -fsSL https://claude.ai/install.sh | bash")
        if code == 0:
            print("  [SUCCESS] Installed Claude Code CLI.")
        else:
            print(f"  [WARN] Failed to install Claude Code via curl ({err}). Trying npm...")
            run_command("npm install -g @anthropic-ai/claude-code")

    # 2. Antigravity / Gemini CLI
    if is_tool_installed("agy"):
        print("  [OK] Antigravity (agy) CLI is installed.")
    else:
        print("  [INSTALL] Installing Antigravity CLI...")
        code, out, err = run_command("curl -fsSL https://antigravity.google/cli/install.sh | bash")
        if code == 0:
            print("  [SUCCESS] Installed Antigravity CLI.")
        else:
            print(f"  [ERROR] Could not install Antigravity CLI: {err}")

    # 3. GitHub Copilot CLI (Optional)
    if is_tool_installed("copilot") or is_tool_installed("github-copilot-cli"):
        print("  [OK] GitHub Copilot CLI is installed.")
    else:
        should_install = install_copilot_flag
        if not should_install and interactive and sys.stdin.isatty():
            choice = input("  Install GitHub Copilot CLI? [y/N]: ").strip().lower()
            should_install = choice in ("y", "yes")

        if should_install:
            print("  [INSTALL] Installing GitHub Copilot CLI...")
            if is_tool_installed("brew"):
                code, _, err = run_command("brew install --cask copilot-cli")
                if code == 0:
                    print("  [SUCCESS] Installed GitHub Copilot CLI via Homebrew.")
                else:
                    print(f"  [WARN] Homebrew install failed ({err}). Trying npm...")
                    run_command("npm install -g @github/copilot")
            elif is_tool_installed("npm"):
                run_command("npm install -g @github/copilot")
            else:
                print("  [WARN] Neither Homebrew nor npm available to install Copilot CLI.")
        else:
            print("  [SKIP] Skipping GitHub Copilot CLI installation.")


def sync_rules():
    """Sync AIBrain.md across all assistants."""
    print("\n==> Syncing Global Rules (AIBrain.md)...")
    if not BRAIN_FILE.exists():
        print(f"  [ERROR] AIBrain.md not found at {BRAIN_FILE}")
        return

    # Claude Code
    ensure_symlink(BRAIN_FILE, CLAUDE_DIR / "CLAUDE.md")

    # Antigravity / Gemini
    ensure_symlink(BRAIN_FILE, GEMINI_CONFIG_DIR / "GEMINI.md")

    # GitHub Copilot
    ensure_symlink(BRAIN_FILE, COPILOT_DIR / "AGENTS.md")
    ensure_symlink(BRAIN_FILE, COPILOT_CONFIG_DIR / "copilot-instructions.md")
    ensure_symlink(BRAIN_FILE, GITHUB_GLOBAL_DIR / "copilot-instructions.md")


def sync_skills():
    """Sync skills directory across Claude, Antigravity, and Copilot."""
    print("\n==> Syncing Skills Library...")
    if not SKILLS_DIR.exists():
        print(f"  [ERROR] Skills directory not found at {SKILLS_DIR}")
        return

    # Claude Code skills
    ensure_symlink(SKILLS_DIR, CLAUDE_DIR / "skills")

    # Antigravity skills
    ensure_symlink(SKILLS_DIR, GEMINI_CONFIG_DIR / "skills")

    # GitHub Copilot skills
    ensure_symlink(SKILLS_DIR, COPILOT_DIR / "skills")


def sync_mcp():
    """Sync and configure MCP servers for Antigravity, Claude Code, and Copilot."""
    print("\n==> Syncing MCP Servers...")
    if not MCP_CONFIG_FILE.exists():
        print(f"  [ERROR] MCP config not found at {MCP_CONFIG_FILE}")
        return

    with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
        unified_mcp = json.load(f)

    # 1. Antigravity / Gemini MCP
    ensure_symlink(MCP_CONFIG_FILE, GEMINI_CONFIG_DIR / "mcp_config.json")

    # 2. GitHub Copilot MCP
    ensure_symlink(MCP_CONFIG_FILE, COPILOT_DIR / "mcp-config.json")

    # 2. Claude Code MCP (~/.claude.json)
    if CLAUDE_JSON.exists():
        try:
            with open(CLAUDE_JSON, "r", encoding="utf-8") as f:
                claude_data = json.load(f)
        except Exception as e:
            print(f"  [WARN] Could not read ~/.claude.json: {e}")
            claude_data = {}

        if "mcpServers" not in claude_data or not isinstance(claude_data["mcpServers"], dict):
            claude_data["mcpServers"] = {}

        servers_added = 0
        for name, config in unified_mcp.get("mcpServers", {}).items():
            if name not in claude_data["mcpServers"]:
                claude_data["mcpServers"][name] = config
                servers_added += 1
            else:
                # Merge or keep
                claude_data["mcpServers"][name].update(config)

        backup_file = CLAUDE_JSON.with_suffix(".json.bak")
        shutil.copy2(CLAUDE_JSON, backup_file)
        with open(CLAUDE_JSON, "w", encoding="utf-8") as f:
            json.dump(claude_data, f, indent=2)
        print(f"  [OK] Updated ~/.claude.json with MCP servers ({len(unified_mcp.get('mcpServers', {}))} active).")
    else:
        # Create minimal ~/.claude.json
        claude_data = {"mcpServers": unified_mcp.get("mcpServers", {})}
        with open(CLAUDE_JSON, "w", encoding="utf-8") as f:
            json.dump(claude_data, f, indent=2)
        print("  [CREATED] ~/.claude.json with MCP servers.")


def main():
    parser = argparse.ArgumentParser(description="AISourceOfTruthBR Setup & Sync Engine")
    parser.add_argument("--skip-tools", action="store_true", help="Skip checking/installing CLI tools")
    parser.add_argument("--install-copilot", action="store_true", help="Install GitHub Copilot CLI without prompt")
    parser.add_argument("--verify", action="store_true", help="Run verification checks after setup")
    args = parser.parse_args()

    print("==================================================")
    print("  AISourceOfTruthBR - AI Configuration Setup")
    print("==================================================")

    if not args.skip_tools:
        install_tools(interactive=True, install_copilot_flag=args.install_copilot)

    sync_rules()
    sync_skills()
    sync_mcp()

    print("\n==> Synchronization finished successfully!")

    if args.verify:
        verify_script = REPO_ROOT / "verify.py"
        if verify_script.exists():
            subprocess.run([sys.executable, str(verify_script)])


if __name__ == "__main__":
    main()
