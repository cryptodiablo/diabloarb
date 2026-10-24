# Scalper on diablo.bot — knowledge base for AI assistants

Scalper is a bot that scalps Solana meme coins (pump.fun) on dips: when a big sale knocks a coin's price down, the bot
buys the bounce and sells it seconds later, by the exit rules the user set. It runs on diablo.bot (the hosted cabinet),
in the **Solana** section next to Arb and Copytrade: `diablo.bot → Solana → scalper`.

This file is the full public knowledge base for an AI assistant answering a user's questions about Scalper. Every setting
explained, with history numbers and ready setups: [SCALPER-SETTINGS.md](SCALPER-SETTINGS.md). For the
arbitrage bot read [AI_GUIDE.md](AI_GUIDE.md) and [FAQ.md](FAQ.md); for copy trading — [COPYTRADE.md](COPYTRADE.md).

**Rules for the assistant.** Never ask the user for a private key, seed phrase, key file or any API key — Scalper never
needs them from the user. Do not promise profit: Scalper makes many small, fast trades, some days lose, and a coin can
crash in one transaction (§11). Do not guess features that are not described here; say they are not available.

## Contents

1. [Scalper in one minute](#1-scalper-in-one-minute)
2. [Getting started](#2-getting-started)
3. [Strategies (presets)](#3-strategies-presets)
4. [How the ML signal works](#4-how-the-ml-signal-works)
5. [Entry: size and price bound](#5-entry-size-and-price-bound)
6. [Exits](#6-exits)
7. [Limits and stops](#7-limits-and-stops)
8. [Money: fee, network costs, rent](#8-money-fee-network-costs-rent)
9. [Your wallet, Arb and Copytrade](#9-your-wallet-arb-and-copytrade)
10. [The dashboard](#10-the-dashboard)
11. [What results to expect, and why they differ](#11-what-results-to-expect-and-why-they-differ)
12. [Troubleshooting by symptom](#12-troubleshooting-by-symptom)
13. [Questions users ask](#13-questions-users-ask)
14. [Glossary](#14-glossary)
15. [Ready profiles: how to set it up for a user's request](#15-ready-profiles-how-to-set-it-up-for-a-users-request)

## 1. Scalper in one minute

- **What it trades:** pump.fun coins on their bonding curve; after a coin migrates, its PumpSwap pool.
- **When it buys:** right after a big sale drops a coin's price by 10% or more, if the dip looks like it will bounce
  (§4). Not on hype, not on pumps.
- **How fast:** the decision is made on the sale itself, before the next ones; every user's buy is sent at once, in the
  same block as the decision.
- **How long it holds:** seconds. The checked setup sells everything 10 seconds after the buy; you can set your own
  exits (§6).
- **One brain, everyone's own wallet:** one model decides which dips to buy for everyone who has Scalper on; each user
  buys and sells from their own wallet, with their own size, limits and exits.
- **You deposit only SOL.** WSOL, token accounts and nonce accounts are managed by the bot.
- **Fee:** 1% of each buy, sent in a separate transaction after the buy (§8).

## 2. Getting started

1. Log in to diablo.bot and open **Solana → scalper**.
2. Look at the **Radar**: it shows every dip the model scores right now, and which ones it buys (green score).
3. In **Strategy**, pick a strategy card, then go through its three groups from top to bottom: **Entry** (My coins
   only), **Size & limits** and **Exits** (§5–§7). The defaults are the checked ones. Rare exits are under
   **▸ more exits**; a **?** next to a field explains it in full. Press **save** in the bar at the bottom (it lights up
   when something is not saved yet).
4. Read **How the ML signal trades** and tick **I understand how it trades…** — without it Scalper does not start.
5. Press **start**. The first start connects your wallet: Scalper uses the **same wallet as your Arb bot** — no new
   wallet, no key to enter. For a few seconds the page says the wallet is being prepared; it needs about **0.016 SOL**
   once (refundable rent, §8). If your wallet is already connected for Copytrade, nothing is paid again.
6. Keep enough SOL: your buy size × open positions, plus the reserve for Arb (§7, §9).

Scalper can be stopped at any time with **stop**; open positions still exit by their rules. **sell** on a position (or
**sell all**) sells it at once.

## 3. Strategies (presets)

| Preset | Status | What it does | Exit |
|---|---|---|---|
| **Curve dip bounce (ML)** | live | a big sale knocks a pump.fun curve down 10%+; the model scores the dip; the best ones are bought with a 5% price bound | all of it 10 s after the buy (or by your exits); after a migration — in the pool with the brain |
| **My coins** | live | your own list of coins or pools; buys when a sale drops one of them by your % (or it falls by your % from its recent high) | your exits (timer 60 s by default) |
| **Fast scalp** | not yet | coins you arm; bounces after a sale through a terminal | timer 60 s, take profit +8%, crowd ahead |
| **Runner** | not yet | an armed runner bought on a pullback from its peak | take-profit ladder, trailing, stop |

Two strategies trade now: **Curve dip bounce (ML)** and **My coins**; each has its own switch, size, exits and limits, and
both can run at the same time. Pick one by clicking its card; **start / stop** acts on the picked one.

**Why Fast scalp and Runner are "not yet".** We checked both on 7 fresh days (15–21 October 2026) with a user's real
landing and every cost: 66 versions (dip sizes, coin activity, timers, take profit, ladders, trailing, stops). **None of
them made money on any of the 7 days**: the best Fast scalp lost about 5% per trade, the best Runner about 8%. A round
trip costs about 4% (the pump.fun fee both ways, our 1%, the network), and a dip picked by a plain rule more often keeps
falling than bounces. Only the model (Curve dip bounce) picks dips that bounce often enough. They come back only as a
version that is in plus on fresh history; until then the cards stay greyed out.

### My coins — the Entry group

| Setting | What it does | When to change it | Default / example |
|---|---|---|---|
| **Coins or pools** | up to 20 addresses, one per line: a pump.fun coin's mint (traded on its curve, and in its pool after the migration) or a PumpSwap pool; coins priced in SOL. The label shows "N / 20" | add coins you follow and know | — |
| **Dip: one sale** | buys when one sale of at least **Sale at least** SOL drops the price by **Dip %** or more (price just before vs just after it) | a coin that gets single big dumps | 15%, 0.2 SOL |
| **Dip: from peak** | buys when the price is **Dip %** or more below its high of the last **Window** seconds | a coin sliding down over several trades | 15%, 60 s |
| **Price bound** | the buy pays at most this much more than the price right after the dip; past it the buy fails and costs only its network fee | raise it if many buys are missed on a fast coin; lower it to pay less | 5% |
| **Again after** | no new buy of the same coin sooner than this after the last one | raise it so one crash does not buy you in again and again | 30 s |

**Size & limits** and **Exits** of My coins work as in §5–§7, with their own values (timer 60 s by default).

The bot sees every trade of your coins as it executes and buys right after the dip, at the price after it. My coins has
no model: it buys every dip of your size. Our check on fresh history (§3) shows that buying every dip by a plain rule
loses on average — pick coins you know, keep the size small and the limits tight, and treat it as your own strategy.

## 4. How the ML signal works

- **Which coins:** pump.fun coins on their bonding curve that a known curve-trading bot bought before (a list of such
  bots is kept by us). Coins nobody serious trades are not watched.
- **The trigger:** one sale of at least ~0.2 SOL that drops the price by 10% or more.
- **The score:** a model (gradient-boosted trees) trained on weeks of such dips, retrained every few days. Its strongest
  inputs are **who the seller is** — how that wallet's earlier dumps bounced, whether it sells through a terminal or
  directly — and the flow of the coin in the last seconds and minutes. Only dips scoring above the model's bar are
  bought (the radar shows the score and the bar).
- **What it skips by itself:** coins whose creator crashed two curves in the last 6 hours; sales with no price limit
  (fake dumps); coins it cannot sell on the curve.
- **The trade:** buy with your size and a 5% price bound (a buy that would get more than 5% fewer tokens than at the
  decision is refused by the chain), sell about 10 seconds later. The model is trained for exactly that hold.
- **The same signal for everyone:** every user with Scalper on buys the same dip at the same moment. There is no queue:
  each buy goes out at once with its own price bound (§11).

## 5. Size: SOL per buy and price bound

| Setting | What it does | When to change it | Default |
|---|---|---|---|
| **SOL per buy** | the SOL spent on each buy | 0.1 is the checked size; smaller sizes pay relatively more network | 0.1 SOL (0.01–1) |
| **Price bound** (ML) | at most 5% fewer tokens than at the decision; a buy past it fails on chain and costs only its network fee | fixed for the ML strategy | 5% |

**Own priority fee and tip** (Size & limits, per strategy): **ours** — the service's fees (buy 0.0001 priority + 0.0001
tip, sale 0.00002 + 0.000005 SOL); **my own** — your values for buy and sale: route 1 (priority + tip, through the
sending services) and route 2 (priority only, through plain RPCs; empty = twice the buy's priority / the sale's
priority), up to 0.01 SOL each, at most 3% of a buy. Every transaction goes both ways; the first to land counts. They
are this strategy's own — Copytrade's fees do not apply to Scalper. On our own bots bigger tips did not buy a better
place, so "ours" is the recommended choice.

**How much SOL a buy needs.** The wallet must hold at least: SOL per buy + this strategy's **Keep for arb** + about
0.003 SOL (the coin's token account and the network) + any unpaid 1% fee + buys still in flight. Example: size 0.05 and
Keep for arb 0.05 → about 0.103 SOL. With less, signals are skipped as "not enough SOL" (§10, §12).

## 6. Exits

Every buy is its own position with its own exits. The first rule that fires sells; rules that sell a part (ladder,
steps, initial out) leave the rest to the other rules. An empty field is off. The Exits group is per strategy (ML and My
coins have their own); **trailing, spike, dump and quiet are shared by both strategies**.

**The two rows of the Exits group:**

| Exit | What it does | When to turn it on | Example |
|---|---|---|---|
| **Timer** | sells everything this long after the buy | always on; for ML keep 10 s — the model is trained for it | ML 10 s, My coins 60 s |
| **Take profit** | sells everything at +X% | you want to lock a quick gain before the timer | 30 → all at +30% |
| **Stop loss** | sells everything at −X%. A crash in one transaction can jump past it | with long timers, to cap a slow bleed | 25 → all at −25% |
| **Sell on a dump** | the price falls X% within 3 s (a big seller, a bundle dumping): sells all | coins with dev or bundle dumps | 20 |
| **Trailing arms at** | the trailing starts once the position is up X% | with long timers, to ride a runner | 20 → once +20%… |
| **Trailing drop** | …then sells all when the price falls Y% from its best | together with "arms at" | 15 → 15% off the best |
| **Sell into a spike** | while you are up, the price jumps X% within 3 s (someone's big buy): sells into it | to sell into big buyers instead of waiting | 15 |
| **Initial out at ×N** | at N× the cost sells the part that returns your SOL; the rest rides the other rules | for holding a runner "for free" | 2 → at ×2 sell half |

**Under ▸ more exits:**

| Exit | What it does | When to turn it on | Example |
|---|---|---|---|
| **Quiet for** | nobody trades the coin for N seconds: the move is over, sells | long timers on thin coins | 15 s |
| **Take-profit ladder** | up to 4 steps "at +X% sell Y% of the position as bought" | to sell a runner in parts | +30% → 50%, +100% → 25% |
| **Timer in steps** | sells parts before the main timer: "after N s sell Y% of the position as bought"; the main timer sells the rest | to take part of the bounce early | 30% after 5 s |
| **Sell with the brain** (ML, always on) | when the brain sells (its timer, a migration), your position of that coin sells too | — | — |

**Always on:**

- **Sell with the brain:** when the brain sells (its 10-second timer, a migration of the coin to its pool), your position
  of that coin is sold too. If your own exit fires first, it sells first.
- **After a migration** the coin trades in its PumpSwap pool; the position is sold there with the brain.
- **sell / sell all** buttons on the page.

**What the history says** (also behind the **?** next to the Exits heading): on our own copy-trading bots, take profit, trailing and stop losses did worse than a plain
timer with "sell with the copied wallet" (9 953 entries: timer + following 182 SOL, stop −25% 170, take profit +30%
139, trailing 133–144). The checked Scalper setup is the plain 10-second timer. The other exits are there for your own
style — use them knowing that.

Trailing, spike, dump and quiet watch the coin's price about twice a second; they work on the bonding curve, not in the
pool after a migration.

## 7. Limits and stops

These are in the **Size & limits** group, next to SOL per buy, for each strategy.

| Setting | What it does | When to change it | Default |
|---|---|---|---|
| **Daily stop** | Scalper's own loss since 00:00 Moscow time; when reached, no new buys till midnight (exits work) | set it to what you accept to lose in a day | 1 SOL |
| **Open positions** | Scalper positions at once (1–4: your wallet has 4 nonce accounts for sending) | lower it to spread less; at 3 a fourth dip at the same moment is skipped | 3 |
| **SOL in positions** | SOL in Scalper positions at once | keep it ≥ SOL per buy × open positions | 0.3 SOL (= 3 × 0.1) |
| **Keep for arb** | this strategy never spends the wallet's SOL below this, so your Arb bot keeps its fees; never touches WSOL | set it to what Arb needs | your Copytrade value at the split (23.10), else 0.05 SOL |
| **Per coin, max** | the most SOL this strategy keeps in one coin; empty = no cap | keep it above SOL per buy, or every buy is skipped | your Copytrade value at the split (23.10) |

Every setting of Scalper is its own — **nothing is shared with Copytrade any more** (since 23 October 2026): size,
limits, Keep for arb, per-coin cap, fees, exits, the daily stop, start/stop. Each strategy's limits and day count only
its own trades (ML and My coins separately).

**The pause after failed buys is per mode:** 10 failed buys in a row pause new buys of that mode for 10 minutes; then
they resume by themselves. Copytrade's failures do not pause Scalper, and Scalper's do not pause Copytrade.

## 8. Money: fee, network costs, rent

| Cost | How much | Notes |
|---|---|---|
| **Service fee** | **1% of each buy** | a separate small transaction after the buy; several are batched. No fee on sales, no subscription |
| **Network** | Solana fee + priority fee + tips of each transaction | on every buy and sale; small sizes pay relatively more |
| **Failed buy** | its network fee only | a buy that missed its 5% bound (someone was faster) |
| **pump.fun fee** | about 1.25% each way on the curve, ~1.2% in pools | inside the price |
| **Rent** | ~0.016 SOL once (+~0.007 SOL lookup table) | nonce and token accounts; it is a deposit, returned when the accounts are closed; shared with Copytrade |

**Net** on the page = what came back − what went in − 1% fee − network. A 10-second round trip pays the pump.fun fee
twice (≈2.5%) plus the network: the bounce must be bigger than that to win.

## 9. Your wallet, Arb and Copytrade

- Scalper trades from **your diablo.bot wallet — the same one as your Arb bot**. No new wallet, no key to enter.
- **Arb is safe:** Scalper spends SOL only, never touches the wallet's WSOL (Arb's capital) and keeps the **Keep for
  arb** reserve.
- **Scalper never sells tokens it did not buy.** Positions of Scalper, Copytrade and your own trades are kept apart:
  each mode sells only its own positions, even when both hold the same coin.
- Scalper and Copytrade can run at the same time; their limits and daily stops are separate (§7).
- To withdraw, use the wallet section of the cabinet as for Arb; stop Scalper first if you withdraw everything.

## 10. The dashboard

| Part | What it shows |
|---|---|
| **Status** | scalping / stopped / daily stop / paused after failed buys / not started yet; the brain's state (live / warming up / offline) |
| **net · today, MSK** | Scalper's result since 00:00 Moscow time |
| **net · period** | the result for 1h / 24h / 7d / 30d, trades and wins |
| **signals** | buys made, buys missed by the price bound, open positions |
| **Signals the bot skipped** | a line above the numbers when signals were skipped in the period, with the count per reason — see the table below |
| **fees** | 1% fee and network costs |
| **balance** | the wallet's SOL and SOL in Scalper positions |
| **Open positions** | coin, strategy (ML / My coins), bought when, SOL in, value now, PnL, timer left, **sell** |
| **Radar** | the last dips the brain scored: dip %, SOL sold, market cap, curve fill, buyers in the last minute, the seller's route (direct, terminal, router), score vs bar |
| **Trades** | every closed trade: strategy, SOL in and out, costs, net, which exit sold it |

**Skip reasons** (the line "Signals the bot skipped"):

| Reason on the page | What it means | What to do |
|---|---|---|
| not enough SOL | the wallet has less than size + Keep for arb + ≈0.003 SOL (§5) | top up, lower the size or Keep for arb |
| our market data feed was down for a while | the bot did not see the coin's market; nothing was bought | nothing; it is on our side |
| your open positions limit was full | **Open positions** reached | wait, or raise the limit |
| your "in positions" limit was full | **SOL in positions** reached | raise it to ≥ size × open positions |
| your per-coin limit was full | **Per coin, max** is below the size | raise it in Size & limits |
| already holding this coin | a position of this coin is open | nothing |
| your daily stop was hit | the day's loss reached **Daily stop** | wait for 00:00 MSK or raise it |
| service fee unpaid | the 1% fee could not be paid (no SOL) | top up |
| the bot was stopped / the strategy was off | Scalper or that strategy is stopped | press **start** |
| paused after failed buys | several buys in a row failed | it resumes by itself |
| Solana network pause | the network had a pause | nothing |
| CopyTrade already holds this coin | Copytrade has an open position of the coin | nothing; modes do not mix |
| the coin was migrating | the curve was completing | nothing |

## 11. What results to expect, and why they differ

- **Many small trades.** The edge per trade is small next to the fees (§8). Some days lose. Start small.
- **Same signal, different results:** every user buys the same dip at the same moment, one after another in the same
  block. Each buy moves the price up a little, so later buys get a slightly worse price; when many users buy one fresh
  coin, the last ones may miss the 5% bound (the buy fails and costs only its network fee).
- **Size matters:** network costs are about the same for 0.01 and 1 SOL, so tiny sizes pay relatively more.
- **The brain trades on paper:** its decisions are the same for everyone; your result is your own fills, exits and costs.
- **Crashes:** a curve can lose most of its value in one transaction; a stop loss cannot sell at a price that was never
  traded. The 10-second timer limits the time at risk; it does not remove the risk.

## 12. Troubleshooting by symptom

| Symptom | Why | What to do |
|---|---|---|
| **start** says to tick «I understand» | the ML option is not acknowledged | read the card and tick it |
| "Your wallet is not ready" / "being prepared" | the first connection creates accounts (~0.016 SOL) | top up the wallet with SOL; it retries by itself |
| Status "daily stop" | Scalper lost the daily stop since 00:00 MSK | new buys resume at midnight Moscow time, or raise the stop |
| No buys for a long time | the model buys only its best dips — sometimes none for an hour; or a limit is full; or SOL is short | read the line **Signals the bot skipped** (§10); check the radar (any green scores?) |
| "I changed settings, it does not start" | settings are saved only with **save** in the bottom bar; and a signal must come | press **save** (the bar says "all saved"), then **start**; signals come every 10–30 min on average |
| Buys "missed" | someone was faster; the price moved past 5% | normal; costs only the network fee |
| Buys skipped although the radar shows green | **Per coin, max** is below your size, or not enough SOL above Keep for arb | raise it or lower the size; top up |
| A position held longer than the timer | the coin migrated to its pool; it sells there with the brain | wait, or press **sell** |
| Status "paused after failed buys" | 10 buys in a row of this mode failed | it resumes by itself after 10 minutes |

## 13. Questions users ask

**Is it automatic?** Yes, like the Arb bot: set it up, press start, it trades by itself until you stop it.

**Do I choose the coins?** For the ML preset, no — the model picks the dips. For your own coins use **My coins** (§3):
add up to 20 coins or pools, the dip % and your exits.

**Will Scalper use my Arb's WSOL?** No. It spends SOL only and keeps the **Keep for arb** reserve.

**Can Scalper sell my other tokens?** No. It sells only the positions it bought.

**Can I run Copytrade and Scalper together?** Yes, on the same wallet; their positions, limits and days are separate.

**What does it cost?** 1% of each buy plus the network costs of each transaction. No subscription, no fee on sales.

**Why 10 seconds?** The model is trained on what a dip does in the next 10 seconds; that hold is the one checked on our
own trading.

**Why did my result differ from my friend's?** Different sizes, exits and limits; the order of buys in the same block;
a missed price bound (§11).

**Is my key safe?** You never give a key. Scalper uses the wallet the cabinet already keeps for your Arb bot; the key never
reaches the browser or any log.

**How do I stop?** Press **stop**. Open positions still sell by their exits; **sell all** sells them at once.

## 14. Glossary

- **Bonding curve** — pump.fun's built-in market for a new coin, before it "migrates" to a PumpSwap pool.
- **Migration** — the moment a coin's curve fills and its trading moves to a PumpSwap pool.
- **Dip** — for the ML preset, a single sale that drops the price by 10% or more; for My coins, your own % (one sale, or
  from the recent high).
- **Brain** — the one model that decides which dips to buy, for everyone with Scalper on.
- **Price bound (slippage)** — the worst price you accept; past it the buy fails on chain.
- **Position** — one buy and its exits.
- **Nonce account** — a small account that lets the bot send a transaction to several routes at once safely.
- **Moscow day** — days, daily stops and daily results start at 00:00 Moscow time (UTC+3).

## 15. Ready profiles: how to set it up for a user's request

When a user asks "set up Scalper for me — safely / optimally / for maximum profit / for my 0.5 SOL", use these profiles.
Give the exact values field by field, say why, and say what the user risks. **Never promise profit**: the only checked
setup is the ML strategy with a 10-second timer; everything else is the user's own style.

**First ask (or read from the page):** how much SOL is in the wallet; whether the Arb bot runs on it and what **Keep for
arb** is (Size & limits); whether Copytrade also trades on it (its positions use the same SOL); how much the user accepts
to lose in a day.

### The profiles (ML strategy — "Curve dip bounce")

| Field | Safe | Optimal (the checked one) | Higher risk |
|---|---|---|---|
| **SOL per buy** | 0.05 | 0.1 | 0.25–0.5 |
| **Daily stop** | 0.3 | 1 | 2–3 |
| **Open positions** | 2 | 3 | 4 |
| **SOL in positions** | 0.1 | 0.3 | size × 4 |
| **Timer** | 10 s | 10 s | 10 s |
| **Take profit / Stop loss / Trailing / Spike / Dump** | off | off | off |
| **Initial out, more exits** | off | off | off |
| **Wallet SOL needed** (beyond Keep for arb) | ≥ 0.15 | ≥ 0.4 | ≥ size × 4 + 0.05 |

- **Why the timer stays 10 s and other exits stay off in every profile:** the model is trained for a 10-second hold, and
  on our own bots take profit, trailing and stops did worse than a plain timer (§6). Changing exits does not make the
  strategy "more profitable" — it changes it into an unchecked one.
- **Safe:** small size and a tight daily stop; fewer positions at once. Risk: small; the network costs weigh more at
  0.05, so the result per trade is a little worse than at 0.1.
- **Optimal:** the setup we checked; 1 SOL daily stop. Risk: some days lose up to the stop.
- **Higher risk — what "maximum profit" really means:** there is no setting that makes the edge bigger; only the size
  makes both wins and losses bigger. Above ~0.25 SOL your own buy moves a fresh curve more, so fills get worse and more
  buys miss the 5% bound; a curve can crash in one transaction and take a bigger sum with it. Suggest it only to users
  who accept losing the daily stop on a bad day.

### By wallet size (ML, with Keep for arb set separately)

| SOL free for Scalper | SOL per buy | Open positions | SOL in positions | Daily stop |
|---|---|---|---|---|
| 0.1–0.2 | 0.03 | 1 | 0.03 | 0.1 |
| 0.2–0.5 | 0.05 | 2 | 0.1 | 0.3 |
| 0.5–2 | 0.1 | 3 | 0.3 | 1 |
| 2–5 | 0.2 | 3 | 0.6 | 1.5 |
| 5+ | 0.3 | 4 | 1.2 | 2–3 |

"Free" = wallet SOL − Keep for arb − SOL that Copytrade keeps in its positions. Each buy also needs ≈0.003 SOL (§5).
Below ~0.1 SOL free, Scalper will mostly skip signals as "not enough SOL" — tell the user to top up first.

### My coins (the user's own strategy)

My coins buys every dip of the user's size by a plain rule; on fresh history such rules lost on average (§3). Set it
up only for a user who asks for it and knows their coins, and say so plainly.

| Field | Careful setup | Why |
|---|---|---|
| **Coins** | 1–5 coins the user follows, priced in SOL | fewer coins = fewer bad dips |
| **Dip** | one sale, 20%, sale at least 0.5 SOL | only real dumps, not noise |
| **Price bound** | 5% | the same as the checked ML |
| **Again after** | 300 s | one crash does not buy in again and again |
| **SOL per buy** | 0.02–0.05 | it is unchecked — keep it small |
| **Daily stop / Open positions / SOL in positions** | 0.2 / 1 / = size | one position at a time |
| **Timer** | 30–60 s | a bounce lasts seconds |
| **Stop loss / Sell on a dump** | 25% / 20% | a coin that keeps falling is cut |

### Copytrade and Scalper together

Both use one wallet, but every setting is separate: Scalper's **Keep for arb**, **Per coin, max** and fees are set in its
Size & limits, Copytrade's on its own tab. Keep Scalper's Per coin above its SOL per buy, set Keep for arb in both if Arb
runs, and leave enough SOL for both (Copytrade's size × its max positions + Scalper's). The pause after 10 failed buys
is per mode (§7). For Copytrade's own profiles see [COPYTRADE.md](COPYTRADE.md).

### After the values are set

Tell the user to press **save** in the bottom bar (it says "all saved" when done), tick «I understand…» for the ML card,
and press **start**. Signals come every 10–30 minutes on average; the line **Signals the bot skipped** (§10) tells why a
signal was not bought.
