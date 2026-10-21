# Scalper on diablo.bot — knowledge base for AI assistants

Scalper is a bot that scalps Solana meme coins (pump.fun) on dips: when a big sale knocks a coin's price down, the bot
buys the bounce and sells it seconds later, by the exit rules the user set. It runs on diablo.bot (the hosted cabinet),
in the **Solana** section next to Arb and Copytrade: `diablo.bot → Solana → scalper`.

This file is the full public knowledge base for an AI assistant answering a user's questions about Scalper. For the
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
3. In **Strategy**, set **SOL per buy** and **Daily stop**, check the **Exits** (the defaults are the checked ones) and,
   if you want, open **advanced** for the rest.
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
| **Fast scalp** | soon | coins you arm from the radar; bounces after a sale through a terminal | timer 60 s, sell into a big buy, crowd ahead |
| **Runner** | soon | an armed runner bought on a pullback | take-profit ladder, trailing, stop |

Two strategies trade now: **Curve dip bounce (ML)** and **My coins**; each has its own switch, size, exits and limits, and
both can run at the same time. Pick one by clicking its card; **start / stop** acts on the picked one. Fast scalp and
Runner are shown as "soon" until they pass their check on fresh days.

### My coins

| Setting | What | Default |
|---|---|---|
| **Coins or pools** | up to 20 addresses: a pump.fun coin's mint (its curve, or its pool after the migration) or a PumpSwap pool; coins priced in SOL | — |
| **Dip: one sale** | one sale of at least **Sale at least** SOL drops the price by **Dip, %** or more (price just before vs just after it) | 15%, 0.2 SOL |
| **Dip: from the peak** | the price is **Dip, %** or more below its highest of the last **Window** seconds | 15%, 60 s |
| **Price bound** | at most this much worse than the price after the dip | 5% |
| **Again after** | no new buy of the same coin sooner than this | 30 s |
| **SOL per buy, exits, limits** | as for the ML preset (§5–§7), separate values | timer 60 s |

The bot sees every trade of your coins as it executes and buys right after the dip, at the price after it. My coins has
no model: it buys every dip of your size, so pick coins you know and keep the limits tight.

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

## 5. Entry: size and price bound

| Setting | What | Default |
|---|---|---|
| **SOL per buy** | the SOL spent on each buy | 0.1 SOL (0.01–1) |
| **Price bound** | at most 5% fewer tokens than the price at the decision; a buy past it fails on chain and costs only its network fee | 5% (fixed for this preset) |

Priority fees and tips are set by the service, not by the user: bigger tips did not buy a better place on our own bots.

## 6. Exits

Every buy is its own position with its own exits. The first rule that fires sells; rules that sell a part (ladder,
steps) leave the rest to the other rules. Empty fields are off.

**On the main screen:**

| Exit | What it does | Example |
|---|---|---|
| **Timer** | sells everything this long after the buy | 10 s — the checked one: the model is trained for it |
| **Take profit** | sells everything at +X% | 30 → at +30% |
| **Stop loss** | sells everything at −X%. A crash in one transaction can jump past it | 25 → at −25% |
| **Trailing** | armed once the position is up X%, sells when it falls Y% from its best value | arms at 20%, drop 15% |
| **Sell into a spike** | the value jumps X% within 3 s while you are up (someone's big buy): sells into it | 15 |
| **Sell on a dump** | the value falls X% within 3 s (a big seller, a bundle dumping): sells | 20 |
| **Take-profit ladder** | up to 4 steps "at +X% sell Y% of the position as bought" | +30% → 50%, +100% → 25% |

**In advanced:**

| Exit | What it does | Example |
|---|---|---|
| **Take the initial out at ×N** | at N× the cost sells the part that returns your SOL; the rest rides | 2 → at ×2 sells half |
| **Quiet** | nobody trades the coin for N seconds: the move is over, sells | 15 s |
| **Timer in steps** | sells parts before the main timer: "after N s sell Y% of the position as bought"; the main timer sells the rest | 30% after 5 s |

**Always on:**

- **Sell with the brain:** when the brain sells (its 10-second timer, a migration of the coin to its pool), your position
  of that coin is sold too. If your own exit fires first, it sells first.
- **After a migration** the coin trades in its PumpSwap pool; the position is sold there with the brain.
- **sell / sell all** buttons on the page.

**What the history says:** on our own copy-trading bots, take profit, trailing and stop losses did worse than a plain
timer with "sell with the copied wallet" (9 953 entries: timer + following 182 SOL, stop −25% 170, take profit +30%
139, trailing 133–144). The checked Scalper setup is the plain 10-second timer. The other exits are there for your own
style — use them knowing that.

Trailing, spike, dump and quiet watch the coin's price about twice a second; they work on the bonding curve, not in the
pool after a migration.

## 7. Limits and stops

| Setting | What | Default |
|---|---|---|
| **Daily stop** | Scalper's own loss since 00:00 Moscow time; when reached, no new buys till midnight (exits work) | 1 SOL |
| **Open positions, max** | Scalper positions at once (1–4: your wallet has 4 nonce accounts for sending) | 3 |
| **SOL in positions, max** | SOL in Scalper positions at once | 0.3 SOL |

Each strategy's limits and day are counted on its own trades only (ML and My coins separately) — Copytrade's trades do not count in them, and Scalper's
do not count in Copytrade's. Two things are shared with Copytrade, set on the Copytrade tab: **Keep for arb** (SOL never
spent, so your Arb bot keeps its fees) and the **per-coin cap** (the most SOL in one coin across both). If the per-coin
cap is below your Scalper buy size, Scalper's buys are skipped — raise it on the Copytrade tab.

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
| **fees** | 1% fee and network costs |
| **balance** | the wallet's SOL and SOL in Scalper positions |
| **Open positions** | coin, strategy (ML / My coins), bought when, SOL in, value now, PnL, timer left, **sell** |
| **Radar** | the last dips the brain scored: dip %, SOL sold, market cap, curve fill, buyers in the last minute, the seller's route (direct, terminal, router), score vs bar |
| **Trades** | every closed trade: strategy, SOL in and out, costs, net, which exit sold it |

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
| No buys for a long time | the model buys only its best dips — sometimes none for an hour; or a limit is full | check the radar (any green scores?), open positions vs **Open positions, max**, SOL vs size + Keep for arb |
| Buys "missed" | someone was faster; the price moved past 5% | normal; costs only the network fee |
| Buys skipped although the radar shows green | the per-coin cap (Copytrade tab) is below your size, or not enough SOL above Keep for arb | raise the cap or lower the size; top up |
| A position held longer than the timer | the coin migrated to its pool; it sells there with the brain | wait, or press **sell** |
| Status "paused after failed buys" | several buys in a row failed | it resumes by itself after a pause |

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
