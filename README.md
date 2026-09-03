# AISourceOfTruthBR

Single source of truth and automated setup engine for AI CLI assistants:
- **AGY CLI** (Google Antigravity) — Core
- **Claude Code CLI** (Anthropic) — Core
- **GitHub Copilot CLI** — *Optional*

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
2. Prompts to install `copilot` (GitHub Copilot CLI) — **Optional** (press `n` to skip).
3. Links [AIBrain.md](file:///Users/alfbaro-mac-pro/.config/AISourceOfTruthBR/AIBrain.md) as the global instruction file for Claude Code, AGY CLI, and Copilot CLI (if installed).
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

### A. Force Syncing Components (`./manage.py sync` or `./sync.py`)
If an assistant creates or edits a skill, rule, or MCP locally, run `sync` to reconcile and propagate the changes to all assistants immediately:

- **Sync Skills:**
  ```bash
  ./manage.py sync skill
  ```
  *(Detects any new or updated skill in Claude Code, AGY, or Copilot, imports it to `skills/`, and restores links).*

- **Sync Memory & Rules:**
  ```bash
  ./manage.py sync brain
  ```
  *(Reconciles changes from `CLAUDE.md`, `GEMINI.md`, or `AGENTS.md` into `AIBrain.md` and restores links).*

- **Sync MCP Servers:**
  ```bash
  ./manage.py sync mcp
  ```
  *(Reconciles servers added in Claude Code via `claude mcp add` into `mcp/mcp_config.json` and syncs AGY and Copilot).*

- **Sync All Components:**
  ```bash
  ./manage.py sync all
  ```
  *(Syncs skills, brain, and MCP, then executes a complete parity verification).*

---

### B. MCP Servers (`./manage.py mcp`)
Any change here updates `mcp/mcp_config.json`, Antigravity, Copilot, and Claude Code automatically.

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

### E. GitHub Copilot CLI (Optional Status)

GitHub Copilot CLI is completely optional in this project.
- **Skipping Copilot**: When running `./setup.py`, press `N` when asked. Both AGY CLI and Claude Code CLI will configure and synchronize normally.
- **Enabling Copilot later**: Run `./setup.py --install-copilot` or install manually (`brew install --cask copilot-cli`). The setup engine automatically links `copilot-instructions.md` to `AIBrain.md`.
- **Verification**: If Copilot is not installed, `./manage.py verify` marks Copilot as `INFO (optional)` and core verification still passes with 100% success.

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
| **Memory / Rules** | Symbolic links from `~/.claude/CLAUDE.md`, `~/.gemini/config/GEMINI.md`, and Copilot files (if used) -> `AISourceOfTruthBR/AIBrain.md` | Instant. Editing `AIBrain.md` updates all active assistants at the same time. |
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
