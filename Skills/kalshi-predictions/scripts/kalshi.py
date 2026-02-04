#!/usr/bin/env python3
"""Kalshi Prediction Markets CLI
Full-featured tool for market discovery and automated trading
Follows official Kalshi API documentation

Usage:
    kalshi.py opportunities [--min-volume N] [--limit N]
    kalshi.py hot [--limit N]
    kalshi.py markets [--status STATUS] [--series SERIES] [--event EVENT] [--tickers T1,T2] [--mve-filter only|exclude] [--min-close-ts TS] [--max-close-ts TS] [--min-created-ts TS] [--max-created-ts TS] [--min-updated-ts TS] [--min-settled-ts TS] [--max-settled-ts TS] [--min-volume N] [--resolve-soon DAYS] [--min-liquidity N] [--sort volume]
    kalshi.py search "query" [--min-volume N]
    kalshi.py market <TICKER>
    kalshi.py size --price P --probability P --portfolio-value V [--kelly-fraction F] [--side yes|no]
    kalshi.py watchlist <add|remove|list|scan> [TICKER...]
    kalshi.py pnl
    kalshi.py events-mve [--series SERIES] [--collection COLLECTION] [--with-nested-markets] [--limit N]
    kalshi.py balance
    kalshi.py positions
"""

import os
import sys
import argparse
import base64
import json
import requests
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding

# Production API endpoint (default)
PRODUCTION_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
# Demo environment for testing
DEMO_BASE_URL = "https://demo-api.kalshi.co/trade-api/v2"


class KalshiClient:
    """Kalshi API Client with proper RSA-PSS signing"""
    
    def __init__(self, use_demo: bool = False):
        self.api_key_id = os.environ.get("KALSHI_API_KEY_ID", "")
        self.private_key_pem = os.environ.get("KALSHI_PRIVATE_KEY", "")
        self.base_url = DEMO_BASE_URL if use_demo else PRODUCTION_BASE_URL
        
        if not self.api_key_id or not self.private_key_pem:
            raise ValueError(
                "Missing KALSHI_API_KEY_ID or KALSHI_PRIVATE_KEY environment variables"
            )
        
        self._private_key = self._load_private_key()
    
    def _load_private_key(self):
        """Load private key from PEM, handling PKCS#1 format with proper line wrapping"""
        pem = self.private_key_pem
        
        # If the key is all on one line (from env var), format it properly
        if pem.count('\n') < 2:
            header = '-----BEGIN RSA PRIVATE KEY-----'
            footer = '-----END RSA PRIVATE KEY-----'
            
            # Remove header/footer if present
            body = pem
            if header in body:
                body = body.split(header)[1]
            if footer in body:
                body = body.split(footer)[0]
            
            # Clean up - remove all whitespace
            body = body.replace(' ', '').replace('\n', '').replace('\r', '')
            
            # Reconstruct with proper line wrapping (64 chars per line)
            lines = [body[i:i+64] for i in range(0, len(body), 64)]
            pem = f"{header}\n" + "\n".join(lines) + f"\n{footer}\n"
        
        return serialization.load_pem_private_key(pem.encode(), password=None)
    
    def _sign_message(self, message: str) -> str:
        """Sign message with RSA-PSS using SHA256"""
        signature = self._private_key.sign(
            message.encode('utf-8'),
            rsa_padding.PSS(
                mgf=rsa_padding.MGF1(hashes.SHA256()),
                salt_length=rsa_padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def _request(self, method: str, path: str, body: dict = None) -> dict:
        """Make authenticated request to Kalshi API"""
        timestamp = str(int(datetime.now().timestamp() * 1000))
        # Sign with full API path including /trade-api/v2
        path_without_query = '/trade-api/v2' + path.split('?')[0]
        message = f"{timestamp}{method}{path_without_query}"
        signature = self._sign_message(message)
        
        headers = {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
        }
        if body:
            headers["Content-Type"] = "application/json"
        
        url = f"{self.base_url}{path}"
        response = requests.request(method, url, headers=headers, json=body)
        
        if response.status_code >= 400:
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
        return response.json() if response.text else {}


def _format_market_row(m, show_close=True):
    """Format a market for display - handles MVE markets specially"""
    yes_ask = m.get('yes_ask_dollars', m.get('yes_ask', 0))
    yes_bid = m.get('yes_bid', 0)
    volume = m.get('volume', 0)
    volume_24h = m.get('volume_24h', 0)
    close_time = m.get('close_time') or m.get('close_date')
    close_date = close_time[:10] if close_time else 'N/A'
    
    # Handle MVE markets with long compound titles
    title = m.get('title', 'N/A')
    legs = m.get('mve_selected_legs', [])
    
    if legs:
        # For MVE markets, show leg count instead of full title
        num_legs = len(legs)
        # Try to extract a concise summary
        short_title = title[:35] + '...' if len(title) > 38 else title
        title_display = f"[{num_legs} legs] {short_title}"
    else:
        # Standard market
        if len(title) > 50:
            title = title[:47] + '...'
        title_display = title
    
    # Truncate very long tickers
    ticker = m.get('ticker', 'N/A')
    if len(ticker) > 35:
        ticker = ticker[:32] + '...'
    
    try:
        yes_ask_val = float(yes_ask)
    except (TypeError, ValueError):
        yes_ask_val = 0.0

    row = f"{ticker} | {title_display} | ${yes_ask_val:.2f} | {volume:,.0f}"
    if show_close:
        row += f" | {close_date}"
    
    # Highlight high-activity markets
    if volume_24h > 10000:
        row = f"🔥 {row}"
    elif volume_24h > 1000:
        row = f"📈 {row}"
    
    return row


def _parse_time(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    try:
        s = str(value)
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _orderbook_liquidity(client, ticker, depth):
    book = client._request("GET", f"/markets/{ticker}/orderbook")
    yes_bids = book.get('orderbook', {}).get('yes', book.get('yes_bids', []))
    no_bids = book.get('orderbook', {}).get('no', book.get('no_bids', []))

    def _sum(side):
        total = 0
        for level in side[:depth]:
            if isinstance(level, dict):
                count = level.get('count', 0)
            else:
                count = level[1] if len(level) > 1 else 0
            total += count or 0
        return total

    return _sum(yes_bids) + _sum(no_bids)


def _watchlist_path():
    env_path = os.environ.get('KALSHI_WATCHLIST_PATH')
    if env_path:
        return env_path
    cwd_kalshi = os.path.join(os.getcwd(), 'kalshi')
    if os.path.isdir(cwd_kalshi):
        return os.path.join(cwd_kalshi, 'watchlist.json')
    return os.path.join(os.path.expanduser('~'), '.kalshi_watchlist.json')


def _load_watchlist():
    path = _watchlist_path()
    if not os.path.exists(path):
        return path, []
    try:
        data = json.loads(open(path, 'r', encoding='utf-8').read())
        tickers = data.get('tickers', [])
        return path, [t for t in tickers if isinstance(t, str)]
    except Exception:
        return path, []


def _save_watchlist(path, tickers):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'tickers': tickers}, f, indent=2)


# CLI Commands
def cmd_opportunities(client, args):
    """Find the best trading opportunities with smart filtering"""
    # Lower default for MVE markets (most have < 500 volume)
    min_vol = args.min_volume if args.min_volume is not None else 50
    limit = args.limit or 30
    
    print("\n🔍 Finding trading opportunities...")
    print(f"   Min Volume: {min_vol}")
    print(f"   Max Results: {limit}")
    print("   Note: Kalshi now uses MVE markets - see SKILL.md for details\n")
    
    # Fetch markets with generous limit
    fetch_limit = max(limit * 10, 500)
    params = {'status': 'open', 'limit': fetch_limit}
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    data = client._request("GET", f"/markets?{query}")
    markets = data.get('markets', [])
    
    # Filter for volume
    filtered = [m for m in markets if (m.get('volume', 0) >= min_vol or m.get('volume_24h', 0) >= min_vol)]
    
    # Sort by 24h volume (most active first), fallback to total volume
    filtered.sort(key=lambda x: (x.get('volume_24h', 0) or x.get('volume', 0)), reverse=True)
    
    if not filtered:
        print("No markets found with sufficient volume.")
        print(f"Try: python3 kalshi.py markets --status open --limit 300")
        print(f"Then filter manually. Most MVE markets have 0-100 volume.")
        return
    
    print(f"✅ Found {len(filtered)} opportunities:\n")
    print(f"{'Ticker':<40} | {'Market':<50} | Ask | Volume | Close")
    print("-" * 130)
    
    for m in filtered[:limit]:
        print(_format_market_row(m))
    
    print(f"\n📊 Showing top {min(limit, len(filtered))} of {len(filtered)} markets")
    print("💡 Always check orderbook before trading: kalshi.py orderbook TICKER")


def cmd_hot(client, args):
    """Show trending markets by 24h volume"""
    print("\n🔥 Trending Markets (by 24h Volume)\n")
    
    # Fetch many markets
    params = {'status': 'open', 'limit': 500}
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    data = client._request("GET", f"/markets?{query}")
    markets = data.get('markets', [])
    
    # Sort by 24h volume
    markets.sort(key=lambda x: x.get('volume_24h', 0) or 0, reverse=True)
    
    # Filter to only those with 24h volume
    hot_markets = [m for m in markets if m.get('volume_24h', 0) > 0]
    
    if not hot_markets:
        print("⚠️  No markets with 24h volume found.")
        print("\nThis is expected - Kalshi's MVE markets don't report 24h volume.")
        print("Use this instead to find active markets:")
        print("  python3 kalshi.py markets --status open --sort volume --limit 20")
        print("\nOr find markets by total lifetime volume:")
        print("  python3 kalshi.py opportunities --min-volume 50")
        return
    
    print("Ticker | Title | Yes Ask | 24h Volume | Total Volume")
    print("-" * 100)
    
    for m in hot_markets[:args.limit or 20]:
        yes_ask = m.get('yes_ask', 0)
        vol_24h = m.get('volume_24h', 0)
        volume = m.get('volume', 0)
        title = m.get('title', 'N/A')
        if len(title) > 45:
            title = title[:42] + '...'
        print(f"{m.get('ticker', 'N/A')} | {title} | ${yes_ask:.2f} | {vol_24h:,.0f} | {volume:,.0f}")


def cmd_markets(client, args):
    params = {}
    if args.status: params['status'] = args.status
    if args.series: params['series_ticker'] = args.series
    if args.event: params['event_ticker'] = args.event
    if args.tickers: params['tickers'] = args.tickers
    if args.mve_filter: params['mve_filter'] = args.mve_filter
    if args.min_close_ts: params['min_close_ts'] = args.min_close_ts
    if args.max_close_ts: params['max_close_ts'] = args.max_close_ts
    if args.min_created_ts: params['min_created_ts'] = args.min_created_ts
    if args.max_created_ts: params['max_created_ts'] = args.max_created_ts
    if args.min_updated_ts: params['min_updated_ts'] = args.min_updated_ts
    if args.min_settled_ts: params['min_settled_ts'] = args.min_settled_ts
    if args.max_settled_ts: params['max_settled_ts'] = args.max_settled_ts
    if args.cursor: params['cursor'] = args.cursor
    if args.limit: params['limit'] = max(args.limit, 100)  # Ensure we fetch enough for filtering
    
    if args.min_updated_ts:
        # Kalshi API does not allow other filters when min_updated_ts is provided
        # except mve_filter=exclude.
        keep = {'min_updated_ts', 'limit', 'cursor', 'mve_filter'}
        params = {k: v for k, v in params.items() if k in keep}
        if params.get('mve_filter') != 'exclude':
            params.pop('mve_filter', None)

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    path = f"/markets?{query}" if query else "/markets"
    
    print(f"\n📊 Fetching markets...")
    print()
    
    data = client._request("GET", path)
    markets = data.get('markets', [])
    
    filtered = markets
    if args.min_volume:
        filtered = [m for m in filtered if (m.get('volume') or 0) >= args.min_volume]
    if args.max_volume:
        filtered = [m for m in filtered if (m.get('volume') or 0) <= args.max_volume]
    if args.min_yes_ask is not None:
        filtered = [m for m in filtered if (m.get('yes_ask_dollars', m.get('yes_ask', 0)) or 0) >= args.min_yes_ask]
    if args.max_yes_ask is not None:
        filtered = [m for m in filtered if (m.get('yes_ask_dollars', m.get('yes_ask', 0)) or 0) <= args.max_yes_ask]
    if args.spread_max is not None:
        next_filtered = []
        for m in filtered:
            yes_ask = m.get('yes_ask_dollars', m.get('yes_ask', None))
            yes_bid = m.get('yes_bid_dollars', m.get('yes_bid', None))
            try:
                ask_val = float(yes_ask)
                bid_val = float(yes_bid)
            except (TypeError, ValueError):
                continue
            spread = ask_val - bid_val
            m['_spread'] = spread
            if spread <= args.spread_max:
                next_filtered.append(m)
        filtered = next_filtered
    if args.resolve_soon is not None:
        horizon = datetime.now(timezone.utc) + timedelta(days=args.resolve_soon)
        next_filtered = []
        for m in filtered:
            close_time = m.get('close_time') or m.get('close_date')
            dt = _parse_time(close_time)
            if dt and dt <= horizon:
                next_filtered.append(m)
        filtered = next_filtered
    if args.min_liquidity is not None:
        next_filtered = []
        for m in filtered:
            ticker = m.get('ticker')
            if not ticker:
                continue
            try:
                liquidity = _orderbook_liquidity(client, ticker, args.liquidity_depth)
            except Exception:
                liquidity = 0
            m['_liquidity'] = liquidity
            if liquidity >= args.min_liquidity:
                next_filtered.append(m)
        filtered = next_filtered
    
    if args.sort:
        if args.sort in ('yes_ask', 'yes_ask_dollars'):
            key_fn = lambda x: x.get('yes_ask_dollars', x.get('yes_ask', 0)) or 0
        elif args.sort in ('yes_bid', 'yes_bid_dollars'):
            key_fn = lambda x: x.get('yes_bid_dollars', x.get('yes_bid', 0)) or 0
        elif args.sort in ('close_date', 'close_time'):
            key_fn = lambda x: x.get('close_time') or x.get('close_date') or ''
        elif args.sort == 'liquidity':
            key_fn = lambda x: x.get('_liquidity', 0) or 0
        elif args.sort == 'spread':
            key_fn = lambda x: x.get('_spread', 0) or 0
        else:
            key_fn = lambda x: x.get(args.sort) or 0
        filtered.sort(key=key_fn, reverse=not args.no_desc)
    
    if not filtered:
        print("No markets found matching criteria")
        print(f"\n💡 Tip: Try without --min-volume to see all markets")
        print(f"   Most markets have 0 volume. Try: --min-volume 10")
        return
    
    print(f"✅ Found {len(filtered)} markets:\n")
    print(f"{'Ticker':<40} | {'Market':<50} | Ask | Volume | Close")
    print("-" * 130)
    
    for m in filtered[:args.limit or 50]:
        print(_format_market_row(m))
    
    # Summary stats
    mve_count = sum(1 for m in filtered if 'mve_collection_ticker' in m)
    if mve_count > 0:
        print(f"\n📊 {mve_count} of {len(filtered)} are MVE markets")


def cmd_search(client, args):
    print(f"\n🔍 Searching for '{args.query}'...")
    
    # Fetch many markets to search through
    fetch_limit = max(args.limit * 10, 300)
    data = client._request("GET", f"/markets?status={args.status or 'open'}&limit={fetch_limit}")
    markets = data.get('markets', [])
    
    # Parse query (support OR/AND)
    query_lower = args.query.lower()
    terms = [t.strip() for t in query_lower.replace(' or ', '|').split('|')]
    
    filtered = []
    for m in markets:
        text = f"{m.get('title', '')} {m.get('ticker', '')} {m.get('category', '')}".lower()
        if any(term in text for term in terms):
            filtered.append(m)
    
    if args.min_volume:
        filtered = [m for m in filtered if (m.get('volume') or 0) >= args.min_volume]
    
    if args.sort == 'volume':
        filtered.sort(key=lambda x: x.get('volume') or 0, reverse=True)
    elif args.sort == 'volume_24h':
        filtered.sort(key=lambda x: x.get('volume_24h') or 0, reverse=True)
    
    if not filtered:
        print(f"\nNo markets found matching '{args.query}'")
        print(f"Searched {len(markets)} markets. Try:")
        print(f"  - Broader query (e.g., 'NBA' instead of 'Celtics Lakers')")
        print(f"  - Increase --limit (currently searched {fetch_limit})")
        print(f"  - Check SKILL.md for MVE market search tips")
        return
    
    print(f"\n✅ Found {len(filtered)} markets matching '{args.query}':\n")
    print(f"{'Ticker':<40} | {'Market':<50} | Ask | Volume")
    print("-" * 115)
    
    for m in filtered[:args.limit or 30]:
        print(_format_market_row(m, show_close=False))
    
    if len(filtered) > (args.limit or 30):
        print(f"\n... and {len(filtered) - (args.limit or 30)} more")


def cmd_categories(client, args):
    data = client._request("GET", "/series")
    series = data.get('series', [])
    categories = set(s.get('category') for s in series if s.get('category'))
    
    print("\n📂 Available Categories:")
    print("-" * 50)
    print("⚠️  NOTE: Categories only work for non-MVE markets")
    print("   Most active markets are MVE and return category: N/A")
    print("-" * 50)
    for cat in sorted(categories):
        count = sum(1 for s in series if s.get('category') == cat)
        print(f"• {cat} ({count} series)")
    print("\n💡 For MVE markets, use: python3 kalshi.py search \"<keyword>\"")


def cmd_series(client, args):
    params = {}
    if args.category: params['category'] = args.category
    if args.tags: params['tags'] = args.tags
    if args.include_product_metadata: params['include_product_metadata'] = 'true'
    if args.include_volume: params['include_volume'] = 'true'

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    path = f"/series?{query}" if query else "/series"

    data = client._request("GET", path)
    series = data.get('series', [])
    
    print("\n📚 Available Series:")
    print("-" * 80)
    print("Ticker | Category | Title")
    print("-" * 80)
    
    for s in series[:50]:
        title = s.get('title', 'N/A')
        if len(title) > 45:
            title = title[:42] + '...'
        print(f"{s.get('ticker', 'N/A')} | {s.get('category', 'N/A')} | {title}")
    
    if len(series) > 50:
        print(f"\n... and {len(series) - 50} more series")


def cmd_events(client, args):
    params = {'status': args.status or 'open'}
    if args.limit: params['limit'] = args.limit
    if args.with_nested_markets: params['with_nested_markets'] = 'true'
    if args.with_milestones: params['with_milestones'] = 'true'
    if args.series: params['series_ticker'] = args.series
    if args.min_close_ts: params['min_close_ts'] = args.min_close_ts
    if args.cursor: params['cursor'] = args.cursor
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    data = client._request("GET", f"/events?{query}")
    events = data.get('events', [])
    
    print(f"\n📅 {len(events)} Events:\n")
    print("Ticker | Category | Markets | Title")
    print("-" * 90)
    
    # Sort by number of markets (most interesting first)
    events.sort(key=lambda x: x.get('markets_count', 0), reverse=True)
    
    for e in events[:args.limit or 30]:
        title = e.get('title', 'N/A')
        if len(title) > 40:
            title = title[:37] + '...'
        print(f"{e.get('ticker', 'N/A')} | {e.get('category', 'N/A')} | {e.get('markets_count', 0)} | {title}")


def cmd_events_mve(client, args):
    if args.series and args.collection:
        print("❌ Error: Use only one of --series or --collection for MVE events.")
        return
    params = {}
    if args.series: params['series_ticker'] = args.series
    if args.collection: params['collection_ticker'] = args.collection
    if args.with_nested_markets: params['with_nested_markets'] = 'true'
    if args.limit: params['limit'] = args.limit
    if args.cursor: params['cursor'] = args.cursor

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    data = client._request("GET", f"/events/multivariate?{query}" if query else "/events/multivariate")
    events = data.get('events', [])

    print(f"\n🧩 {len(events)} MVE Events:\n")
    print("Ticker | Series | Markets | Title")
    print("-" * 90)

    for e in events[:args.limit or 30]:
        title = e.get('title', 'N/A')
        if len(title) > 40:
            title = title[:37] + '...'
        print(f"{e.get('ticker', 'N/A')} | {e.get('series_ticker', 'N/A')} | {e.get('markets_count', 0)} | {title}")


def cmd_market(client, args):
    market_data = client._request("GET", f"/markets/{args.ticker}")
    market = market_data.get('market', market_data)
    title = market.get('title', 'N/A')
    status = market.get('status', 'N/A')
    close_time = market.get('close_time') or market.get('close_date')
    volume = market.get('volume', 0)
    yes_ask = market.get('yes_ask_dollars', market.get('yes_ask', 0))
    yes_bid = market.get('yes_bid_dollars', market.get('yes_bid', 0))

    print(f"\n📌 {title}")
    print(f"Ticker: {args.ticker}")
    print(f"Status: {status}")
    if close_time:
        print(f"Close Time: {close_time}")
    print(f"Volume: {volume:,}")
    try:
        print(f"Yes Ask: ${float(yes_ask):.2f} | Yes Bid: ${float(yes_bid):.2f}")
    except (TypeError, ValueError):
        print("Yes Ask/Yes Bid: N/A")

    cmd_orderbook(client, argparse.Namespace(ticker=args.ticker))
    try:
        cmd_trades(client, argparse.Namespace(ticker=args.ticker, limit=20))
    except Exception as exc:
        print(f"\n⚠️  Trades unavailable: {exc}")


def cmd_size(client, args):
    price = args.price
    prob_yes = args.probability
    portfolio_value = args.portfolio_value
    kelly_fraction = args.kelly_fraction
    max_position = args.max_position
    side = args.side

    if price <= 0 or price >= 1:
        print("❌ Error: --price must be between 0 and 1 (exclusive).")
        return
    if prob_yes <= 0 or prob_yes >= 1:
        print("❌ Error: --probability must be between 0 and 1 (exclusive).")
        return
    if portfolio_value <= 0:
        print("❌ Error: --portfolio-value must be > 0.")
        return
    if kelly_fraction <= 0 or kelly_fraction > 1:
        print("❌ Error: --kelly-fraction must be > 0 and <= 1.")
        return
    if max_position is not None and (max_position <= 0 or max_position > 1):
        print("❌ Error: --max-position must be > 0 and <= 1.")
        return

    if side == "yes":
        prob_side = prob_yes
        implied_yes = price
    else:
        prob_side = 1 - prob_yes
        implied_yes = 1 - price

    implied_side = price
    edge = prob_side - implied_side

    b = (1 - price) / price
    p = prob_side
    q = 1 - p
    kelly = (b * p - q) / b if b != 0 else 0
    position_fraction = kelly * kelly_fraction
    capped = False
    if max_position is not None and position_fraction > max_position:
        position_fraction = max_position
        capped = True
    position_dollars = max(position_fraction * portfolio_value, 0)
    contracts = position_dollars / price if price > 0 else 0
    ev_per_contract = (prob_side * 1.0 + (1 - prob_side) * 0.0) - price
    ev_roi = ev_per_contract / price if price > 0 else 0
    max_loss = price * contracts

    print("\n📐 Order Sizing")
    print("-" * 40)
    print(f"Side: {side.upper()}")
    print(f"Contract price: {implied_side:.4f} ({implied_side*100:.2f}%)")
    print(f"Implied YES: {implied_yes:.4f} ({implied_yes*100:.2f}%)")
    print(f"Your YES probability: {prob_yes:.4f} ({prob_yes*100:.2f}%)")
    print(f"Edge on {side.upper()}: {edge:.4f} ({edge*100:.2f}%)")
    print(f"EV per contract: ${ev_per_contract:.4f}")
    print(f"Expected ROI: {ev_roi*100:.2f}%")
    print(f"Kelly fraction: {kelly:.4f}")
    print(f"Applied Kelly (x{kelly_fraction:.2f}): {position_fraction:.4f}")
    print(f"Portfolio value: ${portfolio_value:,.2f}")
    print(f"Position size: ${position_dollars:,.2f}")
    print(f"Contracts (approx): {contracts:,.2f}")
    print(f"Max loss (approx): ${max_loss:,.2f}")
    if capped:
        print(f"\n✅ Capped at max position: {max_position:.4f} ({max_position*100:.2f}%)")

    if edge <= 0:
        print("\n⚠️  Edge <= 0: sizing suggests no trade.")
    if position_fraction > 0.2:
        print("\n⚠️  Position fraction > 20% of portfolio.")


def cmd_watchlist(client, args):
    path, tickers = _load_watchlist()

    if args.action == 'list':
        print(f"\n📋 Watchlist ({len(tickers)})")
        print(f"Path: {path}")
        for t in tickers:
            print(f"- {t}")
        return

    if args.action in ('add', 'remove'):
        if not args.tickers:
            print("❌ Error: Provide at least one ticker.")
            return
        incoming = [t.strip() for t in args.tickers if t.strip()]
        if args.action == 'add':
            for t in incoming:
                if t not in tickers:
                    tickers.append(t)
            _save_watchlist(path, tickers)
            print(f"✅ Added {len(incoming)} tickers. Total: {len(tickers)}")
            print(f"Path: {path}")
            return
        else:
            tickers = [t for t in tickers if t not in incoming]
            _save_watchlist(path, tickers)
            print(f"✅ Removed {len(incoming)} tickers. Total: {len(tickers)}")
            print(f"Path: {path}")
            return

    if args.action == 'scan':
        if not tickers:
            print("No tickers in watchlist.")
            return
        count = 0
        for t in tickers:
            try:
                cmd_market(client, argparse.Namespace(ticker=t))
                count += 1
            except Exception as exc:
                print(f"\n⚠️  Failed to scan {t}: {exc}")
        print(f"\n✅ Scanned {count} tickers.")


def cmd_orderbook(client, args):
    book = client._request("GET", f"/markets/{args.ticker}/orderbook")
    
    # Try to get market details
    try:
        market_data = client._request("GET", f"/markets/{args.ticker}")
        if 'market' in market_data:
            market = market_data['market']
        else:
            market = market_data
    except:
        market = {'title': 'N/A'}
    
    print(f"\n📖 Orderbook: {market.get('title', 'N/A')}")
    print(f"Ticker: {args.ticker}")
    
    # Show MVE info if applicable
    legs = market.get('mve_selected_legs', [])
    if legs:
        print(f"\n🧩 MVE Market with {len(legs)} legs:")
        for i, leg in enumerate(legs[:5], 1):
            print(f"   {i}. {leg['side'].upper()} on {leg['market_ticker']}")
        if len(legs) > 5:
            print(f"   ... and {len(legs) - 5} more legs")
    
    print("-" * 60)
    
    yes_bids = book.get('orderbook', {}).get('yes', book.get('yes_bids', []))
    no_bids = book.get('orderbook', {}).get('no', book.get('no_bids', []))
    
    print("\n🟢 YES Orders (Buy YES / Sell NO):")
    print("Price | Count")
    print("-" * 30)
    def _price_to_dollars(val):
        try:
            num = float(val)
        except (TypeError, ValueError):
            return 0.0
        return num / 100 if num > 1 else num

    if yes_bids:
        for bid in yes_bids[:10]:
            if isinstance(bid, dict):
                price = bid.get('price', 0)
                count = bid.get('count', 0)
            else:
                price = bid[0] if len(bid) > 0 else 0
                count = bid[1] if len(bid) > 1 else 0
            print(f"${_price_to_dollars(price):.2f} | {count}")
    else:
        print("No YES orders available")
    
    print("\n🔴 NO Orders (Buy NO / Sell YES):")
    print("Price | Count")
    print("-" * 30)
    if no_bids:
        for bid in no_bids[:10]:
            if isinstance(bid, dict):
                price = bid.get('price', 0)
                count = bid.get('count', 0)
            else:
                price = bid[0] if len(bid) > 0 else 0
                count = bid[1] if len(bid) > 1 else 0
            print(f"${_price_to_dollars(price):.2f} | {count}")
    else:
        print("No NO orders available")
    
    # Market summary - handle both string and numeric values
    yes_ask = market.get('yes_ask_dollars', market.get('yes_ask', 0))
    yes_bid = market.get('yes_bid_dollars', market.get('yes_bid', 0))
    
    try:
        yes_ask_val = float(yes_ask)
    except (TypeError, ValueError):
        yes_ask_val = 0.0
    try:
        yes_bid_val = float(yes_bid)
    except (TypeError, ValueError):
        yes_bid_val = 0.0
    
    volume = market.get('volume', 0)
    
    print(f"\n📊 Market Summary:")
    print(f"   Yes Ask: ${yes_ask_val:.2f}")
    print(f"   Yes Bid: ${yes_bid_val:.2f}")
    print(f"   Volume: {volume:,}")
    
    # Liquidity warning
    if yes_ask_val >= 1.0 and yes_bid_val <= 0:
        print("\n⚠️  WARNING: No liquidity - Ask is $1.00, Bid is $0.00")
        print("   This market cannot be traded at reasonable prices.")


def cmd_candlesticks(client, args):
    """Get candlestick/price history for a market"""
    data = client._request("GET", f"/markets/{args.ticker}/candlesticks?limit={args.limit or 100}")
    candles = data.get('candlesticks', [])
    
    # Try to get market details
    try:
        market_data = client._request("GET", f"/markets/{args.ticker}")
        market = market_data.get('market', market_data)
    except:
        market = {'title': 'N/A'}
    
    print(f"\n📊 Price History: {market.get('title', 'N/A')}")
    print(f"Ticker: {args.ticker}\n")
    
    if not candles:
        print("No price history available for this market.")
        return
    
    print("Time | Open | High | Low | Close | Volume")
    print("-" * 70)
    
    for c in candles[-20:]:  # Show last 20
        time = c.get('time', 'N/A')[:16] if c.get('time') else 'N/A'
        open_p = c.get('open_price', 0)
        high = c.get('high_price', 0)
        low = c.get('low_price', 0)
        close = c.get('close_price', 0)
        vol = c.get('volume', 0)
        print(f"{time} | ${open_p:.2f} | ${high:.2f} | ${low:.2f} | ${close:.2f} | {vol}")


def cmd_trades(client, args):
    data = client._request("GET", f"/markets/{args.ticker}/trades?limit={args.limit or 20}")
    trades = data.get('trades', [])
    
    print(f"\n💰 Recent Trades for {args.ticker}:\n")
    print("Time | Side | Price | Count")
    print("-" * 50)
    
    if not trades:
        print("No trades found for this market.")
        return
    
    for t in trades:
        print(f"{t.get('created_at', 'N/A')[:19]} | {t.get('side', 'N/A')} | ${t.get('price', 0):.2f} | {t.get('count', 0)}")


def cmd_buy(client, args):
    order_data = {
        "ticker": args.ticker,
        "side": args.side,
        "action": "buy",
        "count": args.count,
        "type": "limit" if args.price else "market",
    }
    if args.price:
        if args.price <= 0 or args.price >= 1:
            print("❌ Error: --price must be between 0 and 1 (exclusive).")
            return
        price_key = "yes_price_dollars" if args.side == "yes" else "no_price_dollars"
        order_data[price_key] = args.price
    
    result = client._request("POST", "/portfolio/orders", order_data)
    
    print(f"\n✅ BUY order placed!")
    print(f"Order ID: {result.get('order_id', 'N/A')}")
    print(f"Ticker: {args.ticker} | Side: {args.side.upper()} | Count: {args.count}")
    if args.price:
        print(f"Price: ${args.price}")
    
    print(f"\n💡 Check orderbook before placing orders:")
    print(f"   python3 kalshi.py orderbook {args.ticker}")


def cmd_sell(client, args):
    order_data = {
        "ticker": args.ticker,
        "side": args.side,
        "action": "sell",
        "count": args.count,
        "type": "limit" if args.price else "market",
    }
    if args.price:
        if args.price <= 0 or args.price >= 1:
            print("❌ Error: --price must be between 0 and 1 (exclusive).")
            return
        price_key = "yes_price_dollars" if args.side == "yes" else "no_price_dollars"
        order_data[price_key] = args.price
    
    result = client._request("POST", "/portfolio/orders", order_data)
    
    print(f"\n✅ SELL order placed!")
    print(f"Order ID: {result.get('order_id', 'N/A')}")
    print(f"Ticker: {args.ticker} | Side: {args.side.upper()} | Count: {args.count}")
    if args.price:
        print(f"Price: ${args.price}")


def cmd_orders(client, args):
    params = {}
    if args.status: params['status'] = args.status
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    path = f"/portfolio/orders?{query}" if query else "/portfolio/orders"
    
    data = client._request("GET", path)
    orders = data.get('orders', [])

    if args.cancel_stale and args.stale_minutes is None:
        print("\n❌ Error: --cancel-stale requires --stale-minutes")
        return

    if args.stale_minutes is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=args.stale_minutes)
        next_orders = []
        for o in orders:
            created = o.get('created_time') or o.get('created_at')
            dt = _parse_time(created)
            if dt and dt <= cutoff:
                next_orders.append(o)
        orders = next_orders
    
    if not orders:
        print("\nNo orders found")
        return
    
    print(f"\n📋 {len(orders)} Orders:\n")
    print("ID | Ticker | Side | Action | Count | Price | Status")
    print("-" * 100)
    
    for o in orders[:args.limit or 50]:
        oid = o.get('order_id', 'N/A')[:8] + "..."
        price = f"${o.get('price', 0):.2f}" if o.get('price') else "MARKET"
        print(f"{oid} | {o.get('ticker', 'N/A')} | {o.get('side', 'N/A')} | {o.get('action', 'N/A')} | {o.get('count', 0)} | {price} | {o.get('status', 'N/A')}")

    if args.cancel_stale:
        cancelled = 0
        for o in orders:
            oid = o.get('order_id')
            if not oid:
                continue
            try:
                client._request("DELETE", f"/portfolio/orders/{oid}")
                cancelled += 1
            except Exception:
                continue
        print(f"\n✅ Cancelled {cancelled} stale orders")


def cmd_cancel(client, args):
    client._request("DELETE", f"/portfolio/orders/{args.order_id}")
    print(f"✅ Order {args.order_id} cancelled")


def cmd_positions(client, args):
    data = client._request("GET", "/portfolio/positions")
    positions = data.get('positions', [])

    close_info = {}
    if args.close_soon is not None:
        horizon = datetime.now(timezone.utc) + timedelta(days=args.close_soon)
        next_positions = []
        for p in positions:
            ticker = p.get('ticker')
            if not ticker:
                continue
            try:
                market_data = client._request("GET", f"/markets/{ticker}")
                market = market_data.get('market', market_data)
                close_time = market.get('close_time') or market.get('close_date')
                dt = _parse_time(close_time)
            except Exception:
                dt = None
                close_time = None
            if dt and dt <= horizon:
                close_info[ticker] = close_time
                next_positions.append(p)
        positions = next_positions
    
    if not positions:
        print("\n📭 No open positions")
        return
    
    print(f"\n📈 {len(positions)} Open Positions:\n")
    if args.close_soon is not None:
        print("Ticker | Position | Avg Entry | Mark | Unrealized P&L | Close")
        print("-" * 120)
    else:
        print("Ticker | Position | Avg Entry | Mark | Unrealized P&L")
        print("-" * 90)
    
    total_pnl = 0
    for p in positions:
        unrealized = p.get('unrealized_pnl', 0)
        total_pnl += unrealized
        pnl_str = f"+${unrealized:.2f}" if unrealized >= 0 else f"-${abs(unrealized):.2f}"
        if args.close_soon is not None:
            close_time = close_info.get(p.get('ticker'), 'N/A')
            print(f"{p.get('ticker', 'N/A')} | {p.get('position', 0)} | ${p.get('avg_entry_price', 0):.2f} | ${p.get('mark_price', 0):.2f} | {pnl_str} | {close_time}")
        else:
            print(f"{p.get('ticker', 'N/A')} | {p.get('position', 0)} | ${p.get('avg_entry_price', 0):.2f} | ${p.get('mark_price', 0):.2f} | {pnl_str}")
    
    print("-" * 120 if args.close_soon is not None else "-" * 90)
    total_str = f"+${total_pnl:.2f}" if total_pnl >= 0 else f"-${abs(total_pnl):.2f}"
    print(f"Total Unrealized P&L: {total_str}")


def cmd_balance(client, args):
    """Check account balance (values returned in cents)"""
    data = client._request("GET", "/portfolio/balance")
    
    # Kalshi API returns values in cents - convert to dollars
    balance_cents = data.get('balance', 0)
    portfolio_cents = data.get('portfolio_value', 0)
    unsettled_cents = data.get('unsettled_amount', 0)
    deposit_cents = data.get('available_for_deposit', 0)
    
    balance_dollars = balance_cents / 100
    portfolio_dollars = portfolio_cents / 100
    unsettled_dollars = unsettled_cents / 100
    deposit_dollars = deposit_cents / 100
    
    print("\n💰 Account Balance")
    print("-" * 40)
    print(f"Balance: ${balance_dollars:,.2f}")
    print(f"Portfolio Value: ${portfolio_dollars:,.2f}")
    print(f"Buying Power: ${(balance_dollars - portfolio_dollars):,.2f}")
    if unsettled_cents > 0:
        print(f"Unsettled: ${unsettled_dollars:,.2f}")
    if deposit_cents > 0:
        print(f"Available for Withdrawal: ${deposit_dollars:,.2f}")


def cmd_pnl(client, args):
    data = client._request("GET", "/portfolio/balance")
    positions_data = client._request("GET", "/portfolio/positions")
    positions = positions_data.get('positions', [])

    balance = data.get('balance', 0) / 100
    portfolio_value = data.get('portfolio_value', 0) / 100
    buying_power = balance - portfolio_value

    total_unrealized = 0
    for p in positions:
        total_unrealized += p.get('unrealized_pnl', 0)

    print("\n📊 P&L Snapshot")
    print("-" * 40)
    print(f"Balance: ${balance:,.2f}")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Buying Power: ${buying_power:,.2f}")
    print(f"Open Positions: {len(positions)}")
    print(f"Unrealized P&L: ${total_unrealized:,.2f}")


def main():
    parser = argparse.ArgumentParser(description="Kalshi Prediction Markets CLI")
    parser.add_argument('--demo', action='store_true', help='Use demo environment')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Opportunities
    p = subparsers.add_parser('opportunities', help='Find markets with volume (accounts for MVE markets)')
    p.add_argument('--min-volume', type=int, help='Minimum volume threshold (default: 50)')
    p.add_argument('--limit', type=int, default=30, help='Max results to show')
    
    # Hot
    p = subparsers.add_parser('hot', help='Show trending markets (may be empty for MVE)')
    p.add_argument('--limit', type=int, default=20, help='Number of markets to show')
    
    # Markets
    p = subparsers.add_parser('markets', help='List markets with filters')
    p.add_argument('--status', choices=['unopened', 'open', 'closed', 'settled'], default='open')
    p.add_argument('--series', help='Filter by series_ticker')
    p.add_argument('--event', help='Filter by event_ticker')
    p.add_argument('--tickers', help='Comma-separated list of tickers')
    p.add_argument('--mve-filter', choices=['only', 'exclude'], help='Filter MVE markets')
    p.add_argument('--min-close-ts', type=int, help='Unix timestamp (seconds)')
    p.add_argument('--max-close-ts', type=int, help='Unix timestamp (seconds)')
    p.add_argument('--min-created-ts', type=int, help='Unix timestamp (seconds)')
    p.add_argument('--max-created-ts', type=int, help='Unix timestamp (seconds)')
    p.add_argument('--min-updated-ts', type=int, help='Unix timestamp (seconds) - only compatible with mve_filter=exclude')
    p.add_argument('--min-settled-ts', type=int, help='Unix timestamp (seconds)')
    p.add_argument('--max-settled-ts', type=int, help='Unix timestamp (seconds)')
    p.add_argument('--min-volume', type=int, help='⚠️ Most markets have 0 volume - filter carefully')
    p.add_argument('--max-volume', type=int)
    p.add_argument('--min-yes-ask', type=float)
    p.add_argument('--max-yes-ask', type=float)
    p.add_argument('--resolve-soon', type=int, help='Only include markets closing within N days')
    p.add_argument('--min-liquidity', type=int, help='Min total shares at top orderbook levels')
    p.add_argument('--liquidity-depth', type=int, default=1, help='Orderbook depth levels to sum (default: 1)')
    p.add_argument('--spread-max', type=float, help='Max bid-ask spread (dollars)')
    p.add_argument('--sort', help='Sort by field (e.g., volume, volume_24h, liquidity, spread, yes_ask_dollars, yes_bid_dollars, close_date)')
    p.add_argument('--no-desc', action='store_true')
    p.add_argument('--limit', type=int, default=50)
    p.add_argument('--cursor', help='Pagination cursor from API')
    
    # Search
    p = subparsers.add_parser('search', help='Search markets by keyword')
    p.add_argument('query')
    p.add_argument('--status', default='open')
    p.add_argument('--min-volume', type=int)
    p.add_argument('--sort', default='volume')
    p.add_argument('--limit', type=int, default=30)
    
    # Other commands
    p = subparsers.add_parser('categories', help='Show available categories (limited for MVE)')
    
    p = subparsers.add_parser('series', help='List market series')
    p.add_argument('--category')
    p.add_argument('--tags', help='Comma-separated list of tags')
    p.add_argument('--include-product-metadata', action='store_true')
    p.add_argument('--include-volume', action='store_true')
    
    p = subparsers.add_parser('events', help='List events')
    p.add_argument('--status', default='open', choices=['open', 'closed', 'settled'])
    p.add_argument('--limit', type=int, default=30)
    p.add_argument('--with-nested-markets', action='store_true')
    p.add_argument('--with-milestones', action='store_true')
    p.add_argument('--series', help='Filter by series_ticker')
    p.add_argument('--min-close-ts', type=int, help='Unix timestamp (seconds)')
    p.add_argument('--cursor', help='Pagination cursor from API')

    p = subparsers.add_parser('events-mve', help='List multivariate events')
    p.add_argument('--series', help='Filter by series_ticker')
    p.add_argument('--collection', help='Filter by collection_ticker')
    p.add_argument('--with-nested-markets', action='store_true')
    p.add_argument('--limit', type=int, default=30)
    p.add_argument('--cursor', help='Pagination cursor from API')
    
    p = subparsers.add_parser('orderbook', help='View order book with MVE leg info')
    p.add_argument('ticker')
    
    p = subparsers.add_parser('candlesticks', help='Get price history')
    p.add_argument('ticker')
    p.add_argument('--limit', type=int, default=100)
    
    p = subparsers.add_parser('trades', help='Recent trades')
    p.add_argument('ticker')
    p.add_argument('--limit', type=int, default=20)

    p = subparsers.add_parser('market', help='Unified market view')
    p.add_argument('ticker')

    p = subparsers.add_parser('size', help='Order sizing calculator')
    p.add_argument('--price', type=float, required=True, help='Market price in dollars (0-1)')
    p.add_argument('--probability', type=float, required=True, help='Your YES probability estimate (0-1)')
    p.add_argument('--side', choices=['yes', 'no'], default='yes', help='Contract side to size (default: yes)')
    p.add_argument('--portfolio-value', type=float, required=True, help='Total portfolio value in dollars')
    p.add_argument('--kelly-fraction', type=float, default=0.3, help='Fraction of Kelly to use (default: 0.3)')
    p.add_argument('--max-position', type=float, help='Cap position fraction of portfolio (0-1)')
    
    p = subparsers.add_parser('buy', help='Place buy order')
    p.add_argument('--ticker', required=True)
    p.add_argument('--side', required=True, choices=['yes', 'no'])
    p.add_argument('--count', required=True, type=int)
    p.add_argument('--price', type=float, help='Limit price in dollars (omit for market order)')
    
    p = subparsers.add_parser('sell', help='Place sell order')
    p.add_argument('--ticker', required=True)
    p.add_argument('--side', required=True, choices=['yes', 'no'])
    p.add_argument('--count', required=True, type=int)
    p.add_argument('--price', type=float, help='Limit price in dollars (omit for market order)')
    
    p = subparsers.add_parser('orders', help='List orders')
    p.add_argument('--status')
    p.add_argument('--limit', type=int, default=50)
    p.add_argument('--stale-minutes', type=int, help='Only show orders older than N minutes')
    p.add_argument('--cancel-stale', action='store_true', help='Cancel orders selected by --stale-minutes')
    
    p = subparsers.add_parser('cancel', help='Cancel order')
    p.add_argument('order_id')
    
    p = subparsers.add_parser('positions', help='View positions')
    p.add_argument('--close-soon', type=int, help='Only show positions closing within N days')
    subparsers.add_parser('balance', help='Check balance')
    subparsers.add_parser('pnl', help='P&L snapshot')

    p = subparsers.add_parser('watchlist', help='Manage watchlist')
    p.add_argument('action', choices=['add', 'remove', 'list', 'scan'])
    p.add_argument('tickers', nargs='*')
    
    parsed = parser.parse_args()
    if not parsed.command:
        parser.print_help()
        print("\n📚 For MVE market help, see: file 'Skills/kalshi-predictions/SKILL.md'")
        sys.exit(0)

    if parsed.demo:
        print("-- USING DEMO API --")
    
    try:
        client = KalshiClient(use_demo=parsed.demo)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nSet environment variables:")
        print("  export KALSHI_API_KEY_ID='your-key-id'")
        print("  export KALSHI_PRIVATE_KEY='your-private-key'")
        print("\nOr add them in [Settings > Developers](/?t=settings&s=developers)")
        sys.exit(1)
    
    try:
        cmds = {
            'opportunities': cmd_opportunities,
            'hot': cmd_hot,
            'markets': cmd_markets, 
            'search': cmd_search, 
            'categories': cmd_categories,
            'series': cmd_series, 
            'events': cmd_events, 
            'events-mve': cmd_events_mve,
            'market': cmd_market,
            'size': cmd_size,
            'orderbook': cmd_orderbook,
            'candlesticks': cmd_candlesticks,
            'trades': cmd_trades, 
            'buy': cmd_buy, 
            'sell': cmd_sell, 
            'orders': cmd_orders,
            'cancel': cmd_cancel, 
            'positions': cmd_positions, 
            'balance': cmd_balance,
            'pnl': cmd_pnl,
            'watchlist': cmd_watchlist,
        }
        cmds[parsed.command](client, parsed)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
