---
name: kalshi-predictions
description: |
  Trade on prediction markets via Kalshi's REST API. Search, filter, and discover
  market opportunities across crypto, politics, sports, economics, and more. Full trading capability
  with Python CLI that follows official Kalshi documentation exactly.

  Documentation: https://docs.kalshi.com
  API Reference: https://trading-api.readme.io
compatibility: Created for Zo Computer. Requires KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY.
metadata:
  author: Kaden Griffith
---

# Kalshi Prediction Markets

Trade event-based prediction markets via Kalshi's REST API. Bet on sports, politics,
economics, and more with full programmatic control.

## ⚡ Quick Start

```bash
# Set credentials in [Settings > Developers](/?t=settings&s=developers)
export KALSHI_API_KEY_ID='your-key-id'
export KALSHI_PRIVATE_KEY='your-private-key'

# Install prerequisites
python3 -m pip install --user cryptography requests

# Test connection
python3 /home/workspace/Skills/kalshi-predictions/scripts/kalshi.py balance

# QUICK: Find liquid markets (use these series - they're proven)
python3 kalshi.py markets --series KXTESLADELIVERYBY --min-volume 100 --sort volume
python3 kalshi.py markets --series KXBTC --min-volume 50 --sort volume
python3 kalshi.py markets --series KXETH --min-volume 50 --sort volume

# Check your positions
python3 kalshi.py positions
```

## 🔑 Authentication

Requires environment variables:
- `KALSHI_API_KEY_ID` - Your API key ID from Kalshi settings
- `KALSHI_PRIVATE_KEY` - RSA private key (PKCS#1 format)

Add these in [Settings > Developers](/?t=settings&s=developers).

## ✅ Prerequisites

Install required Python packages:

```bash
python3 -m pip install --user cryptography requests
```

## 🎯 TL;DR: Finding Markets That Actually Trade

**The Problem**: Kalshi now has 8,200+ series. Most have $0 volume. The default market listing shows NEWEST markets first (mostly MVE parlays with no activity).

**The Solution**: Use `--series` filter on these **proven liquid series**:

| Series | Category | Typical Volume | What It Trades |
|--------|----------|----------------|----------------|
| `KXTESLADELIVERYBY` | Companies | 50K+ | Tesla delivery targets |
| `KXBTC` | Crypto | 1K-8K | Bitcoin daily price ranges |
| `KXETH` | Crypto | 500-2K | Ethereum daily price ranges |
| `KXSP500` | Financials | 100-1K | S&P 500 targets |
| `KXNAS` | Financials | 50-500 | NASDAQ targets |

```bash
# Best discovery command pattern:
python3 kalshi.py markets --series SERIES_TICKER --min-volume 100 --sort volume
```

## 📊 Understanding Kalshi Market Types

Kalshi has two types of markets:

### 1. Binary Markets (Standard)
Single yes/no outcomes:
- "Will Tesla deliveries exceed 750,000 in a quarter by 2027?"
- "Will BTC close above $100,000 on Dec 31?"
- Tickers like `KXTESLADELIVERYBY-27-750000`
- Usually 50K+ volume on popular ones

### 2. MVE Markets (Multi-variate Event)
Combo/parlay bets requiring multiple conditions:
- "LeBron scores 15+ AND Luka scores 20+ AND Lakers win"
- Tickers like `KXMVESPORTSMULTIGAMEEXTENDED-S2026...`
- Usually 0-500 volume
- Returned by default `/markets` endpoint (why discovery is hard!)

## 🔴 Commands to AVOID (Broken/Limited)

| Command | Why It Fails | What To Use Instead |
|---------|--------------|---------------------|
| `kalshi.py hot` | MVE markets don't report 24h volume (always empty) | `--sort volume` flag |
| `kalshi.py search "bitcoin"` | Only searches MVE markets; misses all binary markets | `--series KXBTC` |
| `kalshi.py markets` (no filters) | Returns 100 newest MVE markets with $0 volume | `--series` + `--min-volume` |
| `kalshi.py trades TICKER` | Returns 404 for many market types | Check `orderbook` instead |
| `kalshi.py categories` | MVE markets return N/A category | Use `--series` directly |

## ✅ Commands That WORK

### Market Discovery

```bash
# Find liquid markets in a series (THE command to use)
python3 kalshi.py markets --series KXTESLADELIVERYBY --min-volume 100 --sort volume

# Find markets resolving soon (e.g., next 7 days)
python3 kalshi.py markets --series KXBTC --resolve-soon 7 --sort close_time

# Require top-of-book liquidity (sum of best bid/ask shares)
python3 kalshi.py markets --series KXBTC --min-liquidity 50 --liquidity-depth 1 --sort liquidity

# Filter by max bid-ask spread
python3 kalshi.py markets --series KXBTC --spread-max 0.05 --sort spread

# See all series (8,200+ - overwhelming but complete)
python3 kalshi.py series

# Find series by keyword in title
python3 kalshi.py series | grep -i "bitcoin"

# Find MVE markets with some volume
python3 kalshi.py opportunities --min-volume 50 --limit 20
```

### Market Analysis

```bash
# View orderbook (shows bids/asks, works for all markets)
python3 kalshi.py orderbook KXTESLADELIVERYBY-27-500000

# Unified market view (metadata + orderbook + recent trades)
python3 kalshi.py market KXTESLADELIVERYBY-27-500000

# View price history
python3 kalshi.py candlesticks TICKER --limit 50

# Order sizing (Kelly fraction of 0.3 default)
python3 kalshi.py size --price 0.55 --probability 0.70 --portfolio-value 1000
python3 kalshi.py size --price 0.55 --probability 0.70 --portfolio-value 1000 --kelly-fraction 0.2
python3 kalshi.py size --price 0.55 --probability 0.70 --portfolio-value 1000 --max-position 0.2

# See market metadata (check if MVE)
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from kalshi import KalshiClient
m = KalshiClient()._request('GET', '/markets/TICKER')['market']
print('MVE' if 'mve_collection_ticker' in m else 'Binary', '|', m.get('volume', 0), 'volume')
"
```

### Trading

```bash
# Check balance
python3 kalshi.py balance

# Place buy order
python3 kalshi.py buy --ticker KXTESLADELIVERYBY-27-500000 --side yes --count 10 --price 0.22

# View positions
python3 kalshi.py positions

# Positions closing soon (e.g., next 3 days)
python3 kalshi.py positions --close-soon 3

# Cancel order
python3 kalshi.py cancel ORDER_ID

# Find and cancel stale orders (older than 120 minutes)
python3 kalshi.py orders --stale-minutes 120
python3 kalshi.py orders --stale-minutes 120 --cancel-stale

# P&L snapshot
python3 kalshi.py pnl
```

## 💰 Market Discovery Strategies

### Strategy 1: Scan Known Liquid Series (Recommended)

```bash
#!/bin/bash
# Quick scan of proven high-volume series
echo "=== Scanning liquid markets ==="
for series in KXTESLADELIVERYBY KXBTC KXETH KXSP500 KXNAS; do
  echo ""
  echo "--- $series ---"
  python3 kalshi.py markets --series $series --min-volume 50 --sort volume --limit 5 2>/dev/null | grep -E "(Ticker|KX)" | tail -6
done
```

### Strategy 2: Find MVE Markets With Volume

```bash
# MVE markets with >50 volume (9 markets as of testing)
python3 kalshi.py opportunities --min-volume 50 --limit 20
```

### Strategy 3: Check a Specific Series

```bash
# Step 1: Search series for topics
python3 kalshi.py series | grep -iE "weather|politics|sports" | head -10

# Step 2: Query with volume filter
python3 kalshi.py markets --series KXWEATHER --min-volume 10 --sort volume
```

## 🏷️ Understanding Market Data

### Price Formats

| Display | Actual Value | Meaning |
|---------|--------------|---------|
| `$0.22` | $0.22 | 22 cents per share |
| `$22.00` | $0.22 | Same, but display bug (divide by 100) |
| `Ask: $0.15` | 15¢ | Correct from orderbook |

**Always verify prices in the orderbook** before trading:
```bash
python3 kalshi.py orderbook TICKER
```

### Volume Fields

| Field | Reliability | Notes |
|-------|-------------|-------|
| `volume` | ✅ Reliable | Total lifetime volume |
| `volume_24h` | ❌ Usually 0 | MVE markets don't report this |
| `yes_ask` | ⚠️ Check orderbook | May be cents or dollars |

## 🐍 Python Client Usage

```python
import sys
sys.path.insert(0, '/home/workspace/Skills/kalshi-predictions/scripts')
from kalshi import KalshiClient

client = KalshiClient()

# Get markets for a specific series (returns binary markets)
data = client._request("GET", "/markets?series_ticker=KXTESLADELIVERYBY&status=open")

for m in data['markets']:
    volume = m.get('volume', 0)
    if volume > 100:  # Filter for liquid markets
        print(f"{m['ticker']}: {m['title'][:50]}")
        print(f"  Volume: {volume:,} | Ask: {m.get('yes_ask', 0)}c")
```

## 🚨 Known Limitations (From Testing)

1. **Default market listing** - Returns newest MVE markets with 0 volume. Always use `--series` filter.
2. **Search command** - Only searches MVE markets from default endpoint. Cannot find binary markets like Tesla or Bitcoin.
3. **Hot/trending** - Returns empty because MVE markets don't report 24h volume.
4. **Trades endpoint** - Returns 404 for many markets. Use `orderbook` instead.
5. **Price display** - Some markets show cents as dollars (e.g., $22 instead of $0.22). Verify in orderbook.
6. **8,200+ series** - Overwhelming list with no "active only" filter. Use the curated list above.
7. **Event markets** - Events show 0 associated markets (API limitation).

## 📚 Resources

- **Main Docs**: https://docs.kalshi.com
- **API Reference**: https://trading-api.readme.io
- **OpenAPI Spec**: https://docs.kalshi.com/openapi.yaml
- **Kalshi Trading Console**: https://kalshi.com

## 🔧 API Endpoints

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.elections.kalshi.com/trade-api/v2` |

---

**Agent Note**: When helping users find trading opportunities, always use the `--series` approach. The `search` command and default `markets` listing are essentially broken for finding liquid binary markets due to Kalshi's shift to MVE markets. The 5 proven series in the table above are the fastest path to active markets.
