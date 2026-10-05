## 🖇️ Useful Links

- Official Website: https://diabloarb.bot
- Realtime Profits: https://t.me/diabloarb
- Telegram Chat: https://t.me/diabloarbchat
- Discord: https://discord.gg/Zaykhzwh
- Pools Extractor: https://moneyprinter.bot/pools/
- Beginners Guide: https://telegra.ph/DiabloArb--Full-Guide-Overview-Quick-Start-Risks-and-FAQ-01-30
- RU Beginners Guide: https://telegra.ph/Diablo-Arb-Bot---gajd-01-26
- **Ask an AI about the bot:** [how](#-ask-an-ai-about-the-bot) — knowledge base [`AI_GUIDE.md`](AI_GUIDE.md), index [`llms.txt`](llms.txt)
- **Full settings reference for your AI assistant:** [`USER_CONFIG.md`](USER_CONFIG.md)
- **Build your own sender on our executor (SDK, IDL, AI-agent guide):** [`sdk/`](sdk/README.md)
- 🇷🇺 **На русском:** [описание бота на русском](#-на-русском)

## 🤖 Ask an AI about the bot

Any AI assistant (ChatGPT, Claude, Gemini, Cursor, Codex…) can answer questions about this bot — settings, costs,
modes, log lines, "why did it stop". Paste this as your first message:

```
Read https://raw.githubusercontent.com/cryptodiablo/diabloarb/main/llms.txt and every file it lists
(AI_GUIDE.md and USER_CONFIG.md completely). Then answer my questions about the DiabloArb bot using only them.
```

Running Claude Code or Codex inside the bot's folder? It reads [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md) by
itself. Never paste your private key, `key.json` or API keys into any chat.

## 😈 Diablo Arb Bot

Automated arbitrage trading bot for Solana that identifies and executes profitable opportunities across multiple DEXs in real-time.

Arb tx with over 12k$ profit:
https://solscan.io/tx/3CVwFndtJyJHbgHozCtfBnYaKDcz57pgskSJveeYAN4VTh3XXovKgZ2SXAsjWnMGPAFJDMAX7JghYDRtRbK5uqvg
<img width="872" height="181" alt="image" src="https://github.com/user-attachments/assets/75b799ac-de9b-48b2-a2b1-cd252cf269b7" />


Sample of tx with 5.1k$ profit:
<img width="1816" height="444" alt="image" src="https://github.com/user-attachments/assets/41c56bbb-5e74-4e90-90b6-00d1008e450a" />

## 🆕 What's new (October 2026)

The bot was rebuilt from scratch. **Your existing `config.toml`, `gas.json` and markets file keep working
unchanged**, and the old binary updates itself to the new one on its next restart.

- **New on-chain executor.** The trade size is no longer guessed off-chain: the program finds the best amount at the
  moment of execution, using up to your WSOL/USDC/USDT balance plus — with `flashloan = true` — the whole DiabloArb
  flash-loan vault. If the opportunity is gone, the transaction does nothing and paid lanes keep their tip.
- **SOL, USDC and USDT routes.** Cycles start and end in any of the three, including 3-hop routes through another coin.
- **Live hot markets.** `https://moneyprinter.bot/auto/mp.toml` is rebuilt continuously from the routes the on-chain
  arbitrage bots are winning right now — whole routes, never fragments, ordered by their profit, recent wins weighing
  more (each win counts half as much every 2.5 minutes). The bot shoots them in that order.
- **Hot modes (new, need Geyser).** `mode = "ladder"` watches the arbitrage bots live and only shoots while they are
  earning, escalating from cheap RPC copies to paid senders as a coin heats up; `mode = "flow"` shoots the top coins
  non-stop. These are the modes we run ourselves. See [`USER_CONFIG.md`](USER_CONFIG.md#8-hot-modes-mode--ladder-and-mode--flow).
- **One landing per shot.** In the hot modes all copies of a shot to different senders share one durable nonce, so at
  most one lands — no double tips.
- **15 landing services:** Jito, Helius (+SWQoS, + new Helius bundles), Temporal (+ new Temporal bundles), Harmonic bundles, Flashblock,
  HelloMoon, Astralane, 0slot, Falcon, Stellium, NextBlock, Fast (+SWQoS), plus your own RPCs.
- **Geyser optional.** With your Yellowstone gRPC (`geyser_endpoint`) pools update in real time; without it the bot
  polls them over RPC and still works.
- **New coins handled on the fly.** Missing token accounts are created automatically while the other coins keep
  shooting.
- **Clear logs.** One line per send, failures summarized every 10 s, `✅ Success!` on every win and a per-minute
  summary of sends, wins, balances and the coins being shot.
- **Safe test run.** `DIABLO_SENDER_DRY=1 ./sender config.toml` builds and logs everything without sending.

## 🔁 Supported DEXs

Arbitrage routes (2 or 3 swaps, starting and ending in SOL, USDC or USDT) across any mix of:

| DEX | Pool type |
|---|---|
| Meteora DLMM | dynamic liquidity bins |
| Meteora DAMM v2 | dynamic AMM |
| Meteora Pools (DAMM v1) | AMM over Meteora vaults |
| Meteora DBC | dynamic bonding curve (launchpad pools) |
| Pump.fun AMM (PumpSwap) | constant product |
| Raydium AMM v4 | constant product |
| Raydium CPMM | constant product |
| Raydium CLMM | concentrated liquidity |
| Orca Whirlpool | concentrated liquidity |
| Orca v2 / SPL Token Swap | constant product |
| PancakeSwap CLMM | concentrated liquidity |
| Byreal CLMM | concentrated liquidity |
| DefiTuna Fusion | concentrated liquidity with limit orders |
| Manifest | on-chain order book |
| MetaDAO Futarchy | spot market |

SPL Token and Token-2022 coins are supported (tokens with an active transfer hook are skipped). Any pool of these
DEXs can be put in your own markets file; the live `mp.toml` picks the ones where the arbitrage is happening.

## ⚙️ How It Works

The bot monitors price discrepancies across Solana DEXs:

1. **Monitoring:** Follows the pools where arbitrage is happening right now (live markets file or, in hot modes, the
   on-chain arbitrage bots seen over Geyser)
2. **Analysis:** Prices every route in real time from the pools' state
3. **Execution:** Sends the transaction through your landing services; the on-chain program sizes the trade and
   executes only if it is profitable
4. **Settlement:** Profit lands in your wallet's WSOL/USDC/USDT; 7% of each profit goes to the DiabloArb vault

## 🧳 Whats inside
- `sender` — binary (Linux x86_64, static — runs on any distribution)
- `config.toml` — main config
- `markets.toml` — pools/markets list (example; the default config uses the live `mp.toml`)
- `gas.json` — priority fee / tip / cooldown values referenced from `config.toml`
- [`USER_CONFIG.md`](USER_CONFIG.md) — full settings reference: give it to your AI assistant (ChatGPT, Claude…) and ask it to help you set up the bot
- [`sdk/`](sdk/README.md) — for developers: the executor's instruction format, every DEX's accounts, a JSON IDL and an `AGENTS.md` for Codex / Claude Code to build your own sender

## 📊 Quick Install
```
wget -O diabloarb.zip https://github.com/cryptodiablo/diabloarb/archive/refs/heads/main.zip
unzip diabloarb.zip
cd diabloarb-main
chmod +x ./sender
```

## ✅ How to Run
```
./sender config.toml
```

Test without sending anything:
```
DIABLO_SENDER_DRY=1 ./sender config.toml
```

**`config.toml` (overview)** — every key is explained in [`USER_CONFIG.md`](USER_CONFIG.md)
- **rpc**: RPC for reading state (quotes/accounts)
- **send_rpcs**: RPCs for broadcasting transactions (also used to create token accounts — must accept transactions)
- **gas_file**: path to `gas.json`
- **markets_file**: markets file (local path or URL)
- **luts**: lookup table list (local path or URL)
- **flashloan**: `true` lets the trade use the DiabloArb vault besides your own balance
- **geyser_endpoint**, **geyser_x_token**: your Yellowstone gRPC (optional; required for hot modes)
- **mode**: `markets` (default), `ladder` or `flow`
- **jito**, **jito_uuid**, **temporal**, **helius**, …: landing services, each with its own tips, priority and cooldown

Config paths are examples — adjust for your server.

**Market data**
- No Geyser needed for the default mode: without it the bot reads the pools over `rpc` (every second) and works out of the box.
- Your own Yellowstone gRPC makes it faster: add `geyser_endpoint = "..."` and `geyser_x_token = "***"` to `config.toml`.
- `markets_file` and `luts` point to https://moneyprinter.bot/auto/mp.toml and https://moneyprinter.bot/auto/mplutall.txt —
  the routes the arbitrage bots win most on right now and their lookup tables, refreshed live.
- `jito_uuid`: your own Jito UUID; the `"uuid"` placeholder is ignored (Jito without one).

**Updates**
On every start the bot checks this repository and updates itself to the latest `sender`, then restarts with the same
arguments. `./sender update` updates now, `./sender version` shows the version, and
`DIABLO_SENDER_AUTO_UPDATE=0 ./sender config.toml` keeps the current one.

**`gas.json`**
Dynamic parameters (priority fee / tip / cooldown) referenced from `config.toml` as `"{name}"`; edits apply without a
restart. A value only works if `config.toml` references it.

**`markets.toml` / `mp.toml`**
List of pool addresses; in `mp.toml` each `[[group]]` is one complete route, in priority order.

## 💸 Wallet commands

- Wrap 0.1 SOL → WSOL
```
./sender wrap 0.1
./sender wrap config.toml 0.1
```

- Unwrap 0.1 WSOL → SOL
```
./sender unwrap 0.1
./sender unwrap config.toml 0.1
```

- Unwrap ALL WSOL balance → SOL (without closing ATA for WSOL)
```
./sender unwrap all
./sender unwrap config.toml all
```

- Close the durable nonce accounts of the hot modes (returns their rent, ≈0.00145 SOL each)
```
./sender nonces close
```

Repo: https://github.com/cryptodiablo/diabloarb

## ⚠️ Risks

Arbitrage is competitive: every landed transaction pays network and priority fees whether it wins or not, and wins
come in bursts. Start with small priority fees and a dry run, watch the per-minute summary, and only add paid
senders once you see wins.

## 🇷🇺 На русском

**DiabloArb** — бот арбитража на Solana: находит маршрут из 2–3 обменов между пулами DEX, который начинается и
заканчивается в SOL (WSOL), USDC или USDT, и отправляет его в сеть. Сделку исполняет программа DiabloArb в сети:
она сама подбирает сумму в момент исполнения и ничего не делает, если выгоды уже нет.

### Что нового (октябрь 2026)

Бот переписан с нуля. **Старые `config.toml`, `gas.json` и файл рынков работают без правок**, старый бинарник сам
обновится до нового при следующем перезапуске.

- **Новая программа исполнения.** Сумма сделки подбирается в сети в момент исполнения: до вашего баланса
  WSOL/USDC/USDT плюс, при `flashloan = true`, всё хранилище флешлоана DiabloArb. Если возможность ушла — транзакция
  ничего не делает, платные отправители не берут чаевые.
- **Маршруты в SOL, USDC и USDT**, включая трёхшаговые через другую монету.
- **Живой список рынков.** `https://moneyprinter.bot/auto/mp.toml` постоянно пересобирается из маршрутов, на которых
  арбитражные боты в сети выигрывают прямо сейчас: целые маршруты, по порядку их прибыли (свежие выигрыши весят больше:
  каждый вдвое легче за 2,5 минуты).
  Бот стреляет в этом порядке.
- **Горячие режимы (нужен Geyser).** `mode = "ladder"` (лестница) следит за ботами в сети и стреляет только пока они
  зарабатывают, поднимая расходы по мере «нагрева» монеты: сначала дешёвые RPC-копии, потом платные отправители.
  `mode = "flow"` (поток) — без остановки по верхним монетам. Это режимы, на которых работаем мы сами.
- **Одна посадка на выстрел.** В горячих режимах копии выстрела для разных отправителей подписаны одним durable
  nonce — садится не больше одной, чаевые дважды не платятся.
- **15 сервисов отправки:** Jito, Helius (+SWQoS, + новые пакеты Helius), Temporal (+ новые пакеты Temporal), пакеты Harmonic, Flashblock,
  HelloMoon, Astralane, 0slot, Falcon, Stellium, NextBlock, Fast (+SWQoS) и ваши RPC.
- **Geyser не обязателен.** Со своим Yellowstone gRPC (`geyser_endpoint`) пулы обновляются мгновенно, без него бот
  опрашивает их через RPC и тоже работает.
- **Новые монеты на ходу.** Недостающие токен-счета создаются автоматически, остальные монеты в это время стреляют.
- **Понятный журнал:** строка на каждую отправку, ошибки раз в 10 с, `✅ Success!` на каждый выигрыш и сводка раз в
  минуту.
- **Безопасная проверка:** `DIABLO_SENDER_DRY=1 ./sender config.toml` — всё собирается и пишется в журнал, но ничего
  не отправляется.

### Поддерживаемые DEX

Meteora DLMM, DAMM v2, Pools (DAMM v1) и DBC; Pump.fun AMM (PumpSwap); Raydium AMM v4, CPMM и CLMM; Orca Whirlpool и
Orca v2 / SPL Token Swap; PancakeSwap CLMM; Byreal CLMM; DefiTuna Fusion; Manifest (книга заявок); MetaDAO Futarchy.
Монеты SPL Token и Token-2022 (кроме токенов с действующим transfer hook).

### Установка и запуск

```
wget -O diabloarb.zip https://github.com/cryptodiablo/diabloarb/archive/refs/heads/main.zip
unzip diabloarb.zip
cd diabloarb-main
chmod +x ./sender
./sender config.toml
```

Проверка без отправки:
```
DIABLO_SENDER_DRY=1 ./sender config.toml
```

Главное в `config.toml`: `rpc` (чтение), `send_rpcs` (отправка; через них же создаются токен-счета — они должны
принимать транзакции), `keypair` (путь к ключу), `markets_file` и `luts`, `flashloan`, `geyser_endpoint` и
`geyser_x_token`, `mode` (`markets` по умолчанию, `ladder` или `flow`) и отправители (`jito`, `temporal`, `helius`…) со
своими чаевыми, приоритетом и паузой. Значения из `gas.json` подставляются как `"{имя}"` и применяются без
перезапуска.

**Свой отправитель на нашем контракте** — в папке [`sdk/`](sdk/README.md): формат инструкции, аккаунты всех DEX, IDL и
`AGENTS.md` для Codex / Claude Code.

**Все настройки подробно — в [`USER_CONFIG.md`](USER_CONFIG.md).** Дайте этот файл своему ИИ-помощнику (ChatGPT,
Claude…) и попросите помочь настроить бота — он ответит по-русски. Приватный ключ и seed никому не показывайте,
в том числе ИИ.

### Команды кошелька

```
./sender wrap 0.1           # 0.1 SOL -> WSOL
./sender unwrap 0.1         # 0.1 WSOL -> SOL
./sender unwrap all         # весь WSOL -> SOL (счёт WSOL остаётся)
./sender nonces close       # закрыть nonce-счета горячих режимов, вернуть аренду (≈0.00145 SOL каждый)
./sender update             # обновиться сейчас
./sender version            # версия
```

При каждом запуске бот сам обновляется из этого репозитория; `DIABLO_SENDER_AUTO_UPDATE=0 ./sender config.toml`
оставляет текущую версию.

### Спросить ИИ

Любой ИИ-помощник ответит на вопросы о боте — настройки, расходы, режимы, строки журнала. Вставьте первым сообщением:

```
Прочитай https://raw.githubusercontent.com/cryptodiablo/diabloarb/main/llms.txt и все файлы из него
(AI_GUIDE.md и USER_CONFIG.md целиком). Отвечай на мои вопросы о боте DiabloArb только по ним, по-русски.
```

Никогда не вставляйте в чат приватный ключ, `key.json` или API-ключи.

### Комиссия и риски

С каждой прибыли 7% уходит в хранилище DiabloArb, остальное — в ваш кошелёк. Арбитраж — это конкуренция: каждая
севшая транзакция платит комиссию сети и приоритет, даже без выигрыша, а выигрыши приходят всплесками. Начинайте с
малого приоритета и сухого прогона, следите за минутной сводкой и добавляйте платных отправителей, когда увидите
выигрыши.

## 🔑 Keywords

- Solana Arbitrage Bot  
- Solana Arb Bot  
- Solana Trading Bot  
- DEX Arbitrage  
- Crypto Arbitrage  
- Flash Loan Arbitrage  
- Automated Trading Bot  
- Crypto Trading Strategy  
- On-chain Arbitrage  
- Raydium Arbitrage  
- Solana DeFi Bot  
- High-Frequency Trading (HFT)  
