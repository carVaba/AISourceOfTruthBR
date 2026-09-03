#!/usr/bin/env python3
"""
AISourceOfTruthBR Memory & Rules Management Engine.
Manages global rules and AI memory in AIBrain.md and synchronizes across all assistants.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BRAIN_FILE = REPO_ROOT / "AIBrain.md"

HOME = Path.home()
CLAUDE_RULE = HOME / ".claude" / "CLAUDE.md"
GEMINI_RULE = HOME / ".gemini" / "config" / "GEMINI.md"
COPILOT_RULE = HOME / ".config" / "github-copilot" / "copilot-instructions.md"
COPILOT_AGENT_RULE = HOME / ".copilot" / "AGENTS.md"
GITHUB_RULE = HOME / ".github" / "copilot-instructions.md"

TARGETS = [
    ("Claude Code CLI", CLAUDE_RULE),
    ("Antigravity (AGY) CLI", GEMINI_RULE),
    ("GitHub Copilot CLI (AGENTS.md)", COPILOT_AGENT_RULE),
    ("GitHub Copilot CLI (~/.config)", COPILOT_RULE),
    ("GitHub Copilot CLI (~/.github)", GITHUB_RULE),
]


def ensure_symlinks():
    """Ensure all assistant rule files point directly to AIBrain.md."""
    if not BRAIN_FILE.exists():
        print(f"[ERROR] AIBrain.md not found at {BRAIN_FILE}")
        return False

    print("\n==> Synchronizing AI Memory / Rules (AIBrain.md)...")
    for name, target in TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            if target.resolve() != BRAIN_FILE.resolve():
                target.unlink()
                target.symlink_to(BRAIN_FILE)
                print(f"  [FIXED] Repaired symlink for {name}: {target} -> {BRAIN_FILE}")
            else:
                print(f"  [OK] {name} is linked to AIBrain.md")
        elif target.exists():
            backup = target.with_suffix(".backup")
            print(f"  [INFO] Backing up existing {target} to {backup}")
            if backup.exists():
                if backup.is_dir():
                    shutil.rmtree(backup)
                else:
                    backup.unlink()
            target.rename(backup)
            target.symlink_to(BRAIN_FILE)
            print(f"  [CREATED] Symlink for {name}: {target} -> {BRAIN_FILE}")
        else:
            target.symlink_to(BRAIN_FILE)
            print(f"  [CREATED] Symlink for {name}: {target} -> {BRAIN_FILE}")

    print("[SUCCESS] All AI assistants share the exact same memory and rules in real time.\n")
    return True


def show_status():
    """Show status of memory file and assistant links."""
    print("\n" + "=" * 80)
    print("  AISourceOfTruthBR - Memory & Rules Status (AIBrain.md)")
    print("=" * 80)
    fmt = "{:<32} | {:<10} | {}"
    print(fmt.format("Assistant", "Status", "Resolved Path"))
    print("-" * 80)

    for name, target in TARGETS:
        if target.is_symlink() and target.resolve() == BRAIN_FILE.resolve():
            status = "SYNCED"
            detail = f"Symlinked -> {BRAIN_FILE.name}"
        elif target.exists():
            status = "LOCAL FILE"
            detail = f"Separate file ({target.stat().st_size} bytes)"
        else:
            status = "MISSING"
            detail = "Not created yet"
        print(fmt.format(name, status, detail))

    print("=" * 80)
    print("Editing AIBrain.md updates all synced assistants instantly.\n")


def edit_brain():
    """Open AIBrain.md in nvim."""
    editor = shutil.which("nvim") or "nvim"
    try:
        subprocess.run([editor, str(BRAIN_FILE)])
        ensure_symlinks()
    except Exception as e:
        print(f"[ERROR] Could not open editor: {e}")


def add_rule(rule_text: str):
    """Append a new rule directly to AIBrain.md."""
    if not BRAIN_FILE.exists():
        print(f"[ERROR] AIBrain.md not found at {BRAIN_FILE}")
        return

    rule_formatted = rule_text.strip()
    if not rule_formatted.startswith("- "):
        rule_formatted = f"- {rule_formatted}"

    with open(BRAIN_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{rule_formatted}\n")

    print(f"[SUCCESS] Appended rule to AIBrain.md:\n  {rule_formatted}")
    ensure_symlinks()


def show_brain():
    """Display the contents of AIBrain.md."""
    if not BRAIN_FILE.exists():
        print(f"[ERROR] AIBrain.md not found at {BRAIN_FILE}")
        return
    print(BRAIN_FILE.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="AISourceOfTruthBR Memory & Rules Manager")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # status
    subparsers.add_parser("status", help="Show memory sync status across all assistants")

    # edit
    subparsers.add_parser("edit", help="Open AIBrain.md in nvim")

    # show
    subparsers.add_parser("show", help="Display AIBrain.md contents")

    # add
    p_add = subparsers.add_parser("add", help="Append a rule to AIBrain.md")
    p_add.add_argument("rule", help="Rule text to append")

    # sync
    subparsers.add_parser("sync", help="Synchronize and repair rule symlinks")

    args = parser.parse_args()

    if args.action == "edit":
        edit_brain()
    elif args.action == "show":
        show_brain()
    elif args.action == "add":
        add_rule(args.rule)
    elif args.action == "sync":
        ensure_symlinks()
    else:
        show_status()


if __name__ == "__main__":
    main()
