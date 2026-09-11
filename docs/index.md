# seshforge

Lock-free **session forge** for Telegram: **Telethon** + **Pyrogram** + Desktop **tdata**, with a Telethon `Client` that keeps the full messaging API.

[Get started](quickstart.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }

---

## Why

| Pain | Fix |
|------|-----|
| `database is locked` under workers | runtime is always in-memory `StringSession` |
| auth in Desktop **tdata** | convert via opentele |
| Telethon ↔ Pyrogram formats | pack/unpack + factories |
| `.session` files don't travel | export to portable strings |

Companion for phone login: [tg-session](https://github.com/xvDoshik/tg-session).

## Features

- **Lock-free** - no shared SQLite in production paths
- **Full convert matrix** - tdata / Telethon / Pyrogram file & string
- **Full Telethon** - `Client` subclasses `TelegramClient`
- **Pyrogram factory** - `open_pyrogram(...)` for Pyrogram method style
- **CLI + library** - forge, convert, export

```python
from seshforge import Client

client = await Client.create(API_ID, API_HASH, tdata="/path/to/tdata")
print(client.session_string)
```
