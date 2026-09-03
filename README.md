# AISourceOfTruthBR

Single source of truth and automated setup engine for AI CLI assistants:
- **AGY CLI** (Google Antigravity)
- **Claude Code CLI** (Anthropic)
- **GitHub Copilot CLI**

## Quick Start (New Mac Setup)

Clone this repository and run the setup script:

```bash
git clone git@github.com:carVaba/AISourceOfTruthBR.git ~/.config/AISourceOfTruthBR
cd ~/.config/AISourceOfTruthBR
./setup.py
```

The script will automatically:
1. Verify / install `claude` (Claude Code CLI) and `agy` (Antigravity CLI).
2. Prompt if you want to install `copilot` (GitHub Copilot CLI).
3. Symlink `AIBrain.md` as the global instruction file for Claude, AGY, and Copilot.
4. Symlink the unified `skills/` library (10 skills) to all assistants.
5. Configure unified MCP servers (`glab`, `proxyman`, `XcodeBuildMCP`) for both AGY and Claude Code.
6. Run verification to confirm parity across all tools.

---

## Unified Management CLI (`./manage.py`)

You can manage MCP servers, Skills, and AI Memory/Rules from the unified `./manage.py` tool:

```bash
# MCP servers
./manage.py mcp list
./manage.py mcp add fetch uvx mcp-server-fetch
./manage.py mcp remove fetch

# Skills
./manage.py skills list
./manage.py skills new my-new-skill
./manage.py skills add /path/to/existing/skill
./manage.py skills remove my-old-skill

# Memory & Global Rules
./manage.py brain status
./manage.py brain edit
./manage.py brain add "New global instruction"
./manage.py brain show

# Verification & Parity Audit
./manage.py verify
```

*(You can also call individual scripts directly: `./mcp.py`, `./skills.py`, `./brain.py`, `./verify.py`).*

---

## How Real-Time Synchronization Works

- **Skills**: `~/.claude/skills` and `~/.gemini/config/skills` are symbolic links pointing directly to `~/.config/AISourceOfTruthBR/skills`. Any skill added or modified here is available immediately to both Claude and AGY without restarting or copying.
- **Memory / Rules**: `~/.claude/CLAUDE.md`, `~/.gemini/config/GEMINI.md`, and Copilot instruction files are symbolic links pointing to `~/.config/AISourceOfTruthBR/AIBrain.md`. Any change made via `./manage.py brain edit` or `./manage.py brain add` updates all assistants immediately.
- **MCP Servers**: Central registry is `mcp/mcp_config.json`. AGY reads it via symlink. Claude Code receives automated updates in `~/.claude.json` whenever you run `./manage.py mcp add` or `./manage.py mcp remove`.

---

## Repository Structure

```
AISourceOfTruthBR/
├── manage.py           # Unified management CLI
├── setup.py            # Automated bootstrap & setup engine
├── mcp.py              # MCP server manager with auto-sync
├── skills.py           # Skills manager with auto-sync
├── brain.py            # AI Memory & Rules manager
├── verify.py           # Parity test suite
├── AIBrain.md          # Unified global rules & memory
├── CLAUDE.md           # Original Claude rules (reference)
├── GEMINI.md           # Original Gemini rules (reference)
├── mcp/
│   └── mcp_config.json # Central MCP server registry
└── skills/             # Central skills directory (10 skills)
```
