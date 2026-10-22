# CopyTrade on diablo.bot — knowledge base for AI assistants

CopyTrade copies the Solana meme-coin trades of the wallets a user picks: when a copied wallet buys a coin, the user's
bot buys it too, a moment later, and sells it by the exit rules the user set. It runs on diablo.bot (the hosted
cabinet), in the **Solana** section next to Arb: `diablo.bot → Solana → Copytrade`.

This file is the full public knowledge base for an AI assistant answering a user's questions about CopyTrade. For the
arbitrage bot read [AI_GUIDE.md](AI_GUIDE.md) and [FAQ.md](FAQ.md).

**Rules for the assistant.** Never ask the user for a private key, seed phrase, key file or any API key — CopyTrade
never needs them from the user. Do not promise profit: copying a wallet is not getting its result (§9). Do not guess
features that are not described here; say they are not available.

## Contents

1. [CopyTrade in one minute](#1-copytrade-in-one-minute)
2. [Getting started](#2-getting-started)
3. [Whom to copy (sources)](#3-whom-to-copy-sources)
4. [Which buys are copied (entry)](#4-which-buys-are-copied-entry)
5. [Exits](#5-exits)
6. [Limits and stops](#6-limits-and-stops)
7. [Money: fee, network costs, rent](#7-money-fee-network-costs-rent)
8. [Your wallet, Arb and other modes](#8-your-wallet-arb-and-other-modes)
9. [Why my result differs from the copied wallet's](#9-why-my-result-differs-from-the-copied-wallets)
10. [The dashboard](#10-the-dashboard)
11. [Troubleshooting by symptom](#11-troubleshooting-by-symptom)
12. [Questions users ask](#12-questions-users-ask)
13. [Glossary](#13-glossary)

## 1. CopyTrade in one minute

- **What it copies:** buys of pump.fun coins on the bonding curve and in PumpSwap pools, bought directly or through
  trading terminals and bots (FOMO, Axiom, GMGN, Photon, Pump App, Jupiter, Telegram bots and others). The terminal does
  not matter: the bot sees the wallet's trade on-chain.
- **Coins priced in another token** (USDC or any other quote token, not SOL) are copied too: the bot swaps SOL → that
  token → the coin in one transaction, and back to SOL on the sale. You never hold USDC or the quote token.
- **Speed:** the bot watches the copied wallets' transactions before they are executed and sends its own buy right
  after — usually in the same or the next block.
- **Each buy is its own position** with its own exits: a timer, following the copied wallet's sales, take profit, stop
  loss and more (§5). Only that position's tokens are sold.
- **You deposit only SOL.** WSOL, token accounts, nonces and lookup tables are managed by the bot.
- **Fee:** 1% of each buy, sent in a separate transaction after the buy (§7).

## 2. Getting started

1. Log in to diablo.bot and open **Solana → Copytrade**.
2. Press **Connect copytrade**. CopyTrade uses the **same wallet as your Arb bot** — no new wallet, no key to enter.
3. Make sure the wallet holds enough SOL: about **0.016 SOL** for the one-time preparation (§7, mostly refundable rent)
   plus your buy size, plus the **Keep for arb** reserve (§6). Top up the same address you use for Arb.
4. The page shows "wallet is being prepared" for a few seconds while the bot creates its accounts. If it says the
   wallet needs funding, top it up — preparation retries by itself every 2 minutes.
5. Add sources in **Who to copy** (§3), check **Entry**, **Exit** and **Limits**, and switch copying on.
6. Watch **Copies**: every buy and sale with its transaction, result, fee and network cost.

Copying can be switched off at any time; open positions still exit by their rules. **Sell** on a position or **Sell all**
sells at once.

## 3. Whom to copy (sources)

| Source type | What you enter | Notes |
|---|---|---|
| Wallet | a Solana address and an optional label | up to 20 sources per user |
| Wallet bundle | a wallet plus **other wallets of the same trader** (up to 9 more) | see "Bundles" below |
| FOMO @username | a FOMO trader's username, e.g. `@frankdegods` | works for traders in our FOMO directory (influencers and the top lists, growing daily); an unknown name — the page asks for the wallet |
| Top traders | one click in **Top traders**: copy one trader or the whole list | per platform (FOMO, Pump App, Axiom, GMGN, Terminal, Photon, Jupiter, Telegram bots) and period (24 h — refreshed hourly; 7 d and 30 d — daily after 03:40 MSK) |

**Top traders, how they are ranked.** PnL of the period counts only coins the trader bought **and** sold in it, minus
what the coins they still hold cost (held coins count as worth nothing — a copier would hold them too). All the
trader's trades count, whichever terminal they used. Removed from the lists: bots (over ~200 trades a day), snipers
who hold a coin under 30 seconds (a copy cannot follow them), wallets that launched 3+ coins in 30 days (deployers),
results made by 1–3 lucky coins, traders with under 30% of coins in profit, and over 90% in profit across 20+ coins
(nobody wins that often but insiders, bundlers and bots). Each row shows **Win** (share of coins
in profit), **Trades/day**, **Avg buy**, **Hold** (median time from buy to last sale); open a row for coins closed,
median result per coin, last trade and links (GMGN, Solscan, FOMO profile). A copied list follows its changes by
itself: traders who drop out stop being copied, new ones start. The 24 h lists change every hour.

**Bundles.** Many traders buy with several wallets at once (a "bundle"). Put them in one source: **+ wallet of the same
trader** (paste a list). A buy by **any** of them is copied — once per coin, after the wallet that bought first. Sales:
by default a sale by **any** wallet of the bundle is followed (**Follow sells: Bundle**); switch to **Designated** to
follow only the wallet you bought after. Example: A, B and C are one trader; B buys first — you buy after B; then A
sells half its coins — with Bundle you sell half too, with Designated you wait for B.

**Market per source** (Advanced in the source card): **Both** (default), **Internal** — copy only this source's buys on the
pump.fun bonding curve, or **External** — only its buys in PumpSwap pools (after the migration). Use Internal for early
curve snipers, External for traders who buy migrated coins. Skipped buys show *not curve* / *not pool*.

- Next to each source the page shows **your copies and your net for 7 days** from that source.
- A source can be paused by the bot for the rest of the day (§6) — the page says why.
- Copying a whole terminal's flow without selection is not offered: unselected flows lose money.
- A trader's own PnL is not your result as a copier (§9): judge a source by **your net** on the page.
- Why a username needs our directory: FOMO's app shows a profile address that is not the wallet that actually trades;
  we find the trading wallet on-chain and keep the match in our directory.

## 4. Which buys are copied (entry)

| Setting (page label) | What it does | Default |
|---|---|---|
| **Size → Buy** | fixed SOL per copy, or a share of their buy, or a share of your balance (with **At least / At most**) | 0.1 SOL fixed |
| **Slippage** | how far above the price right after their buy you still buy; above it the copy is not filled | 20% |
| **Their buy, at least** | smaller buys of the source are not copied | 0.05 SOL |
| **Crowd, at most** | skip a coin many wallets bought in the minute before | 20 wallets |
| **First buy only** | only the wallet's first buy of a coin (in 30 min); their top-ups are not copied | on |
| **Curve only** | copy only bonding-curve buys, not PumpSwap pools | off (both copied) |
| **Coins quoted in other tokens** | copy coins priced in USDC and other tokens through that token | on |
| **Their buy, at most** | larger buys of the source are not copied (with **at least**: a range) | off |
| **Dump protection** | a copied wallet that sells a coin within N seconds of buying it is not copied for M minutes | on for new users: 10 s → 30 min |
| *Advanced:* **Market cap** | copy only when the coin's market cap (USD) at your buy is in the range | off |
| *Advanced:* **Slippage in SOL** | instead of %: at most X SOL of others' buys may land ahead of you | off (% is used) |
| *Advanced:* **Buy tiers** | a different size and slippage by market cap and venue (curve / pool) | off |

**Dump protection, how it works.** Some wallets buy, let copiers buy after them, and sell into the copiers a few seconds
later. When a wallet you copy sells a coin within **N seconds** of buying it (default 10 s), the bot stops copying that
wallet for **M minutes** (default 30). Copies already open still exit by their rules. Skipped buys show the reason
**quick flip**. Example: the wallet buys at 12:00:00 and sells at 12:00:04 — it is paused till 12:30:04. Turn it off for
scalpers you trust who really trade in seconds.

**Their buy range.** *At least 0.1 SOL* skips small test buys; *at most 5 SOL* skips oversized buys, which are often a
bundle or a pump and leave you buying at the top.

**Market cap.** The cap is computed from the price right after the copied buy (pump.fun coins: 1 billion supply) and SOL's
price in USD. Example: **from 6K to 40K** copies only early coins. Leave the upper bound empty for no limit. When the cap
cannot be computed, the range does not block the copy.

**Slippage in % or in SOL.**
- **%** (default): with 20% you get at least 80% of the tokens the price right after their buy would give.
- **SOL**: you set how much others may buy **ahead of you** (e.g. 1 SOL); the bound is the tokens you would get after
  that much was bought first. Use it when coins differ a lot in liquidity: on a thin curve 1 SOL ahead is a big move,
  on a pool it is nothing, and the SOL bound follows that automatically.

**Buy tiers.** Different coins deserve different sizes: e.g. **1.3 SOL with 30% slippage from 6K to 40K, 0.5 SOL with
20% from 40K to 61K, curve only**. Each tier has a venue (any, bonding curve or PumpSwap pool), a market cap range, a
size (fixed, share of theirs or of your balance) and its own slippage (% or SOL; empty — the general one). The **first**
tier that fits is used; when none fits, the general settings above (**General**) are used, and the general market cap
range, if set, decides whether to copy at all. Tiers apply to wallets and lists, not to Scalper and "my coins".

Always skipped, not configurable: transactions that also sell (arbitrage, sandwiches), mayhem-mode coins, coins whose
transfers are hooked. A coin you already hold a copy of is not bought again by another source.

**Many users copy the same wallet:** there is no queue and no priority — whoever's slippage covers the price gets
filled.

## 5. Exits

Every buy is a separate position with its own clock. All rules that are on apply; **the first that fires sells**. With
all rules off, positions sell only by hand.

| Rule (page label) | What it does | Default |
|---|---|---|
| **Timer → Sell after** | sell after N seconds; or in steps (e.g. 30% after 60 s, the rest after 300 s) | all after 300 s |
| **Follow the wallet** | the copied wallet sells a share — your position sells the same share (they sold 50% — you sell 50%) | on |
| **Take profit** | at +X% over your entry price sell Y% of the position (up to 3 levels) | off |
| **Stop loss** | at −X% sell all | off |
| **Take initial at** | at ×N (e.g. ×2) sell the SOL you put in; the rest follows the other rules | off |
| **Crowd ahead → Others bought, at least** | if others bought at least X SOL between the copied wallet and you, sell Y seconds after your buy (you bought late, at a high price) | 2 SOL, 5 s |
| **Sell slippage** | price tolerance on every sale; a failed sale is retried | 25%, 3 retries |
| **Sell** / **Sell all** (manual) | sell a position or everything now | always available |
| **Follow the wallet → sell all at** | once the copied wallet has sold X% of its coin in total, sell the whole position (no tails) | off (80% suggested) |
| **Trailing** | after the price rose X% over your entry, sell Y% when it falls Z% from its high (up to 3 phases) | off |
| *Advanced:* **Stop wick filter** | the stop waits N s below its line; if the price comes back it was a wick — no sale | 0 (at once) |
| *Advanced:* **No stop for the first N s** | the stop starts N s after the buy | 0 |
| *Advanced:* **Early stop** | another stop for the first N s, then the normal one | off |
| *Advanced:* **Take-profit timeout** | the first take profit not reached within N s — sell all | off |
| *Advanced:* **Clear the rest below** | after a partial sale, what is left is worth less than X SOL — sell it | off |
| *Advanced:* **Moonbag** | X% of the position is never sold by the rules | off |
| *Advanced:* **On migration** | the coin leaves the curve for its PumpSwap pool — sell X% | off |
| *Advanced:* **Follow sells: Bundle / Designated** | for a bundle source: follow a sale by any of its wallets, or only by the one you bought after | Bundle |

**Which rule sells first.** Rules are checked in this order, and the first that fires sells: your manual sell → the
copied wallet's sale (Follow the wallet) → migration → stop loss → take-profit timeout → clear the rest → crowd ahead →
take initial → take profit → trailing → timer. Each position has its own clock and its own high.

**Trailing, step by step.** Each phase has **Activate** (+X% over your entry), **Drawdown** (Z% down from the high) and
**Sell** (Y% of what is left). The highest phase the price has reached is the one in force. Example with one phase
+50% / 20% / 30%, entry price 100:
- the price goes to 140 — under +50%, nothing is watched;
- it reaches 160 — the phase is active, the high is 160, the line is 160 × 0.8 = 128;
- it falls to 128 — sell 30%; the new reference is 128, the next line is 20% under the next high;
- it rises to 130 and falls to 104 — sell 30% of the rest again.
Add a second phase, e.g. +150% / 15% / 100%, to sell everything on a 15% pullback once the coin has gone ×2.5.
Trailing complements **Take profit** (fixed levels) — use both or either.

**Stop loss, the advanced parts.**
- **Wick filter** (0–60 s): pump.fun dumps by the dev often recover in 2–3 seconds. With 3 s the stop sells only if
  the price is still below the line 3 seconds after it first broke it; if it came back, the wait starts over next
  time. 3–5 s is a good setting; 0 sells at once.
- **No stop for the first N s**: the first seconds after a buy are the most volatile; with 5 s and a stop of −30% the
  stop is ignored for 5 seconds, then sells if the price is still 30% down.
- **Early stop**: e.g. **−60% for the first 10 s, then −30%** — a wide stop while the copy settles, a tight one after.
  Use either "No stop for the first N s" or "Early stop", not both.

**Follow the wallet → sell all at.** Copying partial sales leaves small tails when the wallet sells in many pieces.
With 80%: they sell 50% — you sell 50%; they sell 60% of the rest (80% in total) — you sell everything.

**Take-profit timeout.** With take profit +50% and a timeout of 60 s: if +50% is not reached within a minute of the
buy, the position is sold — a trade that goes nowhere frees your SOL.

**Clear the rest below.** After a take profit or a partial follow sale, a remainder worth e.g. under 0.01 SOL is sold
at once instead of waiting.

**Moonbag.** With 10%: every rule sells at most 90% of the bought tokens. When only the moonbag is left, the position
closes on the page and the moonbag tokens stay in your wallet for a possible moon; **Sell** on the position before that
sells everything. The moonbag's cost counts as spent in the position's result.

**On migration.** When a coin fills its curve and moves to its PumpSwap pool, the price often jumps and then falls.
With 50% the bot sells half right after the migration; the rest follows the other rules (sales go to the pool).

- A sale sells **exactly that position's tokens** — never more.
- A coin that migrates from the curve to its PumpSwap pool keeps its position: the sale goes to the pool.
- A coin priced in another token is sold back to SOL through that token in one transaction, also in shares.

### Presets and Advanced

**Presets** set sensible values in one click; change anything afterwards. Everything not in a preset stays off and sits
under **Advanced**.

| | Safe | Balanced | Aggressive |
|---|---|---|---|
| Buy | 0.05 SOL | 0.1 SOL | 0.2 SOL |
| Slippage | 15% | 20% | 30% |
| Crowd, at most / their buy, at least | 10 / 0.1 SOL | 20 / 0.05 SOL | 20 / 0.05 SOL |
| Stop loss | −30%, wick 3 s | −40%, wick 3 s | off |
| Trailing | +50% / 20% / 50% | +50% / 20% / 50%; +150% / 15% / 100% | +100% / 25% / 50%; +300% / 20% / 100% |
| Take initial | — | — | at ×2 |
| Timer | 300 s | 300 s | 900 s |
| Follow the wallet | on, sell all at 80% | on, sell all at 80% | on, sell all at 80% |
| Moonbag | — | — | 10% |
| Dump protection | 10 s → 30 min | 10 s → 30 min | 5 s → 15 min |
| Daily stop | 0.5 SOL | 1 SOL | 2 SOL |

**When to open Advanced:** buy tiers and market cap — you copy traders who buy coins of very different sizes; SOL
slippage — you copy into thin curves and pools alike; stop wick filter / early stop — your stops sell on dev dumps that
recover; take-profit timeout — your copies sit flat for minutes; clear the rest — tails pile up after partial sales;
moonbag — you want to keep a small piece of every coin; on migration — you trade curve coins that often fill.

## 6. Limits and stops

The day runs from **00:00 Moscow time (MSK, UTC+3)**.

| Setting (page label) | What it does | Default |
|---|---|---|
| **Open positions** | positions at most | 10 |
| **In positions, at most** | SOL in open positions at most | 2 SOL |
| **Per coin** | SOL in one coin at most | 0.5 SOL |
| **Daily stop** | lost this much today — no new copies till 00:00 MSK (positions still exit) | 1 SOL |
| **Per source a day** | a source that cost this much today is paused till 00:00 MSK | 0.5 SOL |
| **Rugs per source a day** | after this many copies of a source that lost half or more, it is paused for the day | 2 |
| **Keep for arb** | SOL never spent by CopyTrade, so your Arb bot keeps its fees | 0.05 SOL |
| failed buys in a row | after 10 failed buys in a row copying pauses for 10 minutes | 10 / 10 min |

## 7. Money: fee, network costs, rent

| What | How much | Notes |
|---|---|---|
| **Service fee** | **1% of each buy** | sent in a separate small transaction after the buy (not inside it); several are batched (≥0.01 SOL or once a minute). Shown on each copy as **Fee 1%**. No fee on sales. |
| **Network** | Solana fees, priority and tips of each buy and sale | shown on each copy as **Network**; our defaults (roughly 0.0001–0.00025 SOL per transaction) or your own in **Advanced → Fees** (see below) |
| **Venue fees** | pump.fun / PumpSwap / the intermediate pool | inside the price |
| **Preparation (one-time)** | ≈0.006 SOL for 4 nonce accounts + a few token accounts | **rent — refundable** when the accounts are closed |
| **Lookup table (one-time)** | ≈0.002 SOL + ≈0.0002 SOL per address (usually 0.005–0.01 SOL) | rent, refundable; lets trades through other tokens fit a transaction |
| **Coin token account** | ≈0.002 SOL per coin while held | returned when the position is sold out |

**Your own priority fee and tip (Advanced → Fees).** By default the bot uses its fixed fees: a buy pays 0.0001 SOL priority
and a 0.0001 SOL tip, a sale 0.00002 SOL priority and a 0.000005 SOL tip. You can set your own for buys and for sales (up
to 0.01 SOL each). When many users copy the same wallet, a higher tip and priority land your transaction sooner — at a
better price — but every trade costs that much more, win or lose. A buy's fees never exceed 3% of the buy: anything over
is cut, the tip first. Example: with 0.05 SOL buys a 0.001 SOL tip is 2% of each buy; it pays off only if it often gets
you in ahead of other copiers. Changes apply at once.

**Net** on the page = what came back − what went in − 1% fee − network. Small buys pay relatively more network cost:
at 0.01 SOL per copy the network is ~2–3% of the buy per round trip; at 0.1 SOL it is ~0.25%.

## 8. Your wallet, Arb and other modes

- CopyTrade uses **the same wallet as your Arb bot**. The key never leaves diablo.bot's servers; you never type it.
- **WSOL is not touched:** your Arb capital in WSOL stays as it is. Buys wrap exactly their own SOL inside the buy;
  sale proceeds come back as plain SOL — a sale through another token (USDC, PUMP…) first lands as WSOL and exactly that
  amount is unwrapped to SOL right after, in its own small transaction.
- **Keep for arb** guarantees SOL for Arb's fees.
- CopyTrade has **its own nonce accounts**, separate from Arb's — they never block each other.
- **Modes never touch each other's coins.** On a shared wallet each mode (CopyTrade, Scalper, Arb) sells only the
  tokens it bought itself, never closes a token account that holds another mode's tokens, and does not buy a coin
  another mode holds.
- **Users never affect each other:** each user trades from their own wallet with their own settings.
- Withdrawing and downloading the key work as in the Arb cabinet.

## 9. Why my result differs from the copied wallet's

- **You buy after them.** Your buy lands right after theirs, at a higher price — their own buy moved it. The more
  others copy the same wallet, the higher the price you get (the **Crowd ahead** exit handles the worst cases).
- **Their exits are not yours** unless **Follow the wallet** is on, and even then your sale lands after theirs.
- **Costs:** 1% fee and network costs are on every copy; small sizes pay relatively more (§7).
- **Slippage refusals:** if the price ran above your **Slippage**, the copy is not filled — it shows as a refusal, not
  a loss.
- A wallet that earns well itself can still be unprofitable to copy. Judge a source by **your net** on the page, not
  by the wallet's PnL.

## 10. The dashboard

### Open positions

Every buy is a row with its own exits ("every buy sells on its own timer and rules").

| Column | Meaning |
|---|---|
| **Coin** | the coin; a "via USDC" (or other token) mark when it is bought through that quote token |
| **Source** | which source it copied (a wallet, a @username, a list entry like `pnl7d +913.5 SOL · 802 trades`) and the terminal tag |
| **Landed** | how fast your buy landed after the copied trade (in slots: "same slot", "+1 slot"…). **`sending…`** = the buy was sent and is waiting for the network to confirm it — normally a fraction of a second. If a row stays in `sending…` for minutes, the transaction did not land: no SOL is spent; the row is cleared automatically |
| **In, SOL** | SOL you put in |
| **Now, SOL** | what the position is worth now (sold part + the rest at the current price); `pool` = coin in a pool, price shown after the next trade; `—` = not known yet |
| **PnL** | % gain or loss of the position so far |
| **Exit** | the rules that will sell it, e.g. `with wallet · timer 300 s · crowd` = sells when the copied wallet sells, or 300 s after your buy, or earlier if a crowd bought ahead of you |
| **Next** | countdown to the next timer step; `waits` = no timer left, it waits for another rule (wallet sells, TP/SL…) |
| **sell** | sell this position now (`selling…` while the sale goes) |

### Copied trades

| Column | Meaning |
|---|---|
| **When** | when it closed (or was tried) |
| **Coin / Source** | as above |
| **Exit** | why it sold: `timer`, `wallet sold 50%`, `take profit +15%`, `stop loss`, `×2 — initial out`, `crowd ahead ≥ 2 SOL · 5 s`, `sold by you`, `sold by another trader` (another mode on the wallet sold it), `missed — price past your 20% slippage` (not bought), `not filled — <reason>` (the buy failed on-chain) |
| **In, SOL** | SOL put in |
| **Net, SOL** | back − in − 1% − network |
| **Fee 1%** | the service fee of this buy |
| **Network** | Solana fees, priority and tips of its transactions |
| **Transaction** | link to the buy/sale on Solscan |

Amounts come from the chain, not from estimates. **Today** at the top: closed copies since 00:00 MSK, net after the 1% and
the network.

### Who to copy

- **sources** — your sources: **On** (switch), **Source**, **Via** (terminal), **Copier 7d** (coming: what copying it
  would have made), **Net** for the period, **Copies**, **State** (copying / paused for the day and why).
- **recommended** — ready lists: **FOMO top traders 7d** first (`@handle · pnl7d +X SOL · N trades`), FOMO influencers
  and others; **copy** one account or **copy list** for all; **Your copies 7d / Your net 7d** — your own results from it.
- Add a source: paste a wallet address or type a FOMO `@username`.

### Settings

**Entry**, **Exit**, **Limits** — see §4–§6. Saving applies within seconds. If the settings were changed in another tab,
the page reloads them — edit again.

## 11. Troubleshooting by symptom

| Symptom | Why | What to do |
|---|---|---|
| "Wallet is being prepared" for long / "fund it with SOL" | the wallet has less SOL than preparation needs | top up ~0.02 SOL; it retries every 2 minutes |
| No copies at all | copying is off, no sources, the source did not buy, or every buy was filtered | check the switch and sources; see the skip reasons under signals |
| Copies show "slippage" refusals | the price ran above your Slippage before your buy landed | normal for hot coins; raise Slippage only if you accept worse prices |
| Copies skipped "balance" / "keep" | SOL is below buy size + Keep for arb | top up or lower the size |
| Copies stopped for the day | Daily stop reached, or the source paused (cost / rugs) | resumes at 00:00 MSK; adjust limits if needed |
| Copying paused 10 minutes | 10 failed buys in a row (network trouble) | resumes by itself |
| A row stays in `sending…` for minutes | the buy did not land (network or a temporary fault) | nothing is spent; the row clears itself; copying continues |
| A position does not sell | sale retries failed (price beyond Sell slippage, coin rugged) | use **Sell**; raise Sell slippage for illiquid coins |
| Coin account rent not returned | the account still held another position's or another mode's tokens, so it was left open | it closes with the last sale of that coin; ~0.002 SOL |
| Result worse than the copied wallet | see §9 | judge by your net per source |

## 12. Questions users ask

**Do I need a new wallet?** No. CopyTrade uses your Arb wallet; just keep SOL on it.

**Will CopyTrade use my Arb's WSOL?** No. It never spends WSOL and keeps **Keep for arb** SOL untouched.

**What does it cost?** 1% of each buy, plus Solana network costs of each transaction (§7). No subscription, no fee on
sales or profit.

**Why is the 1% a separate transaction?** So the buy stays as light and fast as possible. Fees are batched, so you see
small transfers every minute or so, not one per buy.

**Can I copy several wallets?** Yes, up to 20 sources, and a recommended list counts as one source.

**Can I copy a FOMO user by username?** Yes, if they are in our FOMO directory (influencers and the daily top lists): type
`@username`. If the page doesn't know the name, paste their wallet address.

**Where do I find good traders to copy?** **recommended** in Who to copy: FOMO top traders of the last 7 days (refreshed
daily) and other lists — copy one trader or the whole list in one click.

**Can I copy an Axiom / GMGN / Photon / Pump App user?** Yes — add their wallet address. Trades through any terminal are
seen on-chain.

**What if the coin is priced in USDC?** It is copied through USDC automatically and sold back to SOL; you never hold USDC.

**What if many people copy the same wallet as me?** No queue: whoever's slippage covers the price is filled. Higher
slippage fills more often at worse prices.

**Can I sell manually?** Yes — **Sell** on a position or **Sell all**.

**What happens when I switch copying off?** No new copies; open positions still exit by their rules (or sell them by
hand).

**Is my key safe?** It stays encrypted on diablo.bot's signing servers and is never shown in logs or to anyone.

**Will Scalper or Arb sell my CopyTrade coins?** No. Each mode sells only its own tokens (§8).

**Does it copy sells of coins I don't hold?** No. A sale is copied only for a position bought from that wallet.

**Why didn't it copy a buy?** Look at the skip reason: crowd, their buy too small, not their first buy, limits, balance,
slippage, or the coin is held by another mode.

**Is profit guaranteed?** No. Copy trading meme coins is risky; use limits and judge sources by your own net.

**Which settings should I start with?** Pick a preset (Safe, Balanced or Aggressive, §5) and leave Advanced alone until a
specific problem shows up in your copies.

**My stop sells on a spike that comes right back.** Turn on the **stop wick filter** (3–5 s) or **No stop for the first
N s** (§5).

**A wallet I copy keeps dumping on me seconds after buying.** That is what **Dump protection** is for (§4): it pauses
such a wallet. Check it is on; lower N if they sell slower.

**The trader uses several wallets.** Add them as one **bundle** source (§3): a buy by any is copied once, a sale by any is
followed.

**Can I buy more on early coins and less on later ones?** Yes — **Buy tiers** by market cap (§4, Advanced).

**Why did my position close while I still have some tokens?** Your **moonbag** is kept on purpose (§5); the tokens are in
your wallet.

**Why did the bot sell when the coin migrated?** **On migration** is on (§5, Advanced).

**What do the skip and sale reasons mean?** Skips: *quick flip* — dump protection paused the wallet; *their buy big* —
above your "at most"; *market cap* — outside your range. Sales: *trailing*, *tp timeout*, *dust* (the rest was below your
floor), *migration*, *stop loss*, *timer*, *wallet* (followed their sale), *manual*.

## 13. Glossary

- **Source** — a wallet or a list you copy.
- **Copy / position** — one buy of yours and its own exits.
- **Bonding curve** — pump.fun's launch market of a coin; after it fills, the coin migrates to a **PumpSwap pool**.
- **Quote token** — the token a coin is priced in (SOL, USDC or another token).
- **Slippage** — how much worse than the expected price you accept.
- **Rug** — a copy that lost half or more.
- **Nonce account** — a small account that lets the bot send transactions fast; refundable rent.
- **Lookup table** — an on-chain list of addresses that makes transactions smaller; refundable rent.
- **MSK** — Moscow time, UTC+3; the trading day starts at 00:00 MSK.
- **Bundle** — several wallets of one trader copied as one source.
- **Trailing** — selling on a pullback from the high after a rise.
- **Wick** — a short spike below a price line that comes right back.
- **Moonbag** — a small part of a position kept and never sold by the rules.
- **Migration** — a pump.fun coin moving from its bonding curve to its PumpSwap pool.
- **Market cap** — price × supply (1 billion for pump.fun coins), in USD.
