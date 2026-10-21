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
| FOMO @username | a FOMO trader's username, e.g. `@frankdegods` | works for traders in our FOMO directory (influencers and the top lists, growing daily); an unknown name — the page asks for the wallet |
| Top traders / recommended list | one click in **recommended**: copy one trader or the whole list | e.g. **FOMO top traders 7d** (ranked by their realized PnL of the last 7 days, refreshed daily after 00:00 MSK), FOMO influencers |

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

- A sale sells **exactly that position's tokens** — never more.
- A coin that migrates from the curve to its PumpSwap pool keeps its position: the sale goes to the pool.
- A coin priced in another token is sold back to SOL through that token in one transaction, also in shares.

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
| **Network** | Solana fees, priority and tips of each buy and sale | shown on each copy as **Network**; fixed by the bot, not configurable; roughly 0.0001–0.00015 SOL per transaction |
| **Venue fees** | pump.fun / PumpSwap / the intermediate pool | inside the price |
| **Preparation (one-time)** | ≈0.006 SOL for 4 nonce accounts + a few token accounts | **rent — refundable** when the accounts are closed |
| **Lookup table (one-time)** | ≈0.002 SOL + ≈0.0002 SOL per address (usually 0.005–0.01 SOL) | rent, refundable; lets trades through other tokens fit a transaction |
| **Coin token account** | ≈0.002 SOL per coin while held | returned when the position is sold out |

**Net** on the page = what came back − what went in − 1% fee − network. Small buys pay relatively more network cost:
at 0.01 SOL per copy the network is ~2–3% of the buy per round trip; at 0.1 SOL it is ~0.25%.

## 8. Your wallet, Arb and other modes

- CopyTrade uses **the same wallet as your Arb bot**. The key never leaves diablo.bot's servers; you never type it.
- **WSOL is not touched:** your Arb capital in WSOL stays as it is. Buys wrap exactly their own SOL inside the buy;
  sale proceeds come back as SOL or WSOL in the same wallet.
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

- **Copies:** each copy — coin, source, terminal, **In, SOL**, **Now, SOL** (open) or result (closed), **Fee 1%**,
  **Network**, **Net, SOL**, state and transactions. Exit reasons are shown: timer, followed the wallet, take profit, stop
  loss, ×N, crowd, sold by you.
- **Today:** closed copies since 00:00 MSK; net = back − in − 1% − network.
- **Who to copy:** sources with your copies and net for 7 days; paused sources with the reason.
- **Settings:** Entry, Exit, Limits. Saving applies within seconds; if settings were changed in another tab, the page
  reloads them — edit again.
- Signals that were not copied are counted with reasons (crowd, slippage, first buy only, limits…).

## 11. Troubleshooting by symptom

| Symptom | Why | What to do |
|---|---|---|
| "Wallet is being prepared" for long / "fund it with SOL" | the wallet has less SOL than preparation needs | top up ~0.02 SOL; it retries every 2 minutes |
| No copies at all | copying is off, no sources, the source did not buy, or every buy was filtered | check the switch and sources; see the skip reasons under signals |
| Copies show "slippage" refusals | the price ran above your Slippage before your buy landed | normal for hot coins; raise Slippage only if you accept worse prices |
| Copies skipped "balance" / "keep" | SOL is below buy size + Keep for arb | top up or lower the size |
| Copies stopped for the day | Daily stop reached, or the source paused (cost / rugs) | resumes at 00:00 MSK; adjust limits if needed |
| Copying paused 10 minutes | 10 failed buys in a row (network trouble) | resumes by itself |
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
