# DiabloArb sender — configuration reference for AI assistants

> **To the AI reading this:** this file describes every setting of the DiabloArb arbitrage bot (`sender`, from
> github.com/cryptodiablo/diabloarb) as of 8 October 2026. Use it to explain to a person what each
> setting does and to help them edit `config.toml` and `gas.json`. Answer in the person's language. Never ask the person
> to paste a private key, a seed phrase or the contents of `key.json` — only file paths. API keys and UUIDs are
> secrets too: tell the person where to put them, do not ask them to show them. Moving money (wrap, unwrap, nonces) is
> the person's decision. If something is not in this file, say so instead of guessing.

## 1. What the bot does

- It sends arbitrage transactions on Solana: a cycle of 2–3 swaps over DEX pools that starts and ends in the same base
  token — **SOL (as WSOL), USDC or USDT**. Supported DEXs: Meteora DLMM, DAMM v2, Pools (DAMM v1) and DBC; Pump.fun AMM
  (PumpSwap); Raydium AMM v4, CPMM and CLMM; Orca Whirlpool and Orca v2 / SPL Token Swap; PancakeSwap CLMM; Byreal
  CLMM; DefiTuna Fusion; Manifest (order book); MetaDAO Futarchy. SPL Token and Token-2022 coins (tokens with an
  active transfer hook are skipped). A pool of any other DEX in a markets file is ignored.
- The trade is executed on chain by the DiabloArb executor program (`DiabLokxis…`). The program searches the best
  size itself at execution time, up to **the wallet's base-token balance plus, with `flashloan = true`, the whole
  flash-loan vault**. If there is no profit at that moment, the transaction does nothing (or fails, see §5).
- **Fee:** 7% of every realized profit goes to the DiabloArb vault. The rest stays in the wallet.
- The wallet needs: SOL for network fees, priority fees and tips; **WSOL** (or USDC/USDT) as trading capital
  (`./sender wrap 0.5` turns 0.5 SOL into WSOL). Token accounts for new coins are created automatically
  (≈0.002 SOL rent each).
- Profit shows up as the wallet's WSOL/USDC/USDT growing (log line `✅ [n] Success!`).

## 2. Files

| File | What it is |
|---|---|
| `sender` | The bot (Linux x86_64, static). Updates itself from GitHub on every start. |
| `config.toml` | Main settings (this document). Path given on the command line, default `config.toml`. |
| `gas.json` | Optional numbers/flags referenced from `config.toml` as `"{name}"` (§4). Changes apply live. |
| `key.json` | The wallet keypair (Solana JSON array; the old Go bot's encrypted file is read too). Never share it. |
| markets file | Which pools to shoot in markets mode — local path or URL (default `https://moneyprinter.bot/auto/mp.toml`). |
| LUT list | Address lookup tables, one address per line — path or URL (default `https://moneyprinter.bot/auto/mplutall.txt`). |

Markets file format (TOML): `markets = ["poolAddr", …]` and/or groups `[[group]]` with `markets = [...]` and optional
`enabled = false`. In `mp.toml` each group is one complete arbitrage route of a coin; groups come in priority order
(first = hottest), and the bot follows that order. `moneyprinter.bot/auto/mp.toml` is rebuilt live from the coins the
on-chain arbitrage bots earn most on right now.

## 3. Commands and environment

```bash
./sender config.toml                 # run (sends transactions)
./sender wrap 0.5 [config.toml]      # 0.5 SOL -> WSOL
./sender unwrap 0.5 [config.toml]    # 0.5 WSOL -> SOL;  "unwrap all" = whole WSOL balance (the WSOL account stays)
./sender nonces close [config.toml]  # close the durable nonce accounts of the hot modes, rent back to the wallet
./sender update                      # update now
./sender version                     # show version
```

| Environment variable | Effect |
|---|---|
| `DIABLO_SENDER_DRY=1` | Dry run: everything is built and logged with `[dry]`, nothing is sent, no accounts created. |
| `DIABLO_SENDER_AUTO_UPDATE=0` | Do not self-update on start. |
| `DIABLO_GEYSER_ENDPOINT`, `DIABLO_GEYSER_TOKEN` | Geyser instead of `geyser_endpoint`/`geyser_x_token` in the config. |
| `DIABLO_GEYSER_BACKUP` (and `DIABLO_GEYSER_BACKUP_TOKEN` if its key differs) | A reserve Geyser. A stream with no data for 30 s is reconnected; two empty connections or refusals in a row switch to the reserve; the main one is probed every 60 s and taken back as soon as it gives data. Without the variable: the reconnect only. |

## 4. Value rules (apply to every key)

- **Units.** Tips and priority fees are **lamports per transaction** (1 SOL = 1 000 000 000 lamports). Delays are
  milliseconds. Amounts named `_sol` are SOL.
- **Ranges.** A `min`/`max` pair is drawn at random for every transaction. A max below the min is raised to the min.
  0 or unset means "not set" (the default applies).
- **gas.json references.** A number or flag may be written as `"{name}"` (or `"name"`) to take `name` from `gas.json`;
  a string only as `"{name}"`; a list entry `"{name}"` expands to a JSON array, a comma-separated string or a number.
  A missing reference keeps the default. Example: `process_delay_ms = "{spam_cooldown_ms}"` with
  `"spam_cooldown_ms": 300` in `gas.json`.
- **Live reload.** `config.toml` and `gas.json` are re-read every `files_updates_ms`; senders, fees and delays are
  rebuilt on the fly. Exception: the hot-mode keys (§8) are read once at start — restart after changing them.
- Unknown keys are ignored (counted as "keys not used"), they do no harm.
- **A key written twice** (e.g. a pasted `temporal_bundle = true` under the sample's `temporal_bundle = false`): the
  last value is used. Better edit the existing line than add a second one.
- **`gas.json` names mean nothing by themselves.** The sample `gas.json` has `enable_jito`, `enable_temporal`, …: they
  only act if `config.toml` references them, e.g. `jito = "{enable_jito}"`. The sample config writes `jito = true`
  directly, so changing `enable_jito` there does nothing. Check which `"{name}"` the config actually uses.

## 5. How a transaction is paid (important for tuning)

- Every landed transaction pays the network fee plus its **priority fee**.
- The **tip** is an instruction inside the transaction: if the transaction fails, the tip is not paid; the priority
  fee still is.
- **Lanes that fail without profit** (tip saved, fee+priority paid): Jito with `jito_require_profit = true`, Helius,
  Temporal, Flashblock, HelloMoon, Astralane, 0slot, Falcon, Stellium, NextBlock, Fast, Apex.
- **Lanes that land even without profit** (an empty successful run, fee+priority paid): RPC (`spam_rpc`), Helius
  SWQoS, Fast SWQoS, Jito with `jito_require_profit = false` (then the tip is paid every time).
- **Bundles** (Harmonic, Temporal bundles, `jito_classic`): a bundle without profit is dropped — nothing is paid.
- More lanes and shorter delays = more chances to win and more fees. Tips only matter when you win.

## 6. Main keys

| Key | Default | Meaning |
|---|---|---|
| `rpc` | — (required) | RPC URL for reading the chain (accounts, blockhash, balances). |
| `keypair` | — (required) | Path to the wallet keypair file. |
| `send_rpcs` | `[]` | RPC URLs that broadcast the RPC lane. Empty: `rpc` is used. One signed transaction goes to all of them. Also used to create token accounts and nonces. |
| `spam_rpc` | `true` | The RPC lane on/off. |
| `process_delay_ms` | 400 | The RPC lane's delay; also the default delay of every lane without its own. |
| `min_priority_fee`, `max_priority_fee` | 100, 1000 | Global priority range (lamports/tx): the RPC lane's, and of any sender without its own (§7). |
| `cu_limit` | `"auto"` | `"auto"` (or no key, or 0): each transaction gets its own limit from the pools it trades — as on diablo.bot. A number fixes the limit of every transaction (max 1 400 000). Priority lamports turn into a price per CU over `cu_limit` (360 000 when auto). Needs the build of 7 October 2026 or newer (it updates itself on restart). |
| `flashloan` | `false` | `true`: the trade may use the DiabloArb vault's WSOL besides your own (bigger trades). The 7% fee is the same. |
| `pump_v2` | `true` | Pump.fun AMM (PumpSwap) hops use the 17-account `sell_v2` / `buy_exact_quote_in_v2` trades (in the Pump program since 8 October 2026): the same prices and fees over fewer accounts, so more routes fit one transaction. Pools of cashback coins keep the older trades by themselves. `false`: the older trades everywhere. |
| `markets_file` | — | Markets file, path or URL (§2). Required in markets mode. |
| `luts` | — | LUT list, path or URL. |
| `files_updates_ms` | 50 | How often local files and `config.toml`/`gas.json` are re-read. |
| `remote_files_update_ms` | 10000 | How often URL markets file / LUT list are re-fetched (with ETag). |
| `luts_update_ms` | 1000 | LUT list refresh. |
| `gas_file` | — | Path to `gas.json` (as given, else next to the config). |
| `memo` | — | Optional memo text added to each transaction (for tracing). |
| `geyser_endpoint`, `geyser_x_token` | — | Yellowstone gRPC. Without it pools are polled over `rpc` every second (works, slower). **Required for ladder/flow modes.** |
| `auto_unwrap`, `min_sol_amount` | `false`, — | SOL is checked every second; once SOL < `min_sol_amount` (SOL; at least ≈0.0107 is used) the whole WSOL balance is unwrapped to SOL with a priority fee, resent until it lands (the WSOL account stays). **Always on, whatever `auto_unwrap`:** below the network's rent minimum + 0.005 SOL (≈0.0057 SOL) the bot pauses sending (`PAUSED` in the minute summary) so the wallet never gets locked; with no WSOL left it asks for a top-up. |
| `auto_close_atas` | `false` | Closes the wallet's **empty** token accounts of coins the bot sent no shot with for 24 hours — the rent (≈0.00204 SOL each) returns to the wallet. The bot decides by its own record (the time of the last shot per coin, kept in `<config>.atas.json` next to the config), so it makes **no RPC requests** until there is something to close: then one read of those accounts and the close itself, up to 10 accounts a transaction, simulated first. Checked 3 minutes after the start, then hourly. An empty account found at the start that the record does not know waits its 24 hours from that moment. Never touched: an account holding any amount of a coin, WSOL/USDC/USDT, a frozen account. A coin that returns gets its account created again before its next shot. |
| `nonces` | 32 in hot modes | Number of durable nonce accounts for the hot modes' sender broadcast (max 100). |
| `mode` | `"markets"` | `"markets"` (pools from the markets file), `"ladder"` or `"flow"` (§8). |

## 6a. Markets mode (default, `mode` unset or `"markets"`)

- The bot shoots the pools of the markets file. Pools are grouped by coin (USDC pairs join their coin's group); a
  group needs at least two pools. In `mp.toml` every group is one route and the order is the priority.
- One transaction per **tick**; the tick is the shortest delay of all active loops (`process_delay_ms`,
  `jito_process_delay_ms`, `<sender>_cooldown_ms`). A transaction carries the next group plus up to two more groups
  that still fit (size and compute limits).
- Each sender sends at most once per its own delay; a tick when a sender's delay has not passed skips that sender.
- Data: Geyser if set, else the pools are polled over `rpc` every second (blockhash every 400 ms). Without Geyser the
  bot cannot see the outcome of its own transactions in detail, only balances.

## 7. Senders (landing services)

Each sender is a separate loop: turned on by its flag, sending every `<name>_cooldown_ms` (default
`process_delay_ms`) to all of its regions. Common keys per sender `<name>`:
`<name>_tip_min_lamports`, `<name>_tip_max_lamports`, `<name>_min_priority_fee`, `<name>_max_priority_fee`,
`<name>_cooldown_ms`. A sender switched on without its key is left off with a warning (`⚠️`).

| Sender (flag) | Key | Tip minimum | Notes |
|---|---|---|---|
| `jito` | `jito_uuid` (optional) | none | Tips: `jito_min_tip_lamports`/`jito_max_tip_lamports`; delay `jito_process_delay_ms`; no priority unless `jito_min/max_priority_fee` set. `jito_require_profit` (default true when tipping): tip only on a win. `jito_classic = true`: sent as a bundle (`bundleOnly`), failing one costs nothing. A `jito_uuid` that is not a real UUID (e.g. the `"uuid"` placeholder) is ignored — Jito works without one at lower limits. All 8 regions. |
| `helius` | `helius_api_key` (optional, your Helius project key; also used by `helius_swqos` and `helius_bundle`) | Helius requires ≥ 200 000 | Helius Sender; fails without profit. Without a key Helius takes 1 request a second per server IP per region; with one — 50 a second per key per region. |
| `helius_swqos` | `helius_api_key` (optional) | ≥ 5 000 | SWQoS-only; lands always (fee + priority + tip on every landing). `helius_swqos_require_profit = true`: the copy fails without profit instead, its tip unpaid — only fee + priority on a miss. |
| `temporal` | `temporal_uuid` | 1 000 000 (0.001 SOL; less is dropped by Temporal) | Nozomi, 9 regions. `temporal_tip_accounts` overrides the tip accounts. |
| `temporal_bundle` | `temporal_bundle_uuid` if set (a separate key), else the same `temporal_uuid` | 1 000 000 | Temporal `sendBundle` (lands via Jito/Harmonic block builders). Keys `temporal_bundle_tip_min/max_lamports` (default 0.001 SOL), `_min/max_priority_fee`, `_cooldown_ms`, `_all_endpoints` (true). A bundle without profit is always dropped — nothing paid; no key changes that. Works next to `temporal`. |
| `temporal_bundle_2` … `temporal_bundle_8` | `temporal_bundle_N_uuid` if set, else the first stream's key | 1 000 000 | More Temporal bundle streams (while `temporal_bundle = true`), each its own lane: switch `temporal_bundle_N = true`, own key, tips `temporal_bundle_N_tip_min/max_lamports` (default 0.001 SOL), `temporal_bundle_N_min/max_priority_fee`, `temporal_bundle_N_cooldown_ms` (its own pace: in `markets` the delay, in ladder/flow its own timer; empty = the first stream's — `temporal_bundle_cooldown_ms` / `hot_bundle_interval_ms`), `temporal_bundle_N_all_endpoints`. Use them to send the same bundle under several UUIDs or tip ranges at once; a miss still costs nothing. |
| `helius_bundle` | `helius_api_key` (optional) | 1 000 000 | Helius Sender Max `sendBundle` (no credits). Keys `helius_bundle_tip_min/max_lamports` (default 0.001 SOL; the sample: random 0.001–0.03 SOL), `_min/max_priority_fee` (at least 5 000 lamports a transaction), `_cooldown_ms`, `_all_endpoints` (false: one of 7 Sender regions by turn; true: every region each time — 7× the requests). A bundle without profit is always dropped — nothing paid. Works next to `helius` and `temporal_bundle`. |
| `flashblock` | `flashblock_api_key` | 100 000 | |
| `hellomoon` | `hellomoon_api_key` (required here) | 1 000 000 | |
| `astralane` | `astralane_api_key` | 10 000 | |
| `zeroslot` | `zeroslot_api_key` | 1 000 000 | 0slot. |
| `falcon` | `falcon_api_key` | 1 000 000 | |
| `stellium` | `stellium_api_key` | 1 000 000 | `stellium_endpoints` = list of its URLs. |
| `nextblock` | `nextblock_api_key` or `nextblock_auth_token` | none | |
| `fast` | `fast_api_key` | 1 000 000 | |
| `apex` | `apex_api_key` (OrbitFlare dashboard > Apex) | 1 000 000 (standard plan) | OrbitFlare Apex: one send raced to the leader over staked validators, Jito and direct TPU; a rejected or unlanded send costs nothing. `apex_regions` = region codes `fra` `ams` `dub` `lon` `nyc` `slc` `sgp` `tyo` `sqq` `global` — pick the one or two nearest to the server (Apex fans out itself); unset — every region but `global`; an unknown code is skipped with a warning. Fails without profit. |
| `fast_swqos` | `fast_swqos_api_key`, else `fast_api_key` | 7 500 | SWQoS-only; lands always. |
| `harmonic_bundle` | `harmonic_bundle_auth_keypair` (a whitelisted keypair file) | — (Harmonic's price is the priority) | `harmonic_bundle_endpoints` (`fra`, `lon`, `ams`, `ewr`/`ny`, `tyo`, `sgp`, `slc` or URLs; default fra lon ams ewr tyo sgp), `_all_endpoints` (true), `_cooldown_ms`, `_min/max_priority_fee`. A bundle without profit is always dropped — nothing paid (the old `harmonic_bundle_require_profit` is ignored). |

**Rate per sender.** Every send goes to all regions of the sender at once (Apex: to `apex_regions`; `helius_bundle`: one Sender region by turn); a sender sends at most once per its delay
(`<name>_cooldown_ms`, Jito `jito_process_delay_ms`, RPC `process_delay_ms`). Providers have their own limits per
key — too fast gives `❌ … send failed … 429`.

Priority without a sender's own range: Helius, NextBlock and Harmonic copy a single given bound; others use 0..max;
none set: the global `min_priority_fee`/`max_priority_fee`.

## 8. Hot modes: `mode = "ladder"` and `mode = "flow"`

Instead of a fixed markets file, the bot watches the on-chain arbitrage bots **over Geyser** and shoots the coins they
are earning on right now, with whole routes (the exact pools of their winning arbitrages first). These are the modes
DiabloArb runs itself. **Geyser is required**; without `geyser_endpoint` the bot warns and falls back to the markets
file. The markets file is not used in these modes.

- **What the bot measures.** For every coin: the realized profit of the watched bots' winning arbitrages (only
  `program` entries of the bot list; single wallets are ignored), attributed to the coins of the route they actually
  executed.
  - *rate* — their profit over the last 30 s, per minute;
  - *temperature* — the same profit with every trade fading by half each `hot_half_life_s` (15 s), per minute;
  - *earned* — their profit over the last 5 minutes (ladder ordering) or `flow_rank_s` (flow).
- **Ladder** — a coin turns **on** when its rate ≥ `hot_sol_per_min` and the bots made at least 3 paying trades on it
  in those 30 s; it stays on until its temperature falls below a quarter of the threshold. The tier follows the
  temperature:
  - tier 1 — on: RPC copies only, one every `process_delay_ms` (recent blockhash, lands even without profit). Their priority is random from
    1 000 lamports up to a ceiling: twice the median priority the winning bots pay on that coin (last 60 s), at most
    10% of the bots' earnings per our landings per minute, never above `hot_priority_cap`;
  - tier 2 — temperature ≥ `hot_senders_x` × threshold: plus a broadcast to every configured sender every
    `hot_sender_pause_ms`, all copies signed over one durable nonce (at most one lands). Each sender's tip is its own `<name>_tip_*` range, priority
    random in `hot_sender_min/max_priority_fee`. Jito joins if `hot_jito_as_sender`; its tip is then raised to at
    least the lowest minimum tip of the other senders (within its own max);
  - tier 3 — temperature ≥ `hot_jito_x` × threshold: Jito with its own tier (`hot_jito_step`), every
    `hot_jito_pause_ms` (unset: the senders' pause).
  Each tier shoots at its own pause, on a timer of their common step (`hot_interval_ms`, `hot_fast_ms` are not read).
  The transaction carries the top coin's best route first, then other hot coins' routes that fit. When no coin is
  on, nothing is sent (no fees) — idle periods are normal.
- **What a shot carries (`route_memory`, on by default).** The bot remembers every route the arbitrage bots won on, for
  hours, and scores it by what it paid lately (15 s, 150 s and 30 min scales). Each shot is the best single transaction:
  the best route first, then the routes with the most score per account they add, of any coin — a second coin goes in
  when it fits, otherwise the room goes to more routes of the first. The set changes only when the scores do. A copy
  sent less than 200 ms after another gives its room to the next routes on the list.
- **Bundle lanes** (Temporal bundles, Harmonic, `jito_classic`) get the hottest route every `hot_bundle_interval_ms`
  whenever any coin is tracked — also while no coin is on; a bundle without profit costs nothing. Their tips are their
  own keys; their priority is their own `<name>_min/max_priority_fee` (`harmonic_bundle_…`, `temporal_bundle_…`,
  `helius_bundle_…`, lamports a transaction) when set, else the senders' `hot_sender_min/max_priority_fee`.
- **Flow** — non-stop: one shot every `hot_sender_pause_ms` (unset: 250 ms) with the top 2 coins, or one and the
  next one's pools when two do not fit (every coin with any profit in the last 900 s competes; the place is the higher
  of its average rate over those 900 s and its temperature; `hot_interval_ms`, `flow_top`, `flow_rank_s` are not read), by the
  senders' broadcast on durable nonces plus RPC copies when `spam_rpc = true` (the same transaction on the same nonce,
  at the senders' priority and pause), Jito as one of the senders, priority random from
  `hot_sender_min_priority_fee` to `hot_sender_max_priority_fee`. Costs fees all the time, also when nothing is hot.
- **Pauses.** `hot_sender_pause_ms` is every sender's pause in place of its `<name>_cooldown_ms`: a copy to all its
  regions at most this often. Without it each sender keeps its own cooldown (and mind the providers' limits).
- **Still used in hot modes:** the senders and their keys/tips, `flashloan`, `memo`, `cu_limit`, `send_rpcs`,
  `auto_unwrap`, `auto_close_atas`. **Not used:** `markets_file`, `luts` (tables come from what the bots use).
- **Durable nonces.** The broadcast to many senders is signed over one durable nonce per shot, so at most one copy
  lands (no double tips). On a start that sends, missing nonce accounts are created (≈0.00145 SOL rent each,
  32 ≈ 0.046 SOL); `./sender nonces close` returns the rent. A dry run only reports them.

| Key | Default | Meaning |
|---|---|---|
| `hot_sol_per_min` | 0.03 | Ladder threshold: the bots' earnings on a coin, SOL per minute, that turns it on. |
| `hot_senders_x` | 2 | Ladder: tier 2 at this multiple of the threshold. |
| `hot_jito_x` | 4 | Ladder: tier 3 (Jito's own) at this multiple. |
| `hot_rpc_sol_per_min`, `hot_senders_sol_per_min`, `hot_jito_sol_per_min` | `hot_sol_per_min` × 1, × `hot_senders_x`, × `hot_jito_x` | Ladder: each step's own threshold, SOL per minute, in place of the multiples (any order; a step that is off does not count). |
| `hot_senders_on` | `true` | Ladder: the senders' step (tier 2) as a whole; `false` — never reached (the senders' own switches stay as they are). |
| `hot_jito_as_sender` | `true` | Jito joins the senders' broadcast from tier 2. |
| `hot_jito_step` | `true` only when `hot_jito_as_sender = false` | Ladder: Jito's own tier 3 (from `hot_jito_x`), also when it is one of the senders. **Its tip is paid on every landing, win or not.** |
| `hot_jito_step_tip_min_lamports`, `hot_jito_step_tip_max_lamports` | from the floor up to the coin's ceiling | Ladder: tier 3 Jito's tip range, lamports (never the senders' win-only tips). |
| `process_delay_ms` | 400 | Ladder: the RPC tier's pause, ms. |
| `hot_sender_pause_ms` | — | The senders' pause, ms (ladder: tier 2; flow: the shot itself). |
| `hot_jito_pause_ms` | the senders' | Ladder: Jito's own tier's pause, ms. |
| `hot_half_life_s` | 15 | Seconds in which a coin's temperature halves. |
| `hot_sender_min_priority_fee`, `hot_sender_max_priority_fee` | 100, 1000 | Senders' priority, lamports/tx, random in the range. |
| `hot_priority_cap` | 100000 | Ladder: ceiling of the RPC copies' priority (lamports/tx). Flow: not used — RPC copies take the senders' range. |
| `route_memory` | `true` | Both modes: the routes the arbitrage bots won on are remembered for hours (file `route-memory.txt` next to the config, kept over restarts) and every shot is the best single transaction by them — routes of any coin, by their profit (last 15 s, 150 s, 30 min) per account they take; the room left is filled as before. `false`: the selection as before (the top coins of the last minutes only). |
| `max_hops` | `4` | Every mode, markets too: the longest route a shot lists, 2 to 5 pools (the program runs 5). Four covers the loops through a second base — SOL → USDC → coin A → coin B → SOL; in markets mode a group of four pools gives its four-pool loop; in ladder and flow a remembered route is recognised whichever base it starts from. A longer route asks more compute units of a transaction: set `3` to keep the shots as before. |
| `hot_lanes_off` | `[]` | Senders not used in this mode, e.g. `["landx", "nextblock"]`. |
| `hot_bundle_interval_ms` | 100 | Timer of the bundle lanes (Temporal bundles, Harmonic, `jito_classic`): the hottest route this often. 0 = with the shots. |
| `arb_sources_file` | built in | Own list of bots to watch: `<address> <program|wallet|aggregator> <name>` per line. Only `program` entries count for the heat ranking. |
| `nonces` | 32 | Durable nonce accounts (max 100). |

Minimal ladder setup (without `mode`, `geyser_endpoint` and `geyser_x_token` the bot falls back to markets):

```toml
geyser_endpoint = "https://your-geyser:443"
geyser_x_token = "…"
mode = "ladder"
# senders as usual, e.g.
jito = true
jito_min_tip_lamports = 1000
jito_max_tip_lamports = 100000
temporal = true
temporal_uuid = "…"
temporal_tip_min_lamports = 1000000
```

Full ladder setup — every key of the mode with its default (commented lines are optional):

```toml
# base (any mode)
rpc = "https://your-rpc"                 # reading
send_rpcs = ["https://your-send-rpc"]    # RPCs that accept transactions
keypair = "key.json"
flashloan = true
pump_v2 = true                       # PumpSwap hops as the 17-account v2 trades (false: the older ones)
cu_limit = "auto"
auto_unwrap = true
min_sol_amount = 0.1
auto_close_atas = true               # rent of token accounts idle for 24 h back to the wallet (default false)

# ladder: required
mode = "ladder"
geyser_endpoint = "https://your-geyser:443"
geyser_x_token = "…"

# thresholds: SOL a minute the arbitrage bots earn on a coin
hot_sol_per_min = 0.03          # step 1 (RPC) turns on
hot_senders_x = 2               # step 2 (senders) at 2x
hot_jito_x = 4                  # step 3 (Jito's own) at 4x
# hot_rpc_sol_per_min = 0.03    # or each step's own threshold
# hot_senders_sol_per_min = 0.06
# hot_jito_sol_per_min = 0.12
hot_half_life_s = 15

# step 1: RPC copies (priority from 1000 lamports up to what the winners pay, capped)
spam_rpc = true
process_delay_ms = 400
hot_priority_cap = 100000

# step 2: the senders' broadcast on one durable nonce
hot_senders_on = true
hot_sender_min_priority_fee = 1000   # the senders' priority, one range for all of them
hot_sender_max_priority_fee = 10000
hot_sender_pause_ms = 250            # unset: each sender's own <name>_cooldown_ms
hot_lanes_off = []
route_memory = true                  # every shot the best transaction by the routes remembered (false: as before)
max_hops = 4                         # the longest route of a shot in every mode, 2-5 pools (3: as before)
# each sender: on, its key, its own tips (lamports, drawn per copy, paid only on a win)
temporal = true
temporal_uuid = "…"
temporal_tip_min_lamports = 1000000     # min 1 000 000
temporal_tip_max_lamports = 5000000
helius = true
# helius_api_key = "…"                 # optional: 50 requests/s per region instead of 1 per server IP
helius_tip_min_lamports = 200000        # min 200 000
helius_tip_max_lamports = 2000000
# astralane = true
# astralane_api_key = "…"
# astralane_tip_min_lamports = 10000    # min 10 000
# astralane_tip_max_lamports = 1000000
# zeroslot = true
# zeroslot_api_key = "…"
# zeroslot_tip_min_lamports = 1000000   # 0slot; min 1 000 000
# zeroslot_tip_max_lamports = 3000000
# falcon = true
# falcon_api_key = "…"
# falcon_tip_min_lamports = 1000000     # min 1 000 000
# falcon_tip_max_lamports = 3000000
# stellium = true
# stellium_api_key = "…"
# stellium_tip_min_lamports = 1000000   # min 1 000 000; + stellium_endpoints = ["…"]
# stellium_tip_max_lamports = 3000000
# nextblock = true
# nextblock_api_key = "…"
# nextblock_tip_min_lamports = 100000   # no minimum
# nextblock_tip_max_lamports = 1000000
# flashblock = true
# flashblock_api_key = "…"
# flashblock_tip_min_lamports = 100000  # min 100 000
# flashblock_tip_max_lamports = 1000000
# hellomoon = true
# hellomoon_api_key = "…"
# hellomoon_tip_min_lamports = 1000000  # min 1 000 000
# hellomoon_tip_max_lamports = 3000000
# fast = true
# fast_api_key = "…"
# fast_tip_min_lamports = 1000000       # min 1 000 000
# fast_tip_max_lamports = 3000000
# apex = true
# apex_api_key = "…"
# apex_tip_min_lamports = 1000000       # min 1 000 000; + apex_regions = ["fra"]
# apex_tip_max_lamports = 3000000

# Jito (as a sender: the tip paid only on a win, raised to at least the other senders' lowest minimum tip)
jito = true
# jito_uuid = "…"               # optional, a real UUID only
jito_min_tip_lamports = 1000
jito_max_tip_lamports = 100000
hot_jito_as_sender = true
hot_jito_step = false           # true: Jito's own step 3, its tip paid on every landing
# hot_jito_step_tip_min_lamports = 10000
# hot_jito_step_tip_max_lamports = 1000000
# hot_jito_pause_ms = 250

# bundles in the background: non-stop, top routes, a miss is free
hot_bundle_interval_ms = 100
harmonic_bundle = true
harmonic_bundle_auth_keypair = "harmonic.json"
harmonic_bundle_min_priority_fee = 50000
harmonic_bundle_max_priority_fee = 200000
harmonic_bundle_cooldown_ms = 100
temporal_bundle = true
# temporal_bundle_uuid = "…"    # unset: temporal_uuid
temporal_bundle_tip_min_lamports = 1000000
temporal_bundle_tip_max_lamports = 5000000
temporal_bundle_min_priority_fee = 20000
temporal_bundle_max_priority_fee = 100000
temporal_bundle_cooldown_ms = 200
helius_bundle = true
helius_bundle_tip_min_lamports = 1000000
helius_bundle_tip_max_lamports = 30000000
helius_bundle_min_priority_fee = 5000
helius_bundle_max_priority_fee = 50000
helius_bundle_cooldown_ms = 100

# other
# nonces = 32                   # created on start, ~0.00145 SOL rent each
# arb_sources_file = "my-bots.txt"
```

## 9. Log lines

| Line | Meaning |
|---|---|
| `😈 DiabloArb sender … — config …` | Start, version (commit), config. |
| `🔑 Wallet: …` | The wallet address. |
| `🏦 Flashloan: on/off` | Whether the vault lends. |
| `<icon> <sender> enabled: endpoints=N, tip a..b lamports, priority a..b lamports, require_profit=…` | Each active sender with its regions, tips, priority. `temporal bundle enabled` = Temporal bundles. |
| `📡 Geyser stream` / `📡 No Geyser: pools over RPC every N ms` | Data source. |
| `🔥 Mode: ladder/flow …` | A hot mode is on. `⚠️ mode = … needs Geyser` — fell back to the markets file. |
| `🔐 Durable nonces: N of M ready` / `Creating N durable nonce accounts` | Nonces for the hot modes. |
| `✅ Markets loaded: N pools` / `🔄 Markets updated: N pools` | Markets file read / changed. |
| `📚 LUTs: N loaded` | Lookup tables. |
| `👛 Token accounts: N` | Token accounts the wallet has. |
| `🪙 Creating token accounts for N mint(s); the other coins shoot on meanwhile` | A new coin needs a token account; it is being created via `send_rpcs`. |
| `❌ token accounts not created: …` | Creation failed — check `send_rpcs` accepts transactions and the wallet has SOL. |
| `🎯 Starting spam loop... every N ms` | Running; `(dry run: nothing sent)` with `DIABLO_SENDER_DRY=1`. |
| `📤 Dispatched tx`, `⚡ Dispatched Jito tx`, `🌀 Dispatched temporal tx/bundle`, `🎼 Dispatched Harmonic bundle`, … | One transaction sent: tip, priority, number of regions, signature start. |
| `❌ <sender> send failed (N in 10 s): …` | A sender refused requests (bad key, rate limit, 400/429). At most one line per 10 s. |
| `✅ [n] Success! +X SOL (wallet …)` | A win: the base token balance grew. |
| `📊 Last minute: …` | Per-minute summary: sent, failed, wins, balances; in markets mode pools/groups, in hot modes the top 2 coins with their rate and tier. |
| `⚠️ …` | Configuration warning (sender without key, bad UUID, unknown mode). |
| `update: …` | Self-update result. |

## 10. Common questions

- **It sent, then suddenly stopped.** Check `🪙`/`❌ token accounts` lines (needs a working `send_rpcs` and SOL), `❌ …
  send failed` (key/limits), the SOL balance (fees), and in hot modes whether any coin is hot (`📊 … coins: none yet`
  or tier 0 — the ladder waits for a hot coin by design).
- **No wins.** Normal for periods: wins come in bursts on hot coins. More senders and a faster loop raise the
  chance and the fees. Hot modes need Geyser.
- **Jito answers 400.** Usually a `jito_uuid` that is not a valid UUID or not yours.
- **Too expensive.** Lower priority ranges, longer delays, fewer always-landing lanes (§5).
  There is no spending cap: the bot runs until stopped (an old `max_spend_sol` is ignored).
- **Test safely.** `DIABLO_SENDER_DRY=1 ./sender config.toml` shows what would be sent.
- **Failed transactions in the explorer.** `custom program error: 0x7` (`NoProfit`) is normal: the opportunity was gone
  when the transaction executed; the tip was not paid, only the network fee and priority. Many of them = paying
  priority for nothing: lower the priority or shoot less often.
- **Which mode?** Markets (default): simplest, works without Geyser, follows `moneyprinter.bot/auto/mp.toml`. Ladder:
  needs Geyser, shoots only while bots are earning, escalates fees with the heat — usually the best cost/benefit.
  Flow: needs Geyser, never stops, highest fees, most presence.
- **Self-update.** On start the bot compares the latest GitHub commit of `sender` with the one it last installed
  (`/tmp/sender.update.commit`), downloads, checks and replaces itself, then restarts with the same arguments.
- **Not supported here** (ignored): `proxy`, `autoluts`, `autodelete_dead_luts`, `temporal_transport`, `bin_limit`,
  `program_id`, `force_mode`, `max_amount_in`, `jito_endpoints`, `temporal_endpoints` (all regions are used).
