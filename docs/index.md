# seshforge

Lock-free **Telethon** client: forge a **StringSession** from Telegram Desktop **tdata** or a `.session` file, then use the full MTProto API without SQLite locks.

[Get started](quickstart.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }

---

## Why

| Pain | Fix |
|------|-----|
| `database is locked` under workers | runtime is always in-memory `StringSession` |
| auth lives in Desktop **tdata** | auto-convert via opentele |
| `.session` files don't travel well | export once to a portable string |

Companion for phone login: [tg-session](https://github.com/xvDoshik/tg-session).

## Features

- **Lock-free** - no shared SQLite in production paths
- **tdata / `.session` / string** - one factory entrypoint
- **Full Telethon** - `Client` subclasses `TelegramClient`
- **CLI + library** - forge strings or keep a live client

```python
from seshforge import Client

client = await Client.create(API_ID, API_HASH, tdata="/path/to/tdata")
print(client.session_string)
```
