# Kalshi Agent Workspace

This repo contains two things:

1. A Kalshi skill for agent use (Python CLI + docs) under `Skills/kalshi-predictions/`.
2. A Kalshi working directory under `kalshi/` for prompts, learnings, and local state.

## Skill: `kalshi-predictions`

Location: `Skills/kalshi-predictions/`

What it includes:
- `SKILL.md` with usage guidance and command examples.
- `scripts/kalshi.py` CLI for querying markets, orderbooks, balances, and trades.
- `references/` with `kalshi-api-documentation.md` (official API docs snapshot).

## Working Directory: `kalshi/`

Expected files:
- `kalshi/KalshiTradingAgent.prompt.md` — agent prompt used for trading workflows.
- `kalshi/learnings.md` — running notes and strategy learnings.
- `kalshi/portfolio_state.schema.json` — JSON schema for local portfolio snapshots.
- `kalshi/portfolio_state.json` — local-only snapshot file (ignored by git).
- `kalshi/watchlist.json` — local watchlist file (ignored by git).

### Portfolio Snapshot Schema

The schema is defined in `kalshi/portfolio_state.schema.json` and is intended to validate
local snapshots of account state (balances, positions, orders, scans, and notes). Keep
`kalshi/portfolio_state.json` out of version control to avoid leaking account-specific data.

### Testing

Run the demo smoke test:

```bash
python ./test_skill_demo.py
```
