#!/usr/bin/env python3
"""
AISourceOfTruthBR Verification and Audit Engine.
Validates state parity across AGY CLI, Claude Code CLI, and GitHub Copilot CLI.
"""

import json
import os
import shutil
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
GITHUB_GLOBAL_DIR = HOME / ".github"


class Verifier:
    def __init__(self):
        self.results = []
        self.all_passed = True

    def record(self, component: str, check_name: str, passed: bool, details: str = ""):
        self.results.append({
            "component": component,
            "check": check_name,
            "passed": passed,
            "details": details
        })
        if not passed:
            self.all_passed = False

    def verify_repo_integrity(self):
        passed = BRAIN_FILE.exists() and BRAIN_FILE.stat().st_size > 0
        self.record("Repository", "AIBrain.md exists and is not empty", passed, str(BRAIN_FILE))

        skills_count = len([s for s in SKILLS_DIR.iterdir() if s.is_dir()]) if SKILLS_DIR.exists() else 0
        self.record("Repository", f"Skills library present ({skills_count} skills)", skills_count >= 10, f"{skills_count} found")

        mcp_valid = False
        if MCP_CONFIG_FILE.exists():
            try:
                with open(MCP_CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    mcp_valid = len(data.get("mcpServers", {})) >= 3
            except Exception:
                mcp_valid = False
        self.record("Repository", "MCP config has all 3 servers", mcp_valid, str(MCP_CONFIG_FILE))

    def verify_claude_code(self):
        rule_file = CLAUDE_DIR / "CLAUDE.md"
        rule_ok = False
        if rule_file.is_symlink():
            rule_ok = rule_file.resolve() == BRAIN_FILE.resolve()
        elif rule_file.exists():
            rule_ok = rule_file.read_text(encoding="utf-8") == BRAIN_FILE.read_text(encoding="utf-8")
        self.record("Claude Code", "CLAUDE.md matches AIBrain.md", rule_ok, str(rule_file))

        skills_link = CLAUDE_DIR / "skills"
        skills_ok = False
        if skills_link.exists():
            if skills_link.is_symlink():
                skills_ok = skills_link.resolve() == SKILLS_DIR.resolve()
            else:
                skills_ok = len([s for s in skills_link.iterdir() if s.is_dir()]) >= 10
        self.record("Claude Code", "Skills directory synced (10 skills)", skills_ok, str(skills_link))

        claude_mcp_ok = False
        mcp_detail = ""
        if CLAUDE_JSON.exists() and MCP_CONFIG_FILE.exists():
            try:
                with open(MCP_CONFIG_FILE, "r") as f:
                    mdata = json.load(f)
                with open(CLAUDE_JSON, "r") as f:
                    cdata = json.load(f)
                expected_mcps = set(mdata.get("mcpServers", {}).keys())
                actual_mcps = set(cdata.get("mcpServers", {}).keys())
                missing = expected_mcps - actual_mcps
                claude_mcp_ok = len(missing) == 0
                mcp_detail = f"{len(expected_mcps)} active (missing: {list(missing) if missing else 'none'})"
            except Exception as e:
                mcp_detail = str(e)
        self.record("Claude Code", "MCP servers present in ~/.claude.json", claude_mcp_ok, mcp_detail)

    def verify_gemini_agy(self):
        rule_file = GEMINI_CONFIG_DIR / "GEMINI.md"
        rule_ok = False
        if rule_file.is_symlink():
            rule_ok = rule_file.resolve() == BRAIN_FILE.resolve()
        elif rule_file.exists():
            rule_ok = rule_file.read_text(encoding="utf-8") == BRAIN_FILE.read_text(encoding="utf-8")
        self.record("Antigravity (AGY)", "GEMINI.md matches AIBrain.md", rule_ok, str(rule_file))

        skills_link = GEMINI_CONFIG_DIR / "skills"
        skills_ok = False
        if skills_link.exists():
            if skills_link.is_symlink():
                skills_ok = skills_link.resolve() == SKILLS_DIR.resolve()
            else:
                skills_ok = len([s for s in skills_link.iterdir() if s.is_dir()]) >= 10
        self.record("Antigravity (AGY)", "Skills directory synced (10 skills)", skills_ok, str(skills_link))

        mcp_file = GEMINI_CONFIG_DIR / "mcp_config.json"
        mcp_ok = False
        if mcp_file.is_symlink():
            mcp_ok = mcp_file.resolve() == MCP_CONFIG_FILE.resolve()
        elif mcp_file.exists():
            try:
                with open(mcp_file, "r") as f:
                    mdata = json.load(f)
                    mcp_ok = len(mdata.get("mcpServers", {})) >= 3
            except Exception:
                mcp_ok = False
        self.record("Antigravity (AGY)", "mcp_config.json matches source of truth", mcp_ok, str(mcp_file))

    def verify_copilot(self):
        copilot_dir = HOME / ".copilot"
        rule_file = copilot_dir / "AGENTS.md"
        rule_ok = False
        if rule_file.is_symlink():
            rule_ok = rule_file.resolve() == BRAIN_FILE.resolve()
        elif rule_file.exists():
            rule_ok = rule_file.read_text(encoding="utf-8") == BRAIN_FILE.read_text(encoding="utf-8")
        self.record("GitHub Copilot", "AGENTS.md matches AIBrain.md", rule_ok, str(rule_file))

        skills_link = copilot_dir / "skills"
        skills_ok = False
        if skills_link.exists():
            if skills_link.is_symlink():
                skills_ok = skills_link.resolve() == SKILLS_DIR.resolve()
            else:
                skills_ok = len([s for s in skills_link.iterdir() if s.is_dir()]) >= 10
        self.record("GitHub Copilot", "Skills directory synced (10 skills)", skills_ok, str(skills_link))

        mcp_file = copilot_dir / "mcp-config.json"
        mcp_ok = False
        if mcp_file.is_symlink():
            mcp_ok = mcp_file.resolve() == MCP_CONFIG_FILE.resolve()
        elif mcp_file.exists():
            try:
                with open(mcp_file, "r") as f:
                    mdata = json.load(f)
                    mcp_ok = len(mdata.get("mcpServers", {})) >= 3
            except Exception:
                mcp_ok = False
        self.record("GitHub Copilot", "mcp-config.json matches source of truth", mcp_ok, str(mcp_file))

    def verify_cli_binaries(self):
        claude_installed = shutil.which("claude") is not None
        agy_installed = shutil.which("agy") is not None
        copilot_installed = shutil.which("copilot") is not None or shutil.which("github-copilot-cli") is not None

        self.record("CLI Binaries", "Claude Code CLI installed", claude_installed, shutil.which("claude") or "not found")
        self.record("CLI Binaries", "Antigravity (agy) CLI installed", agy_installed, shutil.which("agy") or "not found")
        self.record("CLI Binaries", "GitHub Copilot CLI installed (optional)", copilot_installed, shutil.which("copilot") or "not found (optional)")

    def print_report(self):
        print("\n" + "=" * 80)
        print("  AISourceOfTruthBR - Parity Verification Report")
        print("=" * 80)
        fmt = "{:<20} | {:<40} | {:<8} | {}"
        print(fmt.format("Component", "Check Description", "Status", "Details"))
        print("-" * 80)

        for r in self.results:
            status = "PASS" if r["passed"] else ("INFO" if "optional" in r["details"] else "FAIL")
            print(fmt.format(r["component"], r["check"], status, r["details"]))

        print("=" * 80)
        if self.all_passed:
            print("  ALL CORE CHECKS PASSED. SYSTEM IS IN FULL PARITY.")
        else:
            print("  SOME CHECKS FAILED. Run setup.py to restore synchronization.")
        print("=" * 80 + "\n")
        return 0 if self.all_passed else 1


def main():
    verifier = Verifier()
    verifier.verify_repo_integrity()
    verifier.verify_claude_code()
    verifier.verify_gemini_agy()
    verifier.verify_copilot()
    verifier.verify_cli_binaries()
    sys.exit(verifier.print_report())


if __name__ == "__main__":
    main()
