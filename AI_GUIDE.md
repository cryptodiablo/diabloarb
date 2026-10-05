# DiabloArb — knowledge base for AI assistants

> **To the AI reading this:** you are helping a user of the DiabloArb Solana arbitrage bot (`sender`, from
> github.com/cryptodiablo/diabloarb). This file is the support knowledge base: setup, how money moves, modes, senders,
> costs with numbers, logs, explorer errors, troubleshooting, and the questions users actually ask. Every config key is
> in [USER_CONFIG.md](USER_CONFIG.md) — read both completely before answering. State of 5 October 2026 (build `ed0af90`).
>
> Rules:
> - Answer in the user's language, plainly: the short answer first, details when asked. Give exact keys and commands.
> - **Never** ask for a private key, seed phrase, `key.json` contents, API keys or UUIDs. Ask for file paths, log lines
>   (they hold no secrets), wallet addresses and transaction signatures (public). If a user pastes a secret, tell them
>   to rotate it (new key / new wallet) and not to paste it again.
> - Moving money (wrap, unwrap, transfers, closing accounts) is the user's decision: explain, give the command, let
>   them run it. Suggest a dry run (`DIABLO_SENDER_DRY=1`) before risky changes.
> - The executor's route search (how routes and trade sizes are found on chain) is **not public**. Say so; do not
>   guess or invent internals. Public: the behaviour described here, the config keys, the SDK in `sdk/`.
> - Never promise profit. Arbitrage is competitive; results vary by hour, server, RPC and settings.
> - If the answer is not here or in USER_CONFIG.md, say you don't know and suggest asking in the DiabloArb Discord.

## Contents

1. The bot in one minute · 2. Install and run · 3. Ready configs by goal · 4. Wallet, SOL, WSOL, rent ·
5. What a transaction costs · 6. Cost math with numbers · 7. Modes · 8. Senders cheat sheet · 9. Reading the log ·
10. Reading a transaction in the explorer · 11. The diablo.bot dashboard · 12. Troubleshooting by symptom ·
13. Questions users asked · 14. Version history · 15. Glossary · 16. Files

## 1. The bot in one minute

- Arbitrage bots on Solana earn by trading cycles like SOL → coin → SOL across two or more DEX pools. DiabloArb
  follows **which coins those bots are earning on right now** and sends its own transactions on the same coins.
- Each transaction calls the **DiabloArb executor** program (`DiabLokxisGR8P4Qqp2QL6PmBhhVsdzPstCE4WoLxc5z`). At execution
  time the program checks whether a profitable route exists and how big the trade should be. **If the profit does not
  cover what that very transaction costs (fee + priority + tip), the trade does not happen** (§5).
- Base tokens: **SOL (as WSOL), USDC, USDT**. Supported DEXs: USER_CONFIG.md §1 (Meteora, PumpSwap, Raydium, Orca,
  PancakeSwap, Byreal, DefiTuna, Manifest, MetaDAO…). Coins with an active transfer hook are skipped.
- Capital: the wallet's WSOL/USDC/USDT plus, with `flashloan = true`, a shared vault that lends for the duration of a
  single transaction (repaid inside it). **7% of each realized profit** goes to the vault; the rest stays in the wallet.
  No fee on losses or misses.
- The bot (`sender`) runs on the user's own Linux server with their own wallet and RPC; the key never leaves the
  server. It updates itself from GitHub on every start.
- Where the coin list comes from: `https://moneyprinter.bot/auto/mp.toml` (markets mode) is rebuilt live from the coins
  the arbitrage bots earn most on; hot modes (ladder/flow) measure this themselves through the user's Geyser.

## 2. Install and run

- **Server:** any Linux x86_64 VPS (the binary is static; Windows works through WSL2; macOS — use a VPS). Closer to
  your RPC/Geyser and to Solana validators (Frankfurt, Amsterdam, New York…) reacts faster.
- **Install:**
  ```bash
  wget -O diabloarb.zip https://github.com/cryptodiablo/diabloarb/archive/refs/heads/main.zip
  unzip diabloarb.zip && cd diabloarb-main && chmod +x ./sender
  ```
- **Wallet:** put the keypair JSON (Solana CLI format, or the old Go bot's encrypted file) next to the config and set
  `keypair = "key.json"`; `chmod 600 key.json`. Fund it with SOL, then `./sender wrap 0.5` for trading capital.
- **Minimum config:** `rpc` (reading), `keypair`; everything else has defaults. Add `send_rpcs` that accept
  transactions, then senders (§8).
- **First run — dry:** `DIABLO_SENDER_DRY=1 ./sender config.toml` builds and logs everything with `[dry]`, sends nothing.
- **Run for real:** `./sender config.toml`. Keep it running with `screen`/`tmux` or systemd:
  ```ini
  # /etc/systemd/system/diabloarb.service
  [Unit]
  Description=DiabloArb sender
  After=network-online.target
  [Service]
  WorkingDirectory=/root/diabloarb-main
  ExecStart=/root/diabloarb-main/sender config.toml
  Restart=always
  RestartSec=5
  [Install]
  WantedBy=multi-user.target
  ```
  `systemctl daemon-reload && systemctl enable --now diabloarb`; logs: `journalctl -u diabloarb -f`.
- **Several bots on one server:** one process per config (different folders or config names). Several servers on one
  wallet also work (in hot modes they share the same durable nonces, so one opportunity lands once).
- **Updates:** a restart updates. `./sender version` shows the build; `DIABLO_SENDER_AUTO_UPDATE=0` keeps the current one.

## 3. Ready configs by goal

Add these to the sample `config.toml` (edit existing lines rather than adding duplicates — a key written twice uses the
last value). Keys and defaults: USER_CONFIG.md.

- **Cheapest start, no Geyser (markets mode):**
  ```toml
  spam_rpc = true
  process_delay_ms = 400        # one RPC copy every 400 ms
  min_priority_fee = 100
  max_priority_fee = 1000
  flashloan = true
  temporal_bundle = true        # misses free; needs temporal_uuid
  helius_bundle = true          # misses free; no key
  ```
- **"No losing transactions" (bundles only):** turn off `spam_rpc` and the always-landing lanes, keep only bundle lanes
  (`temporal_bundle`, `helius_bundle`, `harmonic_bundle`, or Jito with `jito_classic = true`). A miss costs nothing; you
  pay only on wins. Fewer wins than spam lanes, but no bleeding.
- **Ladder with Geyser (usually the best cost/benefit):**
  ```toml
  geyser_endpoint = "https://your-yellowstone-endpoint"
  geyser_x_token = "your-token"     # keep secret
  mode = "ladder"
  hot_sol_per_min = 0.03            # lower = more active, higher = pickier
  helius = true                     # step-2 senders: add the ones you have keys for
  temporal = true
  temporal_bundle = true
  helius_bundle = true
  ```
- **Maximum presence (flow):** `mode = "flow"`, more senders, short cooldowns. Costs fees all the time.

## 4. Wallet, SOL, WSOL, rent

| Where | What it is for |
|---|---|
| **SOL** | Network fees, priority fees, tips, account rent. Must never run out. |
| **WSOL / USDC / USDT** | Trading capital. Profit lands here (`✅ [n] Success!`). |
| **Token accounts** | One per coin the bot trades (created automatically): ≈0.002 SOL rent each, Token-2022 coins a bit more. |
| **Durable nonces** | Hot modes create 32 nonce accounts, ≈0.00145 SOL each (≈0.046 SOL total). |

- **Rent is not lost**; it returns when an account is closed. A busy bot can hold 0.1–0.4 SOL in token-account rent
  after a day or two — so "SOL + WSOL" can look lower than expected while profit is positive.
- **Getting rent back:** `./sender nonces close` (stop the bot first; hot modes recreate them on the next start).
  Empty token accounts: `spl-token accounts` lists them, `spl-token close --address <ACCOUNT>` closes an empty one
  (Solana CLI tools). The bot recreates an account (≈0.002 SOL) when it trades that coin again. No built-in command yet.
- **Commands:** `./sender wrap 0.5` (SOL → WSOL), `./sender unwrap 0.5`, `./sender unwrap all` (all WSOL → SOL; the WSOL
  account stays). A config path may be added: `./sender unwrap config.toml all`.
- **SOL reserve and auto-unwrap (always on):** SOL is checked every second. Below the network minimum for a wallet
  (≈0.00065 SOL) plus a 0.005 SOL reserve, the bot **pauses sending** (`💧 … sending paused`, `PAUSED` in the minute
  summary) so the wallet can still pay for an unwrap; it resumes when SOL is back. With `auto_unwrap = true`, once
  SOL < `min_sol_amount` (at least ≈0.0107 SOL) the whole WSOL is unwrapped automatically, with a priority fee, resent
  until it lands.
- **Locked wallet:** if SOL is already at the network minimum (≈0.00065), no transaction of that wallet can land — not
  even an unwrap. Fix: send ~0.001–0.01 SOL from another wallet; a current build unwraps by itself within seconds.
  Builds since 5 October 2026 (`ed0af90`) prevent this.
- **Withdrawing profit:** stop the bot, `./sender unwrap all`, then transfer SOL with any wallet. USDC/USDT stay as tokens.

## 5. What a transaction costs (the most asked topic)

Every landed transaction pays the **network fee** (5 000 lamports) plus its **priority fee**. The **tip** is an
instruction inside the transaction: it is paid only if the transaction succeeds. Transactions that never land (dropped,
expired) cost nothing.

**Required profit includes the tip.** For every copy the bot sends, the minimum profit the program must reach is raised
to that copy's own cost: base fee + priority (on the full compute limit) + the tip drawn for that copy. A route that
does not cover its own tip and fees never executes. There is no "required profit" key — it is automatic. The vault's
7% is checked too: the profit after it must still reach that minimum.

| Lane type | Miss (no profit) | Win |
|---|---|---|
| **Bundles** — Temporal bundles, Helius bundles, Harmonic bundles, Jito with `jito_classic = true` | Dropped whole: **nothing paid** | fee + priority + tip, covered by the profit |
| **Senders that fail without profit** — Helius, Temporal, Astralane, Falcon, 0slot, NextBlock, Stellium, Flashblock, HelloMoon, Fast, Apex, Jito (default) | Lands as failed (`0x7 NoProfit`): **fee + priority paid, tip not** | fee + priority + tip |
| **Always-landing** — RPC copies (`spam_rpc`), Helius SWQoS, Fast SWQoS, Jito with `jito_require_profit = false`, ladder step-3 Jito | Lands as an empty success: **fee + priority (+ tip, where it has one) paid** | same + profit |

`require_profit=true` in a sender's start line means its tip is paid only on a win.

## 6. Cost math with numbers

1 SOL = 1 000 000 000 lamports. Priority is set in **lamports per transaction** (USER_CONFIG §4).

- **RPC lane (always lands):** cost per landed copy = 5 000 + priority. With `process_delay_ms = 400` (150 copies a
  minute) and priority 100–1 000 (average ≈550): 150 × 5 550 ≈ 0.00083 SOL a minute ≈ **1.2 SOL a day** if every copy
  lands. Halve the pace or the priority to halve it.
- **Fail-without-profit senders:** a landed miss costs 5 000 + priority; tips only on wins. With low sender priority
  (100–1 000) a miss costs ≈0.000006 SOL.
- **Bundles:** misses free. A win pays its tip (e.g. 0.001–0.03 SOL for Helius bundles) out of a profit that covered it.
- **Ladder:** costs only while a coin is hot (§7), so quiet hours cost ≈0.
- **Rule of thumb:** daily cost ≈ (landed copies a day) × (5 000 + average priority) + tips of wins. Compare with
  wins a day × average win. If fees outrun profit: lower priority, slower loops, drop always-landing lanes, rely on
  bundles, or switch to ladder.

## 7. Modes

- **markets** (default, `mode` unset): shoots the pools of the markets file in a loop, one transaction per tick (the
  shortest delay of the active loops), the next coin group each time, hottest first. Works without Geyser (pools polled
  over RPC every second). Constant cost.
- **ladder** (needs Geyser): spends only when there is money on the table.
  1. Measures how much SOL/min the known arb bots earn on each coin right now (a coin needs ≥ 3 paying trades in 30 s).
  2. Quiet coin → nothing sent, nothing paid.
  3. Above `hot_sol_per_min` (0.03) → **step 1**: RPC copies every `hot_interval_ms` (250 ms); their priority follows
     what the winning bots pay (up to `hot_priority_cap`).
  4. Above `hot_senders_x` × (2×) → **step 2**: also one broadcast to all paid senders, signed over one durable nonce so at
     most one copy lands; tips only on a win; extra shots every `hot_fast_ms` (60 ms). Jito is one of these senders by
     default (`hot_jito_as_sender = true`).
  5. Above `hot_jito_x` × (4×) → **step 3**, only if Jito has its own lane (`hot_jito_as_sender = false` or
     `hot_jito_step = true`): Jito without priority, a tip that grows with the coin's heat and is **paid every time it
     lands, win or not** (`hot_jito_step_tip_min/max_lamports` cap it). Use with care.
  6. The heat fades with a 15 s half-life (`hot_half_life_s`); the coin stays on until it falls below a quarter of the
     threshold, then steps down and stops.
  Each lane can have its own threshold instead of the multiples: `hot_rpc_sol_per_min`, `hot_senders_sol_per_min`,
  `hot_jito_sol_per_min`. Bundle lanes run in the background on the hottest coin every `hot_bundle_interval_ms` (100).
  Hot-mode keys are read at start — restart after changing them.
- **flow** (needs Geyser): never stops; the top `flow_top` coins of the last `flow_rank_s` seconds, sender broadcasts on
  durable nonces, plus RPC copies when `spam_rpc = true`. Highest presence, highest cost.
- **Choosing:** new users — markets with bundles; with Geyser — ladder. Flow only with good senders and budget.

## 8. Senders cheat sheet

Keys and minimum tips: USER_CONFIG.md §7. Each sender is its own loop: `<name>_cooldown_ms` (default
`process_delay_ms`), tip and priority ranges, all its regions per send.

| Sender | Key needed | Miss costs | Notes |
|---|---|---|---|
| RPC (`spam_rpc`) | your RPC | fee + priority (always lands) | `send_rpcs` must accept `sendTransaction`. |
| Jito | optional `jito_uuid` (a real UUID, else leave empty) | fee only (default) | Without a UUID: lower rate limits. `jito_classic = true` → bundle, miss free. |
| Helius Sender | no | fee + priority | Tip ≥ 0.0002 SOL. Rate limit per server IP. |
| Helius bundles (`helius_bundle`) | no | nothing | Tip ≥ 0.001 SOL, priority ≥ 5 000 lamports a transaction, one of 7 regions by turn. |
| Temporal (Nozomi) | `temporal_uuid` | fee + priority | Tip ≥ 0.001 SOL. |
| Temporal bundles | same key (or `temporal_bundle_uuid`) | nothing | Tip ≥ 0.001 SOL. |
| Harmonic bundles | whitelisted keypair file | nothing | Price = priority. |
| OrbitFlare Apex | `apex_api_key` | fee + priority if it lands as failed; nothing if rejected | Tip ≥ 0.001 SOL. Pick 1–2 nearest `apex_regions`. |
| Astralane, 0slot, Falcon, NextBlock, Stellium, Flashblock, HelloMoon, Fast | their API key | fee + priority | Minimum tips in USER_CONFIG §7. |
| Helius SWQoS, Fast SWQoS | none / Fast key | fee + priority + small tip (always lands) | Cheap presence, but every copy costs. |

- Keys come from each provider's own dashboard/sign-up. A sender switched on without its key is skipped with `⚠️`.
- `429` from a provider = too fast for that key/IP: raise its `_cooldown_ms`.
- More senders = more chances on hot coins; each failing copy that lands still pays fee + priority.

## 9. Reading the log

Example start (values vary):

```text
😈 DiabloArb sender 0.1.0 (ed0af909f6f9, rust) — config config.toml   ← build and config
🔑 Wallet: 7xKX…                                                       ← public address
🏦 Flashloan: on                                                       ← vault lending
☀️ helius bundle enabled: endpoints=7 (one by turn), tip 1000000..30000000 lamports, priority 100..3000 lamports, require_profit=true
📡 Geyser stream                                                       ← or "No Geyser: pools over RPC every N ms"
✅ Markets loaded: 120 pools
🎯 Starting spam loop... every 50 ms
☀️ Dispatched helius bundle (tip=14579858, priority_fee=5000, endpoints=1, sig=5k67…)
✅ [1] Success! +0.0123 SOL (wallet …)
📊 Last minute: 830 sent, 2 failed | since start: helius 830 | wins 1 (+0.0123 SOL) | balance 0.4200 SOL, 1.2000 WSOL | 120 pools, 24 groups
```

- `📊 Last minute` parts: sent / failed this minute · per-sender totals since start · wins · balances · markets mode:
  pools and groups (and `N pools still loading over RPC: <reason>`) · hot modes: top 2 coins with rate and tier ·
  `RPC reads failed: N (last: …)` · `PAUSED: SOL at its reserve…`.
- `💧 …` lines: the SOL reserve and auto-unwrap (§4). `🪙 Creating token accounts…`: a new coin. `❌ <sender> send failed
  (N in 10 s): …`: that sender's error, at most one line per 10 s. `⚠️ …`: a config problem.
- Every icon is listed in USER_CONFIG.md §9.

## 10. Reading a transaction in the explorer

Open the signature on solscan.io / solana.fm.

- **Success with token balance changes** (WSOL in → coin → WSOL out bigger): a win. Fee + priority + tip were paid,
  the profit covered them.
- **Success with no swaps**: an always-landing lane found nothing (RPC copy, SWQoS, step-3 Jito): fee + priority (+ tip) paid.
- **Failed, executor error** (`custom program error: 0x…` from `DiabLok…`):

| Code | Name | Meaning |
|---|---|---|
| 0x7 | NoProfit | Nothing reached the required profit at that moment — **normal**, the opportunity was taken. Tip not paid. |
| 0x3 | Unprofitable | The route ran but realized less than expected (state moved) or, after the vault fee, below the minimum. |
| 0x8 | BadVault | Vault section wrong or not repaid — should not happen with the official sender; report it. |
| 0x1, 0x2, 0x4, 0x5, 0x6, 0x9 | data / account errors | Should not happen with the official sender; report the signature. |

- **Failed inside a DEX** (an error from Raydium/Meteora/Orca…, e.g. Anchor `3007`, slippage): the pool changed between
  build and execution — normal in small numbers.
- **`InsufficientFundsForRent`** / transactions refused: the wallet is at the SOL minimum (§4).
- Bundles that missed never appear on chain at all.

## 11. The diablo.bot dashboard

- **Net** of a bot over a period = profit of its landed arbs − fees and tips of **all** the wallet's transactions in
  that period (from an on-chain scanner). If the history is shorter than the period, the label says `since HH:MM`.
- **Balance** = SOL + WSOL. Under it, `+X rent` = SOL held in the wallet's token and nonce accounts (§4): not counted in
  Net, comes back when the accounts are closed.
- Per-trade **Net, SOL** = what actually landed in the wallet (after fee and tip); **Fee + tip** shown next to it.
- Health `no SOL for fees` = SOL too low (§4); `losing since start` = fees outrun profit over the run.
- diablo.bot can also run bots for users (hosted): the same sender, settings in the cabinet; the same costs and keys apply.

## 12. Troubleshooting by symptom

| Symptom | Check / fix |
|---|---|
| Sends, then stops | Minute summary: `PAUSED` → SOL at the reserve (§4); `0 groups` / `N pools still loading over RPC: <reason>` → markets still loading or the RPC fails (reason shown: better RPC or Geyser); hot modes `coins: none yet` / tier 0 → nothing hot, by design. |
| Nothing sent at all | Dry run on? (`DIABLO_SENDER_DRY`); `⚠️` lines; no senders enabled; `spam_rpc = false` with no other lane; ladder with nothing hot. |
| `RPC reads failed: N (last: …)` | The read RPC rejects or rate-limits. Use a paid RPC; public RPC works, slowly. |
| `❌ <sender> send failed … 429` | Provider rate limit: raise `<name>_cooldown_ms`, check the plan/key. Helius Sender limits per IP. |
| `❌ jito send failed … 400` | `jito_uuid` is not a valid UUID or not yours — leave it empty. |
| `❌ … 401/403` | Wrong or missing API key for that sender. |
| `❌ token accounts not created` | `send_rpcs` must accept transactions and the wallet needs SOL. |
| Harmonic bundles stop | Usually markets not loaded (`0 groups`) — the minute summary tells why. Check the keypair is whitelisted. |
| `⚠️ mode = … needs Geyser` | Ladder/flow need `geyser_endpoint`; the bot fell back to markets. |
| Geyser errors / reconnects | Endpoint or `geyser_x_token` wrong, or the provider limits streams. |
| Lots of `0x7 NoProfit` | Normal in moderation; reduce priority/pace, add bundle lanes. |
| No wins for hours | Normal at times; wins come in bursts on hot coins. Check the bot actually sends (minute summary). |
| Fees outrun profit | §6: lower priority, slower loops, drop always-landing lanes, bundles, ladder. |
| Balance lower than expected | Rent in token/nonce accounts (§4) and fees; compare Net on the dashboard. |
| Wallet stuck, unwrap fails | Locked wallet (§4): top up ~0.001–0.01 SOL. |
| A setting has no effect | Key written twice (last wins); a `gas.json` name not referenced from `config.toml`; hot-mode keys need a restart. |
| Old config from the Go bot | Works as is; unsupported keys are ignored (USER_CONFIG §10). |

Ask the user for: the first ~30 log lines after start (wallet, senders, mode, data source), the last few `📊 Last minute`
lines, any `❌`/`⚠️`/`💧` lines, and a transaction signature if they ask about one. Never ask for `config.toml` as a
whole unless they remove keys first.

## 13. Questions users asked

- **Does the required profit include my tip?** Yes (§5): each copy's minimum = its fee + priority + its own tip.
- **Is the dashboard profit after tips?** Yes: per-trade Net is the wallet's real change, fee and tip already out.
- **Another send like Temporal bundles (miss = free)?** Helius bundles, Harmonic bundles, Jito with `jito_classic`.
- **Helius Sender bundles vs Helius `sendBundle`?** The bot uses Sender bundles: no credits, no key, tip ≥ 0.001 SOL,
  priority ≥ 5 000 lamports a transaction, all-or-nothing — a miss costs nothing.
- **Same key for Temporal and Temporal bundles?** Yes; `temporal_bundle_uuid` empty = `temporal_uuid` is used.
- **How does ladder work?** §7.
- **Do I need Geyser?** For ladder/flow yes; markets works without it, slower.
- **Which RPC?** Any Solana RPC for `rpc`; a paid one is more reliable. `send_rpcs` must accept transactions.
- **How much SOL to keep?** Enough for a day of fees at your settings (§6) plus ≈0.05–0.1 SOL for rent of new accounts;
  the reserve pause protects the wallet if it runs low.
- **How much capital?** Your WSOL/USDC/USDT; with `flashloan = true` the vault lends extra inside each transaction,
  so even a small wallet can execute large routes.
- **Is my key safe?** It stays on your server; the bot signs locally and never sends the key anywhere.
- **Why so many token accounts?** One per coin traded; ≈0.002 SOL rent each, returned when closed (§4).
- **Net is positive but my balance went down?** Rent in token/nonce accounts (§4) — the dashboard shows it as `+X rent`.
- **Why many failed transactions?** `0x7 NoProfit` = someone took the opportunity first (§10); they cost fee + priority.
- **Why are some coins never traded?** Coins with an active transfer hook and pools of unsupported DEXs are skipped.
- **How do I update / roll back?** Restart updates. To stay on a build: `DIABLO_SENDER_AUTO_UPDATE=0`.
- **Test without spending?** `DIABLO_SENDER_DRY=1 ./sender config.toml`.
- **Spending limit?** None. The bot runs until stopped (`max_spend_sol` is ignored).
- **SOL is 0 but I have WSOL?** A current build pauses and unwraps by itself; a locked wallet needs a small SOL top-up (§4).
- **Can I use my own markets file?** Yes: `markets_file` = path or URL, format in USER_CONFIG §2.
- **Two wallets on one server?** Two processes, two configs. **One wallet on two servers?** Works; fees add up.
- **Windows / Mac?** Linux x86_64 only; Windows via WSL2; otherwise a VPS.
- **Jito UUID — where?** From Jito on request; it is optional.
- **What is `require_profit=true` in the start line?** That sender's tip is paid only on a win.
- **What does the 7% fee apply to?** Only to realized profit of a win; nothing on misses or losses.
- **Can I build my own sender?** Yes — `sdk/README.md` documents the executor's public instruction format and IDL.
- **How do I see my wins?** `✅ [n] Success!` lines, the wallet's WSOL/USDC growth, or the diablo.bot dashboard.

## 14. Version history

- **4 Oct 2026** — the sender rebuilt in Rust; old `config.toml`/`gas.json` keep working; self-update.
- **5 Oct 2026** — hot modes `ladder`/`flow` with their keys; Temporal bundles; Harmonic bundles no longer stall;
  a key written twice is allowed; OrbitFlare Apex; auto-unwrap without a temporary account's rent; Helius Sender bundles
  (`helius_bundle`); SOL reserve with sending pause and priority auto-unwrap, no spending cap (`ed0af90`).

## 15. Glossary

- **Tip** — payment to a landing service inside the transaction; paid only if it succeeds.
- **Priority fee** — fee to the validator for compute; paid by every landed transaction.
- **Bundle** — a group sent all-or-nothing; a failing bundle is dropped, nothing paid.
- **Durable nonce** — lets one signed transaction go to many services while only one copy can land.
- **Geyser (Yellowstone gRPC)** — live stream of account updates; needed for hot modes.
- **Markets file (`mp.toml`)** — pools/routes to shoot in markets mode. **LUT** — address lookup table.
- **Vault / flash loan** — shared capital lent within one transaction; 7% of profit goes to it.
- **NoProfit (0x7)** — the program found nothing worth executing at that moment.
- **Rent** — SOL kept in an account while it exists; returned when it is closed.
- **SWQoS** — stake-weighted quality of service: a cheaper landing path that lands every copy.

## 16. Files

- [USER_CONFIG.md](USER_CONFIG.md) — every config key, senders, modes, log lines.
- [README.md](README.md) — install, run, wallet commands, supported DEXs.
- [sdk/README.md](sdk/README.md) — building your own sender against the executor (public ABI).
- `config.toml`, `gas.json` — the sample configuration.
