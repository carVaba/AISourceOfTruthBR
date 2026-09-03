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
./setup.sh
```

The script will automatically:
1. Verify / install `claude` (Claude Code CLI) and `agy` (Antigravity CLI).
2. Prompt if you want to install `copilot` (GitHub Copilot CLI).
3. Symlink `AIBrain.md` as the global instruction file for Claude, AGY, and Copilot.
4. Symlink the unified `skills/` library (10 skills) to all assistants.
5. Configure unified MCP servers (`glab`, `proxyman`, `XcodeBuildMCP`) for both AGY and Claude Code.
6. Run verification to confirm parity across all tools.

---

## Repository Structure

```
AISourceOfTruthBR/
├── AIBrain.md          # Merged primary rule definition (Claude + Gemini + Copilot)
├── CLAUDE.md           # Original Claude Code global instructions (reference)
├── GEMINI.md           # Original Gemini / AGY global instructions (reference)
├── setup.py            # Automated setup and synchronization engine
├── setup.sh            # Lightweight shell entrypoint
├── verify.py           # Configuration parity audit and test suite
├── mcp/
│   ├── mcp_config.json        # Consolidated MCP server registry (glab, proxyman, XcodeBuildMCP)
│   ├── claude_mcp.json        # Claude-specific MCP reference
│   └── gemini_mcp_config.json # AGY / Gemini MCP reference
└── skills/                    # Unified skills library (10 skills)
    ├── audit-xcode-security-settings/
    ├── proxyman-download-setup/
    ├── proxyman-mcp-setup/
    ├── proxyman-traffic-debugging/
    ├── swift-api-design-guidelines-skill/
    ├── swift-architecture-skill-v2/
    ├── swiftui-specialist/
    ├── tldr/
    ├── uikit-app-modernization/
    └── xcodebuildmcp-cli/
```

---

## Usage Commands

### Full Setup & Install
```bash
./setup.sh
```

### Sync Only (Skip Tool Installation)
```bash
python3 setup.py --skip-tools
```

### Verify Configuration Parity
```bash
python3 verify.py
```

---

## MCP Server Management

Manage MCP servers centrally in `AISourceOfTruthBR`. Any change syncs immediately to all installed assistants (Antigravity and Claude Code).

### Add an MCP Server
```bash
# Command line:
./mcp.sh add server-name command [arg1 arg2 ...]

# Example:
./mcp.sh add fetch uvx mcp-server-fetch

# Interactive mode (prompts for details):
./mcp.sh add
```

### List Active MCP Servers
```bash
./mcp.sh list
```

### Remove an MCP Server
```bash
./mcp.sh remove server-name
```

### Force Sync All MCP Servers
```bash
./mcp.sh sync
```

