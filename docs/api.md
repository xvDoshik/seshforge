# API reference

## `Client`

Subclass of `telethon.TelegramClient`. All Telethon methods work (`get_me`, `send_message`, `iter_messages`, ...).

### Constructors

#### `Client(session, api_id, api_hash, **kwargs)`

`session` may be:

- `None` - empty `StringSession` (login yourself)
- `StringSession` instance
- Telethon session string (`1...`)
- path to `.session` (auto-exported to string first)

#### `await Client.create(api_id, api_hash, *, tdata= | session_file= | session_string=, ...)`

Pass **exactly one** source. Returns a connected client by default (`connect=True`).

#### `await Client.from_tdata(path, api_id, api_hash, *, account_index=0, use_current=True)`

Loads Telegram Desktop `tdata`, exports auth into `StringSession`.

- `use_current=True` - reuse Desktop auth key (no QR)
- `use_current=False` - QR login into a fresh session (opentele `CreateNewSession`)

#### `await Client.from_session_file(path, api_id, api_hash)`

Reads Telethon SQLite once, closes it, continues on string.

#### `await Client.from_string(session_string, api_id, api_hash)`

Straight string boot.

### Properties

| Name | Type | Meaning |
|------|------|---------|
| `session_string` | `str` | portable auth blob |
| `export_session_string()` | `str` | same as property |

Telethon kwargs (`proxy`, `timeout`, `connection_retries`, ...) are forwarded.

---

## Converters

```python
from seshforge import tdata_to_string, session_file_to_string, session_to_string

s = await tdata_to_string("/path/tdata", account_index=0)
s = session_file_to_string("acc.session")
s = session_to_string(client.session)
```

---

## Patterns

### Multi-worker

```python
SESSION = os.environ["SESSION_STRING"]
client = await Client.from_string(SESSION, API_ID, API_HASH)
```

### Telethon events

```python
from telethon import events

@client.on(events.NewMessage(pattern="/ping"))
async def ping(event):
    await event.reply("pong")
```

---

## Errors

| Error | Cause |
|-------|-------|
| `ValueError: pass exactly one of...` | multiple sources to `create` |
| `ValueError: no accounts in tdata` | empty / wrong tdata path |
| `FileNotFoundError` | missing `.session` |
| `ValueError: no auth_key` | corrupt / logged-out session file |

Telegram-side errors bubble up from Telethon unchanged.
