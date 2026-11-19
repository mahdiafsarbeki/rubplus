# RubPlus

Asynchronous Python wrapper for the Rubika Bot API.

## Installation

```bash
pip install .
```

Optional features:

```bash
pip install ".[html]"       # HTML-to-message metadata conversion
pip install ".[webhook]"    # FastAPI + Uvicorn webhook server
pip install ".[dev]"        # Test/build tools
```

For a Git checkout, run the installation command from the repository root. Python 3.8+ is supported.

## Minimal polling bot

```python
import asyncio
from rubplus import RubPlus

async def main():
    async with RubPlus("YOUR_RUBIKA_BOT_TOKEN") as bot:
        @bot.on("message")
        async def on_message(message):
            await message["reply"](f"You said: {message.get('text', '')}")
        await bot.start()

asyncio.run(main())
```

For a synchronous script, use `bot.run()`. In an existing asyncio application, use `await bot.start()`; do not call `run()` from inside an active event loop.

## Filters

```python
from rubplus import Filters

@bot.on("message")
async def on_message(message):
    if (Filters.private() & Filters.text())(message):
        await message["reply"]("Private text message")
```

Standalone functions such as `text()`, `command("start")`, and `private_text` are also exported.

## Webhook

Install the optional dependency group, then create `RubPlusWebhook(bot)`. The ASGI application is available as `webhook.app`; run it with `webhook.run(host="127.0.0.1", port=8000)`.

If a secret is configured, the adapter checks `X-Rubika-Bot-Api-Secret-Token` by default; the header is configurable. Confirm the header expected by your Rubika webhook setup before deployment.

## Important notes

- Constructing `RubPlus` does not make a network request. Use `await bot.check_connection()` to validate credentials.
- Polling offsets are saved atomically to `rubplus_offset.json` by default. Set `offset_file=None` to disable persistence.
- A failed update handler prevents the current batch offset from being acknowledged, allowing retry. Make handlers idempotent to avoid duplicate side effects.
- This repository revision does not contain the file-upload implementation. Upload methods therefore raise a clear `NotImplementedError` instead of failing with an opaque import error.
- Verify API response formats and webhook requirements against current Rubika documentation.

## Development

```bash
pip install ".[dev]"
pytest
```
