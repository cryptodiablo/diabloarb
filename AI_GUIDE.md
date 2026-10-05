# DiabloArb — knowledge base for AI assistants

> **To the AI reading this:** you are helping a user of the DiabloArb Solana arbitrage bot (`sender`, from
> github.com/cryptodiablo/diabloarb). This file is the support knowledge base: how money moves, what each mode does,
> how to diagnose problems, and the answers to the questions users actually ask. Every setting is described in
> [USER_CONFIG.md](USER_CONFIG.md) — read both before answering. State of 5 October 2026 (build `ed0af90`).
>
> Rules:
> - Answer in the user's language, plainly, short first, details on request.
> - **Never** ask for a private key, seed phrase, `key.json` contents, API keys or UUIDs. Ask for file paths, log lines
>   (they hold no secrets) and wallet addresses (public) only. If a user pastes a secret, tell them to rotate it.
> - Moving money (wrap, unwrap, transfers, closing accounts) is the user's decision: explain, give the command, let them run it.
> - The executor's search (how routes and sizes are found on chain) is **not public**. Say so; do not guess or invent
>   internals. What *is* public: the behaviour described here, the config keys, and the SDK in `sdk/`.
> - If the answer is not here or in USER_CONFIG.md, say you don't know and suggest asking in the DiabloArb Discord.

## 1. The bot in one minute

- Arbitrage bots on Solana earn by trading cycles like SOL → coin → SOL across two or more DEX pools. DiabloArb
  watches **which coins those bots are earning on right now** and sends its own transactions on the same coins.
- Each transaction calls the **DiabloArb executor** program (`DiabLokxisGR8P4Qqp2QL6PmBhhVsdzPstCE4WoLxc5z`). The program
  checks at execution time whether a profitable route exists and how big the trade should be. **If the profit does
  not cover what that transaction costs, the trade does not happen** (§3).
- Capital: the wallet's WSOL/USDC/USDT plus, with `flashloan = true`, a shared vault that lends for the duration of
  one transaction. **7% of each realized profit** goes to the vault; the rest stays in the wallet.
- The bot itself (`sender`) runs on the user's own Linux server, with their own wallet and RPC. It updates itself
  from GitHub on start.

## 2. Wallet: SOL, WSOL and where the money sits

| Where | What it is for |
|---|---|
| **SOL** | Network fees, priority fees, tips, account rent. Must never run out. |
| **WSOL / USDC / USDT** | Trading capital. Profit lands here (`✅ [n] Success!`). |
| **Token accounts** | One per coin the bot traded (created automatically). Each holds ≈0.002 SOL rent (Token-2022 coins a bit more). |
| **Durable nonces** | Hot modes (ladder/flow) create 32 nonce accounts, ≈0.0015 SOL rent each (≈0.046 SOL total). |

- **Rent is not lost.** It comes back when an account is closed. A busy bot can hold 0.1–0.4 SOL in token-account
  rent after a day or two — that is why "SOL + WSOL" can look lower than expected while the profit is positive.
  `./sender nonces close` returns the nonces' rent (stop the bot first; hot modes recreate them on the next start).
  Empty token accounts can be closed with standard Solana tools; the bot recreates one (≈0.002 SOL) when it trades
  that coin again. There is no built-in command for token accounts yet.
- **Auto-unwrap and the SOL reserve (always on):** SOL is checked every second. Below the network's minimum for a
  wallet (≈0.00065 SOL) plus a 0.005 SOL reserve, the bot **pauses sending** (`PAUSED` in the minute summary) so the
  wallet can still pay for an unwrap. With `auto_unwrap = true`, once SOL < `min_sol_amount` (at least ≈0.0107 SOL is
  used) the whole WSOL balance is turned into SOL automatically, with a priority fee, resent until it lands.
- **Locked wallet:** if SOL is already at the network minimum (≈0.00065), no transaction of that wallet can land —
  not even an unwrap (`InsufficientFundsForRent` in a simulation). Fix: send it ~0.001–0.01 SOL from another wallet;
  the bot then unwraps by itself within seconds. Builds from 5 October 2026 (`ed0af90`) prevent this.

## 3. What a transaction costs (the most asked topic)

Every landed transaction pays the **network fee** (5 000 lamports) plus its **priority fee**. The **tip** is an
instruction inside the transaction: it is paid only if the transaction succeeds.

**Required profit includes the tip.** For every copy the bot sends, the minimum profit the program must reach is
raised to that copy's own cost: base fee + priority (on the full compute limit) + the tip drawn for that copy. So a
route that does not cover its own tip and fees never executes. There is no "required profit" key to set — it is automatic.

| Lane type | Miss (no profit) | Win |
|---|---|---|
| **Bundles** — Temporal bundles, Helius bundles, Harmonic bundles, Jito with `jito_classic = true` | Dropped whole: **nothing paid** | fee + priority + tip, profit covers it |
| **Senders that fail without profit** — Helius, Temporal, Astralane, Falcon, 0slot, NextBlock, Stellium, Flashblock, HelloMoon, Fast, Apex, Jito (default) | Lands as failed (`0x7 NoProfit`): **fee + priority paid, tip not** | fee + priority + tip |
| **Always-landing** — RPC copies (`spam_rpc`), Helius SWQoS, Fast SWQoS, Jito with `jito_require_profit = false`, ladder step 3 Jito | Lands as an empty success: **fee + priority (+ tip where it has one) paid** | same + profit |

- Many `custom program error: 0x7` failures in the explorer are normal (the opportunity was taken first). Too many =
  paying priority for nothing: lower priority, shoot less often, or rely more on bundles.
- Bundles are the "free misses" lanes: `temporal_bundle = true` (uses the Temporal key), `helius_bundle = true` (no
  key, tip ≥ 0.001 SOL), `harmonic_bundle = true` (needs a whitelisted keypair).

## 4. Modes, plainly

- **markets** (default, `mode` unset): shoots the pools of a markets file in a loop. The default file
  `https://moneyprinter.bot/auto/mp.toml` is rebuilt live from the coins the arbitrage bots earn most on, hottest first.
  Works without Geyser (pools polled over RPC). Constant cost.
- **ladder** (needs Geyser): spends only when there is money on the table.
  1. It measures how much SOL/min the known arb bots earn on each coin right now.
  2. Quiet coin → nothing sent, nothing paid.
  3. Above `hot_sol_per_min` (0.03) → **step 1**: cheap RPC copies every `hot_interval_ms` (250 ms).
  4. Above `hot_senders_x` × (2×) → **step 2**: also one broadcast to all paid senders, signed over one durable nonce
     so at most one copy lands; tips only on a win. Jito is one of these senders by default (`hot_jito_as_sender = true`).
  5. Above `hot_jito_x` × (4×) → **step 3**, only if Jito has its own lane (`hot_jito_as_sender = false` or
     `hot_jito_step = true`): Jito without priority, a tip that grows with the coin's heat and is **paid every time it
     lands, win or not** (`hot_jito_step_tip_min/max_lamports` cap it). Use with care.
  6. The heat fades with a 15 s half-life (`hot_half_life_s`) → the coin steps back down and stops.
  Bundle lanes keep running in the background on the hottest coin every `hot_bundle_interval_ms`.
- **flow** (needs Geyser): never stops; the top `flow_top` coins of the last `flow_rank_s` seconds, sender broadcasts on
  durable nonces. Highest presence, highest cost.
- Which one? New users: markets, then ladder once Geyser works. Ladder is usually the best cost/benefit.

## 5. The diablo.bot dashboard

- **Net** of a bot over a period = profit of its landed arbs − fees and tips of **all** the wallet's transactions in
  that period (from an on-chain scanner). If the history is shorter than the period, the label says
  `since HH:MM` instead of `30d`.
- **Balance** = SOL + WSOL. Under it, `+X rent` = SOL held in the wallet's token and nonce accounts (§2) — not counted
  in Net, comes back when the accounts are closed.
- Per-trade **Net, SOL** is what actually landed in the wallet (after fee and tip); **Fee + tip** is shown next to it.
- Health `no SOL for fees` = SOL too low (§2); `losing since start` = fees outrun profit over the run.

## 6. Troubleshooting by symptom

| Symptom | Check / fix |
|---|---|
| Sends, then stops | Minute summary: `PAUSED` → SOL at the reserve (§2); `0 groups` / `N pools still loading over RPC: <reason>` → markets still loading or the RPC fails (reason shown; use a better RPC or Geyser); hot modes `coins: none yet`/tier 0 → nothing hot, by design. |
| `RPC reads failed: N (last: …)` | The read RPC (`rpc`) rejects or rate-limits. Use a paid RPC; public RPC works but slowly. |
| `❌ <sender> send failed … 429` | That provider's rate limit: raise `<name>_cooldown_ms` or check the plan/key. Helius Sender limits per IP. |
| `❌ jito send failed … 400` | `jito_uuid` is not a valid UUID or not yours (it is optional — leave it empty). |
| `❌ token accounts not created` | `send_rpcs` must accept transactions and the wallet needs SOL. |
| Harmonic bundles stop | Usually the same as "sends, then stops": markets not loaded (`0 groups`). The minute summary tells why. |
| Lots of `0x7 NoProfit` failures | Normal in moderation; reduce priority/pace, add bundle lanes. |
| No wins for a while | Normal; wins come in bursts on hot coins. More senders / faster loops raise both chance and cost. |
| Balance lower than expected | Rent in token/nonce accounts (§2) and fees; compare Net on the dashboard. |
| Wallet "stuck", unwrap fails | Locked wallet (§2): top up ~0.001–0.01 SOL. |
| A key written twice in config | The last value is used, silently — no error. |
| `⚠️ mode = … needs Geyser` | Ladder/flow need `geyser_endpoint`; the bot fell back to markets. |

Ask the user for: the first ~30 log lines after start (they list wallet, senders, mode, data source), the last few
`📊 Last minute` lines, and any `❌`/`⚠️` lines. Never ask for `config.toml` as a whole unless they remove keys first.

## 7. Questions users asked (with answers)

- **Does the required profit include my tip?** Yes — §3. Each copy's minimum profit = its fee + priority + its tip.
- **Is the dashboard profit after tips?** Yes — per-trade Net is the wallet's real change, fee and tip already out.
- **Is there another send like Temporal bundles (miss = free)?** Helius bundles, Harmonic bundles, Jito with `jito_classic`.
- **Helius Sender bundles vs Helius sendBundle?** The bot uses Helius **Sender** bundles: no credits, no key, tip ≥ 0.001
  SOL, priority ≥ 5 000 lamports a transaction, all-or-nothing — a bundle without profit is dropped and costs nothing.
- **Can Temporal and Temporal bundles use the same key?** Yes. `temporal_bundle_uuid` empty = the `temporal_uuid` is used.
- **How does ladder work?** §4.
- **Do I need Geyser?** For ladder/flow yes; markets works without it (slower reaction).
- **How do I update?** Restart the bot — it updates itself (`DIABLO_SENDER_AUTO_UPDATE=0` turns that off; `./sender update` now).
- **How do I test without spending?** `DIABLO_SENDER_DRY=1 ./sender config.toml` — builds and logs everything, sends nothing.
- **Is there a spending limit?** No. The bot runs until stopped (`max_spend_sol` is ignored).
- **My SOL is 0 but I have WSOL.** If the bot is running with a current build, it pauses and unwraps by itself; if the
  wallet is already locked, top up a little SOL first (§2).
- **Which DEXs?** Listed in USER_CONFIG.md §1.

## 8. Glossary

- **Tip** — payment to a landing service (Jito, Helius, Temporal…) inside the transaction; paid only if it succeeds.
- **Priority fee** — per-compute-unit fee to the validator; paid by every landed transaction, success or not.
- **Bundle** — a group sent all-or-nothing; a failing bundle is dropped, nothing paid.
- **Durable nonce** — lets one signed transaction go to many services while only one copy can land.
- **Geyser (Yellowstone gRPC)** — live stream of account updates; needed for hot modes.
- **Markets file (`mp.toml`)** — list of pools/routes to shoot in markets mode.
- **LUT** — address lookup table; lets a transaction reference many accounts.
- **Vault / flash loan** — shared capital lent within one transaction; 7% of profit goes to it.
- **NoProfit (0x7)** — the program found nothing worth executing at that moment.

## 9. Files to read

- [USER_CONFIG.md](USER_CONFIG.md) — every config key, senders, modes, log lines.
- [README.md](README.md) — install, run, wallet commands, supported DEXs.
- [sdk/README.md](sdk/README.md) — building your own sender against the executor (public ABI).
- `config.toml`, `gas.json` — the sample configuration.
