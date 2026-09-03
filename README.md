# AISourceOfTruthBR

Unified configuration source of truth for AI command-line assistants:
- **AGY CLI** (Google Antigravity)
- **Claude Code CLI** (Anthropic)
- **GitHub Copilot CLI**

## Repository Structure

```
AISourceOfTruthBR/
├── AIBrain.md          # Merged primary rule definition (Claude + Gemini + Copilot)
├── CLAUDE.md           # Original Claude Code global instructions
├── GEMINI.md           # Original Gemini / AGY global instructions
├── mcp/
│   ├── mcp_config.json        # Consolidated MCP server registry (glab, proxyman, XcodeBuildMCP)
│   ├── claude_mcp.json        # Claude-specific MCP server definitions
│   └── gemini_mcp_config.json # AGY / Gemini MCP server definitions
└── skills/                    # Unified skills library
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

## Setup & Synchronization

### 1. Claude Code CLI
- Global instruction file: `~/.claude/CLAUDE.md` -> link to `AIBrain.md` or `CLAUDE.md`
- Skills directory: `~/.claude/skills/` -> link to `skills/`
- MCP configuration: registered in `~/.claude.json`

### 2. Antigravity / AGY CLI
- Global instruction file: `~/.gemini/config/GEMINI.md` -> link to `AIBrain.md` or `GEMINI.md`
- Skills directory: `~/.gemini/config/skills/` -> link to `skills/`
- MCP configuration: `~/.gemini/config/mcp_config.json` -> link to `mcp/mcp_config.json`

### 3. GitHub Copilot CLI
- Global instruction / skills shared from this repository.
