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

## 🔑 Authentication

Requires environment variables:
- `KALSHI_API_KEY_ID` - Your API key ID from Kalshi settings
- `KALSHI_PRIVATE_KEY` - RSA private key (PKCS#1 format)

Add these in [Settings > Developers](/?t=settings&s=developers).

## ⚡ Quick Start

```bash
# Set credentials in [Settings > Developers](/?t=settings&s=developers)
export KALSHI_API_KEY_ID='your-key-id'
export KALSHI_PRIVATE_KEY='your-private-key'

# Install prerequisites
python3 -m pip install --user cryptography requests pyyaml

# Test connection
python3 /workspace/Skills/kalshi-predictions/scripts/kalshi.py account

# QUICK: Find liquid markets (use these series - they're proven)
python3 kalshi.py markets --series KXTESLADELIVERYBY --min-volume 100 --sort volume
python3 kalshi.py markets --series KXBTC --min-volume 50 --sort volume
python3 kalshi.py markets --series KXETH --min-volume 50 --sort volume

# Check your positions
python3 kalshi.py positions
```

## ✅ Prerequisites

Install required Python packages:

```bash
python3 -m pip install --user cryptography requests pyyaml
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
- Returned by default `/markets` endpoint


### Market Discovery

```bash
# Top series by volume (optionally by category)
python3 kalshi.py hot --limit 50
python3 kalshi.py hot --category Crypto --limit 50

# Output as YAML (hot, series, markets)
python3 kalshi.py hot --yaml
python3 kalshi.py series --include-volume --category Crypto --yaml

# See all series (8,200+ - overwhelming but complete)
python3 kalshi.py series

# Series with volume only, sorted by volume
python3 kalshi.py series --include-volume --sort volume

# List unique categories only
python3 kalshi.py series --categories-only

# Find liquid markets in a series (THE command to use)
python3 kalshi.py markets --series KXTESLADELIVERYBY --min-volume 100 --sort volume

# Find markets resolving soon (e.g., next 7 days)
python3 kalshi.py markets --series KXBTC --resolve-soon 7 --sort close_time

# Require top-of-book liquidity (sum of best bid/ask shares)
python3 kalshi.py markets --series KXBTC --min-liquidity 50 --liquidity-depth 1 --sort liquidity

# Filter by max bid-ask spread
python3 kalshi.py markets --series KXBTC --spread-max 0.05 --sort spread
```

### Market Analysis

The CLI includes Coinbase API integration for real-time crypto price data to help price crypto prediction markets.

```bash
# View orderbook (shows bids/asks, works for all markets)
python3 kalshi.py orderbook KXTESLADELIVERYBY-27-500000

# Unified market view (metadata + orderbook + recent trades)
python3 kalshi.py market KXTESLADELIVERYBY-27-500000

# View price history
python3 kalshi.py candlesticks TICKER --limit 50

# Get current Bitcoin price
python3 kalshi.py crypto-price BTC
python3 kalshi.py crypto-price BTC --yaml

# Get Ethereum price
python3 kalshi.py crypto-price ETH

# View crypto orderbook depth
python3 kalshi.py crypto-orderbook BTC
python3 kalshi.py crypto-orderbook ETH --yaml

# Get price candlesticks (default 1 hour)
python3 kalshi.py crypto-candles BTC --granularity 3600
python3 kalshi.py crypto-candles ETH --granularity 86400 --yaml

# Granularity options: 60 (1m), 300 (5m), 900 (15m), 3600 (1h), 21600 (6h), 86400 (1d)

# Get 24h stats (volume, open, high, low)
python3 kalshi.py crypto-stats BTC
python3 kalshi.py crypto-stats ETH --yaml

# Order sizing (Kelly fraction of 0.3 default)
python3 kalshi.py size --price 0.55 --probability 0.70 --portfolio-value 1000 --side yes
python3 kalshi.py size --price 0.55 --probability 0.70 --portfolio-value 1000 --kelly-fraction 0.2 --side yes
python3 kalshi.py size --price 0.55 --probability 0.70 --portfolio-value 1000 --max-position 0.2 --side yes

Note: `--probability` is always your YES probability. Use `--side no` to size NO contracts; the tool converts internally.

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
# Account snapshot (balance, portfolio value, open positions, open orders, P&L)
python3 kalshi.py account

# Place buy order
python3 kalshi.py buy --ticker KXTESLADELIVERYBY-27-500000 --side yes --count 10 --price 0.22

# View positions
python3 kalshi.py positions

# Positions closing soon (e.g., next 3 days)
python3 kalshi.py positions --close-soon 3

# List resting orders
python3 kalshi.py orders --status resting

# Cancel order
python3 kalshi.py cancel ORDER_ID

# Find and cancel stale orders (older than 120 minutes)
python3 kalshi.py orders --stale-minutes 120
python3 kalshi.py orders --stale-minutes 120 --cancel-stale
```

**Example: Pricing a Bitcoin market**

```bash
# 1. Check current BTC price
python3 kalshi.py crypto-price BTC --yaml

# 2. Find relevant Kalshi markets
python3 kalshi.py markets --series KXBTC --status open --sort volume --limit 10

# 3. View specific market details
python3 kalshi.py market KXBTC-25FEB04-99K

# 4. Calculate fair value and position size
python3 kalshi.py size --price 0.35 --probability 0.55 --portfolio-value 5000 --side yes
```

## 💰 Market Discovery Examples

```bash
# Top 20 markets by total volume
python3 kalshi.py hot --limit 50

# Top 10 in a category (e.g. Crypto, Politics)
python3 kalshi.py hot --category Crypto --limit 50
```

```bash
# Step 1: Search series for topics
python3 kalshi.py series | grep -iE "weather|politics|sports" | head -10

# Step 2: Query with volume filter
python3 kalshi.py markets --series KXWEATHER --sort volume
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
sys.path.insert(0, '/workspace/Skills/kalshi-predictions/scripts')
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

## 📚 Resources

- **Main Kalshi Docs**: https://docs.kalshi.com
- **Kalshi API Reference**: https://trading-api.readme.io
- **Local Kalshi API Docs**: `file Skills/kalshi-predictions/references/kalshi-api-documentation.md`
- **OpenAPI Spec**: https://docs.kalshi.com/openapi.yaml
- **Kalshi Trading Console**: https://kalshi.com
- **Local Coinbase API Docs**: `file Skills/kalshi-predictions/references/coinbase-api-documentation.md`
- **Coinbase API Docs**: https://docs.cdp.coinbase.com/api-reference/v2/introduction

---
