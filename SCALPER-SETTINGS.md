# Scalper settings — every switch explained (for users and their AI assistants)

This file explains **every setting of Scalper on diablo.bot** (`diablo.bot → Solana → scalper`): what it does, how it
changes risk and profit, and what to choose. Give it, together with [SCALPER.md](SCALPER.md), to Claude, Codex or any
other assistant and ask it to set Scalper up for you — it has everything it needs.

**Rules for the assistant.** Never ask for a private key, seed phrase or API key — Scalper never needs them. Never
promise profit: Scalper makes many small, fast trades and some days lose. The history numbers below are from a short
period (21–25 October 2026, 5 days) and are **higher than what to expect** — use them to compare settings with each
other, not as a forecast. The page shows each style card's fresh numbers, counted again every day (§2).

## Contents

1. [Why the entry switches exist](#1-why-the-entry-switches-exist)
2. [Style cards (Curve dip bounce, ML)](#2-style-cards-curve-dip-bounce-ml)
   - [2a. Your own entry (advanced, optional)](#2a-your-own-entry-advanced-optional)
3. [The cards on history](#3-the-cards-on-history)
4. [Size & limits](#4-size--limits)
5. [Exits](#5-exits)
6. [My coins (your own coins)](#6-my-coins-your-own-coins)
7. [Ready setups](#7-ready-setups)
8. [How to read "Signals the bot skipped"](#8-how-to-read-signals-the-bot-skipped)
9. [Export and import settings](#9-export-and-import-settings)

## 1. Why the entry switches exist

One model picks the dips for everyone. If everybody buys the same dip, each buy moves the price up a little and the
later buyers get a worse price: on history one dip holds about **0.5 SOL of our users' buys** before the profit per
trade starts to melt (10 users × 0.1 SOL → about +0.5% per trade, 20 users → a loss).

So Scalper gives you **a choice of style cards**, each buying a different part of the model's dips, plus **your own
entry** for anything else. Users on different cards buy different coins and do not crowd each other — which keeps the
edge for everyone. Every card shows how many users are on it now and how many of their buys missed in the last 24 hours:
a card with fewer users is less crowded.

## 2. Style cards (Curve dip bounce, ML)

The model only proposes dips it expects to bounce. A style card picks which of them you buy and how long you hold; it
never adds dips the model rejected. Click a card to pick it, then **save**. The card you are on is lit and marked
**yours**.

| Card | What it buys | Sells | Same as |
|---|---|---|---|
| **Standard** (default) | every dip the model passes | 10 s after the buy, or with the brain | the old *Balanced* |
| **Calm** | only the model's strongest dips (score at least 1.5× its bar) | 10 s, or with the brain | the old *Calm* |
| **Hold 30 s** | every dip the model passes | **30 s** after the buy, not with the brain (bigger swings both ways) | the old *Bold* |
| **Deep dumps** | only dips where the sale took the price down **15%+** | 10 s, or with the brain | — |
| **Deep dumps, hold 30 s** | only dips of **15%+** | **30 s** after the buy, not with the brain | — |
| **Mid curve, deep** | coins whose curve is **25–75% full**, dips **15%+** | 10 s, or with the brain | — |
| **New coins** | coins whose curve is **under 25% full** | 10 s, or with the brain | — |
| **Your own** | anything else: your own entry (§2a) or your own exits (a take profit, a stop, another timer…) | by your exits | — |

Users who had picked Calm, Balanced or Bold stayed on the same setup: it is now shown as Calm, Standard or Hold 30 s.

**What a card shows.** Its result on our recorded market of the last 7 days (now 21–25 October 2026): the average per
trade, about how many trades a day, and about how much SOL a day one user of 0.1 SOL would have made — for one user
buying one block after the dip, after the pump.fun fee, our 1% and the network. The bars are its days (green — a day in
plus, red — in minus). These numbers are counted again once a day. Under them: how many users are on the card now and
what share of their buys missed in the last 24 hours (refreshed every 5 minutes) — many users on one card buy the same
dips and miss more.

**Grey (paused) cards.** A card whose last 2 days on history are both in minus turns grey and cannot be picked until it
is in plus again. Users already on it are not moved: the page warns them, and they can pick another card.

**What picking a card resets.** A card sets its own entry, its timer and "sell with the brain"; it clears the take
profit, the stop loss, initial out, the take-profit ladder, the timer steps and every field of your own entry (smart
money too). The fast exits (trailing, spike, dump, quiet) stay as they were. Changing any of the cleared fields
afterwards makes the setup **Your own**.

How to choose: **Standard** if unsure; **Calm** for a small wallet or fewer trades; **Deep dumps** or **Mid curve,
deep** for fewer but better dips on history; **Deep dumps, hold 30 s** — the best on history so
far (all 5 days in plus), with the bigger swings of a 30 s hold; **New coins** for the youngest coins (few trades, wild days); **Hold 30 s**
if you accept bigger swings for a bigger average — and keep a daily stop. Prefer a card that is not crowded.

## 2a. Your own entry (advanced, optional)

Under the cards, **▸ your own entry** opens more choices, in groups: **Coins and dip**, **The model**, **The dip**, **The coin** and **Smart money**. It opens by itself when your setup is **Your own**. They are **off until you fill them**: an empty field
changes nothing, and a user who never opens the block trades exactly as before. Each filled field narrows the model's
dips to your taste, so users with different choices buy **different coins** instead of crowding the same dip (when 15+
users buy one dip at once, the first buys move the price and the rest are "missed").

| Setting | What it does | Works with the switches |
|---|---|---|
| **Strictness** (× bar) | buy only dips the model scores at least this many times its own bar: 1 = every dip it passes, 1.5 = Calm, 2–3 = only its surest dips | while set, the setup is Your own; picking a card clears it |
| **Dip from** (%) | the sale took the price down at least this much | replaces Dip size while set; a Dip size button or a card clears it |
| **Dip up to** (%) | at most this much — very deep dips are often a rug or a dead coin | with either Dip size |
| **Sale at least** (SOL) | only dips made by a sale at least this big (a big holder dumping) | with everything |
| **Curve filled from / up to** (%) | how full the bonding curve is: 0% just launched, 100% about to move to a pool — a finer version of Which coins | both apply: a coin must pass Which coins and the range |
| **Coin age from / up to** (min) | minutes since the coin launched | with everything |
| **Smart money** — only coins top traders just bought | off · top 24h · top week · top month: our lists of the most profitable traders of every terminal (Axiom, FOMO, GMGN, Jupiter, Photon, Pump App, Terminal, Telegram bots — about 240 wallets) by their realized profit of that period (24h refreshed hourly, week and month daily). On: a dip is bought only if one of them bought the coin on its curve within **Bought within** minutes (60 if empty) | with everything |

A signal the model sends without one of these figures passes that check (it never blocks a buy by itself).
There is no «enter later» choice on purpose: on history a buy one block after the dip earns about 0.25% less per
trade — the edge is in being first after the dumping sale.
The figures of these ranges are **not checked on history yet** — try one change, compare a day or two on the Stats
card, and keep what works for you. Fewer dips means fewer trades: keep **SOL per buy** and the **Daily stop** as before.

### Coins and dip: Which coins

A pump.fun coin trades on its *bonding curve* until the curve fills and the coin "graduates" (migrates) to a pool.
How full the curve is says how grown the coin is. You can tick one or several:

| Choice | Coins | On history (Standard, 10%+ dips, 21–23 Oct) |
|---|---|---|
| **New** | curve less than 25% full: the youngest, wildest coins | ~15 dips/day, ≈ +10.7% |
| **Growing** | curve 25–75% full: most of the dips are here | ~115 dips/day, ≈ +1.4% |
| **Close to graduating** | curve 75%+ full: about to move to a pool | ~11 dips/day, ≈ +5.1% |

All three ticked = every coin (default). Ticking only Growing with Only deep is the **Mid curve, deep** card, only New — the **New coins** card, Only deep alone — **Deep dumps**. Ticking only New or only Close to graduating gives fewer trades, each better on
history, and puts you on different coins than most users.

### Coins and dip: Dip size

| Choice | What | On history (Standard, all coins, 21–23 Oct) |
|---|---|---|
| **Any 10%+** (default) | every dip the model passes (one sale took the price down 10% or more) | ~141 dips/day, ≈ +2.7% |
| **Only deep 15%+** | only dips where the sale took the price down 15% or more | ~65 dips/day, ≈ +7.8% |

Deep dips bounced more on history; there are about half as many.

**Example setups** (fill only the fields named; the rest stay empty):

| Idea | Fields |
|---|---|
| Young coins, real dumps | Curve filled up to 25 · Coin age up to 15 · Dip from 20 |
| Whale exits only | Sale at least 5 · Dip from 15 |
| Mid-curve, no crashes | Curve filled from 25 up to 60 · Dip from 12 up to 35 |
| The model's surest dips | Strictness 2 |
| First hour of a coin | Coin age up to 60 |
| Older, steadier coins | Coin age from 30 · Curve filled from 50 |
| With today's best traders | Smart money: top 24h · Bought within 15 |
| With steady earners | Smart money: top week · Bought within 60 |

## 3. The cards on history

1 user, 0.1 SOL per buy, buying one block after the dip, with a 5% price bound; every cost included (the pump.fun fee
both ways, our 1%, the network), 21–25 October 2026. "SOL/day" is what one user on that card would have made per day —
it grows with the number of trades, so a card with a high % but few trades can still make less in total. The page shows
the same figures, counted again every day.

| Card | Trades/day | Per trade | SOL/day | Days in plus | Worst day |
|---|---|---|---|---|---|
| Standard | 103 | +1.2% | +0.12 | 3 of 5 | −7.1% |
| Calm | 49 | +1.5% | +0.07 | 3 of 5 | −7.8% |
| Hold 30 s | 103 | +3.3% | +0.34 | 3 of 5 | −7.4% |
| Deep dumps | 48 | +5.5% | +0.26 | 4 of 5 | −1.0% |
| Deep dumps, hold 30 s | 48 | +9.8% | +0.47 | 5 of 5 | — |
| Mid curve, deep | 37 | +4.6% | +0.17 | 4 of 5 | −0.1% |
| New coins | 14 | +5.3% | +0.07 | 3 of 5 | −16.8% |

Why real results are lower: live, some buys miss because other users and market bots buy the same bounce first (a
missed buy costs only its network fee, ~0.0001 SOL) — the more users on one card, the more misses; and 5 days is a
short period. Earlier figures for 21–23 October only were higher; they are replaced by these.

## 4. Size & limits

The page groups them as **Size and risk**, **Wallet and price** and **Fees**.

Each strategy (ML and My coins) has its own values; nothing is shared with Copytrade.

| Setting | What it does | Risk / profit | Recommended |
|---|---|---|---|
| **SOL per buy** | SOL spent on each buy | profit and loss per trade grow with it; above ~0.25 SOL your own buy moves the price and more buys miss | 0.1 (checked); 0.05 for a small wallet |
| **Daily stop** | Scalper's loss since 00:00 Moscow time after which new buys stop till midnight (open positions still sell) | your worst day | 10× SOL per buy (1 SOL at 0.1) |
| **Open positions** | positions at once (1–4) | more = more trades at busy moments, more SOL at risk at once | 3 |
| **SOL in positions** | the most SOL in open positions at once | keep it = SOL per buy × Open positions, or some dips are skipped | 0.3 at 0.1 × 3 |
| **Keep for arb** | SOL this strategy never spends, so your Arb bot keeps its fees | none | what Arb needs; 0.05 if unsure |
| **Per coin, max** | the most SOL in one coin; empty = no cap | below SOL per buy every buy is skipped | empty, or ≥ SOL per buy |
| **Own priority fee and tip** | **ours** = the service's fees; **my own** = your priority and tip for buys and sales | higher fees cost on every trade; on our bots they did not land buys more often | **ours** |
| **Buy price bound** | the most a buy may pay above the price at the signal; past it the buy fails (missed) and costs only its network fee | wider: fewer missed when many buy the same dip, but a worse price | 5% (ours) |

How much SOL the wallet needs: SOL per buy × Open positions + Keep for arb + about 0.003 SOL per buy (token account and
network). Example: 0.1 × 3 + 0.05 + 0.01 ≈ 0.36 SOL.

## 5. Exits

The page groups them as **Main** (timer, take profit, stop loss, sale price bound) and **Fast moves** (dump, trailing, spike, initial out); **more exits** opens the rest.

Every buy sells by the first exit rule that fires; an empty field is off. The **style card** sets the main timer (10 s,
or 30 s for Hold 30 s); the other fields make the setup **Your own**. On our bots take profit, trailing and stops did worse than a plain
timer, so the checked setup leaves them off.

| Exit | What it does | When to turn it on | Example |
|---|---|---|---|
| **Timer** | sells everything this long after the buy | always; set by the card. Type your own seconds (from 1) to sell by your timer instead of with the model — e.g. when two of your bots sell in the same block; picking a card brings its 10 s / 30 s back | 10 s / 30 s, or yours |
| **Take profit** | sells everything at +X% | to lock a quick gain | 30 |
| **Stop loss** | sells everything at −X% (a crash in one transaction can jump past it) | with Hold 30 s or long timers | 25 |
| **Sell on a dump** | the price falls X% within 3 s (a big seller): sells | coins with dev or bundle dumps | 20 |
| **Trailing arms at / drop** | once up X%, sells when the price falls Y% from its best | to ride a runner with a long timer | 20 / 15 |
| **Sell into a spike** | while up, the price jumps X% within 3 s (a big buy): sells into it | to sell into big buyers | 15 |
| **Sale price bound** | the most a sale may take below the price seen; past it the sale fails and is tried again | tighter can leave a falling coin unsold longer | 25% (ours) |
| **Initial out at ×N** | at N× the cost sells the part that returns your SOL | to hold a runner "for free" | 2 |
| **More exits** | quiet (no trades for N s), take-profit ladder, timer in steps | your own style | — |

## 6. My coins (your own coins)

Your own list of up to 20 coins or pools; the bot buys a dip of your size by a plain rule — **no model**. On fresh
history buying every dip by a plain rule lost on average, so use it only for coins you know, with a small size.

| Setting | What it does | Careful value |
|---|---|---|
| **Coins or pools** | the coins to watch (mint or PumpSwap pool) | 1–5 coins you follow |
| **Dip: one sale / from peak** | one sale drops the price by your %, or the price is your % below its recent high | one sale |
| **Dip %** | how deep | 20 |
| **Sale at least / Window** | smaller sales are ignored / the high is taken over this window | 0.5 SOL / 60 s |
| **Price bound** | the most a buy may pay above the price after the dip | 5% |
| **Again after** | no new buy of the same coin sooner | 300 s |
| Size & limits, exits | as above, its own values | 0.02–0.05 SOL, one position, stop 25%, dump 20% |

## 7. Ready setups

Pick one and tell the user exactly these values, then **save** and **start**. If the card is grey (paused), take the
next one that fits and say why.

| Setup | Card | SOL per buy | Daily stop | Open positions | SOL in positions |
|---|---|---|---|---|---|
| **Safe, small wallet (0.2–0.5 SOL)** | Calm | 0.05 | 0.3 | 2 | 0.1 |
| **Standard (checked)** | Standard | 0.1 | 1 | 3 | 0.3 |
| **Picky, fewer but better** | Deep dumps | 0.1 | 0.5 | 3 | 0.3 |
| **Mid-curve, steady** | Mid curve, deep | 0.1 | 0.5 | 3 | 0.3 |
| **Young coins hunter** | New coins | 0.1 | 0.5 | 2 | 0.2 |
| **Bold** | Hold 30 s or Deep dumps, hold 30 s | 0.1 | 1 | 3 | 0.3 |
| **Bigger wallet (5+ SOL)** | Standard or Deep dumps | 0.25 | 2 | 4 | 1.0 |

Keep **Own priority fee and tip** on **ours** and **Keep for arb** at what the user's Arb needs in every setup. Different
users picking different cards is good for everyone — they buy different coins; when two cards fit, prefer the one with
fewer users on it.

## 8. How to read "Signals the bot skipped"

The page shows how many of the model's signals you did not buy, and why. "not your kind of dip" means your entry
switches filtered it out — that is expected and is how users spread over different coins. For the other reasons see
[SCALPER.md §10](SCALPER.md#10-the-dashboard).

### Trying the new settings on a second wallet

If your Scalper works well as it is, leave it: nothing changed for you. To try your own entry, create a second wallet
(the wallet button next to arb / copytrade / scalper → **+ new wallet**). It gets a copy of **all** the open wallet's
settings — arb, Copytrade and Scalper (with the extra exits) — but Copytrade and both Scalper strategies start
**stopped** there. Top it up, turn the new options on, press **start**: the two wallets' results stay apart.
(Wallets made before 26 October 2026 got the arb settings only; **Export** / **Import** (§9) moves a Scalper setup.)

## 9. Export and import settings

At the bottom of the Scalper page, **Settings file**:

- **Export scalper settings** downloads `diablo-scalper-settings-<date>.json`: both strategies' entry switches, size,
  limits, fees and exits, and the extra exits (trailing, spike, dump, quiet). Not in it: the on/off switches
  and no keys (the settings never hold one). It exports the **saved** settings.
- **Import scalper settings** reads such a file and lists every change "was → becomes" (SOL and % in words). **Apply to
  the page** puts it into the form; nothing is saved until you press **save**. Copytrade's settings stay as they are.

Use it to keep a setup, compare setups, move it to another account — or let an AI assistant write one for you: the
file's `settings.scalper` is the ML strategy (its `entry_filter` holds the card: nothing = Standard, `min_score_x100` 150 = Calm,
`min_drop_pct` 15 = Deep dumps, plus `stages: ["growing"]` = Mid curve, deep, `stages: ["new"]` = New coins; Hold 30 s =
`exits.follow_wallet: false` with one 30 s timer step, with `min_drop_pct` 15 — Deep dumps, hold 30 s; anything else is
Your own),
`settings.watch` is My coins.
