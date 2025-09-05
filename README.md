# ArtStyle Muse Discord Bot (py-cord + OpenRouter + Railway)

Analyze **art style** only (no subject matter) using Qwen VL via OpenRouter.

## Quickstart

1) Create a Discord application & bot, invite it to your server.
2) Copy `.env.example` to `.env` and fill in:
   - `DISCORD_TOKEN`
   - `OPENROUTER_API_KEY`
   - (optional) `OPENROUTER_MODEL` (defaults to `qwen/qwen2.5-vl-72b-instruct:free`)
3) Local run:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)  # Windows: set manually in your shell
python -m src.bot
```
4) In Discord:
```
/style image:<attach your image> private:true
```
- `private:true` → encodes as base64 data URL (no external fetch)
- `private:false` → passes the Discord CDN URL to OpenRouter (faster)

## Deploy on Railway

- Push this folder to GitHub, then create a Railway project from that repo.
- Add env vars in Railway: `DISCORD_TOKEN`, `OPENROUTER_API_KEY`, (optional) `OPENROUTER_MODEL`.
- Railway builds the Dockerfile and runs the bot.

## Files
- `src/bot.py` – bot bootstrap & cog loading
- `src/cogs/art_style.py` – `/style` slash command, OpenRouter call
- `src/cogs/ping.py` – simple `/ping` health check
