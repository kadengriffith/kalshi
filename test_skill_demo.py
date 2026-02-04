#!/usr/bin/env python3
"""Smoke-test the Kalshi skill CLI against the demo API.

Runs a small set of read-only commands with --demo to validate wiring.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[0]
SKILL_CLI = REPO_ROOT / "Skills" / "kalshi-predictions" / "scripts" / "kalshi.py"
ENV_FILES = [REPO_ROOT / ".env", REPO_ROOT / "kalshi" / ".env"]


def load_env_files():
    for path in ENV_FILES:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def run_cmd(args, allow_fail=False):
    cmd = [sys.executable, str(SKILL_CLI), "--demo"] + args
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    if result.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed: {' '.join(args)}")
    return result.returncode


def pick_demo_ticker():
    sys.path.insert(0, str(SKILL_CLI.parent))
    try:
        from kalshi import KalshiClient  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"Failed to import KalshiClient: {exc}") from exc

    client = KalshiClient(use_demo=True)
    data = client._request("GET", "/markets?status=open&limit=50")
    markets = data.get("markets", [])
    if not markets:
        return None
    return markets[0].get("ticker")


def main():
    load_env_files()
    if not os.environ.get("KALSHI_API_KEY_ID") or not os.environ.get("KALSHI_PRIVATE_KEY"):
        print("Missing KALSHI_API_KEY_ID or KALSHI_PRIVATE_KEY.")
        print("Set them before running even in demo mode.")
        print(f"Checked: {', '.join(str(p) for p in ENV_FILES)}")
        return 1

    if not SKILL_CLI.exists():
        print(f"Skill CLI not found at: {SKILL_CLI}")
        return 1

    print("Running Kalshi skill demo smoke tests...")

    run_cmd(["balance"])
    run_cmd(["markets", "--status", "open", "--limit", "5", "--sort", "volume"])
    run_cmd(["markets", "--status", "open", "--limit", "5", "--resolve-soon", "7", "--sort", "close_time"])
    run_cmd(["markets", "--status", "open", "--limit", "5", "--spread-max", "0.05", "--sort", "spread"], allow_fail=True)
    run_cmd(["series"])
    run_cmd(["events", "--status", "open", "--limit", "5"])
    run_cmd(["events-mve", "--limit", "5"], allow_fail=True)
    run_cmd(["orders", "--stale-minutes", "120"])
    run_cmd(["size", "--price", "0.55", "--probability", "0.70", "--portfolio-value", "1000", "--max-position", "0.2"])
    run_cmd(["pnl"])

    ticker = pick_demo_ticker()
    if ticker:
        run_cmd(["watchlist", "add", ticker])
        run_cmd(["watchlist", "list"])
        run_cmd(["watchlist", "scan"], allow_fail=True)
        run_cmd(["market", ticker], allow_fail=True)
        run_cmd(["orderbook", ticker], allow_fail=True)
        run_cmd(["markets", "--tickers", ticker, "--min-liquidity", "1", "--liquidity-depth", "1", "--sort", "liquidity"], allow_fail=True)
    else:
        print("No open markets found in demo API; skipping orderbook test.")

    print("\n✅ Demo smoke tests completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
