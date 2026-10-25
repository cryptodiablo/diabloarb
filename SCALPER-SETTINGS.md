# Scalper settings — every switch explained (for users and their AI assistants)

This file explains **every setting of Scalper on diablo.bot** (`diablo.bot → Solana → scalper`): what it does, how it
changes risk and profit, and what to choose. Give it, together with [SCALPER.md](SCALPER.md), to Claude, Codex or any
other assistant and ask it to set Scalper up for you — it has everything it needs.

**Rules for the assistant.** Never ask for a private key, seed phrase or API key — Scalper never needs them. Never
promise profit: Scalper makes many small, fast trades and some days lose. The history numbers below are from a short
period (21–23 October 2026, about 2.4 days) and are **higher than what to expect** — use them to compare settings with
each other, not as a forecast.

## Contents

1. [Why the entry switches exist](#1-why-the-entry-switches-exist)
2. [Entry switches (Curve dip bounce, ML)](#2-entry-switches-curve-dip-bounce-ml)
   - [2a. Your own entry (advanced, optional)](#2a-your-own-entry-advanced-optional)
3. [All combinations on history](#3-all-combinations-on-history)
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

So Scalper gives you **your own entry choices**: the three switches below pick *which* of the model's dips you buy.
Users with different choices buy different coins and do not crowd each other — which keeps the edge for everyone.

## 2. Entry switches (Curve dip bounce, ML)

The model only proposes dips it expects to bounce. The switches narrow that list down to your taste. They never add
dips the model rejected.

### Style

| Choice | What it does | Risk | On history (per trade, 0.1 SOL) |
|---|---|---|---|
| **Calm** | only the model's strongest dips (score at least 1.5× its bar); sells 10 s after the buy | lowest: fewer trades, each better on average | ~72 dips/day, ≈ +3.8% |
| **Balanced** (default) | every dip the model passes; sells 10 s after the buy — the checked setup | medium | ~141 dips/day, ≈ +2.7% |
| **Bold** | every dip the model passes, but holds **30 s** instead of 10 (the bounce often runs longer) | higher: bigger swings both ways, a crash has more time to hit | ~141 dips/day, ≈ +5.2% |

When to pick: **Calm** for a small wallet or when you want fewer, safer trades; **Balanced** if unsure; **Bold** if you
accept bigger swings for a bigger average — and keep a daily stop.

### Which coins

A pump.fun coin trades on its *bonding curve* until the curve fills and the coin "graduates" (migrates) to a pool.
How full the curve is says how grown the coin is. You can tick one or several:

| Choice | Coins | On history (Balanced, 10%+ dips) |
|---|---|---|
| **New** | curve less than 25% full: the youngest, wildest coins | ~15 dips/day, ≈ +10.7% |
| **Growing** | curve 25–75% full: most of the dips are here | ~115 dips/day, ≈ +1.4% |
| **Close to graduating** | curve 75%+ full: about to move to a pool | ~11 dips/day, ≈ +5.1% |

All three ticked = every coin (default). Ticking only New or only Close to graduating gives fewer trades, each better on
history, and puts you on different coins than most users.

### Dip size

| Choice | What | On history (Balanced, all coins) |
|---|---|---|
| **Any 10%+** (default) | every dip the model passes (one sale took the price down 10% or more) | ~141 dips/day, ≈ +2.7% |
| **Only deep 15%+** | only dips where the sale took the price down 15% or more | ~65 dips/day, ≈ +7.8% |

Deep dips bounced more on history; there are about half as many.

## 2a. Your own entry (advanced, optional)

Under the three switches, **▸ your own entry** opens more choices, in groups: **The model**, **The dip**, **The coin**, **Timing** and **Wallets**. They are **off until you fill them**: an empty field
changes nothing, and a user who never opens the block trades exactly as before. Each filled field narrows the model's
dips to your taste, so users with different choices buy **different coins** instead of crowding the same dip (when 15+
users buy one dip at once, the first buys move the price and the rest are "missed").

| Setting | What it does | Works with the switches |
|---|---|---|
| **Strictness** (× bar) | buy only dips the model scores at least this many times its own bar: 1 = every dip it passes, 1.5 = Calm, 2–3 = only its surest dips | replaces Calm/Balanced while set; pressing a Style button clears it |
| **Dip from** (%) | the sale took the price down at least this much | replaces Dip size while set; pressing a Dip size button clears it |
| **Dip up to** (%) | at most this much — very deep dips are often a rug or a dead coin | with either Dip size |
| **Sale at least** (SOL) | only dips made by a sale at least this big (a big holder dumping) | with everything |
| **Curve filled from / up to** (%) | how full the bonding curve is: 0% just launched, 100% about to move to a pool — a finer version of Which coins | both apply: a coin must pass Which coins and the range |
| **Coin age from / up to** (min) | minutes since the coin launched | with everything |
| **Coins to skip** | mint addresses the bot never buys (up to 200, one per line) | with everything |
| **Enter later by** (ms) | your buy is decided this long after the signal, on the price then — not in the same block as everyone else (one block ≈ 400 ms) | with everything |
| **Only if it bounced** (%) | with Enter later: buy only if by then the price rose at least this much from the signal; otherwise the signal is skipped ("the price did not rise in time") | needs Enter later |
| **Only coins these wallets bought** + **Within** (min) | up to 50 wallets: buy a dip only if one of them bought that coin on its curve within the minutes set (60 if empty) | with everything |

A signal the model sends without one of these figures passes that check (it never blocks a buy by itself).
The figures of these ranges are **not checked on history yet** — try one change, compare a day or two on the Stats
card, and keep what works for you. Fewer dips means fewer trades: keep **SOL per buy** and the **Daily stop** as before.

**Example setups** (fill only the fields named; the rest stay empty):

| Idea | Fields |
|---|---|
| Young coins, real dumps | Curve filled up to 25 · Coin age up to 15 · Dip from 20 |
| Whale exits only | Sale at least 5 · Dip from 15 |
| Mid-curve, no crashes | Curve filled from 25 up to 60 · Dip from 12 up to 35 |
| The model's surest dips | Strictness 2 |
| First hour of a coin | Coin age up to 60 |
| Older, steadier coins | Coin age from 30 · Curve filled from 50 |
| Out of the crowd's block | Enter later by 400 |
| Ride a started bounce | Enter later by 800 · Only if it bounced 3 |
| Follow smart wallets | Only coins these wallets bought: your 5–10 wallets · Within 30 |

## 3. All combinations on history

1 user, 0.1 SOL per buy, every cost included (the pump.fun fee both ways, our 1%, the network), 21–23 Oct 2026.
"SOL/day" is what one user with that setup would have made per day — it grows with the number of trades, so a setup
with a high % but few trades can still make less in total.

| Style | Coins | Dip | Dips/day | Per trade | SOL/day |
|---|---|---|---|---|---|
| Calm | all | 10%+ | 72 | +3.8% | +0.27 |
| Calm | all | 15%+ | 32 | +10.5% | +0.33 |
| Calm | new | 10%+ | 4 | +11.9% | +0.05 |
| Calm | growing | 10%+ | 63 | +3.2% | +0.20 |
| Calm | growing | 15%+ | 27 | +9.6% | +0.25 |
| Calm | close to graduating | 10%+ | 5 | +5.7% | +0.03 |
| Balanced | all | 10%+ | 141 | +2.7% | +0.37 |
| Balanced | all | 15%+ | 65 | +7.8% | +0.49 |
| Balanced | new | 10%+ | 15 | +10.7% | +0.15 |
| Balanced | new | 15%+ | 11 | +13.9% | +0.14 |
| Balanced | growing | 10%+ | 115 | +1.4% | +0.15 |
| Balanced | growing | 15%+ | 50 | +6.6% | +0.32 |
| Balanced | close to graduating | 10%+ | 11 | +5.1% | +0.06 |
| Bold | all | 10%+ | 141 | +5.2% | +0.72 |
| Bold | all | 15%+ | 65 | +13.7% | +0.85 |
| Bold | new | 10%+ | 15 | +13.7% | +0.20 |
| Bold | growing | 10%+ | 115 | +3.7% | +0.42 |
| Bold | growing | 15%+ | 50 | +11.7% | +0.57 |
| Bold | close to graduating | 10%+ | 11 | +8.7% | +0.10 |

Why real results are lower: on history every buy got in; live, about 15% of buys miss because other market bots buy
the same bounce first (a missed buy costs only its network fee, ~0.0001 SOL). And 2.4 days is a short period.

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

Every buy sells by the first exit rule that fires; an empty field is off. **Style** sets the main timer (10 s, or 30 s
for Bold); the fields below are for your own style. On our bots take profit, trailing and stops did worse than a plain
timer, so the checked setup leaves them off.

| Exit | What it does | When to turn it on | Example |
|---|---|---|---|
| **Timer** | sells everything this long after the buy | always; set by Style. Type your own seconds (from 1) to sell by your timer instead of with the model — e.g. when two of your bots sell in the same block; pressing a Style button brings its 10 s / 30 s back | 10 s / 30 s, or yours |
| **Take profit** | sells everything at +X% | to lock a quick gain | 30 |
| **Stop loss** | sells everything at −X% (a crash in one transaction can jump past it) | with Bold or long timers | 25 |
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

Pick one and tell the user exactly these values, then **save** and **start**.

| Setup | Style | Coins | Dip | SOL per buy | Daily stop | Open positions | SOL in positions |
|---|---|---|---|---|---|---|---|
| **Safe, small wallet (0.2–0.5 SOL)** | Calm | all | 10%+ | 0.05 | 0.3 | 2 | 0.1 |
| **Standard (checked)** | Balanced | all | 10%+ | 0.1 | 1 | 3 | 0.3 |
| **Picky, fewer but better** | Calm | all | 15%+ | 0.1 | 0.5 | 3 | 0.3 |
| **Young coins hunter** | Balanced | new | 10%+ | 0.1 | 0.5 | 2 | 0.2 |
| **Bold** | Bold | all | 15%+ | 0.1 | 1 | 3 | 0.3 |
| **Bigger wallet (5+ SOL)** | Balanced | all | 10%+ | 0.25 | 2 | 4 | 1.0 |

Keep **Own priority fee and tip** on **ours** and **Keep for arb** at what the user's Arb needs in every setup. Different
users picking different setups is good for everyone — they buy different coins.

## 8. How to read "Signals the bot skipped"

The page shows how many of the model's signals you did not buy, and why. "not your kind of dip" means your entry
switches filtered it out — that is expected and is how users spread over different coins. For the other reasons see
[SCALPER.md §10](SCALPER.md#10-the-dashboard).

## 9. Export and import settings

At the bottom of the Scalper page, **Settings file**:

- **Export scalper settings** downloads `diablo-scalper-settings-<date>.json`: both strategies' entry switches, size,
  limits, fees and exits, and the extra exits (trailing, spike, dump, quiet). Not in it: the on/off switches, the
  «I understand» tick — and no keys (the settings never hold one). It exports the **saved** settings.
- **Import scalper settings** reads such a file and lists every change "was → becomes" (SOL and % in words). **Apply to
  the page** puts it into the form; nothing is saved until you press **save**. Copytrade's settings stay as they are.

Use it to keep a setup, compare setups, move it to another account — or let an AI assistant write one for you: the
file's `settings.scalper` is the ML strategy (its `entry_filter` holds the switches: `min_score_x100` 150 = Calm,
`stages` = which coins, `min_drop_pct` 15 = only deep; Bold = `exits.follow_wallet: false` with a 30 s timer),
`settings.watch` is My coins.
