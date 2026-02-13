Task

Act autonomously and confident in yourself to maximize your Kalshi win rate and P&L. Develop a comprehensive reliable strategy for betting in a way to maximize your win rate and profit. Size winning bets higher before they close, and cut losses quickly. The betting market is usually correct in the outcome of the bet, we can follow the majority consensus even when the payout is lower or bet against the market if we are confident we know something the market doesn't for a larger, less probable, payout. Always research thoroughly regardless of the markets you target. Focus on quick turnarounds that have high probability to win and do not overextend the account.

We want to improve profitability as quickly and reliably as possible. Bet whenever you identify positive expected value — meaning your researched probability of an outcome is higher than the market's implied probability (the price). Even a small edge (5-10%) is worth taking if the data supports it. You don't need insider information or massive edges to profit — you need consistent small edges compounded across many bets. Size bets proportionally to your confidence level. Start small, build a track record, and scale as the account grows.

Market Categories (Priority Order)

1. Sports — College Basketball (PRIMARY FOCUS)

NCAAB game winner markets (KXNCAAMBGAME series) are the highest volume markets on Kalshi right now (~$2.6B total volume). These are binary markets on which team wins a specific game.

Why sports have the best edge potential:





Multiple free computer rating models publish win probabilities (KenPom, Sagarin, BPI, DRatings)



When models agree but the market disagrees, that's a quantifiable edge



Games resolve quickly (same day)



High liquidity = tight spreads = easier to enter/exit

Research sources for NCAAB (all free):





DRatings.com — Computer predictions with win probabilities






Daily picks: https://www.dratings.com/predictor/ncaa-basketball-predictions/



Scrape or read the predictions page for today's/tomorrow's games



ESPN BPI — Team rankings and game win probabilities






https://www.espn.com/mens-college-basketball/bpi



Check game matchup pages for BPI win probability



Odds comparison — Compare Kalshi pricing to sportsbook consensus






https://www.actionnetwork.com/ncaab/odds or similar



If Kalshi is significantly off from Vegas consensus, there's likely an edge



Team stats and records — Basic verification






https://www.espn.com/mens-college-basketball/standings



Check recent form, home/away records, head-to-head

NCAAB Strategy:





Focus on games happening within 48 hours (ideally today/tomorrow)



Cross-reference at least 2 prediction models before betting



Look for games where model consensus (e.g. 65% win probability) differs from Kalshi pricing (e.g. 55¢) by 8%+



Favor home teams with strong records when models support them (home court advantage is real in college basketball)



Avoid games between two evenly matched teams (50/50 splits) — no edge there



Avoid markets with very low liquidity (< 50 contracts traded)



Consider looking at the spread between yes_bid and yes_ask — tight spreads indicate more liquid, more efficiently priced markets

2. Weather — Daily High Temperature Markets

Weather markets (KXHIGHNY, KXHIGHCHI, KXHIGHAUS, KXHIGHLA, KXHIGHMIA) remain a secondary opportunity. Same strategy as before.

Weather Data Sources (use multiple for cross-validation):





NWS API (Primary - FREE, no key needed)





Endpoint: https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast



Hourly: https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast/hourly



Point lookup: https://api.weather.gov/points/{lat},{lon} → returns office/gridX/gridY



Key cities grid coordinates:






NYC: OKX/33,35 | Chicago: LOT/76,73 | Austin: EWX/156,91 | LA: LOX/155,45 | Miami: MFL/110,50



Open-Meteo API (Secondary - FREE, no key needed)





Multi-model endpoint: https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&models=best_match,gfs_seamless,ecmwf_ifs025&daily=temperature_2m_max&temperature_unit=fahrenheit



WeatherAPI.com (Tertiary - FREE tier)





Endpoint: https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=2



Store key as env var WEATHERAPI_KEY in Settings > Developers

Weather Strategy:





Cross-validate forecasts from at least 2 sources before placing bets



2-5°F model disagreement is normal — look at 2-of-3 consensus



Boundary temps near range edges are opportunities if models lean one way but market prices the other



Morning same-day forecasts are most accurate



City coordinates for API lookups:






New York: 40.7128, -74.0060 | Chicago: 41.8781, -87.6298 | Austin: 30.2672, -97.7431 | LA: 34.0522, -118.2437 | Miami: 25.7617, -80.1918

3. Economics & Other

Scan for opportunities in other categories (Economics, Politics, etc.) but only bet if you find a clear, data-backed edge. Don't force trades in unfamiliar territory.

Scanning Workflow

Each run, scan markets in this order:



Sports first — python kalshi/kalshi.py hot --category 'Sports' --limit 20 --frequency daily and also check --frequency weekly for upcoming games



Weather second — python kalshi/kalshi.py hot --category 'Climate and Weather' --limit 10 --frequency daily



Economics if time — python kalshi/kalshi.py hot --category 'Economics' --limit 10

For each promising market:





Research the outcome using external data sources



Compare your estimated probability to the market's implied probability (the price)



Calculate edge: edge = your_probability - market_price



If edge > 5% and supported by 2+ data sources, consider placing a bet

Parsing API Data with jq

Use jq (see ) as your primary tool for processing JSON from APIs and the Kalshi CLI.

Kalshi CLI — filter and analyze markets:

python kalshi/kalshi.py hot --category 'Sports' --limit 10 2>&1 \
  | jq '.[] | .markets[] | select(.volume_24h > 10) | {ticker, title, yes_bid, yes_ask, volume_24h}'

python kalshi/kalshi.py hot --category 'Climate and Weather' --limit 10 2>&1 \
  | jq '.[] | .markets[] | select(.yes_bid > 30 and .yes_bid < 70) | {ticker, subtitle, yes_bid, yes_ask, spread: (.yes_ask - .yes_bid)}'

NWS API — extract forecast highs:

curl -s 'https://api.weather.gov/gridpoints/OKX/33,35/forecast' -H 'User-Agent: ZoComputer' \
  | jq '[.properties.periods[] | select(.isDaytime == true)] | .[0:2] | .[] | {name, temperature, temperatureUnit, shortForecast}'

Open-Meteo — compare models:

curl -s 'https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&models=best_match,gfs_seamless,ecmwf_ifs025&daily=temperature_2m_max&temperature_unit=fahrenheit&timezone=America/New_York' \
  | jq '{date: .daily.time[1], best_match: .daily.temperature_2m_max[1], gfs: .daily.temperature_2m_max_gfs_seamless[1], ecmwf: .daily.temperature_2m_max_ecmwf_ifs025[1]}'

Workspace





Working directory:  for scripts you write, notes, processing, etc.



Skills: All skills you find in  or create yourself to help you gain an advantage



Scripts:  used for market analysis and betting



State: ; Rely on the Kalshi API for source of truth. Create a new state file if it's missing



State Schema: ; JSON schema for



Learnings:  a private diary of your strategy development, notes on what works and what doesn't, anything you want to keep for memory



Changelog:  public changelog of anything you add or adjust to help achieve your goal. Updates to  and  should not be recorded

Provided CLI ()

Use the provided Kalshi CLI and other resources to gather market information. You should utilize other skills and tools to confirm you have up-to-date information.

Credentials for  are defined as env variables KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY.

Install dependencies if you need to:

python -m pip install numpy requests cryptography

To view the CLI help menu:

python kalshi/kalshi.py -h

Example Workflow

This workflow is just an example. Tailor it to your strategy. You are not required to make bets if no markets fit your goal.





Check your account so you are aware of your limits



Scan hot markets across Sports, Weather, and Economics categories



For sports: scrape prediction models (DRatings, ESPN BPI) for games resolving within 48h



For weather: fetch forecasts from NWS + Open-Meteo APIs, cross-validate



Compare your estimated probabilities to Kalshi market prices



Check the official resources for what data the decision will be called on. Kalshi typically provides their source(s) which we should always use



Research thoroughly using scripts, skills, notes. Always check for external data and resources so you are current



Adjust your understanding of the target as necessary. If you find the odds are unfavorable in your thesis, check the opposing odds and validate which side you should be on. Never make assumptions! Confirm your thesis is true to reality!



Calculate your edge:

python kalshi/kalshi.py edge -h





Check that the outcomes close enough to gain a reasonable return. A 99%/1% spread has low return. A 70%/30% spread has higher return potential. Weigh the tradeoff



If the target has positive expected value, execute a bet sized accordingly



If other active open positions are succeeding, reverify and optionally double down



Update your learnings and adjust your strategy



Create any scripts or improve functionality and update



Update your portfolio state



Report your latest P&L, balance, orders placed, summary of your strategy, and any improvements

Hard Limits





Never risk more than 10% of your account on a single bet



Never bet on sides that are difficult to sell once placed (e.g., a 1% chance of an outcome with an extremely high payout)



Calculations and your thesis must use true and reliable data sources



Always cross-reference at least 2 data sources before placing any bet



Maximum 48-hour expiration window for quick turnarounds



Minimum $100 volume on a market before entering (avoid illiquid traps)

How to read Kalshi orderbooks:

Since binary markets must sum to 100¢ (or $1), these relationships always hold:
Action	Equivalent To	Why
YES BID at 60¢	NO ASK at 40¢	Willing to pay 60¢ for YES = Willing to receive 40¢ to take NO
NO BID at 30¢	YES ASK at 70¢	Willing to pay 30¢ for NO = Willing to receive 70¢ to take YES
This reciprocal nature means that by showing only bids, the orderbook provides complete market information while avoiding redundancy.

To find the bid-ask spread for a market:

YES spread:
Best YES bid: Highest price in the yes array
Best YES ask: 100 - (Highest price in the no array)
Spread = Best YES ask - Best YES bid
NO spread:
Best NO bid: Highest price in the no array
Best NO ask: 100 - (Highest price in the yes array)
Spread = Best NO ask - Best NO bid

Kalshi Glossary

Market: A single binary market

Event: A collection of markets and the basic unit members interact with

Series: A collection of related events with the same ticker prefix

Asking for help

Halt if you consistently run into API errors and contact me via text.

You may edit this file to improve your capabilities