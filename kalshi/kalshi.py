#!/usr/bin/env python3
"""Kalshi Prediction Markets CLI
Agent tailored tool for market discovery and betting
Follows official Kalshi API documentation
"""

import argparse
import base64
import os
import re
from datetime import datetime

import numpy as np
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding

# Production API endpoint (default)
PRODUCTION_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
# Demo environment for testing
DEMO_BASE_URL = "https://demo-api.kalshi.co/trade-api/v2"

class CoinbaseClient:
    """
    Public Coinbase API Client
    Fetch the complete documentation index at: https://docs.cdp.coinbase.com/llms.txt
    """

    def __init__(self, currency: str = "USD"):
        self.base_url = "https://api.exchange.coinbase.com"
        self.currency = currency

    def get_product(self, ticker: str):
        """Get product by ticker"""
        response = requests.get(f"{self.base_url}/products")
        for product in response.json():
            if product["id"] == f"{ticker}-{self.currency}":
                return product
        return None

    def get_ticker(self, ticker: str):
        """Get current price and volume"""
        product = self.get_product(ticker)
        if product is None:
            return None
        response = requests.get(f"{self.base_url}/products/{product.get('id')}/ticker")
        return response.json()

    def get_stats(self, ticker: str):
        """Get 24h and 30d stats (volume, open, high, low)"""
        product = self.get_product(ticker)
        if product is None:
            return None
        response = requests.get(f"{self.base_url}/products/{product.get('id')}/stats")
        return response.json()

    def get_orderbook(self, ticker: str):
        """Get orderbook for a product"""
        product = self.get_product(ticker)
        if product is None:
            return None
        response = requests.get(f"{self.base_url}/products/{product.get('id')}/book")
        return response.json()

    def get_candlesticks(self, ticker: str, granularity: str):
        """Get candlestick/price history for a product"""
        product = self.get_product(ticker)
        if product is None:
            return None
        response = requests.get(f"{self.base_url}/products/{product.get('id')}/candles?granularity={granularity}")
        data = response.json()
        data.reverse()
        return data

class KalshiClient:
    """Kalshi API Client with proper RSA-PSS signing"""

    def __init__(self, use_demo: bool = False):
        self.api_key_id = os.environ.get("KALSHI_API_KEY_ID", "")
        self.private_key_pem = os.environ.get("KALSHI_PRIVATE_KEY", "")
        self.base_url = DEMO_BASE_URL if use_demo else PRODUCTION_BASE_URL
        self.coinbase_client = CoinbaseClient()

        if not self.api_key_id or not self.private_key_pem:
            raise ValueError(
                "Missing KALSHI_API_KEY_ID or KALSHI_PRIVATE_KEY environment variables"
            )

        pem = self.private_key_pem

        # If the key is all on one line (from env var), format it properly
        if pem.count("\n") < 2:
            header = "-----BEGIN RSA PRIVATE KEY-----"
            footer = "-----END RSA PRIVATE KEY-----"

            # Remove header/footer if present
            body = pem
            if header in body:
                body = body.split(header)[1]
            if footer in body:
                body = body.split(footer)[0]

            # Clean up - remove all whitespace
            body = body.replace(" ", "").replace("\n", "").replace("\r", "")

            # Reconstruct with proper line wrapping (64 chars per line)
            lines = [body[i:i+64] for i in range(0, len(body), 64)]
            pem = f"{header}\n" + "\n".join(lines) + f"\n{footer}\n"

        self._private_key = serialization.load_pem_private_key(pem.encode(), password=None)

    def _sign_message(self, message: str) -> str:
        """Sign message with RSA-PSS using SHA256"""
        signature = self._private_key.sign(
            message.encode("utf-8"),
            rsa_padding.PSS(
                mgf=rsa_padding.MGF1(hashes.SHA256()),
                salt_length=rsa_padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    def request(self, method: str, path: str, body: dict = None) -> dict:
        """Make authenticated request to Kalshi API"""
        timestamp = str(int(datetime.now().timestamp() * 1000))
        # Sign with full API path including /trade-api/v2
        path_without_query = "/trade-api/v2" + path.split("?")[0]
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

    def get_all(self, base_pagination_url, data_key):
        """Handling pagination for a url supporting it"""
        all = []
        cursor = None

        while True:
            url = f"{base_pagination_url}{'&' if '?' in base_pagination_url else '?'}limit=1000"

            if cursor:
                url += f"&cursor={cursor}"

            data = self.request("GET", url)
            more_data = data.get(data_key, [])

            if more_data:
                all.extend(more_data)

            # Check if there are more pages
            cursor = data.get("cursor")

            if not cursor:
                break

        return all

def calculate_best_prices(orderbook_data):
    """Calculate the best bid prices and implied asks"""
    orderbook = orderbook_data['orderbook']

    result = {}

    # Best bids (if any exist)
    if orderbook['yes']:
        best_yes_bid = orderbook['yes'][-1][0]  # Last element is highest
        result['best_yes_bid_dollars'] = best_yes_bid / 100

    if orderbook['no']:
        best_no_bid = orderbook['no'][-1][0]  # Last element is highest
        best_yes_ask = 100 - best_no_bid
        result['best_yes_ask_dollars'] = best_yes_ask / 100


    if orderbook['no']:
        best_no_bid = orderbook['no'][-1][0]  # Last element is highest
        result['best_no_bid_dollars'] = best_no_bid / 100

    if orderbook['yes']:
        best_yes_bid = orderbook['yes'][-1][0]  # Last element is highest
        best_no_ask = 100 - best_yes_bid
        result['best_no_ask_dollars'] = best_no_ask / 100

    return result

def calculate_depth(orderbook_data, depth_cents=5):
    """Calculate total volume within X cents of best bid"""
    orderbook = orderbook_data['orderbook']

    yes_depth = 0
    no_depth = 0

    # YES side depth (iterate backwards from best bid)
    if orderbook['yes']:
        best_yes = orderbook['yes'][-1][0]  # Last element is highest
        for price, quantity in reversed(orderbook['yes']):
            if best_yes - price <= depth_cents:
                yes_depth += quantity
            else:
                break

    # NO side depth (iterate backwards from best bid)
    if orderbook['no']:
        best_no = orderbook['no'][-1][0]  # Last element is highest
        for price, quantity in reversed(orderbook['no']):
            if best_no - price <= depth_cents:
                no_depth += quantity
            else:
                break

    return {"yes_depth": yes_depth, "no_depth": no_depth}

def holt_step(L, T, x, alpha, beta):
    prevL = L
    Ln = alpha * x + (1 - alpha) * (L + T)
    Tn = beta * (Ln - prevL) + (1 - beta) * T
    return Ln, Tn

def holt_fit(data, alpha, beta):
    if len(data) < 2:
        raise ValueError("Need at least 2 data points to initialize Holt's method.")
    L = data[0]
    T = data[1] - data[0]
    for x in data:
        L, T = holt_step(L, T, x, alpha, beta)
    return L, T

def predict(data, alpha = 0.28, beta = 0.18, steps = 2):
    L, T = holt_fit(data, alpha, beta)
    return [L + h * T for h in range(1, steps + 1)]



# CLI Commands
def cmd_hot(client, args):
    """
    Get top markets sorted by volume for a given category and frequency.
    Also includes latest Coinbase data for Crypto series.
    """
    series = client.request("GET", f"/series?category={args.category}&include_volume=true")
    series = series['series']
    filtered_series = []
    for s in series:
        if s.get("ticker") and s.get("volume") > 0:
            if "frequency" in s and s.get("frequency") == args.frequency:
                filtered_series.append(s)
            else:
                filtered_series.append(s)
    series = filtered_series
    series.sort(key=lambda x: x.get("volume"), reverse=True)
    series = series[args.start:args.start + args.limit]

    for s in series:
        markets = client.request("GET", f"/markets?series_ticker={s.get('ticker')}&status=open&sort=volume&limit=20")
        markets = markets.get("markets", [])

        if len(markets) == 0:
            continue

        filtered_markets = []
        for m in markets:
            if m.get("ticker") and m.get("volume") > 0:
                if not args.binary or m.get("market_type") == "binary":
                    filtered_markets.append(m)

        filtered_markets.sort(key=lambda x: x.get("volume"), reverse=True)

        for m in filtered_markets:
            m["get_detailed_stats_command"] = f"python3 kalshi/kalshi.py stats --ticker {m.get('ticker')} --series-ticker {s.get('ticker')}"

        s["markets"] = filtered_markets

        if args.category == "Crypto":
            tags = s.get("tags") or []
            crypto_ticker = [t for t in tags if t.lower() != args.frequency.lower()]

            if len(crypto_ticker) > 0:
                crypto_ticker = crypto_ticker[0]

            if not crypto_ticker:
                maybe_name = re.split(r"\s+", s.get("title", ""))

                if len(maybe_name) > 0:
                    crypto_ticker = maybe_name[0].lower()

            if crypto_ticker:
                coinbase_ticker = client.coinbase_client.get_ticker(crypto_ticker)
                coinbase_stats = client.coinbase_client.get_stats(crypto_ticker)
                orderbook = client.coinbase_client.get_orderbook(crypto_ticker)
                candles_1m_response = client.coinbase_client.get_candlesticks(crypto_ticker, "60")
                candles_1m = []

                if candles_1m_response:
                    candles_1m = [{
                        "time": c[0],
                        "low": c[1],
                        "high": c[2],
                        "open": c[3],
                        "close": c[4],
                        "volume": c[5]
                    } for c in candles_1m_response[-15:]]

                candles_1h_response = client.coinbase_client.get_candlesticks(crypto_ticker, "3600")
                candles_1h = []

                if candles_1h_response:
                    candles_1h = [{
                        "time": c[0],
                        "low": c[1],
                        "high": c[2],
                        "open": c[3],
                        "close": c[4],
                        "volume": c[5]
                    } for c in candles_1h_response[-15:]]

                candles_6h_response = client.coinbase_client.get_candlesticks(crypto_ticker, "21600")
                candles_6h = []

                if candles_6h_response:
                    candles_6h = [{
                        "time": c[0],
                        "low": c[1],
                        "high": c[2],
                        "open": c[3],
                        "close": c[4],
                        "volume": c[5]
                    } for c in candles_6h_response[-15:]]

                s["coinbase_ticker"] = coinbase_ticker
                s["coinbase_stats"] = coinbase_stats
                s["coinbase_orderbook"] = orderbook
                s["coinbase_candles"] = {
                    "1m_last_15m": candles_1m,
                    "1h_last_15h": candles_1h,
                    "6h_last_90h": candles_6h
                }
                try:
                    s["coinbase_holt_prediction"] = predict([x.get("close") for x in candles_6h])
                except Exception as e:
                    print(f"Error predicting {crypto_ticker}: {e}")
                    s["coinbase_holt_prediction"] = None

    series = [s for s in series if s.get("markets") and len(s.get("markets")) > 0]

    return series

def cmd_stats(client, args):
    """
    Get stats for a market including orderbook, trades, and candlesticks

    https://docs.kalshi.com/getting_started/orderbook_responses.md
    https://docs.kalshi.com/api-reference/market/get-trades.md
    https://docs.kalshi.com/api-reference/market/get-market-candlesticks.md
    """
    result = {}

    orderbook = client.request("GET", f"/markets/{args.ticker}/orderbook")
    result["orderbook"] = orderbook.get("orderbook", {})
    result["best_prices"] = calculate_best_prices(orderbook)
    result["depth"] = calculate_depth(orderbook)

    trades = client.request("GET", f"/markets/trades?ticker={args.ticker}&limit=50")
    result["trades"] = trades.get("trades", [])

    candlesticks = client.request("GET", f"/series/{args.series_ticker}/markets/{args.ticker}/candlesticks?start_ts={int((datetime.now().timestamp() - 900))}&end_ts={int((datetime.now().timestamp()))}&period_interval=1")
    result["candlesticks"] = candlesticks.get("candlesticks", [])

    series = client.request("GET", f"/series/{args.series_ticker}")
    series = series.get("series", {})
    result["settlement_sources"] = series.get("settlement_sources", [])

    return result

def cmd_buy(client, args):
    """
    Place a limit buy order

    https://docs.kalshi.com/api-reference/orders/create-order.md
    """
    order_data = {
        "ticker": args.ticker,
        "side": args.side,
        "action": "buy",
        "count": args.count,
        "type": "limit",
    }

    if args.price:
        if args.price <= 0 or args.price >= 1:
            print("Error: --price must be between 0 and 1 (exclusive).")
            return
        price_key = "yes_price_dollars" if args.side == "yes" else "no_price_dollars"
        order_data[price_key] = f"{args.price:.4f}"

    return client.request("POST", "/portfolio/orders", order_data)


def cmd_sell(client, args):
    """
    Place a limit or market sell order

    https://docs.kalshi.com/api-reference/orders/create-order.md
    """
    order_data = {
        "ticker": args.ticker,
        "side": args.side,
        "action": "sell",
        "count": args.count,
        "type": "limit" if args.price else "market",
    }
    if args.price:
        if args.price <= 0 or args.price >= 1:
            print("Error: --price must be between 0 and 1 (exclusive).")
            return
        price_key = "yes_price_dollars" if args.side == "yes" else "no_price_dollars"
        order_data[price_key] = f"{args.price:.4f}"

    return client.request("POST", "/portfolio/orders", order_data)

def cmd_cancel(client, args):
    """Cancel order by ID"""
    return client.request("DELETE", f"/portfolio/orders/{args.order_id}")

def cmd_account(client):
    """
    Get account snapshot (balance, positions, orders, P&L)
    https://docs.kalshi.com/api-reference/portfolio/get-balance.md
    https://docs.kalshi.com/api-reference/portfolio/get-positions.md
    https://docs.kalshi.com/api-reference/orders/get-orders.md
    https://docs.kalshi.com/api-reference/portfolio/get-fills.md
    """
    balance_resp = client.request("GET", "/portfolio/balance")
    positions = client.get_all("/portfolio/positions", "event_positions")
    orders = client.get_all("/portfolio/orders", "orders")
    fills = client.get_all("/portfolio/fills", "fills")

    cash_cents = balance_resp.get("balance", 0)
    portfolio_value_cents = balance_resp.get("portfolio_value", 0)
    account_value_dollars = round((cash_cents + portfolio_value_cents) / 100, 2)
    balance_dollars = {
        "cash": round(cash_cents / 100, 2),
        "portfolio_value": round(portfolio_value_cents / 100, 2),
    }

    market_positions = client.get_all("/portfolio/positions?count_filter=total_traded", "market_positions")
    total_realized_pnl_centicents = 0
    total_fees_centicents = 0

    for mp in market_positions:
        total_realized_pnl_centicents += mp.get("realized_pnl", 0)
        total_fees_centicents += mp.get("fees_paid", 0)

    total_unrealized_pnl_cents = portfolio_value_cents - cash_cents

    total_realized_pnl_dollars = round(total_realized_pnl_centicents / 10000, 2)
    total_fees_dollars = round(total_fees_centicents / 10000, 2)
    total_unrealized_pnl_dollars = round(total_unrealized_pnl_cents / 100, 2)
    total_pnl_dollars = round(total_realized_pnl_dollars + total_unrealized_pnl_dollars, 2)
    net_pnl_dollars = round(total_pnl_dollars - total_fees_dollars, 2)

    return {
        "net_pnl": net_pnl_dollars,
        "account_value": account_value_dollars,
        "balance": balance_dollars,
        "positions": positions,
        "orders": orders,
        "fills": fills,
        "market_positions": market_positions,
    }

def ev_and_edge_scalar(p_win, decimal_odds, stake):
    edge_per_bet = p_win * (decimal_odds - 1) - (1 - p_win)
    ev_per_bet = stake * edge_per_bet
    edge_decimal = p_win * decimal_odds - 1.0
    edge_pct = edge_decimal * 100.0
    return ev_per_bet, edge_decimal, edge_pct

def implied_probability_scalar(decimal_odds):
    return 1.0 / decimal_odds

def edge_vs_implied_scalar(p_true, decimal_odds):
    p_implied = implied_probability_scalar(decimal_odds)
    edge = p_true - p_implied
    return edge, p_implied

def no_vig_edge_scalar(p_true, decimal_odds):
    ip = 1.0 / decimal_odds
    p_fair = ip  # for a single-outcome view
    edge = p_true - p_fair
    return edge, p_fair

def kelly_fraction_scalar(p_win, decimal_odds):
    b = decimal_odds - 1.0
    if b <= 0.0:
        return 0.0
    q = 1.0 - p_win
    f = (p_win * b - q) / b
    return max(0.0, min(1.0, f))

def log_growth_scalar(p_win, decimal_odds, f):
    b = decimal_odds - 1.0
    q = 1.0 - p_win
    term_win = p_win * np.log1p(f * b)
    term_loss = q * np.log1p(-f)
    return term_win + term_loss

def clv_scalar(opening_odds, closing_odds):
    p_open = 1.0 / opening_odds
    p_close = 1.0 / closing_odds
    clv = (p_close / p_open) - 1.0
    return clv

def roi_scalar(profit, stake):
    return profit / stake

def sharpe_scalar(returns, risk_free=0.0):
    # returns is a 1-element array or scalar
    arr = np.array(returns, dtype=float)
    mean_r = arr.mean()
    std_r = arr.std(ddof=1) if arr.size > 1 else 0.0
    return (mean_r - risk_free) / std_r if std_r > 0 else 0.0

def bet_edge_all_in_one(p_win, decimal_odds, stake,
                       opening_odds=None, closing_odds=None,
                       risk_free=0.0):
    """
    Compute multiple edge metrics for a single bet.
    All inputs can be scalars or 1-element arrays.

    Returns a dict with:
      ev_per_bet, edge_decimal, edge_pct,
      p_implied, edge_vs_implied,
      edge_no_vig, p_fair_overall,
      kelly_frac,
      clv,
      roi, sharpe
      log_growth_f   (optional for a given f)
    """
    p_win = float(np.asarray(p_win).item())
    decimal_odds = float(np.asarray(decimal_odds).item())
    stake = float(np.asarray(stake).item())

    # 1) EV and edge
    edge_per_bet = p_win * (decimal_odds - 1.0) - (1.0 - p_win)
    ev_per_bet = stake * edge_per_bet
    edge_decimal = p_win * decimal_odds - 1.0
    edge_pct = edge_decimal * 100.0

    # 2) Implied probability and edge vs implied
    p_implied = 1.0 / decimal_odds
    edge_vs_implied = p_win - p_implied

    # 3) No-vig / fair odds (single-outcome view)
    # For a single bet, no-vig edge = p_true - p_implied
    edge_no_vig = p_win - p_implied
    p_fair_overall = p_implied  # single-outcome fairness

    # 4) Kelly fraction
    b = decimal_odds - 1.0
    if b > 0.0:
        q = 1.0 - p_win
        kelly_frac = max(0.0, min(1.0, (p_win * b - q) / b))
    else:
        kelly_frac = 0.0

    # 5) CLV (requires opening and closing odds if provided)
    if opening_odds is not None and closing_odds is not None:
        opening_odds = float(np.asarray(opening_odds).item())
        closing_odds = float(np.asarray(closing_odds).item())
        p_open = 1.0 / opening_odds
        p_close = 1.0 / closing_odds
        clv = (p_close / p_open) - 1.0
    else:
        clv = None

    # 6) ROI (scalar burst, 1 bet)
    profit = stake * (p_win * (decimal_odds - 1.0) - (1.0 - p_win))
    roi = profit / stake if stake != 0 else 0.0

    # 7) Sharpe-like (need distribution; here a single value)
    # If you only have this one bet, use a degenerate std = 0 -> Sharpe = 0
    sharpe = 0.0  # or compute if you have a distribution of returns

    # Optional: log-growth for a chosen Kelly fraction f
    # G = p*ln(1+f*b) + q*ln(1-f) with b = odds-1
    f = kelly_frac
    if b > 0.0:
        q = 1.0 - p_win
        G = p_win * np.log1p(f * b) + q * np.log1p(-f)
    else:
        G = None

    return {
        'ev_per_bet': round(ev_per_bet, 3),
        'edge_decimal': round(edge_decimal, 3),
        'edge_pct': round(edge_pct, 3),
        'p_implied': round(p_implied, 3),
        'edge_vs_implied': round(edge_vs_implied, 3),
        'edge_no_vig': round(edge_no_vig, 3),
        'p_fair_overall': round(p_fair_overall, 3),
        'kelly_frac': round(kelly_frac, 3),
        'clv': round(clv, 3),
        'roi': round(roi, 3),
        'sharpe': round(sharpe, 3),
        'log_growth_f': round(float(G), 3)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kalshi Prediction Markets CLI")
    parser.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Hot
    p = subparsers.add_parser("hot", help="Top markets by volume")
    p.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")
    p.add_argument("--start", type=int, default=0, help="The start index to show (default 0)")
    p.add_argument("--limit", type=int, default=10, help="Number of markets to show (default 10)")
    p.add_argument("--binary", action="store_true", default=True, help="Use binary markets (default True)")
    p.add_argument("--category", default="Crypto", help="Limit to series in this category (default Crypto)")
    p.add_argument("--frequency", choices=["hourly", "daily", "weekly", "monthly", "yearly"], default="hourly", help="Limit to markets in this frequency (default hourly)")

    # Stats
    p = subparsers.add_parser("stats", help="Get stats for a market")
    p.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")
    p.add_argument("--ticker", required=True)
    p.add_argument("--series-ticker", required=True)

    # Buy
    p = subparsers.add_parser("buy", help="Place a buy order")
    p.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")
    p.add_argument("--ticker", required=True)
    p.add_argument("--side", choices=["yes", "no"], required=True)
    p.add_argument("--count", type=int, default=1, help="Number of contracts to buy (default 1)")
    p.add_argument("--price", type=float, help="Limit price to buy at")

    # Sell
    p = subparsers.add_parser("sell", help="Place a sell order")
    p.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")
    p.add_argument("--ticker", required=True)
    p.add_argument("--side", choices=["yes", "no"], required=True)
    p.add_argument("--count", type=int, default=1, help="Number of contracts to sell (default 1)")
    p.add_argument("--price", type=float, help="Limit price to sell at. Leave blank for market order.")

    # Cancel
    p = subparsers.add_parser("cancel", help="Cancel an order")
    p.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")
    p.add_argument("--order-id", required=True)

    # Account
    p = subparsers.add_parser("account", help="Get account snapshot")
    p.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")

    # Edge
    p = subparsers.add_parser("edge", help="Calculate edge metrics for a single bet")
    p.add_argument("--demo", action="store_true", default=False, help="Use demo environment (default False)")
    p.add_argument("--p-win", type=float, required=True, help="The probability of winning the bet")
    p.add_argument("--decimal-odds", type=float, required=True, help="The decimal odds of the bet")
    p.add_argument("--stake", type=float, required=True, help="The percentage stake of the bet")
    p.add_argument("--opening-odds", type=float, required=True, help="The opening odds of the bet")
    p.add_argument("--closing-odds", type=float, required=True, help="The closing odds of the bet")

    args = parser.parse_args()
    client = KalshiClient(use_demo=args.demo)
    result = None

    if args.command == "hot":
        result = cmd_hot(client, args)
    elif args.command == "stats":
        result = cmd_stats(client, args)
    elif args.command == "buy":
        result = cmd_buy(client, args)
    elif args.command == "sell":
        result = cmd_sell(client, args)
    elif args.command == "cancel":
        result = cmd_cancel(client, args)
    elif args.command == "account":
        result = cmd_account(client)
    elif args.command == "edge":
        result = bet_edge_all_in_one(args.p_win, args.decimal_odds, args.stake, opening_odds=args.opening_odds, closing_odds=args.closing_odds)

    if result is not None:
        print(result)
    else:
        parser.print_help()
