# DiabloArb sender — configuration reference for AI assistants

> **To the AI reading this:** this file describes every setting of the DiabloArb arbitrage bot (`sender`, from
> github.com/cryptodiablo/diabloarb) as of 5 October 2026 (build `ed0af90`). Use it to explain to a person what each
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
| `cu_limit` | 360000 | Compute-unit limit of a transaction (max 1 400 000). Priority per CU = lamports × 10⁶ / `cu_limit`. |
| `flashloan` | `false` | `true`: the trade may use the DiabloArb vault's WSOL besides your own (bigger trades). The 7% fee is the same. |
| `markets_file` | — | Markets file, path or URL (§2). Required in markets mode. |
| `luts` | — | LUT list, path or URL. |
| `files_updates_ms` | 50 | How often local files and `config.toml`/`gas.json` are re-read. |
| `remote_files_update_ms` | 10000 | How often URL markets file / LUT list are re-fetched (with ETag). |
| `luts_update_ms` | 1000 | LUT list refresh. |
| `gas_file` | — | Path to `gas.json` (as given, else next to the config). |
| `memo` | — | Optional memo text added to each transaction (for tracing). |
| `geyser_endpoint`, `geyser_x_token` | — | Yellowstone gRPC. Without it pools are polled over `rpc` every second (works, slower). **Required for ladder/flow modes.** |
| `auto_unwrap`, `min_sol_amount` | `false`, — | SOL is checked every second; once SOL < `min_sol_amount` (SOL; at least ≈0.0107 is used) the whole WSOL balance is unwrapped to SOL with a priority fee, resent until it lands (the WSOL account stays). **Always on, whatever `auto_unwrap`:** below the network's rent minimum + 0.005 SOL (≈0.0057 SOL) the bot pauses sending (`PAUSED` in the minute summary) so the wallet never gets locked; with no WSOL left it asks for a top-up. |
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
| `helius` | none | Helius requires ≥ 200 000 | Helius Sender; fails without profit. |
| `helius_swqos` | none | ≥ 5 000 | SWQoS-only; lands always. |
| `temporal` | `temporal_uuid` | 1 000 000 (0.001 SOL; less is dropped by Temporal) | Nozomi, 9 regions. `temporal_tip_accounts` overrides the tip accounts. |
| `temporal_bundle` | `temporal_bundle_uuid` if set (a separate key), else the same `temporal_uuid` | 1 000 000 | Temporal `sendBundle` (lands via Jito/Harmonic block builders). Keys `temporal_bundle_tip_min/max_lamports` (default 0.001 SOL), `_min/max_priority_fee`, `_cooldown_ms`, `_all_endpoints` (true). A bundle without profit is always dropped — nothing paid; no key changes that. Works next to `temporal`. |
| `helius_bundle` | none | 1 000 000 | Helius Sender Max `sendBundle` (no credits). Keys `helius_bundle_tip_min/max_lamports` (default 0.001 SOL; the sample: random 0.001–0.03 SOL), `_min/max_priority_fee` (at least 5 000 lamports a transaction), `_cooldown_ms`, `_all_endpoints` (false: one of 7 Sender regions by turn; true: every region each time — 7× the requests). A bundle without profit is always dropped — nothing paid. Works next to `helius` and `temporal_bundle`. |
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
  - tier 1 — on: RPC copies only (recent blockhash, lands even without profit). Their priority is random from
    1 000 lamports up to a ceiling: twice the median priority the winning bots pay on that coin (last 60 s), at most
    10% of the bots' earnings per our landings per minute, never above `hot_priority_cap`;
  - tier 2 — temperature ≥ `hot_senders_x` × threshold: plus one broadcast to every configured sender, all copies
    signed over one durable nonce (at most one lands). Each sender's tip is its own `<name>_tip_*` range, priority
    random in `hot_sender_min/max_priority_fee`. Jito joins if `hot_jito_as_sender`; its tip is then raised to at
    least the lowest minimum tip of the other senders (within its own max). Plus extra broadcast shots every
    `hot_fast_ms`;
  - tier 3 — temperature ≥ `hot_jito_x` × threshold: Jito with its own tier (only when `hot_jito_as_sender = false`).
  The transaction carries the top coin's best route first, then other hot coins' routes that fit. When no coin is
  on, nothing is sent (no fees) — idle periods are normal.
- **Bundle lanes** (Temporal bundles, Harmonic, `jito_classic`) get the hottest route every `hot_bundle_interval_ms`
  whenever any coin is tracked — also while no coin is on; a bundle without profit costs nothing.
- **Flow** — non-stop: every `hot_interval_ms` the top `flow_top` coins (every coin with any profit in
  `flow_rank_s` competes; the place is the higher of its average rate over `flow_rank_s` and its temperature), by the
  senders' broadcast on durable nonces plus RPC copies when `spam_rpc = true`, Jito as one of the senders, priority random from
  `hot_sender_min_priority_fee` to `hot_sender_max_priority_fee`. Costs fees all the time, also when nothing is hot.
- **Sender delays still apply.** A sender whose `<name>_cooldown_ms` is longer than `hot_interval_ms` (or
  `hot_fast_ms`) skips the shots in between. For the mode's full pace set the senders' delays ≤ `hot_interval_ms`
  (and mind the providers' limits).
- **Still used in hot modes:** the senders and their keys/tips, `flashloan`, `memo`, `cu_limit`, `send_rpcs`,
  `auto_unwrap`. **Not used:** `markets_file`, `luts` (tables come from what the bots use), `process_delay_ms` as the
  pace.
- **Durable nonces.** The broadcast to many senders is signed over one durable nonce per shot, so at most one copy
  lands (no double tips). On a start that sends, missing nonce accounts are created (≈0.00145 SOL rent each,
  32 ≈ 0.046 SOL); `./sender nonces close` returns the rent. A dry run only reports them.

| Key | Default | Meaning |
|---|---|---|
| `hot_sol_per_min` | 0.03 | Ladder threshold: the bots' earnings on a coin, SOL per minute, that turns it on. |
| `hot_senders_x` | 2 | Ladder: tier 2 at this multiple of the threshold. |
| `hot_jito_x` | 4 | Ladder: tier 3 (Jito) at this multiple, if Jito is not a sender. |
| `hot_jito_as_sender` | `true` | Jito joins the senders' broadcast from tier 2. |
| `hot_interval_ms` | 250 | One shot this often. |
| `hot_fast_ms` | 60 (ladder), 0 (flow) | Extra broadcast shots between ticks at tier ≥ 2, each on its own nonce. 0 = off. |
| `hot_half_life_s` | 15 | Seconds in which a coin's temperature halves. |
| `flow_top` | 2 | Flow: how many top coins. |
| `flow_rank_s` | 900 | Flow: ranking window, seconds. |
| `hot_sender_min_priority_fee`, `hot_sender_max_priority_fee` | 100, 1000 | Senders' priority, lamports/tx, random in the range. |
| `hot_priority_cap` | 100000 | Ceiling of the RPC copies' priority (lamports/tx). |
| `hot_lanes_off` | `[]` | Senders not used in this mode, e.g. `["landx", "nextblock"]`. |
| `hot_bundle_interval_ms` | 100 | Timer of the bundle lanes (Temporal bundles, Harmonic, `jito_classic`): the hottest route this often. 0 = with the shots. |
| `arb_sources_file` | built in | Own list of bots to watch: `<address> <program|wallet|aggregator> <name>` per line. Only `program` entries count for the heat ranking. |
| `nonces` | 32 | Durable nonce accounts (max 100). |

Minimal ladder setup:

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
