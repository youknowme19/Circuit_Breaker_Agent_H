# TrueForge — Circuit Breaker Financial Agent

TrueForge is TrueFoundry's open-source agent harness. Circuit Breaker ships the
financial MCP server and skill pack so a TrueForge agent can **propose** payments
without owning execution.

## What is real vs demo-safe

| Path | What happens |
| :--- | :--- |
| **Demo scripts / UI Attack Lab** | In-process sandbox: the same MCP tool functions run inside Python. No LLM key required. Honest fallback for judges. |
| **TrueForge local harness** | Real MCP stdio transport. TrueForge runs the agent loop, sandbox, and human checkpoints. Circuit Breaker still authorizes. |

This repository does **not** vendor TrueForge. Install it separately:

```bash
npx @truefoundry/trueforge@latest
```

## Connect the MCP server

In TrueForge initial setup, add a custom MCP server:

- **Name:** `circuit-breaker-finance`
- **Command:** `python`
- **Args:** `scripts/run_mcp.py` (run from the repo root with `PYTHONPATH=.` and the project venv)

Example:

```bash
cd /path/to/circuit_breaker
source venv/bin/activate
export PYTHONPATH=.
python scripts/run_mcp.py
```

TrueForge should spawn that command as stdio MCP (not a fake HTTP wrapper).

## Load the skill

Import `trueforge/skills/circuit-breaker-finance/SKILL.md` as a skill pack.

Create an agent named **Circuit Breaker Financial Agent** with:

- MCP server: `circuit-breaker-finance`
- Skill: circuit-breaker finance
- Tool approval / human checkpoint: enabled for irreversible actions (TrueForge pause)
- Circuit Breaker REVIEW is a second, independent human gate

## Mandatory rule

The harness may pause on tool approval. That does **not** replace Circuit Breaker.
Even if TrueForge approves a tool call, `execute_payment` still requires a
Circuit Breaker HMAC token bound to the canonical action hash.
