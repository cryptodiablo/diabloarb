## 🖇️ Useful Links

- Official Website: https://diabloarb.bot
- Realtime Profits: https://t.me/diabloarb
- Telegram Chat: https://t.me/diabloarbchat
- Discord: https://discord.gg/Zaykhzwh
- Pools Extractor: https://moneyprinter.bot/pools/
- Beginners Guide: https://telegra.ph/DiabloArb--Full-Guide-Overview-Quick-Start-Risks-and-FAQ-01-30
- RU Beginners Guide: https://telegra.ph/Diablo-Arb-Bot---gajd-01-26

## 😈 Diablo Arb Bot

Automated arbitrage trading bot for Solana that identifies and executes profitable opportunities across multiple DEXs in real-time.

Arb tx with over 12k$ profit:
https://solscan.io/tx/3CVwFndtJyJHbgHozCtfBnYaKDcz57pgskSJveeYAN4VTh3XXovKgZ2SXAsjWnMGPAFJDMAX7JghYDRtRbK5uqvg
<img width="872" height="181" alt="image" src="https://github.com/user-attachments/assets/75b799ac-de9b-48b2-a2b1-cd252cf269b7" />


Sample of tx with 5.1k$ profit:
<img width="1816" height="444" alt="image" src="https://github.com/user-attachments/assets/41c56bbb-5e74-4e90-90b6-00d1008e450a" />

## ⚙️ How It Works

The bot monitors price discrepancies across Solana DEXs:

1. **Monitoring:** Scans multiple DEXs for price differences
2. **Analysis:** Calculates profitability (spreads, fees, gas, slippage)
3. **Execution:** Automatically executes profitable trades
4. **Optimization:** Maximizes profit margins

## 🧳 Whats inside
- `sender` — binary (Linux x86_64)
- `config.toml` — main config
- `markets.toml` — pools/markets list
- `gas.json` — priority fee / Jito tip params

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


**`config.toml` (overview)**
- **rpc**: RPC for reading state (quotes/accounts)
- **send_rpcs**: RPCs for broadcasting transactions
- **gas_file**: path to `gas.json`
- **markets_file**: path to `markets.toml`
- **jito**, **jito_endpoints**, **jito_uuid**: Jito delivery settings
- **luts**: path to LUT list (if used)

Config paths are examples — adjust for your server.

**Market data**
- No Geyser needed: without it the bot reads the pools over `rpc` (every second) and works out of the box.
- Your own Yellowstone gRPC makes it faster: add `geyser_endpoint = "..."` and `geyser_x_token = "..."` to `config.toml`.
- `markets_file` and `luts` point to https://moneyprinter.bot/auto/mp.toml and https://moneyprinter.bot/auto/mplutall.txt —
  the coins the arbitrage bots earn most on right now and their lookup tables, refreshed live.
- `jito_uuid`: your own Jito UUID; the `"uuid"` placeholder is ignored (Jito without one).

**Updates**
On every start the bot checks this repository and updates itself to the latest `sender`, then restarts with the same
arguments. `./sender update` updates now, `./sender version` shows the version, and
`DIABLO_SENDER_AUTO_UPDATE=0 ./sender config.toml` keeps the current one.

**`gas.json`**
Dynamic parameters (priority fee / tip / cooldown) that can be adjusted without editing the main TOML.

**`markets.toml`**
List of pool/market addresses grouped by token and direction.

- Wrap 0.1 SOL → WSOL
```  ./sender wrap 0.1
    ./sender wrap config.toml 0.1
```

- Unwrap 0.1 WSOL → SOL
```  ./sender unwrap 0.1
    ./sender unwrap config.toml 0.1
```

- Unwrap ALL WSOL balance → SOL (without closing ATA for WSOL)
```  ./sender unwrap all
    ./sender unwrap config.toml all
```

Repo: https://github.com/cryptodiablo/diabloarb

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



