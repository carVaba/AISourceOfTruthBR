#!/usr/bin/env python3
"""
AISourceOfTruthBR Skills Management Engine.
Manages skills centrally and synchronizes them to AGY CLI and Claude Code CLI.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / "skills"

HOME = Path.home()
CLAUDE_SKILLS_DIR = HOME / ".claude" / "skills"
GEMINI_SKILLS_DIR = HOME / ".gemini" / "config" / "skills"


def parse_skill_description(skill_path: Path) -> str:
    """Extract description from SKILL.md frontmatter or body."""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return "No SKILL.md file found"

    try:
        content = skill_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        in_frontmatter = False
        desc = ""
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and line.lower().startswith("description:"):
                desc = line.split(":", 1)[1].strip().strip("'\"")
                break
        if desc:
            return desc
        for line in lines:
            if line.strip() and not line.startswith("#") and not line.startswith("---"):
                return line.strip()[:60]
        return "Custom skill"
    except Exception:
        return "Unable to parse description"


def sync_skills():
    """Ensure symlinks for Claude Code and Antigravity point to skills directory."""
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    targets = [
        ("Claude Code", CLAUDE_SKILLS_DIR),
        ("Antigravity (AGY)", GEMINI_SKILLS_DIR),
    ]

    for name, target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            if target.resolve() != SKILLS_DIR.resolve():
                target.unlink()
                target.symlink_to(SKILLS_DIR)
                print(f"[FIXED] Repaired {name} skills symlink: {target} -> {SKILLS_DIR}")
            else:
                print(f"[OK] {name} skills symlink is active: {target}")
        elif target.exists():
            backup = target.with_suffix(".backup")
            print(f"[INFO] Backing up existing {target} to {backup}")
            if backup.exists():
                shutil.rmtree(backup)
            target.rename(backup)
            target.symlink_to(SKILLS_DIR)
            print(f"[CREATED] {name} skills symlink: {target} -> {SKILLS_DIR}")
        else:
            target.symlink_to(SKILLS_DIR)
            print(f"[CREATED] {name} skills symlink: {target} -> {SKILLS_DIR}")

    return True


def list_skills():
    """List all installed skills."""
    if not SKILLS_DIR.exists():
        print("[WARN] Skills directory does not exist.")
        return

    skills = sorted([s for s in SKILLS_DIR.iterdir() if s.is_dir()])
    print("\n" + "=" * 80)
    print("  AISourceOfTruthBR - Installed Skills")
    print("=" * 80)
    fmt = "{:<32} | {}"
    print(fmt.format("Skill Name", "Description"))
    print("-" * 80)

    for skill in skills:
        desc = parse_skill_description(skill)
        print(fmt.format(skill.name, desc[:45]))

    print("=" * 80)
    print(f"Total Skills: {len(skills)}\n")
    print("Status: Both Claude Code and AGY CLI access these skills directly via symlinks.\n")


def add_skill(source_path: str):
    """Import an existing skill folder into the central skills library."""
    src = Path(source_path).resolve()
    if not src.exists() or not src.is_dir():
        print(f"[ERROR] Source folder does not exist or is not a directory: {src}")
        return

    dest = SKILLS_DIR / src.name
    if dest.exists():
        print(f"[WARN] Skill '{src.name}' already exists in {SKILLS_DIR}. Overwriting...")
        shutil.rmtree(dest)

    shutil.copytree(src, dest)
    print(f"[SUCCESS] Imported skill '{src.name}' into {dest}")
    sync_skills()


def new_skill(name: str):
    """Scaffold a new skill directory with a standard SKILL.md template."""
    dest = SKILLS_DIR / name
    if dest.exists():
        print(f"[ERROR] Skill '{name}' already exists at {dest}")
        return

    dest.mkdir(parents=True, exist_ok=True)
    template = f"""---
name: {name}
description: Concise description of what {name} does.
---

# {name}

## Purpose
Describe the purpose of this skill.

## Instructions
1. Step one.
2. Step two.
"""
    (dest / "SKILL.md").write_text(template, encoding="utf-8")
    print(f"[SUCCESS] Created new skill template at {dest / 'SKILL.md'}")
    sync_skills()


def remove_skill(name: str):
    """Remove a skill from the central library."""
    dest = SKILLS_DIR / name
    if not dest.exists():
        print(f"[ERROR] Skill '{name}' not found in {SKILLS_DIR}")
        return

    shutil.rmtree(dest)
    print(f"[SUCCESS] Removed skill '{name}' from central library.")


def main():
    parser = argparse.ArgumentParser(description="AISourceOfTruthBR Skills Manager")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # list
    subparsers.add_parser("list", aliases=["ls"], help="List all installed skills")

    # add
    p_add = subparsers.add_parser("add", help="Import an existing skill directory")
    p_add.add_argument("path", help="Path to skill directory to import")

    # new
    p_new = subparsers.add_parser("new", help="Create a new skill template")
    p_new.add_argument("name", help="Name of new skill")

    # remove
    p_rm = subparsers.add_parser("remove", aliases=["rm"], help="Remove a skill")
    p_rm.add_argument("name", help="Name of skill to remove")

    # sync
    subparsers.add_parser("sync", help="Synchronize / repair skills symlinks")

    args = parser.parse_args()

    if args.action in ("list", "ls") or not args.action:
        list_skills()
    elif args.action == "add":
        add_skill(args.path)
    elif args.action == "new":
        new_skill(args.name)
    elif args.action in ("remove", "rm"):
        remove_skill(args.name)
    elif args.action == "sync":
        sync_skills()


if __name__ == "__main__":
    main()
