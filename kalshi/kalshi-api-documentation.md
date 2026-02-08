# API Documentation

## Docs

- [Get Account API Limits](https://docs.kalshi.com/api-reference/account/get-account-api-limits.md):  Endpoint to retrieve the API tier limits associated with the authenticated user.
- [Create API Key](https://docs.kalshi.com/api-reference/api-keys/create-api-key.md):  Endpoint for creating a new API key with a user-provided public key.  This endpoint allows users with Premier or Market Maker API usage levels to create API keys by providing their own RSA public key. The platform will use this public key to verify signatures on API requests.
- [Delete API Key](https://docs.kalshi.com/api-reference/api-keys/delete-api-key.md):  Endpoint for deleting an existing API key.  This endpoint permanently deletes an API key. Once deleted, the key can no longer be used for authentication. This action cannot be undone.
- [Generate API Key](https://docs.kalshi.com/api-reference/api-keys/generate-api-key.md):  Endpoint for generating a new API key with an automatically created key pair.  This endpoint generates both a public and private RSA key pair. The public key is stored on the platform, while the private key is returned to the user and must be stored securely. The private key cannot be retrieved again.
- [Get API Keys](https://docs.kalshi.com/api-reference/api-keys/get-api-keys.md):  Endpoint for retrieving all API keys associated with the authenticated user.  API keys allow programmatic access to the platform without requiring username/password authentication. Each key has a unique identifier and name.
- [Accept Quote](https://docs.kalshi.com/api-reference/communications/accept-quote.md):  Endpoint for accepting a quote. This will require the quoter to confirm
- [Confirm Quote](https://docs.kalshi.com/api-reference/communications/confirm-quote.md):  Endpoint for confirming a quote. This will start a timer for order execution
- [Create Quote](https://docs.kalshi.com/api-reference/communications/create-quote.md):  Endpoint for creating a quote in response to an RFQ
- [Create RFQ](https://docs.kalshi.com/api-reference/communications/create-rfq.md):  Endpoint for creating a new RFQ. You can have a maximum of 100 open RFQs at a time.
- [Delete Quote](https://docs.kalshi.com/api-reference/communications/delete-quote.md):  Endpoint for deleting a quote, which means it can no longer be accepted.
- [Delete RFQ](https://docs.kalshi.com/api-reference/communications/delete-rfq.md):  Endpoint for deleting an RFQ by ID
- [Get Communications ID](https://docs.kalshi.com/api-reference/communications/get-communications-id.md):  Endpoint for getting the communications ID of the logged-in user.
- [Get Quote](https://docs.kalshi.com/api-reference/communications/get-quote.md):  Endpoint for getting a particular quote
- [Get Quotes](https://docs.kalshi.com/api-reference/communications/get-quotes.md):  Endpoint for getting quotes
- [Get RFQ](https://docs.kalshi.com/api-reference/communications/get-rfq.md):  Endpoint for getting a single RFQ by id
- [Get RFQs](https://docs.kalshi.com/api-reference/communications/get-rfqs.md):  Endpoint for getting RFQs
- [Get Event](https://docs.kalshi.com/api-reference/events/get-event.md):  Endpoint for getting data about an event by its ticker.  An event represents a real-world occurrence that can be traded on, such as an election, sports game, or economic indicator release. Events contain one or more markets where users can place trades on different outcomes.
- [Get Event Candlesticks](https://docs.kalshi.com/api-reference/events/get-event-candlesticks.md):  End-point for returning aggregated data across all markets corresponding to an event.
- [Get Event Forecast Percentile History](https://docs.kalshi.com/api-reference/events/get-event-forecast-percentile-history.md): Endpoint for getting the historical raw and formatted forecast numbers for an event at specific percentiles.
- [Get Event Metadata](https://docs.kalshi.com/api-reference/events/get-event-metadata.md):  Endpoint for getting metadata about an event by its ticker.  Returns only the metadata information for an event.
- [Get Events](https://docs.kalshi.com/api-reference/events/get-events.md): Get all events. This endpoint excludes multivariate events.
To retrieve multivariate events, use the GET /events/multivariate endpoint.

- [Get Multivariate Events](https://docs.kalshi.com/api-reference/events/get-multivariate-events.md): Retrieve multivariate (combo) events. These are dynamically created events from multivariate event collections. Supports filtering by series and collection ticker.
- [Get Exchange Announcements](https://docs.kalshi.com/api-reference/exchange/get-exchange-announcements.md):  Endpoint for getting all exchange-wide announcements.
- [Get Exchange Schedule](https://docs.kalshi.com/api-reference/exchange/get-exchange-schedule.md):  Endpoint for getting the exchange schedule.
- [Get Exchange Status](https://docs.kalshi.com/api-reference/exchange/get-exchange-status.md):  Endpoint for getting the exchange status.
- [Get Series Fee Changes](https://docs.kalshi.com/api-reference/exchange/get-series-fee-changes.md)
- [Get User Data Timestamp](https://docs.kalshi.com/api-reference/exchange/get-user-data-timestamp.md):  There is typically a short delay before exchange events are reflected in the API endpoints. Whenever possible, combine API responses to PUT/POST/DELETE requests with websocket data to obtain the most accurate view of the exchange state. This endpoint provides an approximate indication of when the data from the following endpoints was last validated: GetBalance, GetOrder(s), GetFills, GetPositions
- [Get FCM Orders](https://docs.kalshi.com/api-reference/fcm/get-fcm-orders.md): Endpoint for FCM members to get orders filtered by subtrader ID.
This endpoint requires FCM member access level and allows filtering orders by subtrader ID.

- [Get FCM Positions](https://docs.kalshi.com/api-reference/fcm/get-fcm-positions.md): Endpoint for FCM members to get market positions filtered by subtrader ID.
This endpoint requires FCM member access level and allows filtering positions by subtrader ID.

- [Get Incentives](https://docs.kalshi.com/api-reference/incentive-programs/get-incentives.md):  List incentives with optional filters. Incentives are rewards programs for trading activity on specific markets.
- [Get Live Data](https://docs.kalshi.com/api-reference/live-data/get-live-data.md): Get live data for a specific milestone
- [Get Multiple Live Data](https://docs.kalshi.com/api-reference/live-data/get-multiple-live-data.md): Get live data for multiple milestones
- [Batch Get Market Candlesticks](https://docs.kalshi.com/api-reference/market/batch-get-market-candlesticks.md): Endpoint for retrieving candlestick data for multiple markets.

- Accepts up to 100 market tickers per request
- Returns up to 10,000 candlesticks total across all markets
- Returns candlesticks grouped by market_id
- Optionally includes a synthetic initial candlestick for price continuity (see `include_latest_before_start` parameter)

- [Get Market](https://docs.kalshi.com/api-reference/market/get-market.md):  Endpoint for getting data about a specific market by its ticker. A market represents a specific binary outcome within an event that users can trade on (e.g., "Will candidate X win?"). Markets have yes/no positions, current prices, volume, and settlement rules.
- [Get Market Candlesticks](https://docs.kalshi.com/api-reference/market/get-market-candlesticks.md): Time period length of each candlestick in minutes. Valid values: 1 (1 minute), 60 (1 hour), 1440 (1 day).
- [Get Market Orderbook](https://docs.kalshi.com/api-reference/market/get-market-orderbook.md):  Endpoint for getting the current order book for a specific market.  The order book shows all active bid orders for both yes and no sides of a binary market. It returns yes bids and no bids only (no asks are returned). This is because in binary markets, a bid for yes at price X is equivalent to an ask for no at price (100-X). For example, a yes bid at 7¢ is the same as a no ask at 93¢, with identical contract sizes.  Each side shows price levels with their corresponding quantities and order counts, organized from best to worst prices.
- [Get Markets](https://docs.kalshi.com/api-reference/market/get-markets.md): Filter by market status. Possible values: `unopened`, `open`, `closed`, `settled`. Leave empty to return markets with any status.
 - Only one `status` filter may be supplied at a time.
 - Timestamp filters will be mutually exclusive from other timestamp filters and certain status filters.

 | Compatible Timestamp Filters | Additional Status Filters| Extra Notes |
 |------------------------------|--------------------------|-------------|
 | min_created_ts, max_created_ts | `unopened`, `open`, *empty* | |
 | min_close_ts, max_close_ts | `closed`, *empty* | |
 | min_settled_ts, max_settled_ts | `settled`, *empty* | |
 | min_updated_ts | *empty* | Incompatible with all filters besides `mve_filter=exclude` |

- [Get Series](https://docs.kalshi.com/api-reference/market/get-series.md):  Endpoint for getting data about a specific series by its ticker.  A series represents a template for recurring events that follow the same format and rules (e.g., "Monthly Jobs Report", "Weekly Initial Jobless Claims", "Daily Weather in NYC"). Series define the structure, settlement sources, and metadata that will be applied to each recurring event instance within that series.
- [Get Series List](https://docs.kalshi.com/api-reference/market/get-series-list.md):  Endpoint for getting data about multiple series with specified filters.  A series represents a template for recurring events that follow the same format and rules (e.g., "Monthly Jobs Report", "Weekly Initial Jobless Claims", "Daily Weather in NYC"). This endpoint allows you to browse and discover available series templates by category.
- [Get Trades](https://docs.kalshi.com/api-reference/market/get-trades.md):  Endpoint for getting all trades for all markets.  A trade represents a completed transaction between two users on a specific market. Each trade includes the market ticker, price, quantity, and timestamp information.  This endpoint returns a paginated response. Use the 'limit' parameter to control page size (1-1000, defaults to 100). The response includes a 'cursor' field - pass this value in the 'cursor' parameter of your next request to get the next page. An empty cursor indicates no more pages are available.
- [Get Milestone](https://docs.kalshi.com/api-reference/milestone/get-milestone.md):  Endpoint for getting data about a specific milestone by its ID.
- [Get Milestones](https://docs.kalshi.com/api-reference/milestone/get-milestones.md): Minimum start date to filter milestones. Format: RFC3339 timestamp
- [Create Market In Multivariate Event Collection](https://docs.kalshi.com/api-reference/multivariate/create-market-in-multivariate-event-collection.md):  Endpoint for creating an individual market in a multivariate event collection. This endpoint must be hit at least once before trading or looking up a market.
- [Get Multivariate Event Collection](https://docs.kalshi.com/api-reference/multivariate/get-multivariate-event-collection.md):  Endpoint for getting data about a multivariate event collection by its ticker.
- [Get Multivariate Event Collection Lookup History](https://docs.kalshi.com/api-reference/multivariate/get-multivariate-event-collection-lookup-history.md):  Endpoint for retrieving which markets in an event collection were recently looked up.
- [Get Multivariate Event Collections](https://docs.kalshi.com/api-reference/multivariate/get-multivariate-event-collections.md):  Endpoint for getting data about multivariate event collections.
- [Lookup Tickers For Market In Multivariate Event Collection](https://docs.kalshi.com/api-reference/multivariate/lookup-tickers-for-market-in-multivariate-event-collection.md):  Endpoint for looking up an individual market in a multivariate event collection. If CreateMarketInMultivariateEventCollection has never been hit with that variable combination before, this will return a 404.
- [Create Order Group](https://docs.kalshi.com/api-reference/order-groups/create-order-group.md):  Creates a new order group with a contracts limit measured over a rolling 15-second window. When the limit is hit, all orders in the group are cancelled and no new orders can be placed until reset.
- [Delete Order Group](https://docs.kalshi.com/api-reference/order-groups/delete-order-group.md):  Deletes an order group and cancels all orders within it. This permanently removes the group.
- [Get Order Group](https://docs.kalshi.com/api-reference/order-groups/get-order-group.md):  Retrieves details for a single order group including all order IDs and auto-cancel status.
- [Get Order Groups](https://docs.kalshi.com/api-reference/order-groups/get-order-groups.md):  Retrieves all order groups for the authenticated user.
- [Reset Order Group](https://docs.kalshi.com/api-reference/order-groups/reset-order-group.md):  Resets the order group's matched contracts counter to zero, allowing new orders to be placed again after the limit was hit.
- [Trigger Order Group](https://docs.kalshi.com/api-reference/order-groups/trigger-order-group.md):  Triggers the order group, canceling all orders in the group and preventing new orders until the group is reset.
- [Update Order Group Limit](https://docs.kalshi.com/api-reference/order-groups/update-order-group-limit.md):  Updates the order group contracts limit (rolling 15-second window). If the updated limit would immediately trigger the group, all orders in the group are canceled and the group is triggered.
- [Amend Order](https://docs.kalshi.com/api-reference/orders/amend-order.md):  Endpoint for amending the max number of fillable contracts and/or price in an existing order. Max fillable contracts is `remaining_count` + `fill_count`.
- [Batch Cancel Orders](https://docs.kalshi.com/api-reference/orders/batch-cancel-orders.md):  Endpoint for cancelling up to 20 orders at once.
- [Batch Create Orders](https://docs.kalshi.com/api-reference/orders/batch-create-orders.md):  Endpoint for submitting a batch of orders. Each order in the batch is counted against the total rate limit for order operations. Consequently, the size of the batch is capped by the current per-second rate-limit configuration applicable to the user. At the moment of writing, the limit is 20 orders per batch.
- [Cancel Order](https://docs.kalshi.com/api-reference/orders/cancel-order.md):  Endpoint for canceling orders. The value for the orderId should match the id field of the order you want to decrease. Commonly, DELETE-type endpoints return 204 status with no body content on success. But we can't completely delete the order, as it may be partially filled already. Instead, the DeleteOrder endpoint reduce the order completely, essentially zeroing the remaining resting contracts on it. The zeroed order is returned on the response payload as a form of validation for the client.
- [Create Order](https://docs.kalshi.com/api-reference/orders/create-order.md):  Endpoint for submitting orders in a market. Each user is limited to 200 000 open orders at a time.
- [Decrease Order](https://docs.kalshi.com/api-reference/orders/decrease-order.md):  Endpoint for decreasing the number of contracts in an existing order. This is the only kind of edit available on order quantity. Cancelling an order is equivalent to decreasing an order amount to zero.
- [Get Order](https://docs.kalshi.com/api-reference/orders/get-order.md):  Endpoint for getting a single order.
- [Get Order Queue Position](https://docs.kalshi.com/api-reference/orders/get-order-queue-position.md):  Endpoint for getting an order's queue position in the order book. This represents the amount of orders that need to be matched before this order receives a partial or full match. Queue position is determined using a price-time priority.
- [Get Orders](https://docs.kalshi.com/api-reference/orders/get-orders.md): Restricts the response to orders that have a certain status: resting, canceled, or executed.
- [Get Queue Positions for Orders](https://docs.kalshi.com/api-reference/orders/get-queue-positions-for-orders.md):  Endpoint for getting queue positions for all resting orders. Queue position represents the number of contracts that need to be matched before an order receives a partial or full match, determined using price-time priority.
- [Create Subaccount](https://docs.kalshi.com/api-reference/portfolio/create-subaccount.md): Creates a new subaccount for the authenticated user. Subaccounts are numbered sequentially starting from 1. Maximum 32 subaccounts per user.
- [Get All Subaccount Balances](https://docs.kalshi.com/api-reference/portfolio/get-all-subaccount-balances.md): Gets balances for all subaccounts including the primary account.
- [Get Balance](https://docs.kalshi.com/api-reference/portfolio/get-balance.md):  Endpoint for getting the balance and portfolio value of a member. Both values are returned in cents.
- [Get Fills](https://docs.kalshi.com/api-reference/portfolio/get-fills.md):  Endpoint for getting all fills for the member. A fill is when a trade you have is matched.
- [Get Positions](https://docs.kalshi.com/api-reference/portfolio/get-positions.md): Restricts the positions to those with any of following fields with non-zero values, as a comma separated list. The following values are accepted: position, total_traded
- [Get Settlements](https://docs.kalshi.com/api-reference/portfolio/get-settlements.md):  Endpoint for getting the member's settlements historical track.
- [Get Subaccount Transfers](https://docs.kalshi.com/api-reference/portfolio/get-subaccount-transfers.md): Gets a paginated list of all transfers between subaccounts for the authenticated user.
- [Get Total Resting Order Value](https://docs.kalshi.com/api-reference/portfolio/get-total-resting-order-value.md):  Endpoint for getting the total value, in cents, of resting orders. This endpoint is only intended for use by FCM members (rare). Note: If you're uncertain about this endpoint, it likely does not apply to you.
- [Transfer Between Subaccounts](https://docs.kalshi.com/api-reference/portfolio/transfer-between-subaccounts.md): Transfers funds between the authenticated user's subaccounts. Use 0 for the primary account, or 1-32 for numbered subaccounts.
- [Get Filters for Sports](https://docs.kalshi.com/api-reference/search/get-filters-for-sports.md): Retrieve available filters organized by sport.

This endpoint returns filtering options available for each sport, including scopes and competitions. It also provides an ordered list of sports for display purposes.

- [Get Tags for Series Categories](https://docs.kalshi.com/api-reference/search/get-tags-for-series-categories.md): Retrieve tags organized by series categories.

This endpoint returns a mapping of series categories to their associated tags, which can be used for filtering and search functionality.

- [Get Structured Target](https://docs.kalshi.com/api-reference/structured-targets/get-structured-target.md):  Endpoint for getting data about a specific structured target by its ID.
- [Get Structured Targets](https://docs.kalshi.com/api-reference/structured-targets/get-structured-targets.md): Page size (min: 1, max: 2000)
- [API Changelog](https://docs.kalshi.com/changelog/index.md): Stay updated with API changes and version history
- [Connectivity](https://docs.kalshi.com/fix/connectivity.md): Connection setup and endpoints for Kalshi FIX API
- [Drop Copy Session](https://docs.kalshi.com/fix/drop-copy.md): Recover missed execution reports and query historical order events
- [Error Handling](https://docs.kalshi.com/fix/error-handling.md): Understanding and handling errors in the FIX protocol
- [FIX API Overview](https://docs.kalshi.com/fix/index.md): Financial Information eXchange (FIX) protocol implementation for Kalshi
- [Market Settlement](https://docs.kalshi.com/fix/market-settlement.md): Settlement reports for market outcomes and position resolution
- [Order Entry Messages](https://docs.kalshi.com/fix/order-entry.md): Submit, modify, and cancel orders through FIX messages
- [Order Group Messages](https://docs.kalshi.com/fix/order-groups.md): Manage order groups for automatic position management
- [RFQ Messages](https://docs.kalshi.com/fix/rfq-messages.md): Request for Quote functionality for market makers
- [Session Management](https://docs.kalshi.com/fix/session-management.md): Managing FIX sessions including logon, logout, and message sequencing
- [Subpenny Pricing](https://docs.kalshi.com/fix/subpenny-pricing.md): Dollar-based pricing format for subpenny precision
- [API Keys](https://docs.kalshi.com/getting_started/api_keys.md): API Key usage
- [Test In The Demo Environment](https://docs.kalshi.com/getting_started/demo_env.md): Set up and test with Kalshi's demo environment
- [Fixed-Point Contracts](https://docs.kalshi.com/getting_started/fixed_point_contracts.md): Migrating to fixed-point contract quantity representation.
- [Making Your First Request](https://docs.kalshi.com/getting_started/making_your_first_request.md): Start trading with Kalshi API in under 5 minutes
- [Orderbook Responses](https://docs.kalshi.com/getting_started/orderbook_responses.md): Understanding Kalshi orderbook structure and binary prediction market mechanics
- [Understanding Pagination](https://docs.kalshi.com/getting_started/pagination.md): Learn how to navigate through large datasets using cursor-based pagination
- [Quick Start: Authenticated Requests (No SDK)](https://docs.kalshi.com/getting_started/quick_start_authenticated_requests.md): Three simple steps to make your first authenticated API request to Kalshi
- [Quick Start: Create your first order (No SDK)](https://docs.kalshi.com/getting_started/quick_start_create_order.md): Learn how to find markets, place orders, check status, and cancel orders on Kalshi
- [Quick Start: Market Data (No SDK)](https://docs.kalshi.com/getting_started/quick_start_market_data.md): Learn how to access real-time market data without authentication
- [Quick Start: WebSockets (No SDK)](https://docs.kalshi.com/getting_started/quick_start_websockets.md): Learn how to establish and maintain a WebSocket connection to stream real-time market data
- [Rate Limits and Tiers](https://docs.kalshi.com/getting_started/rate_limits.md): Understanding API rate limits and access tiers
- [Subpenny Pricing](https://docs.kalshi.com/getting_started/subpenny_pricing.md): Understanding Kalshi subpenny pricing.
- [Kalshi Glossary](https://docs.kalshi.com/getting_started/terms.md): Core terminology used in the Kalshi exchange
- [ApiKeys](https://docs.kalshi.com/python-sdk/api/ApiKeysApi.md): Python SDK methods for ApiKeys operations
- [Communications](https://docs.kalshi.com/python-sdk/api/CommunicationsApi.md): Python SDK methods for Communications operations
- [Events](https://docs.kalshi.com/python-sdk/api/EventsApi.md): Python SDK methods for Events operations
- [Exchange](https://docs.kalshi.com/python-sdk/api/ExchangeApi.md): Python SDK methods for Exchange operations
- [Markets](https://docs.kalshi.com/python-sdk/api/MarketsApi.md): Python SDK methods for Markets operations
- [Milestones](https://docs.kalshi.com/python-sdk/api/MilestonesApi.md): Python SDK methods for Milestones operations
- [MultivariateCollections](https://docs.kalshi.com/python-sdk/api/MultivariateCollectionsApi.md): Python SDK methods for MultivariateCollections operations
- [Portfolio](https://docs.kalshi.com/python-sdk/api/PortfolioApi.md): Python SDK methods for Portfolio operations
- [Series](https://docs.kalshi.com/python-sdk/api/SeriesApi.md): Python SDK methods for Series operations
- [StructuredTargets](https://docs.kalshi.com/python-sdk/api/StructuredTargetsApi.md): Python SDK methods for StructuredTargets operations
- [Kalshi SDKs](https://docs.kalshi.com/sdks/overview.md): Official SDKs for integrating with the Kalshi API
- [Python SDK Quick Start](https://docs.kalshi.com/sdks/python/quickstart.md): Get started with the Kalshi Python SDK
- [TypeScript SDK Quick Start](https://docs.kalshi.com/sdks/typescript/quickstart.md): Get started with the Kalshi TypeScript SDK
- [ApiKeys](https://docs.kalshi.com/typescript-sdk/api/ApiKeysApi.md): TypeScript SDK methods for ApiKeys operations
- [Communications](https://docs.kalshi.com/typescript-sdk/api/CommunicationsApi.md): TypeScript SDK methods for Communications operations
- [Events](https://docs.kalshi.com/typescript-sdk/api/EventsApi.md): TypeScript SDK methods for Events operations
- [Exchange](https://docs.kalshi.com/typescript-sdk/api/ExchangeApi.md): TypeScript SDK methods for Exchange operations
- [Markets](https://docs.kalshi.com/typescript-sdk/api/MarketsApi.md): TypeScript SDK methods for Markets operations
- [Milestones](https://docs.kalshi.com/typescript-sdk/api/MilestonesApi.md): TypeScript SDK methods for Milestones operations
- [MultivariateCollections](https://docs.kalshi.com/typescript-sdk/api/MultivariateCollectionsApi.md): TypeScript SDK methods for MultivariateCollections operations
- [Portfolio](https://docs.kalshi.com/typescript-sdk/api/PortfolioApi.md): TypeScript SDK methods for Portfolio operations
- [Series](https://docs.kalshi.com/typescript-sdk/api/SeriesApi.md): TypeScript SDK methods for Series operations
- [StructuredTargets](https://docs.kalshi.com/typescript-sdk/api/StructuredTargetsApi.md): TypeScript SDK methods for StructuredTargets operations
- [Communications](https://docs.kalshi.com/websockets/communications.md): Real-time Request for Quote (RFQ) and quote notifications. Requires authentication.

**Requirements:**
- Authentication required
- Market specification ignored
- Optional sharding for fanout control:
  - `shard_factor` (1-100) and `shard_key` (0 <= key < shard_factor)
- RFQ events (RFQCreated, RFQDeleted) always sent
- Quote events (QuoteCreated, QuoteAccepted, QuoteExecuted) are only sent if you created the quote OR you created the RFQ

**Use case:** Tracking RFQs you create and quotes on your RFQs, or quotes you create on others' RFQs. Use QuoteExecuted to correlate fill messages with quotes via client_order_id.

- [Connection Keep-Alive](https://docs.kalshi.com/websockets/connection-keep-alive.md): WebSocket control frames for connection management.

Kalshi sends Ping frames (`0x9`) every 10 seconds with body `heartbeat` to maintain the connection.
Clients should respond with Pong frames (`0xA`). Clients may also send Ping frames to which Kalshi will respond with Pong.

- [Market & Event Lifecycle](https://docs.kalshi.com/websockets/market-&-event-lifecycle.md): Market state changes and event creation notifications.

**Requirements:**
- Receives all market and event lifecycle notifications (`market_ticker` filters are not supported)
- Event creation notifications

**Use case:** Tracking market lifecycle including creation, de(activation), close date changes, determination, settlement

- [Market Positions](https://docs.kalshi.com/websockets/market-positions.md): Real-time updates of your positions in markets. Requires authentication.

**Requirements:**
- Authentication required
- Market specification optional (omit to receive all positions)
- Filters are by `market_ticker`/`market_tickers` only; `market_id`/`market_ids` are not supported
- Updates sent when your position changes due to trades, settlements, etc.

**Monetary Values:**
All monetary values (position_cost, realized_pnl, fees_paid) are returned in centi-cents (1/10,000th of a dollar).
To convert to dollars, divide by 10,000.

**Use case:** Portfolio tracking, position monitoring, P&L calculations

- [Market Ticker](https://docs.kalshi.com/websockets/market-ticker.md): Market price, volume, and open interest updates.

**Requirements:**
- Market specification optional (omit to receive all markets)
- Supports `market_ticker`/`market_tickers` and `market_id`/`market_ids`
- Updates sent whenever any ticker field changes

**Use case:** Displaying current market prices and statistics

- [Market Ticker V2](https://docs.kalshi.com/websockets/market-ticker-v2.md): Incremental ticker updates with delta fields. Messages may contain a subset of fields
depending on which summary triggered the update.

**Requirements:**
- Market specification optional (omit to receive all markets)
- Supports `market_ticker`/`market_tickers` and `market_id`/`market_ids`

**Use case:** Streaming lightweight ticker deltas and combining with your cached state

- [Multivariate Lookups](https://docs.kalshi.com/websockets/multivariate-lookups.md): Multivariate collection lookup notifications.

**Requirements:**
- No filtering parameters; subscription is global

**Use case:** Tracking multivariate market relationships

- [Order Group Updates](https://docs.kalshi.com/websockets/order-group-updates.md): Real-time order group lifecycle and limit updates. Requires authentication.

**Requirements:**
- Authentication required
- Market specification ignored
- Updates sent when order groups are created, triggered, reset, deleted, or have limits updated

**Use case:** Tracking order group lifecycle and limits

- [Orderbook Updates](https://docs.kalshi.com/websockets/orderbook-updates.md): Real-time orderbook price level changes. Provides incremental updates to maintain a live orderbook.

**Requirements:**
- Authentication required
- Market specification required:
  - Use `market_ticker` (string) for a single market
  - Use `market_tickers` (array of strings) for multiple markets
  - `market_id`/`market_ids` are not supported for this channel
- Sends `orderbook_snapshot` first, then incremental `orderbook_delta` updates

**Use case:** Building and maintaining a real-time orderbook

- [Public Trades](https://docs.kalshi.com/websockets/public-trades.md): Public trade notifications when trades occur.

**Requirements:**
- Market specification optional (omit to receive all trades)
- Updates sent immediately after trade execution

**Use case:** Trade feed, volume analysis

- [User Fills](https://docs.kalshi.com/websockets/user-fills.md): Your order fill notifications. Requires authentication.

**Requirements:**
- Authentication required
- Market specification ignored (always sends all your fills)
- Updates sent immediately when your orders are filled

**Use case:** Tracking your trading activity

- [WebSocket Connection](https://docs.kalshi.com/websockets/websocket-connection.md): Main WebSocket connection endpoint. All communication happens through this single connection.
Authentication is required to establish the connection; include API key headers during the WebSocket handshake.
Some channels carry only public market data, but the connection itself still requires authentication.
Use the subscribe command to subscribe to specific data channels. For more information, see the [Getting Started](https://docs.kalshi.com/getting_started/quick_start_websockets) guide.

- [Introduction](https://docs.kalshi.com/welcome/index.md): Welcome to the Kalshi API documentation

