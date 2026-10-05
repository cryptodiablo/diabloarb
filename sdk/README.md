# DiabloArb executor — build your own sender

The DiabloArb on-chain executor `DiabLokxisGR8P4Qqp2QL6PmBhhVsdzPstCE4WoLxc5z` finds and executes the most profitable
arbitrage route **at execution time**. You list candidate routes over hot pools; the program quotes them on chain,
picks the best route and the best amount, borrows from the DiabloArb flash-loan vault if needed, swaps, repays and
keeps the profit in your wallet — or does nothing / fails if there is no profit.

This folder lets you write your own sender against it:

| File | What |
|---|---|
| `README.md` | this guide: instruction format, accounts, every DEX's swap window, errors, budgets, a decoded real transaction |
| [`diabloarb-executor.idl.json`](diabloarb-executor.idl.json) | machine-readable description of the instruction (byte layout, enums, accounts, errors) |
| [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md) | instructions for AI coding agents (Codex, Claude Code…) building a sender from this folder |

There is **no Anchor IDL**: the program is not Anchor (pinocchio, sBPF v3) and its lists are counted by `u8` fields of a
fixed header, not Borsh vectors. The JSON above describes the same layout in plain terms.

The ready-made sender in this repository (`../sender`, `../README.md`) already does all of this; build your own only if
you want your own pool discovery, pricing or landing.

## Contents

1. [Terms and fees](#1-terms-and-fees)
2. [How a search works](#2-how-a-search-works)
3. [Instruction data](#3-instruction-data-tag-1-search)
4. [Accounts](#4-accounts)
5. [Hop windows](#5-hop-windows)
6. [Supported DEXs and their windows](#6-supported-dexs-and-their-windows)
7. [Transaction layout, compute budget, lookup tables](#7-transaction-layout-compute-budget-lookup-tables)
8. [Return data and errors](#8-return-data-and-errors)
9. [A real transaction, decoded](#9-a-real-transaction-decoded)
10. [Checklist](#10-checklist)

## 1. Terms and fees

- **Program:** `DiabLokxisGR8P4Qqp2QL6PmBhhVsdzPstCE4WoLxc5z` (upgradeable; deployed 2026-10-03, ELF SHA-256
  `a6d03e003bd69a78c310afa8aa8d11d68764bd89e79b8231fc8b3b60a6a0d6c0`).
- **Vault (flash loan):** PDA `Bank4kzA4xv6zsLfXXx4YrMK7io8fWTvCEHsbQZoh2Jc` (seeds `"bank"`, `3310317` as u64 LE,
  bump 255). Its token accounts lend to any signer, up to their whole balance, free, repaid in the same instruction:

  | Base | Mint | Vault token account |
  |---|---|---|
  | WSOL | `So11111111111111111111111111111111111111112` | `HGoYKDXhjq1CVXvCDxTZcYhthZj4nTp1R6WSoKSKgceb` |
  | USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | `8QrVSVbhMgpTMjXskuFmmF7WFe4SLLg43tvpQfsnGA7k` |
  | USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | `AzNFA4u7yGkLdN4wUJZ993JkYSiNhhyJnVAefiSLtPJr` |

- **Fee:** 7% of the realized profit (rounded up) goes to the vault token account of the profit's token, in the same
  instruction. Every signer pays it except the program owner. **You must always pass the vault section** (flag bit1):
  without it the program refuses anyone but the owner (`NotOwner`).
- You keep 93% of every profit; a transaction without profit costs you only the network fee and priority (and, on paid
  landing services, nothing more when it fails — see [§8](#8-return-data-and-errors)).
- Only `tag 1` (search) and `tag 2` (quote) are public. `tag 0` (fixed route) and `tag 3` (vault withdrawal) are
  owner-only.

## 2. How a search works

1. You pass **bases** (up to 4: the tokens your routes start and end in — WSOL, USDC, USDT), **windows** (swap steps:
   a pool + direction + its accounts) and **routes** (up to 16; each a base and 1–5 window indexes in swap order).
   A window used by several routes is listed once.
2. The program reads every window's pool state, computes each route's marginal rate and drops routes that cannot pay
   (product of rates ≤ 1). Live routes are searched highest rate first.
3. For each live route it searches the amount: starting at the base's `start`, growing, then narrowing by secant
   bounds until the profit is within `best / 2^(8 + rounds)` of the bound. The amount is capped by `max_in` and by your
   balance of the base plus the vault's.
4. The best route by value (`profit × weight >> 32`, lamports) runs if its value reaches `min_profit`. The vault lends
   first, the swaps run (each hop swaps exactly what the previous one delivered), the vault is repaid plus the fee,
   and the realized profit after the fee is checked against `min_profit` again.
5. With a **budget** (flag bit2) the search watches compute units: it stops early so that the best route found still
   executes within your transaction's limit, and refuses amounts whose execution would not fit.

The profit lands in your base token account (e.g. your WSOL ATA).

## 3. Instruction data (tag 1, search)

Little-endian, no padding.

```text
offset  size  field
0       1     tag = 1
1       1     flags: bit0 FAIL_WHEN_DRY, bit1 VAULT (required), bit2 BUDGET
2       1     rounds: precision (0 is fine); bit7 0x80 = HINT (bases' `start` is an estimate of the optimum)
3       8     min_profit: i64, lamports of value the best route must reach (checked before and after the fee)
11      1     n_bases   (1..=4)
12      1     n_windows (>=1)
13      1     n_routes  (1..=16)
14      24×n_bases   bases:   u64 weight | u64 start | u64 max_in
...     5×n_windows  windows: u8 dex | u8 flags | u8 first | u8 len | u8 out
...     (2+n)×n_routes routes: u8 base | u8 n_hops | n_hops × u8 window index
...     4     u32 budget — only with flag bit2
```

- **weight** — value of one base unit in lamports, Q32: WSOL `1 << 32` = `4294967296`; USDC/USDT `round(2^32 × 1e9 /
  (SOL price in USD × 1e6))` (at 150 USD/SOL ≈ 28 633 115 306). Only used to compare profits of different bases and to
  check `min_profit`.
- **start** — opening amount of the search, base units. A small amount (0.001–0.01 SOL) is safe; with `HINT` give your
  best estimate of the optimum (the search then starts there, cheaper in CU).
- **max_in** — your cap. Use `u64::MAX / 4` (`0x3fffffffffffffff`) for "no cap of mine": the program caps by your balance
  plus the vault anyway.
- **FAIL_WHEN_DRY** — set it on paid landing services (Jito, Temporal, Helius sender…): a transaction without profit
  then fails, so the tip inside it is not paid. Leave it off when you want a successful no-op (e.g. plain RPC spam).
- **min_profit** — the minimum value (lamports) worth executing: at least your tip + priority for that copy.
- **budget** — the transaction's compute-unit limit minus what runs before the executor (we reserve 30 000 CU per
  `CreateIdempotent` ATA instruction in the same transaction). Recommended.

## 4. Accounts

```text
0                       user                       signer, writable (pays the fee to the vault)
1 .. n_bases            base token accounts         writable: your SPL Token account of each base mint, in base order
                                                    (must exist; may hold 0 — the vault lends)
1+n_bases               vault PDA                   Bank4kzA4xv6zsLfXXx4YrMK7io8fWTvCEHsbQZoh2Jc
2+n_bases               SPL Token program           TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
3+n_bases ..            vault token accounts        writable, one per base in the same order (table in §1)
then                    hop windows                 for each window: the DEX program, then its swap accounts (§6)
```

- Indexes in windows (`first`, `out`) are positions in **this instruction's** account list (u8: up to 256 entries).
- The same account may appear many times (every window carries its own full account list, including your token
  accounts, the token programs, etc.). Only the **unique** accounts of the whole transaction count against Solana's
  account-lock limit — use address lookup tables (§7).
- Every intermediate token (the coin you route through) needs **your** token account for it, existing before the
  executor runs (create it in an earlier instruction of the same transaction with ATA `CreateIdempotent`, or beforehand).

## 5. Hop windows

```text
u8 dex    the DEX id (§6)
u8 flags  bit0 A_TO_B: swap the pool's token A into token B (which mint is A — per DEX, §6)
          bit1 PUMP_CANONICAL (Pump AMM only, §6)
          bit2 LEGACY: the older `swap` of Whirlpool / Raydium CLMM (+forks) / DLMM — classic SPL Token mints only;
               fewer accounts and 0.7–3.9 thousand CU less per swap, same output
u8 first  index of the DEX program account; its swap accounts are accounts[first+1 .. first+1+len]
u8 len    number of swap accounts after the program
u8 out    index of your token account that receives this hop's output
```

The program builds each swap's instruction data itself (exact input: the amount the previous hop delivered, minimum
out 0 — the route's profit check protects you) and passes the window's accounts to the DEX **in the order you give
them**, so the window must be exactly the account list of that DEX's swap instruction, as listed in §6.

A route's first hop takes the input from the base token account; each later hop swaps exactly what the previous hop
delivered (the balance change of its `out` account). The last hop's `out` must be the route's base token account.

## 6. Supported DEXs and their windows

Every window below is exactly the account list our router builds and the deployed executor accepts (checked against
the code on 5 October 2026). "Window index" = position after the DEX program (`accounts[first + 1 + index]`). Keep
the order and the writable/signer marks: the executor forwards both to the DEX unchanged, and reads some accounts at
**fixed window indexes** to quote on chain (section 6.16) — a window in another order may still swap but will be
quoted wrongly or dropped.

### 6.0 Common rules

#### Hop encoding

```
hop (5 bytes): u8 dex | u8 flags | u8 first | u8 len | u8 out
accounts[first]                    = DEX program id
accounts[first+1 .. first+1+len]   = the DEX swap instruction's accounts, in the DEX's order ("the window")
accounts[out]                      = the user's token account that receives this hop's output
flags: bit0 (1) a_to_b | bit1 (2) Pump canonical pool | bit2 (4) legacy (older `swap`), see per-DEX sections
```

In this document **window index `i`** means `accounts[first + 1 + i]` (index 0 = first account after the
program). The executor's `quote.rs` uses the same 0-based window indexes.

#### What the executor does with a window

- **CPI** (`swap`): it builds the CPI `AccountMeta`s from the window's `AccountView`s **unchanged**: same
  order, and `is_writable` / `is_signer` copied from the outer transaction. So the writable/signer
  privileges you give an account in the outer executor instruction are exactly what the DEX receives. Mark every
  window account as listed below.
- **Program**: CPI goes to `accounts[first]`. The executor does **not** check that this program matches
  the `dex` byte; the `dex` byte selects the instruction data layout and the on-chain quote math.
- **Instruction data**: `swap_data(dex, amount_in, min_out = 0, a_to_b, legacy)`. The executor
  always passes `min_out = 0` (Pump buy writes `max(min_out, 1)`); slippage protection is the
  executor's own profit check after the route, not a per-hop minimum.
- **Limits**: at most 48 accounts per window (`MAX_CPI_ACCOUNTS`, checked); hop indexes are
  `u8`, so the whole instruction must stay within 256 accounts (the sender refuses more).
- **Hop output**: after the CPI, the executor reads the SPL token amount (bytes 64..72) of `accounts[out]` and
  takes the balance delta as the next hop's input. `out` must be a token account (else
  `NotTokenAccount`). The sender sets `out` to the first position in the account list holding the
  user's token account of the hop's output mint.
- **On-chain quoting** (tag 1 search, tag 2 quote): the executor reads pool state, vault balances, mints (for
  Token-2022 transfer fees), tick/bin arrays at **fixed window indexes** per DEX (`quote.rs`, `legs.rs`). These
  offsets are listed per DEX below (subsection "Executor reads") and summarized in section 16. A window built in a
  different order may still CPI correctly but will be quoted wrongly or not at all (a failed quote drops the
  route).

#### Conventions used by the router

- `user` = the transaction signer (also `accounts[0]` of the executor instruction). Every window's signer slot
  is the same `user`.
- `user_a` / `user_b` = the user's token accounts for the venue's mint A / mint B (`Venue::mints()`), which the
  sender derives as ATA(user, mint, the mint's owner program: SPL Token or Token-2022) (associated token address:
  seeds `[owner, token_program, mint]`, program `ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL`).
- `a_to_b = true` swaps mint A for mint B. "A" is defined per DEX below.
- Programs used in windows:
  - SPL Token `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`, Token-2022 `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`
  - Memo `MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr`, System `11111111111111111111111111111111`
  - Associated Token `ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL`
- **Transfer hooks**: Our router skips any pool where either mint has an active Token-2022 transfer hook
  (non-zero hook program id): no window passes the hook's extra accounts, so the swap would fail (`dex_math::token2022::transfer_hook_active`).
- **Legacy flag** (`FLAG_LEGACY = 4`): only Whirlpool (4), Raydium CLMM family (5, 8) and
  Meteora DLMM (6) have a legacy variant. The router sets it **whenever both mints are owned by classic SPL
  Token** (`spl_only`) and never otherwise. Legacy is only valid for SPL-Token-only pairs (no Token-2022
  handling in the older instruction). The executor reads the bit for these three DEXes only (instruction data and window offsets); other DEXes ignore it.
- **Labels**: `W` = writable, `R` = read-only, `S` = signer.
- **Account letters for the "Executor reads" lines**: `amount(x)` = token account amount (bytes 64..72),
  `supply(x)` = mint supply (bytes 36..44), "T22 fee" = Token-2022 `TransferFeeConfig` read from the mint's data.

#### Pool kind detection (`kind_of`)

| owner program | condition | kind | Dex id |
|---|---|---|---|
| `CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C` | disc `account:PoolState` | cpmm | 0 |
| `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA` | disc `account:Pool` | pump | 1 / 2 |
| `675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8` | data len = 752 | v4 | 3 |
| `whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc` | disc `account:Whirlpool` | whirlpool | 4 |
| `CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK` | disc `account:PoolState` | clmm | 5 |
| `HpNfyc2Saw7RKkQd8nEL4khUcuPhQ7WwY1B2qjx8jxFq` (PancakeSwap CLMM) | disc `account:PoolState` | pancake | 5 |
| `REALQqNEomY6cQGZJUGwywTBD2UmDT32rZcNnfxQ5N2` (Byreal CLMM) | disc `account:PoolState` | byreal | 8 |
| `LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo` | disc `account:LbPair` | dlmm | 6 |
| `cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG` | disc `account:Pool` | damm2 | 7 |
| `MNFSTqtC93rEfYHB6hF82sKdZpUDFWkViLByLd1k1Ms` | u64 discriminant = 4859840929024028656 | manifest | 9 |
| `Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB` | damm1 pool discriminator | damm1 | 10 |
| `FUTARELBfJfQ8RDGhg1wdhddq1odMAJUePHFuBYfUxKq` | DAO discriminator | futarchy | 11 |
| `fUSioN9YKKSa3CUC2YUc4tPkHJ5Y6XW1yz8y6F7qWz9` | Fusion pool discriminator | fusion | 12 |
| `SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8`, `9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP` (Orca v2) | len = 324, bytes[0]=1 (version), bytes[1]=1 (initialized) | tokenswap | 13 |
| `dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN` | DBC pool discriminator and len = 424 | dbc | 14 |

---

### 6.1 Dex 0: Raydium CPMM

- **Program** (`accounts[first]`): `CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C`.
- **Instruction**: `swap_base_input`.
- **Mints**: A = `token_0_mint` (pool offset 168), B = `token_1_mint` (offset 200). `a_to_b` = token0 -> token1.

Pool fields used: `amm_config` (pool offset 8), vault 0/1 (offsets 72/104), mint 0/1 (168/200), token program
0/1 (offsets 232/264), observation (offset 296) (`dex_math::cpmm::pool`).

| idx | account | W/R | S |
|---|---|---|---|
| 0 | user (payer) | R | S |
| 1 | CPMM authority `GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL` (constant) | R | |
| 2 | amm config (pool +8) | R | |
| 3 | pool state | W | |
| 4 | user input token account (`user_a` if a_to_b else `user_b`) | W | |
| 5 | user output token account (`user_b` if a_to_b else `user_a`) | W | |
| 6 | input vault (vault 0 if a_to_b else vault 1) | W | |
| 7 | output vault | W | |
| 8 | input token program (of input mint) | R | |
| 9 | output token program | R | |
| 10 | input mint | R | |
| 11 | output mint | R | |
| 12 | observation state (pool +296) | W | |

Fixed length 13. Flags: bit0 = a_to_b (token0 in). No legacy, no canonical.

**Executor reads**: config = w[2], pool = w[3], `amount(w[6])` input vault,
`amount(w[7])` output vault (mapped back to vault0/1 by a_to_b), mints w[10] (in) / w[11] (out) for T22 fees.
Quote fails if the pool's swap is disabled or before `open_time`.

---

### 6.2 Dex 1 / 2: Pump AMM (PumpSell / PumpBuy)

- **Program**: `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA`.
- **Dex id by direction**: `a_to_b = true` (sell base for quote) -> **1 PumpSell** (`sell`);
  `a_to_b = false` (quote in, base out) -> **2 PumpBuy** (`buy_exact_quote_in`; data also carries
  `track_volume = None`).
- **Mints**: A = base mint (pool offset 43), B = quote mint (pool offset 75) (`dex_math::pump::pool`).

Derived accounts (all PDAs under the Pump AMM program unless stated):

- `global_config` = PDA `["global_config"]`.
- `fee_config` = PDA `["fee_config", PUMP_AMM program id]` under the **Pump fee program**
  `pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ`.
- `event_authority` = PDA `["__event_authority"]`.
- `creator_vault_authority` = PDA `["creator_vault", coin_creator]`, `coin_creator` = pool offset 211.
- `user_volume_accumulator` = PDA `["user_volume_accumulator", user]`.
- `global_volume_accumulator` = PDA `["global_volume_accumulator"]`.
- `pool_v2` = PDA `["pool-v2", base_mint]`.
- `ATA_q(owner)` = ATA(owner, quote_mint, quote mint's token program).
- **Protocol fee recipient**: one of the 8 keys in `global_config` at offsets `57 + 32*i` (i = 0..7); the router
  takes, among those whose quote ATA exists, the one whose quote-ATA bump is highest (cheaper for the program to
  derive).
- **Buyback recipient**: one of the 8 keys at `global_config` offsets `643 + 32*i`; same rule, falling back to the
  first key when none has a quote ATA.
- `is_cashback` = pool byte 244 != 0. `is_pump_pool` (canonical) = pool `creator` (offset 11) equals PDA
  `["pool-authority", base_mint]` under the **Pump bonding-curve program** `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P`.

`accounts(sell, user, user_base, user_quote)` — note the user accounts are passed as base/quote, i.e. `user_a`
= user base account, `user_b` = user quote account, independent of direction.

| idx (sell) | idx (buy) | account | W/R | S |
|---|---|---|---|---|
| 0 | 0 | pool | W | |
| 1 | 1 | user | **W** | S |
| 2 | 2 | global_config | R | |
| 3 | 3 | base mint | R | |
| 4 | 4 | quote mint | R | |
| 5 | 5 | user base token account | W | |
| 6 | 6 | user quote token account | W | |
| 7 | 7 | pool base vault (pool +139) | W | |
| 8 | 8 | pool quote vault (pool +171) | W | |
| 9 | 9 | protocol fee recipient | R | |
| 10 | 10 | ATA_q(protocol fee recipient) | W | |
| 11 | 11 | base token program | R | |
| 12 | 12 | quote token program | R | |
| 13 | 13 | System program | R | |
| 14 | 14 | Associated Token program | R | |
| 15 | 15 | event_authority | R | |
| 16 | 16 | Pump AMM program | R | |
| 17 | 17 | ATA_q(creator_vault_authority) | W | |
| 18 | 18 | creator_vault_authority | R | |
| — | 19 | global_volume_accumulator (buy only) | R | |
| — | 20 | user_volume_accumulator (buy only) | W | |
| 19 | 21 | fee_config | R | |
| 20 | 22 | Pump fee program `pfeeUx…` | R | |
| *remaining accounts, in this order:* |||||
| +0 | +0 | if `is_cashback`: ATA_q(user_volume_accumulator) | W | |
| +1 | — | if `is_cashback` and sell: user_volume_accumulator | W | |
| next | next | if `coin_creator != 0`: pool_v2 | R | |
| next | next | buyback recipient | R | |
| last | last | ATA_q(buyback recipient) | W | |

Length: sell 21 + tail, buy 23 + tail; tail = [cashback: 2 (sell) / 1 (buy)] + [pool_v2: 1 if coin creator set]
+ 2. The remaining-accounts order follows pump-swap-sdk 1.20.0 `offlinePumpAmm`.

**Flags**: bit0 = sell (`a_to_b`, base in); **bit1 = Pump canonical**: set when the pool is the
canonical pool of a token graduated from the Pump bonding curve (`is_pump_pool` above). It selects the fee schedule:
for canonical pools the fee comes from `fee_config` tiers by market cap (for SOL / wSOL-2022 quote: market-cap
tiers; other branches in `dex_math::pump::FeeConfig::fees_for`), otherwise flat fees (``).
The executor cannot afford the PDA derivation on chain, so it trusts this bit.
Setting it wrongly makes the on-chain quote use the wrong fee; the actual swap is unaffected. No legacy.

**Executor reads**: pool = w[0], global_config = w[2], base mint = w[3]
(supply for market cap, and T22 fee), quote mint = w[4], `amount(w[7])` base vault, `amount(w[8])` quote vault,
**fee_config = w[19] for sell, w[21] for buy** (it must be at exactly that index). Input/output mints for T22
fees: sell (w[3], w[4]), buy (w[4], w[3]).

---

### 6.3 Dex 3: Raydium AMM V4

- **Program**: `675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8`.
- **Instruction**: `swap_base_in_v2` (tag 16, 8 accounts, no OpenBook/Serum accounts).
- **Mints**: A = coin mint (amm offset 400), B = pc mint (offset 432). `a_to_b` = coin -> pc.

| idx | account | W/R | S |
|---|---|---|---|
| 0 | SPL Token program (always classic) | R | |
| 1 | amm (pool) | W | |
| 2 | V4 authority `5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1` = PDA `["amm authority"]` (asserted) | R | |
| 3 | coin vault (amm +336) | W | |
| 4 | pc vault (amm +368) | W | |
| 5 | user input token account (`user_a` if a_to_b else `user_b`) | W | |
| 6 | user output token account | W | |
| 7 | user | R | S |

Fixed length 8. Vaults are in coin/pc order regardless of direction. Flags: bit0 only.

**Executor reads**: amm = w[1], `amount(w[3])` coin vault, `amount(w[4])` pc
vault. No Token-2022 handling (V4 is SPL Token only). Quote fails when `can_swap` is false (status / open time).

---

### 6.4 Dex 4: Orca Whirlpool

- **Program**: `whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc`.
- **Instruction**: `swap_v2`, or legacy `swap`. The data carries `a_to_b` explicitly
  (`amount_specified_is_input = 1`, no price limit, `remaining_accounts_info = None` in v2).
- **Mints**: A = `token_mint_a` (pool offset 101), B = `token_mint_b` (offset 181). Vaults A/B offsets 133/213.

PDAs:
- tick array = PDA `["tick_array", pool, start_tick_index as decimal ASCII string]`, e.g. `"-5632"`.
- oracle = PDA `["oracle", pool]`.

Tick array selection (`Whirlpool::tick_array_starts`, ``): with
`T = 88 * tick_spacing` and `base = floor(tick_current_index / T) * T`:
- a_to_b: starts `base, base - T, base - 2T`;
- b_to_a: `base + T, base + 2T, base + 3T` if `tick_current_index + tick_spacing >= base + T`, else `base, base + T, base + 2T`;
- starts outside the valid tick range are dropped (so fewer than 3 near the price limits).
The router always passes **3** tick-array accounts: missing ones are filled by repeating the last valid one
(or the pool address if none). Tick-array accounts that do not exist on chain are passed anyway
(the load step only requires them to have been fetched, "absent on chain is fine"); the executor
treats an empty account as a zeroed array at its start.

**v2 window** (non-legacy; any pair with a Token-2022 mint):

| idx | account | W/R | S |
|---|---|---|---|
| 0 | token program A (owner of mint A) | R | |
| 1 | token program B | R | |
| 2 | Memo program | R | |
| 3 | user (token authority) | R | S |
| 4 | whirlpool | W | |
| 5 | mint A | R | |
| 6 | mint B | R | |
| 7 | user token account A (`user_a`) | W | |
| 8 | vault A | W | |
| 9 | user token account B (`user_b`) | W | |
| 10 | vault B | W | |
| 11 | tick array 0 | W | |
| 12 | tick array 1 | W | |
| 13 | tick array 2 | W | |
| 14 | oracle PDA | W | |

**Legacy window** (`FLAG_LEGACY`, both mints classic SPL Token; `swap`):

| idx | account | W/R | S |
|---|---|---|---|
| 0 | token program (SPL Token) | R | |
| 1 | user (token authority) | R | S |
| 2 | whirlpool | W | |
| 3 | user token account A | W | |
| 4 | vault A | W | |
| 5 | user token account B | W | |
| 6 | vault B | W | |
| 7 | tick array 0 | W | |
| 8 | tick array 1 | W | |
| 9 | tick array 2 | W | |
| 10 | oracle PDA | W | |

User and vault accounts are always in A/B order (not input/output); direction is only in the data.
Fixed length: 15 (v2) / 11 (legacy).

**Flags**: bit0 = a_to_b (A in); bit2 = legacy, set by the router iff both mints are SPL Token.

**Executor reads**: pool = w[4] (legacy w[2]); the executor recomputes
`tick_array_starts(a_to_b)` from the pool on chain and reads the first `n` arrays from w[11..] (legacy w[7..]);
oracle at w[14] (legacy w[10]), empty = no oracle. Mints for T22 fees: w[5]/w[6] (v2 only).
**The tick arrays must be passed in the `tick_array_starts` order.**

---

### 6.5 Dex 5: Raydium CLMM (and PancakeSwap CLMM) — and Dex 8: Byreal CLMM

One builder (`ClmmVenue`) for three programs with the same accounts and instructions:

| program | kind | Dex id |
|---|---|---|
| Raydium CLMM `CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK` | clmm | **5** RaydiumClmm |
| PancakeSwap CLMM `HpNfyc2Saw7RKkQd8nEL4khUcuPhQ7WwY1B2qjx8jxFq` (Raydium fork) | pancake | **5** RaydiumClmm |
| Byreal CLMM `REALQqNEomY6cQGZJUGwywTBD2UmDT32rZcNnfxQ5N2` | byreal | **8** ByrealClmm |

`dex()` returns 8 when the pool was parsed by `Clmm::parse_byreal` (pool owned by the Byreal program), else 5. Put the pool's actual owner program at `accounts[first]`. Byreal pools with the
Pyth dynamic fee (byte at offset 1096 has bit `0x10`) are not supported (``). Byreal
uses its own fee rules on the same accounts. The executor tells PancakeSwap apart only for its
compute-budget estimate, by the program at `accounts[first]`.

- **Instruction**: `swap_v2` or legacy `swap`, `is_base_input = 1`, no price limit. Direction comes
  from which token accounts are passed (input/output), not from the data.
- **Mints**: A = `token_mint_0` (pool offset 73), B = `token_mint_1` (offset 105); `a_to_b` = zero_for_one.
  Pool: amm_config +9, vault 0/1 +137/+169, observation +201.

PDAs (under the pool's own program):
- tick array = PDA `["tick_array", pool, start_tick_index as i32 big-endian 4 bytes]`.
- tick-array bitmap extension = PDA `["pool_tick_array_bitmap_extension", pool]`.

Tick array selection: `Clmm::tick_array_starts(ext, zero_for_one)` (``)
lists the first array the swap uses (the current one if initialized in the bitmap, else the next initialized one in
the direction) and the following initialized ones. The router then keeps only arrays whose accounts **exist**, and
of those **1 or 2**: the second only when the first is not the current tick's array, or the current tick lies in
the half of its array toward the swap direction. Array span = 60 * tick_spacing.
The extension is passed **only when the account exists** ("the program stops at the first account it does not
know").

**v2 window** (non-legacy):

| idx | account | W/R | S |
|---|---|---|---|
| 0 | user (payer) | R | S |
| 1 | amm config | R | |
| 2 | pool state | W | |
| 3 | user input token account (`user_a` if a_to_b else `user_b`) | W | |
| 4 | user output token account | W | |
| 5 | input vault (vault 0 if a_to_b) | W | |
| 6 | output vault | W | |
| 7 | observation state | W | |
| 8 | SPL Token program | R | |
| 9 | Token-2022 program | R | |
| 10 | Memo program | R | |
| 11 | input mint | R | |
| 12 | output mint | R | |
| 13 | [bitmap extension, if it exists] | W | |
| 13/14.. | tick arrays (1–2 by the router), in swap order | W | |

**Legacy window** (`swap`; both mints SPL Token):

| idx | account | W/R | S |
|---|---|---|---|
| 0–8 | same as v2 idx 0–8 (user … SPL Token program) | | |
| 9.. | tick arrays (1–2), the first is the instruction's named `tick_array` | W | |
| last | [bitmap extension, if it exists] — after the tick arrays | W | |

Length: v2 13 + [1] + n_arrays; legacy 9 + n_arrays + [1].

**Flags**: bit0 = zero_for_one (mint 0 in); bit2 = legacy iff both mints SPL Token.

**Executor reads**: config = w[1] (trade fee rate at config offset 47),
pool = w[2]; every account from w[13] (legacy w[9]) on is classified **by data length**: length
`8 + 32 + 64*14*2 = 1832` = bitmap extension, anything else must parse as a tick array (max 10 arrays used) —
a non-existent tick array in the tail breaks the quote. Mints for T22 fees: w[11] (in) / w[12] (out), v2 only.
Tick arrays must be in the swap's walking order.

---

### 6.6 Dex 6: Meteora DLMM

- **Program**: `LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo`.
- **Instruction**: `swap2` (with `remaining_accounts_info` = no slices), or legacy `swap`.
- **Mints**: A = token X (lb_pair offset 88), B = token Y (offset 120); `a_to_b` = swap_for_y (X in).
  Reserves X/Y at +152/+184, oracle at +552.

PDAs:
- bin array = PDA `["bin_array", lb_pair, (index as i64) little-endian 8 bytes]`.
- bitmap extension = PDA `["bitmap", lb_pair]`.
- event authority = PDA `["__event_authority"]`.

Bin array selection: `LbPair::bin_arrays_for_swap` (``) lists bin arrays
**with liquidity** starting at the active bin's array (`bin_array_index(active_id)`, 70 bins per array) in the
swap direction (X->Y: decreasing index). The router keeps **1 or 2**: the second only when the first is not the
active array or the active bin is in the half of its array toward the swap direction; then only those whose
account exists.

Host fee account (`host_fee_in`, idx 9): when the pair pays a host share
(`protocol_share > 0`) and the fee token has no Token-2022 transfer fee:
- fee taken on the output (`LbPair::fee_on_input` is false: `collect_fee_mode == 1` and the swap is X->Y; with mode 1
  the fee is always in token Y) -> the user's **output** token account;
- fee taken on the input and the input mint is wSOL, USDC or USDT -> the user's **input** token account;
- otherwise -> the DLMM program id (Anchor "None").

| idx | account | W/R | S |
|---|---|---|---|
| 0 | lb_pair | W | |
| 1 | bitmap extension if it exists (W), else the DLMM program id (R) | W/R | |
| 2 | reserve X | W | |
| 3 | reserve Y | W | |
| 4 | user input token account (`user_a` if a_to_b else `user_b`) | W | |
| 5 | user output token account | W | |
| 6 | mint X | R | |
| 7 | mint Y | R | |
| 8 | oracle | W | |
| 9 | host fee account: user output (W), user input (W), or DLMM program id (R) | W/R | |
| 10 | user | R | S |
| 11 | token program X | R | |
| 12 | token program Y | R | |
| 13 | Memo program — **omitted in the legacy window** | R | |
| 14 (13) | event authority PDA | R | |
| 15 (14) | DLMM program | R | |
| 16.. (15..) | bin arrays (1–2 by the router), swap order | W | |

(Numbers in parentheses = legacy window.) Length: 16 + n_arrays (legacy 15 + n_arrays). The executor's
comment sizes the longest window as DLMM with 10 bin arrays = 26 accounts.

**Flags**: bit0 = swap_for_y (X in); bit2 = legacy (`swap`, no memo account) iff both mints SPL Token.

**Executor reads**: pair = w[0]; w[1] is the extension iff its data length
equals `BitmapExtension::LEN` (1576); bin arrays from w[16] (legacy w[15]) to the end, each must parse as a bin
array (up to 10; a non-existent account breaks the quote); mints w[6]/w[7] for T22 fees (in = w[6] if a_to_b).
**Fee share** (`DLMM_SHARE = [9, 4, 5]`): the executor compares the address at w[9] with w[4] (input) and
w[5] (output): equal to w[5] -> the host share is counted into the hop output; equal to w[4] -> counted as profit
returned to the route's input (first hop only); anything else -> no share. The compute budget adds
the share transfer whenever w[9] is not the program id at `accounts[first]`.

---

### 6.7 Dex 7: Meteora DAMM v2 (CP-AMM)

- **Program**: `cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG`.
- **Instruction**: `swap2`, `SwapMode::ExactIn`.
- **Mints**: A = token A mint (pool offset 168), B = token B (offset 200); vaults +232/+264.

PDAs: pool authority = PDA `["pool_authority"]`; event authority = PDA `["__event_authority"]`.

Referral account (idx 11): when the pool pays a referral share (`protocol_fee_percent > 0` and
`referral_fee_percent > 0`) and the fee token has no T22 transfer fee: fee on the output -> the user's **output**
account; fee on the input (`!a_to_b && collect_fee_mode in {1,2}`) and the input mint is wSOL/USDC/USDT -> the
user's **input** account; otherwise the DAMM v2 program id.

| idx | account | W/R | S |
|---|---|---|---|
| 0 | pool authority PDA | R | |
| 1 | pool | W | |
| 2 | user input token account (`user_a` if a_to_b else `user_b`) | W | |
| 3 | user output token account | W | |
| 4 | vault A | W | |
| 5 | vault B | W | |
| 6 | mint A | R | |
| 7 | mint B | R | |
| 8 | user (payer) | R | S |
| 9 | token program A | R | |
| 10 | token program B | R | |
| 11 | referral token account: user output (W), user input (W), or DAMM v2 program id (R) | W/R | |
| 12 | event authority PDA | R | |
| 13 | DAMM v2 program | R | |

Fixed length 14. Flags: bit0 = a_to_b (A in).

**Executor reads**: pool = w[1]; mints w[6]/w[7] (in = w[6] if a_to_b) for T22
fees; **fee share** `DAMM2_SHARE = [11, 2, 3]`: w[11] equal to w[3] -> referral counted into output, equal to w[2] ->
returned to input; else none. Budget adds the transfer when w[11] is not the program id.
Quote fails when `pool_status != 0` or before the activation point (spot path).

---

### 6.8 Dex 8: Byreal CLMM

Same window, PDAs, tick-array rules, legacy flag and executor offsets as **section 5** (Raydium CLMM). Program
`REALQqNEomY6cQGZJUGwywTBD2UmDT32rZcNnfxQ5N2`; Dex id 8 so the executor parses the pool with
`Clmm::parse_byreal` (Byreal fee rate at pool offset 393, decay-fee parameters at 1096..1100) (``). Pools with the Pyth dynamic fee flag are rejected. The executor comment notes
Byreal tick arrays may be "fixed or dynamic".

---

### 6.9 Dex 9: Manifest

- **Program**: `MNFSTqtC93rEfYHB6hF82sKdZpUDFWkViLByLd1k1Ms`.
- **Instruction**: `Swap` (tag 4), `is_base_in = a_to_b`, `is_exact_in = 1`.
- **Mints**: A = base mint (market offset 16), B = quote mint (offset 48); vaults +80/+112. `a_to_b` = sell base.

| idx | account | W/R | S |
|---|---|---|---|
| 0 | user (payer) | **W** | S |
| 1 | market | W | |
| 2 | System program | R | |
| 3 | user base token account (`user_a`) | W | |
| 4 | user quote token account (`user_b`) | W | |
| 5 | base vault | W | |
| 6 | quote vault | W | |
| 7 | base token program | R | |
| 8 | base mint | R | |
| 9 | quote token program | R | |
| 10 | quote mint | R | |

Fixed length 11; user accounts in base/quote order regardless of direction. **No global-order accounts** are
passed, so matching stops at a global order. Flags: bit0 only (also encoded in data).

**Executor reads**: market = w[1]; mints w[8] (base) / w[10] (quote) for T22 fees.

---

### 6.10 Dex 10: Meteora Pools (DAMM v1)

- **Program**: `Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB`; Meteora vault program
  `24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi`.
- **Instruction**: Anchor `swap`.
- **Mints**: A = token A mint (pool offset 40), B = token B (offset 72). SPL Token only.

Accounts read from the pool: a/b vault (+104/+136), pool's a/b vault LP token accounts (+168/+200), protocol
token a/b fee accounts (+234/+266). From each Meteora vault account: its token vault (vault +19) and LP mint
(vault +115). (A helper `meteora_vault(mint)` derives vault = PDA `["vault", mint,
HWzXGcGHy4tcpYfaRDCyLNzXqBTv3E6BttpCH2vJxArv]` and token vault = PDA `["token_vault", vault]` under the vault
program, but `accounts()` uses the addresses stored in the pool/vaults; LP mints are not PDAs on old
vaults.) Depeg (LST) stable pools and unknown layouts are rejected (`damm1::Pool::parse`).

| idx | account | W/R | S |
|---|---|---|---|
| 0 | pool | W | |
| 1 | user source (input) token account (`user_a` if a_to_b else `user_b`) | W | |
| 2 | user destination (output) token account | W | |
| 3 | a vault (Meteora vault account) | W | |
| 4 | b vault | W | |
| 5 | a token vault | W | |
| 6 | b token vault | W | |
| 7 | a vault LP mint | W | |
| 8 | b vault LP mint | W | |
| 9 | pool's a vault LP account | W | |
| 10 | pool's b vault LP account | W | |
| 11 | protocol fee account **of the input token** (token A fee if a_to_b, else token B fee) | W | |
| 12 | user | R | S |
| 13 | Meteora vault program | R | |
| 14 | SPL Token program | R | |

Fixed length 15. Flags: bit0 only.

**Executor reads**: pool = w[0], vault a/b = w[3]/w[4] (parsed vault state),
`amount(w[5])`, `amount(w[6])` token vaults, `supply(w[7])`, `supply(w[8])` LP mints, `amount(w[9])`,
`amount(w[10])` pool LP accounts — all in A/B order.

---

### 6.11 Dex 11: MetaDAO Futarchy (spot)

- **Program**: `FUTARELBfJfQ8RDGhg1wdhddq1odMAJUePHFuBYfUxKq`.
- **Instruction**: Anchor `spot_swap`: `input_amount`, `swap_type` (= `a_to_b`: 1 Sell = base in, 0 Buy = quote
  in), `min_output_amount`.
- **Pool account**: the DAO account (the AMM lives in it). Mints/vaults are read from the DAO at layout-dependent
  offsets (`dex_math::futarchy::Amm::parse`, ``).
- **Mints**: A = base, B = quote; `a_to_b` sells base. SPL Token only.

| idx | account | W/R | S |
|---|---|---|---|
| 0 | DAO | W | |
| 1 | user base token account (`user_a`) | W | |
| 2 | user quote token account (`user_b`) | W | |
| 3 | AMM base vault | W | |
| 4 | AMM quote vault | W | |
| 5 | user | R | S |
| 6 | SPL Token program | R | |
| 7 | event authority = PDA `["__event_authority"]` (Futarchy program) | R | |
| 8 | Futarchy program | R | |

Fixed length 9; user accounts in base/quote order. Flags: bit0 (also in data).

**Executor reads**: only w[0] (reserves come from the DAO data, not from vault balances).

---

### 6.12 Dex 12: Fusion AMM

- **Program**: `fUSioN9YKKSa3CUC2YUc4tPkHJ5Y6XW1yz8y6F7qWz9`.
- **Instruction**: Anchor `swap` with Whirlpool `swap_v2` arguments: amount, min out, no price limit,
  `amount_specified_is_input = 1`, `a_to_b`, `remaining_accounts_info = None`.
- **Mints**: A = mint A (pool offset 11), B = mint B (offset 43); vaults +75/+107.

Tick arrays: PDA `["tick_array", pool, start as decimal ASCII string]` under the Fusion program.
Always **exactly 3**, from `FusionPool::tick_array_starts(a_to_b)` (``): with
`size = 88 * tick_spacing` and `first` = start of the current tick's array: a_to_b `first, first - size, first - 2*size`;
b_to_a `first, first + size, first + 2*size`. Passed whether they exist or not (a missing one counts as empty).

| idx | account | W/R | S |
|---|---|---|---|
| 0 | token program A | R | |
| 1 | token program B | R | |
| 2 | Memo program | R | |
| 3 | user | R | S |
| 4 | pool | W | |
| 5 | mint A | R | |
| 6 | mint B | R | |
| 7 | user token account A (`user_a`) | W | |
| 8 | user token account B (`user_b`) | W | |
| 9 | vault A | W | |
| 10 | vault B | W | |
| 11 | tick array 0 | W | |
| 12 | tick array 1 | W | |
| 13 | tick array 2 | W | |

Note the order differs from Whirlpool: **user A, user B, vault A, vault B**. Fixed length 14. Flags: bit0
(A in; also in data). No legacy.

**Executor reads**: pool = w[4]; tick arrays w[11..14] (empty data = empty array at the
recomputed start); mints w[5]/w[6] (in = w[5] if a_to_b) for T22 fees.

---

### 6.13 Dex 13: SPL Token Swap (and Orca v2)

- **Programs**: SPL Token Swap `SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8` or its fork Orca v2
  `9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP` — the pool's owner goes to `accounts[first]`.
  Saros (`SSwapUty…`) has the same layout but is **not supported** (its deployed program charges a different fee).
- **Instruction**: `Swap` (tag 1).
- **Mints**: A = mint A (pool offset 131), B = mint B (offset 163); token accounts A/B +35/+67; pool mint +99; fee
  account +195. Only pools whose stored token program (offset 3) is classic SPL Token and that are initialized
  constant-product pools.

Authority: `create_program_address([pool, [bump]], program)` with `bump` = pool data byte 2.

| idx | account | W/R | S |
|---|---|---|---|
| 0 | swap pool | R | |
| 1 | pool authority | R | |
| 2 | user (transfer authority) | R | S |
| 3 | user input token account (`user_a` if a_to_b else `user_b`) | W | |
| 4 | pool input token account (A if a_to_b) | W | |
| 5 | pool output token account | W | |
| 6 | user output token account | W | |
| 7 | pool mint | W | |
| 8 | pool fee account | W | |
| 9 | SPL Token program | R | |

Fixed length 10. Flags: bit0 only.

**Executor reads**: pool = w[0], `amount(w[4])` input reserve, `amount(w[5])` output reserve.

---

### 6.14 Dex 14: Meteora Dynamic Bonding Curve (DBC)

- **Program**: `dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN`.
- **Instruction**: Anchor `swap` (exact input).
- **Mints**: A = base mint (pool offset 136), B = quote mint (config offset 8); base/quote vault pool +168/+200;
  config = pool +72. `a_to_b` = base in.

PDAs: pool authority = PDA `["pool_authority"]`; event authority = PDA `["__event_authority"]` (DBC program).
Transfer-hook pools (their own layouts) are not supported (``).

| idx | account | W/R | S |
|---|---|---|---|
| 0 | pool authority PDA | R | |
| 1 | config | R | |
| 2 | pool | W | |
| 3 | user input token account (`user_a` if a_to_b else `user_b`) | W | |
| 4 | user output token account | W | |
| 5 | base vault | W | |
| 6 | quote vault | W | |
| 7 | base mint | R | |
| 8 | quote mint | R | |
| 9 | user (payer) | R | S |
| 10 | base token program | R | |
| 11 | quote token program | R | |
| 12 | referral token account: none = the DBC program id | R | |
| 13 | event authority PDA | R | |
| 14 | DBC program | R | |

Fixed length 15. Flags: bit0 only.

**Executor reads**: config = w[1], pool = w[2]; mints w[7] (base) / w[8] (quote) for T22
fees (in = w[7] if a_to_b).

---

### 6.15 Flags summary

| bit | value | meaning | DEXes |
|---|---|---|---|
| 0 | 1 | `a_to_b`: mint A in (A as defined per DEX). For Whirlpool, Fusion, Futarchy, Manifest it is also written into the instruction data; Pump encodes direction in the Dex id (1 sell / 2 buy) **and** bit0. For all others the DEX infers direction from the token accounts, but the executor's quote still uses bit0, so it must match the window. | all |
| 1 | 2 | Pump canonical pool (pool creator = `pool-authority` PDA of the base mint under `6EF8rr…`): fee-tier schedule in the on-chain quote | 1, 2 |
| 2 | 4 | legacy `swap` + legacy window; only for SPL-Token-only pairs | 4, 5, 6, 8 |

---

### 6.16 Executor offset requirements (external builders must respect these)

The executor's quoting (`quote.rs`, mirrored by `legs.rs` and `spot`) reads accounts by window index. For each
DEX, the following positions are load-bearing; everything else is only forwarded in the CPI.

| Dex | window indexes the executor reads | notes |
|---|---|---|
| 0 CPMM | w[2] config, w[3] pool, w[6]/w[7] in/out vault amounts, w[10]/w[11] in/out mints | |
| 1/2 Pump | w[0] pool, w[2] global config, w[3] base mint (supply), w[4] quote mint, w[7] base vault, w[8] quote vault, **w[19] (sell) / w[21] (buy) fee config** | flag bit1 = canonical |
| 3 V4 | w[1] amm, w[3] coin vault, w[4] pc vault | |
| 4 Whirlpool | v2: w[4] pool, w[5]/w[6] mints A/B, w[11..14] tick arrays, w[14] oracle; legacy: w[2] pool, w[7..10] tick arrays, w[10] oracle | arrays in `tick_array_starts` order; empty = zeroed |
| 5/8 CLMM, Pancake, Byreal | w[1] config, w[2] pool, v2: w[11]/w[12] in/out mints, tail from w[13]; legacy: tail from w[9] | tail: extension recognized by length 1832, every other tail account must be an existing tick array (≤ 10 used) |
| 6 DLMM | w[0] pair, w[1] extension (by length 1576) or program, w[4]/w[5] user in/out (share check), w[6]/w[7] mints X/Y, w[9] host account, bin arrays from w[16] (legacy w[15]) | all tail accounts must be existing bin arrays (≤ 10); share: |
| 7 DAMM v2 | w[1] pool, w[2]/w[3] user in/out (share check), w[6]/w[7] mints A/B, w[11] referral | |
| 9 Manifest | w[1] market, w[8] base mint, w[10] quote mint | |
| 10 DAMM v1 | w[0] pool, w[3]/w[4] vaults, w[5]/w[6] token vaults, w[7]/w[8] LP mints, w[9]/w[10] pool LP accounts | |
| 11 Futarchy | w[0] DAO | |
| 12 Fusion | w[4] pool, w[5]/w[6] mints, w[11..14] tick arrays | |
| 13 TokenSwap | w[0] pool, w[4] input reserve, w[5] output reserve | |
| 14 DBC | w[1] config, w[2] pool, w[7]/w[8] mints | |

Other executor-side requirements:

- **Signer**: the window's signer account is forwarded with the signer flag from the outer instruction; the router
  always uses `accounts[0]` (the executor's signer) there.
- **Fee shares** (DLMM w[9], DAMM v2 w[11]): the executor classifies them by address equality with the window's
  user input/output accounts. Pass the DEX program id to mean "none". Any other account is treated as no share in
  the quote, but the budget estimate still charges the transfer.
- **PancakeSwap** is identified only for compute-budget estimates, by the 32 bytes of `accounts[first]`
  (`budget::PANCAKE`).
- **Per-window caching**: in a tag 1 search a window index used by several routes is quoted from one cached state
  (`legs.rs`); windows are deduplicated by (pool, direction) in the sender.
- **Legacy bit** changes both the data and the offsets the executor reads; set it only together with
  the legacy window.

## 7. Transaction layout, compute budget, lookup tables

A typical transaction (the real one in §9 is exactly this):

1. *(paid landing services)* the tip — a System transfer to the service's tip account. It is inside the transaction,
   so with `FAIL_WHEN_DRY` a miss fails and the tip is not paid. *(durable nonce)* `AdvanceNonceAccount` goes first
   instead when you sign over a nonce.
2. `SetComputeUnitLimit` — enough for the search and the best route. Winning searches use ~150–380 thousand CU;
   misses ~40 thousand. We use 350–550 thousand depending on the number of routes.
3. `SetComputeUnitPrice` — your priority (µlamports per CU; priority in lamports = price × limit / 10⁶).
4. `SetLoadedAccountsDataSizeLimit` — the sum of the data sizes of all accounts the transaction loads (programs
   included), rounded up. Optional, but a tight limit lowers the transaction's cost for the scheduler.
5. *(new coins)* ATA `CreateIdempotent` for every intermediate token account you do not have yet.
6. The executor's search instruction, with the `BUDGET` flag set to the limit minus what the earlier instructions
   spend.

**Lookup tables.** A two-route transaction touches 40–70 unique accounts; Solana allows at most 64 locked accounts
and 1232 bytes. Put pools, their vaults, bin/tick arrays, programs, mints and your token accounts in address lookup
tables. The live list `https://moneyprinter.bot/auto/mplutall.txt` contains public tables covering the hot pools of
`https://moneyprinter.bot/auto/mp.toml` — you can use them.

**Pool discovery.** `https://moneyprinter.bot/auto/mp.toml` lists, live, whole routes the on-chain arbitrage bots are
winning right now, hottest first (`[[group]] markets = [...]`, one route per group). It is a good source of windows.

## 8. Return data and errors

Return data of a search (19 bytes): `u8 route | u64 amount_in | u64 profit | u16 quotes` — `route` is the index of
the executed route (255: none reached `min_profit`, a no-op), `profit` in base units before the fee, `quotes` the
number of on-chain quotes the search made. With `simulateTransaction` it tells you what would execute and why.

| Code | Name | Meaning |
|---|---|---|
| 1 (0x1) | InvalidData | malformed data: counts out of range, sizes do not add up, unknown tag |
| 2 (0x2) | AccountIndex | an index (`first`, `out`, base, vault) points past the account list |
| 3 (0x3) | Unprofitable | the route executed but realized less than expected (state moved) or, after the fee, below `min_profit` |
| 4 (0x4) | UnknownDex | `dex` not in 0..=14 |
| 5 (0x5) | NotSigner | account 0 did not sign |
| 6 (0x6) | NotTokenAccount | a base or `out` account is not a token account |
| 7 (0x7) | NoProfit | no route reached `min_profit` with `FAIL_WHEN_DRY` — **normal**: the opportunity was gone |
| 8 (0x8) | BadVault | wrong vault section (PDA, token program, a vault account of another mint) or the vault not repaid |
| 9 (0x9) | NotOwner | owner-only tag, or a search without the vault section |

Errors from inside a swap are the DEX's own (e.g. Anchor `3007` = an account it expected is missing or wrong — check
the window against §6).

## 9. A real transaction, decoded

[`4d5cFudo…LQ9TQL`](https://solscan.io/tx/4d5cFudoRgTjximvywcyRSdSGtzq4Z9uG3ZLak8ZeGVzx4Uo8vcpDfM98G4yXF2YU13zFtX8RtzHFLXYVsLQ9TQL)
(slot 453 465 563): a Temporal bundle — tip transfer, compute limit 426 612, price 2 033 µlamports/CU, loaded data
limit 21 102 592 bytes, then the executor with 243 account references (through lookup tables).

```text
01                                  tag 1 (search)
07                                  flags: FAIL_WHEN_DRY | VAULT | BUDGET
80                                  rounds: HINT, precision 0
96 45 50 00 00 00 00 00             min_profit 5 260 694 lamports (covers the tip)
01 0c 0c                            1 base, 12 windows, 12 routes
00 00 00 00 01 00 00 00             base 0 weight 2^32 (WSOL)
b6 56 cb 05 00 00 00 00                    start 97 212 086 (estimate, HINT)
ff ff ff ff ff ff ff 3f                    max_in u64::MAX/4 (no cap)
06 00 05 11 0b                      window 0: DLMM, B->A, program at 5, 17 accounts, out 11 (coin 1 account)
01 03 17 18 01                      window 1: Pump sell, A_TO_B|PUMP_CANONICAL, at 23, 24 accounts, out 1 (WSOL)
06 00 30 11 36                      window 2: DLMM, at 48, out 54 (coin 2 account)
01 03 42 18 01                      window 3: Pump sell, at 66, out 1
02 02 5b 1a 0b                      window 4: Pump buy, PUMP_CANONICAL, at 91, 26 accounts, out 11
06 01 76 12 01                      window 5: DLMM, A_TO_B, at 118, 18 accounts, out 1
02 02 89 1a 36                      window 6: Pump buy, at 137, out 54
06 01 a4 12 01                      window 7: DLMM, A_TO_B, at 164, out 1
07 01 b7 0e 01                      window 8: DAMM v2, A_TO_B, at 183, 14 accounts, out 1
07 00 c6 0e 0b                      window 9: DAMM v2, at 198, out 11
07 00 d5 0e 36                      window 10: DAMM v2, at 213, out 54
07 01 e4 0e 01                      window 11: DAMM v2, A_TO_B, at 228, out 1
00 02 00 01   00 02 02 03   ...     12 routes, each base 0 with two windows: [0,1] [2,3] [4,5] [6,7] [4,8] [9,1]
                                    [0,8] [9,5] [10,3] [2,11] [6,11] [10,7]
74 82 06 00                         budget 426 612 CU
```

Accounts 0–4: user, user's WSOL account, vault PDA, SPL Token program, vault WSOL account. Return data
`AcCB1S0AAAAAKzuYAAAAAAATAA==` = route 1 executed, 768 967 104 lamports in, profit 9 976 619 lamports, 19 quotes;
257 155 CU used of 426 012.

[`encode_search.py`](encode_search.py) is a reference encoder; run it — it rebuilds these 150 bytes exactly.

## 10. Checklist

- [ ] Vault section present (flag bit1), vault token accounts in base order.
- [ ] Your base token accounts and every intermediate token account exist before the executor runs.
- [ ] Each window is exactly the DEX's swap account list (§6), program at `first`; `len` counts the accounts after it.
- [ ] Every route ends in its base: the last hop's `out` is the base token account.
- [ ] `FAIL_WHEN_DRY` on paid landing services; `min_profit` ≥ tip + priority of that copy.
- [ ] `BUDGET` = compute limit minus earlier instructions; compute limit large enough for a win (≥ 300 thousand for
      2-hop routes with DLMM/CLMM).
- [ ] Simulate first (`simulateTransaction`, `sigVerify: false`) and read the return data and logs; only then send.
- [ ] Start with one window and `tag 2` (quote) to check a window's accounts: data `02 | hop (5 bytes) | u64 amount`,
      accounts `user, then the window`; return data = the quoted output.
