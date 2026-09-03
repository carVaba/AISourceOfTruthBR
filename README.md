# AISourceOfTruthBR

Single source of truth and automated setup engine for AI CLI assistants:
- **AGY CLI** (Google Antigravity)
- **Claude Code CLI** (Anthropic)
- **GitHub Copilot CLI**

---

## 1. Quick Start (New Mac Setup)

To set up a brand-new Mac from scratch:

```bash
git clone git@github.com:carVaba/AISourceOfTruthBR.git ~/.config/AISourceOfTruthBR
cd ~/.config/AISourceOfTruthBR
./setup.py
```

`./setup.py` automatically performs the following actions:
1. Verifies / installs `claude` (Claude Code CLI) and `agy` (Antigravity CLI).
2. Prompts to install `copilot` (GitHub Copilot CLI) if desired.
3. Links [AIBrain.md](file:///Users/alfbaro-mac-pro/.config/AISourceOfTruthBR/AIBrain.md) as the global instruction file for Claude Code, AGY CLI, and Copilot CLI.
4. Links the unified [skills/](file:///Users/alfbaro-mac-pro/.config/AISourceOfTruthBR/skills) library to all assistants.
5. Injects and synchronizes all MCP servers into both Antigravity and Claude Code.
6. Runs parity verification to validate that all assistants are in sync.

---

## 2. Daily Usage Guide (`./manage.py`)

Manage your entire AI configuration using the unified `./manage.py` CLI:

```bash
cd ~/.config/AISourceOfTruthBR
./manage.py <command> [arguments]
```

### A. MCP Servers (`./manage.py mcp`)
Any change here updates `mcp/mcp_config.json`, Antigravity, and Claude Code automatically.

- **List active MCP servers:**
  ```bash
  ./manage.py mcp list
  ```
- **Add an MCP server (direct):**
  ```bash
  ./manage.py mcp add fetch uvx mcp-server-fetch
  ```
- **Add an MCP server (interactive prompt):**
  ```bash
  ./manage.py mcp add
  ```
- **Remove an MCP server:**
  ```bash
  ./manage.py mcp remove fetch
  ```
- **Force re-sync all MCP servers:**
  ```bash
  ./manage.py mcp sync
  ```

---

### B. Skills (`./manage.py skills`)
Both Claude Code and Antigravity link directly to `skills/`.

- **List all installed skills:**
  ```bash
  ./manage.py skills list
  ```
- **Create a new skill template:**
  ```bash
  ./manage.py skills new my-awesome-skill
  ```
  *(Creates `skills/my-awesome-skill/SKILL.md` ready for you to edit).*
- **Import an existing skill from another folder:**
  ```bash
  ./manage.py skills add ~/Downloads/some-skill
  ```
- **Remove a skill:**
  ```bash
  ./manage.py skills remove my-awesome-skill
  ```
- **Repair / check skill links:**
  ```bash
  ./manage.py skills sync
  ```

---

### C. AI Memory & Global Rules (`./manage.py brain`)
All assistants share [AIBrain.md](file:///Users/alfbaro-mac-pro/.config/AISourceOfTruthBR/AIBrain.md) via symlinks.

- **Check memory synchronization status across all assistants:**
  ```bash
  ./manage.py brain status
  ```
- **Open memory in `nvim` to edit:**
  ```bash
  ./manage.py brain edit
  ```
- **Append a new rule directly:**
  ```bash
  ./manage.py brain add "Always use TypeScript for new web projects."
  ```
- **Print current rules:**
  ```bash
  ./manage.py brain show
  ```
- **Repair / verify memory links:**
  ```bash
  ./manage.py brain sync
  ```

---

### D. Verification & Auditing (`./manage.py verify`)
Audit your machine to ensure all assistants have 100% configuration parity:

```bash
./manage.py verify
```

---

## 3. Multi-Computer Synchronization Workflow

When working across multiple machines (e.g. MacBook Pro and Mac Mini):

### On Computer A (where you made changes):
```bash
cd ~/.config/AISourceOfTruthBR
git add .
git commit -m "Add new MCP server and update rules"
git push origin main
```

### On Computer B (to apply updates):
```bash
cd ~/.config/AISourceOfTruthBR
git pull origin main
./setup.py --skip-tools --verify
```

---

## 4. How Synchronization Works Internally

| Component | Synchronization Mechanism | Effect |
| :--- | :--- | :--- |
| **Skills** | Symbolic links from `~/.claude/skills` and `~/.gemini/config/skills` -> `AISourceOfTruthBR/skills` | Instant. Any new or edited skill is immediately accessible in both CLIs. |
| **Memory / Rules** | Symbolic links from `~/.claude/CLAUDE.md`, `~/.gemini/config/GEMINI.md`, and Copilot files -> `AISourceOfTruthBR/AIBrain.md` | Instant. Editing `AIBrain.md` updates all assistants at the same time. |
| **MCP Servers** | Central registry in `mcp/mcp_config.json`. Symlinked for AGY. Automated JSON injection into `~/.claude.json` for Claude Code. | Instant on `./manage.py mcp add/remove`. |

---

## 5. Repository Structure

```
AISourceOfTruthBR/
├── manage.py           # Unified management CLI
├── setup.py            # Automated bootstrap & setup engine
├── mcp.py              # Dedicated MCP server manager
├── skills.py           # Dedicated Skills manager
├── brain.py            # Dedicated AI Memory & Rules manager
├── verify.py           # Parity test suite
├── AIBrain.md          # Unified global rules & memory
├── CLAUDE.md           # Original Claude rules (reference)
├── GEMINI.md           # Original Gemini rules (reference)
├── mcp/
│   └── mcp_config.json # Central MCP server registry
└── skills/             # Central skills directory (10 skills)
```
