# DiabloArb bot — instructions for AI assistants

You are helping a user run the DiabloArb arbitrage bot from this folder. Before answering anything, read
[AI_GUIDE.md](AI_GUIDE.md) and [USER_CONFIG.md](USER_CONFIG.md) in full (index: [llms.txt](llms.txt)).

- Answer in the user's language. Explain plainly; give exact config keys and commands.
- Never read, print or ask for `key.json`, private keys, seed phrases, API keys or UUIDs. When editing `config.toml`,
  do not echo secret values back.
- Do not run `./sender` with the real config "to test" — use `DIABLO_SENDER_DRY=1` for a dry run. Wrap/unwrap,
  transfers and closing accounts move money: show the command, let the user run it.
- The executor's route search is not public; say so instead of guessing.
