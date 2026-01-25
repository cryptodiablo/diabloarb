Realtime Profits: https://t.me/diabloarb

Telegram Chat: https://diabloarbchat

Discord: https://discord.gg/gERHqsMy

Pools Extractor: https://moneyprinter.bot/pools/



**Diablo Arb Bot**

Minimal runtime bundle for running a Solana DEX arbitrage sender.

**What's inside**
- `sender` — binary (Linux x86_64)
- `config.toml` — main config
- `markets.toml` — pools/markets list
- `gas.json` — priority fee / Jito tip params

**Quick Install**
```
wget -O diabloarb.zip https://github.com/cryptodiablo/diabloarb/archive/refs/heads/main.zip
unzip diabloarb.zip
cd diabloarb-main
chmod +x ./sender
```

**Run**
```
./sender config.toml
```

> If you run this on another server, make sure the architecture matches (x86_64).  
> Check with: `uname -m` and `file ./sender`.

**`config.toml` (overview)**
- **rpc**: RPC for reading state (quotes/accounts)
- **send_rpcs**: RPCs for broadcasting transactions
- **gas_file**: path to `gas.json`
- **markets_file**: path to `markets.toml`
- **jito**, **jito_endpoints**, **jito_uuid**: Jito delivery settings
- **luts**: path to LUT list (if used)

Config paths are examples — adjust for your server.

**`gas.json`**
Dynamic parameters (priority fee / tip / cooldown) that can be adjusted without editing the main TOML.

**`markets.toml`**
List of pool/market addresses grouped by token and direction.

Repo: https://github.com/cryptodiablo/diabloarb



