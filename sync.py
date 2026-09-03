#!/usr/bin/env python3
"""
AISourceOfTruthBR Sync Engine.
Reconciles and synchronizes skills, brain (memory/rules), and MCP servers across all assistants.

Usage:
  ./sync.py skill     Sync skills across Claude, AGY, and Copilot
  ./sync.py brain     Sync memory/rules across Claude, AGY, and Copilot
  ./sync.py mcp       Sync MCP servers across Claude, AGY, and Copilot
  ./sync.py all       Sync everything and run verification
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
REPO_SKILLS = REPO_ROOT / "skills"
REPO_BRAIN = REPO_ROOT / "AIBrain.md"
REPO_MCP = REPO_ROOT / "mcp" / "mcp_config.json"

HOME = Path.home()

# Skills paths
CLAUDE_SKILLS = HOME / ".claude" / "skills"
GEMINI_SKILLS = HOME / ".gemini" / "config" / "skills"
COPILOT_SKILLS = HOME / ".copilot" / "skills"

# Memory / Rule paths
CLAUDE_RULE = HOME / ".claude" / "CLAUDE.md"
GEMINI_RULE = HOME / ".gemini" / "config" / "GEMINI.md"
COPILOT_AGENT_RULE = HOME / ".copilot" / "AGENTS.md"
COPILOT_CONFIG_RULE = HOME / ".config" / "github-copilot" / "copilot-instructions.md"
GITHUB_GLOBAL_RULE = HOME / ".github" / "copilot-instructions.md"

# MCP paths
CLAUDE_JSON = HOME / ".claude.json"
GEMINI_MCP = HOME / ".gemini" / "config" / "mcp_config.json"
COPILOT_MCP = HOME / ".copilot" / "mcp-config.json"


def ensure_symlink(source: Path, target: Path):
    """Enforce a symbolic link, backing up conflicting plain files/dirs."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        if target.resolve() == source.resolve():
            return False
        target.unlink()
    elif target.exists():
        backup = target.with_suffix(f"{target.suffix}.backup")
        if backup.exists():
            if backup.is_dir():
                shutil.rmtree(backup)
            else:
                backup.unlink()
        target.rename(backup)

    os.symlink(source, target)
    return True


# ==============================================================================
# 1. SKILLS SYNCHRONIZATION
# ==============================================================================
def sync_skill():
    print("\n" + "=" * 60)
    print("  Syncing Skills across Claude, AGY, and Copilot")
    print("=" * 60)

    REPO_SKILLS.mkdir(parents=True, exist_ok=True)
    targets = [
        ("Claude Code", CLAUDE_SKILLS),
        ("Antigravity (AGY)", GEMINI_SKILLS),
        ("GitHub Copilot", COPILOT_SKILLS),
    ]

    imported_skills = []

    # Step 1: Check if any assistant has physical files that were added or modified
    for name, path in targets:
        if path.exists() and not path.is_symlink() and path.is_dir():
            print(f"  [DISCOVERY] Found detached physical directory at {path}")
            for item in path.iterdir():
                if item.is_dir():
                    dest = REPO_SKILLS / item.name
                    if not dest.exists():
                        shutil.copytree(item, dest)
                        imported_skills.append(item.name)
                        print(f"  [IMPORTED] Adopted skill '{item.name}' from {name}")
                    else:
                        # Copy newer files into source of truth
                        shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                        imported_skills.append(item.name)
                        print(f"  [UPDATED] Synchronized skill '{item.name}' from {name}")

    # Step 2: Enforce symlinks for all assistants
    for name, path in targets:
        changed = ensure_symlink(REPO_SKILLS, path)
        status = "RE-LINKED" if changed else "IN SYNC"
        print(f"  [{status}] {name} skills -> {path}")

    skills_count = len([s for s in REPO_SKILLS.iterdir() if s.is_dir()])
    print(f"\n[SUCCESS] Skills synchronization complete. {skills_count} skills shared across all assistants.")
    return True


# ==============================================================================
# 2. BRAIN (MEMORY & RULES) SYNCHRONIZATION
# ==============================================================================
def sync_brain():
    print("\n" + "=" * 60)
    print("  Syncing Memory & Rules (AIBrain.md)")
    print("=" * 60)

    if not REPO_BRAIN.exists():
        print(f"[ERROR] {REPO_BRAIN} does not exist.")
        return False

    targets = [
        ("Claude Code", CLAUDE_RULE),
        ("Antigravity (AGY)", GEMINI_RULE),
        ("GitHub Copilot (AGENTS.md)", COPILOT_AGENT_RULE),
        ("GitHub Copilot (~/.config)", COPILOT_CONFIG_RULE),
        ("GitHub Copilot (~/.github)", GITHUB_GLOBAL_RULE),
    ]

    # Step 1: Detect if any assistant file was detached and modified
    adopted_content = None
    for name, path in targets:
        if path.exists() and not path.is_symlink() and path.is_file():
            content = path.read_text(encoding="utf-8")
            repo_content = REPO_BRAIN.read_text(encoding="utf-8")
            if content != repo_content and len(content.strip()) > len(repo_content.strip()):
                print(f"  [DISCOVERY] Found modified standalone rule file at {name} ({path})")
                REPO_BRAIN.write_text(content, encoding="utf-8")
                adopted_content = name
                print(f"  [ADOPTED] Updated AIBrain.md from {name}")

    # Step 2: Enforce symlinks for all assistants
    for name, path in targets:
        changed = ensure_symlink(REPO_BRAIN, path)
        status = "RE-LINKED" if changed else "IN SYNC"
        print(f"  [{status}] {name} -> {path}")

    print(f"\n[SUCCESS] Memory & rules synchronization complete. All assistants point to AIBrain.md.")
    return True


# ==============================================================================
# 3. MCP SYNCHRONIZATION
# ==============================================================================
def sync_mcp():
    print("\n" + "=" * 60)
    print("  Syncing MCP Servers across Claude, AGY, and Copilot")
    print("=" * 60)

    # Step 1: Load central MCP config
    if REPO_MCP.exists():
        with open(REPO_MCP, "r", encoding="utf-8") as f:
            central_mcp = json.load(f)
    else:
        central_mcp = {"mcpServers": {}}

    if "mcpServers" not in central_mcp:
        central_mcp["mcpServers"] = {}

    # Step 2: Reconcile servers added inside ~/.claude.json
    if CLAUDE_JSON.exists():
        try:
            with open(CLAUDE_JSON, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            claude_mcps = cdata.get("mcpServers", {})
            for sname, scfg in claude_mcps.items():
                if sname not in central_mcp["mcpServers"]:
                    central_mcp["mcpServers"][sname] = scfg
                    print(f"  [IMPORTED] Imported new MCP server '{sname}' from Claude Code.")
        except Exception as e:
            print(f"  [WARN] Could not inspect ~/.claude.json: {e}")

    # Step 3: Save updated central config
    REPO_MCP.parent.mkdir(parents=True, exist_ok=True)
    with open(REPO_MCP, "w", encoding="utf-8") as f:
        json.dump(central_mcp, f, indent=2)
        f.write("\n")

    # Step 4: Ensure symlinks for AGY and Copilot
    ensure_symlink(REPO_MCP, GEMINI_MCP)
    print(f"  [IN SYNC] Antigravity (AGY) MCP -> {GEMINI_MCP}")

    ensure_symlink(REPO_MCP, COPILOT_MCP)
    print(f"  [IN SYNC] GitHub Copilot MCP -> {COPILOT_MCP}")

    # Step 5: Update Claude Code ~/.claude.json with all servers
    if CLAUDE_JSON.exists():
        try:
            with open(CLAUDE_JSON, "r", encoding="utf-8") as f:
                cdata = json.load(f)
        except Exception:
            cdata = {}
    else:
        cdata = {}

    if "mcpServers" not in cdata or not isinstance(cdata["mcpServers"], dict):
        cdata["mcpServers"] = {}

    for sname, scfg in central_mcp["mcpServers"].items():
        cdata["mcpServers"][sname] = scfg

    for sname in list(cdata["mcpServers"].keys()):
        if sname not in central_mcp["mcpServers"]:
            del cdata["mcpServers"][sname]

    with open(CLAUDE_JSON, "w", encoding="utf-8") as f:
        json.dump(cdata, f, indent=2)
        f.write("\n")
    print(f"  [IN SYNC] Claude Code MCP -> ~/.claude.json ({len(central_mcp['mcpServers'])} servers active)")

    print(f"\n[SUCCESS] MCP synchronization complete. {len(central_mcp['mcpServers'])} servers active across all assistants.")
    return True


# ==============================================================================
# MAIN CLI DISPATCHER
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="AISourceOfTruthBR Sync Engine: Reconcile and synchronize Skills, Brain, and MCP."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=["skill", "skills", "brain", "memory", "mcp", "all"],
        help="Target component to sync: skill, brain, mcp, or all (default: all)"
    )
    args = parser.parse_args()

    target = args.target.lower()

    if target in ("skill", "skills"):
        sync_skill()
    elif target in ("brain", "memory"):
        sync_brain()
    elif target == "mcp":
        sync_mcp()
    elif target == "all":
        sync_skill()
        sync_brain()
        sync_mcp()
        # Run verify report at the end
        verify_script = REPO_ROOT / "verify.py"
        if verify_script.exists():
            subprocess.run([sys.executable, str(verify_script)])


if __name__ == "__main__":
    main()
