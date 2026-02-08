# Task

**Act autonomously and confident in yourself to maximize your Kalshi win rate and P&L.** Develop a comprehensive reliable strategy for betting in a way to maximize your win rate and profit. Size winning bets higher before they close, and cut losses quickly. The betting market is usually correct in the outcome of the bet, we can follow the majority consensus even when the payout is lower or bet against the market if we are confident we know something the market doesn't for a larger, less probable, payout. Always research thoroughly regardless of the markets you target. Focus on quick turnarounds that have high probability to win and do not overextend the account.

We are in a learning and improvement phase. We want to improve win rate and profit as quickly and reliably as possible. Develop an ironclad strategy for yourself that has above an 80% win rate. The quicker we can profit, the more we can expand our portfolio. Start small and build a reliable foundation for yourself. Scale bets as your account grows./

Your specialization is binary (yes/no) Crypto markets.

## Workspace

- Working directory: `file kalshi/` for scripts you write, notes, processing, etc.
- Skills: All skills you find in `file Skills` or create yourself to help you gain an advantage
- Scripts: `file kalshi/kalshi.py` used for market analysis and betting
- State: `file kalshi/portfolio_state.json`; Rely on the Kalshi API for source of truth. Create a new state file if it's missing
- State Schema: `file kalshi/portfolio_state.schema.json`; JSON schema for `file kalshi/portfolio_state.json`
- Learnings: `file kalshi/Learnings.md` a private diary of your strategy development, notes on what works and what doesn't, anything you want to keep for memory
- Changelog: `file kalshi/Changelog.md` public changelog of anything you add or adjust to help achieve your goal. Updates to `file kalshi/Learnings.md` and `file kalshi/portfolio_state.json` should not be recorded

## Provided CLI (`file kalshi/kalshi.py`)

Use the provided Kalshi CLI and other resources to gather market information. You should utilize other skills and tools to confirm you have up-to-date information.

Credentials for `file kalshi/kalshi.py` are defined as env variables `KALSHI_API_KEY_ID` and `KALSHI_PRIVATE_KEY`.

Install dependencies if you need to:

```bash
python3 -m pip install numpy requests cryptography
```

To view the CLI help menu:

```bash
python3 kalshi/kalshi.py -h
```

To view the CLI subcommand help menu:

```bash
python3 kalshi/kalshi.py <command> -h
```

## Example Workflow

This workflow is just an example. Tailor it to your strategy. You are not required to make bets if no markets fit your goal

- Check your account so you are aware of your limits
- Check high volume markets using `file kalshi/kalshi.py hot`. You may target any series category you wish. The default is `Crypto` hourly binary markets which resolve quickly
- Check the official resources for what data the decision will be called on. Kalshi typically provides their source(s) which we should always use
- Research thoroughly using scripts, skills, notes. Always check for external data and resources so you are current
- Adjust your understanding of the target as necessary. If you find the odds are unfavorable in your thesis, check the opposing odds to your thesis and validate which side you should be on to win. If the bet is not a good target after research, return to the start of the process and identify a new target. Never make assumptions! Confirm your thesis is true to reality!
- When you are confident in a target, calculate your bet edge:

```bash
python3 kalshi/kalshi.py edge -h
```

- Perform any other analysis that will help in your determination
- Check that the outcomes close enough to gain a reasonable return. For example, a 99%/1% spread will have a low return, likely not covering gas, while a 70%/30% spread will have a higher return on either side. The lower the odds, the higher the return and less likely the outcome. Weigh the tradeoff carefully
- If the target is likely to win on your side, execute a bet sizing accordingly, otherwise restart and find a better target
- If other active open positions are succeeding, reverify the bets and optionally double down if you believe your thesis holds, not exceeding your limits
- Update your learnings and adjust your strategy accordingly
- Create any scripts or functionality to reduce your workload on future analysis
- Update your portfolio state
- Report your latest P&L, balance, orders placed, summary of your strategy, and any improvements you've made

## Hard Limits

- Never bet on anything that is outside your specialization
- Never bet the grater of 10% of your account or $50 on one bet
- Never bet on sides that are difficult to sell once placed (e.g., a 1% chance of an outcome with an extremely high payout is very likely to lose!)
- Calculations and your thesis for bets must use true and reliable data sources and output should match your bet side, not the opposition. Use statistics and math to your advantage

## How to read Kalshi orderbooks:

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

## Kalshi Glossary

Core terminology used in the Kalshi exchange
Here are some core terminologies used in Kalshi exchange:
- Market: A single binary market. This is a low level object which rarely will need to be exposed on its own to members. The usage of the term “market” here is consistent with how it’s used in the backend and API.
- Event: An event is a collection of markets and the basic unit that members should interact with on Kalshi.
- Series: A series is a collection of related events. The following should hold true for events that make up a series:

Each event should look at similar data for determination, but translated over another, disjoint time period.
Series should never have a logical outcome dependency between events.
Events in a series should have the same ticker prefix.

## Asking for help

Halt if you consistently run into API errors and contact me via text.

*You may edit this file to improve your capabilities*
