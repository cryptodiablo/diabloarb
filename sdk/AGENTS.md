# Building a sender for the DiabloArb executor — instructions for AI coding agents

You (Codex, Claude Code or another agent) are helping a person build their own Solana arbitrage sender that calls the
DiabloArb executor `DiabLokxisGR8P4Qqp2QL6PmBhhVsdzPstCE4WoLxc5z`. Answer the person in their language.

## Read first

1. [`README.md`](README.md) — the specification. §3 data layout, §4 accounts, §5 windows, §6 every DEX's swap
   account list, §7 transaction layout, §8 errors, §9 a real transaction decoded byte by byte.
2. [`diabloarb-executor.idl.json`](diabloarb-executor.idl.json) — the same layout as data: enums (`Dex`, flags),
   types (`Hop`, `Base`, `Route`), the `search` and `quote` instructions with accounts, return data, error codes. Use it
   to generate encoders/decoders in any language. It is **not** an Anchor IDL — do not feed it to Anchor's client
   generator; there are no Borsh vectors and no 8-byte discriminators (the tag is one byte).
3. [`encode_search.py`](encode_search.py) — reference encoder. Port it to the person's language and keep its
   self-test: your encoder must reproduce the real transaction's 150 bytes from §9 exactly.

## Facts you must not get wrong

- Only `tag 1` (search) and `tag 2` (quote) are usable; `tag 0` and `tag 3` are owner-only (`NotOwner`).
- **Always** set flag bit1 and pass the vault section right after the base token accounts: vault PDA
  `Bank4kzA4xv6zsLfXXx4YrMK7io8fWTvCEHsbQZoh2Jc`, SPL Token program, then one vault token account per base in base order
  (WSOL `HGoYKDXhjq1CVXvCDxTZcYhthZj4nTp1R6WSoKSKgceb`, USDC `8QrVSVbhMgpTMjXskuFmmF7WFe4SLLg43tvpQfsnGA7k`,
  USDT `AzNFA4u7yGkLdN4wUJZ993JkYSiNhhyJnVAefiSLtPJr`). Without it every search fails with `NotOwner` (9).
- 7% of each realized profit goes to the vault automatically; the person keeps 93%. There is nothing to configure.
- A window's accounts are forwarded to the DEX unchanged: they must be exactly that DEX's swap instruction accounts
  in README §6 order, with the DEX program at index `first`. Most failures are wrong window accounts — check §6, not
  the executor.
- Indexes (`first`, `out`) are u8 positions in the executor instruction's own account list. Accounts may repeat; only
  unique accounts of the whole transaction count against the 64-account lock limit — use address lookup tables.
- The last hop's `out` must be the route's base token account; every intermediate token account must already exist.
- `min_profit` is in lamports of value (`profit × weight >> 32`), checked before execution and again after the fee.
- Error 7 (`NoProfit`) is normal (the opportunity was gone). Error 3 means state changed mid-way. Error 8 means a
  wrong vault section.

## How to build it, step by step

1. **Encoder + decoder.** Port `encode_search` and `decode_return`; unit-test against §9.
2. **One window, read-only.** Pick a pool from `https://moneyprinter.bot/auto/mp.toml`, read its accounts over RPC,
   build its window per §6, and call `tag 2` (quote) with `simulateTransaction` (`sigVerify: false`,
   `replaceRecentBlockhash: true`). A sensible output amount in the return data means the window is right. Repeat for
   every DEX the person needs.
3. **One route, simulated.** Two windows forming a cycle over WSOL; full transaction per README §7; simulate. Read
   `Program return:` in the logs: route 255 = no profit now (fine), otherwise the route and amounts. Fix every
   `InvalidData` / `AccountIndex` / DEX error before going further.
4. **Pool state.** Keep pool accounts fresh (Geyser or RPC polling) only to choose windows; the executor quotes on
   chain itself, so the sender does not need exact off-chain math to be correct — only to be selective.
5. **Landing.** Send to the person's RPCs / landing services. Paid services: put the tip inside the transaction and set
   `FAIL_WHEN_DRY`, so a miss costs no tip. Several services at once: sign every copy over one durable nonce so at most
   one lands.
6. **Measure.** Log every send and its outcome (landed / failed with code / not found) and the realized profit; compare
   spend (fees, priority, tips) against profit per hour before scaling up.

## Rules for you, the agent

- Never ask for, print, log or commit a private key, seed phrase or keypair file contents. Refer to key files by path.
  Treat RPC URLs with API keys as secrets too.
- Do not send transactions that move the person's funds (sends, swaps, wraps, ATA creation, nonce accounts) without
  the person's explicit go-ahead for that action; simulate first and show what it will do.
- Prefer simulation and small amounts until the error rate is understood. Every landed transaction pays fees even when
  it finds no profit.
- If README and observed behaviour disagree, trust the chain: decode a real executor transaction (any recent one of
  program `DiabLokxis…` on a block explorer) the way §9 does, and report the discrepancy to the person.
