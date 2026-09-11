# API reference

Full public surface of **seshforge 0.2**. Runtime auth is always a Telethon `StringSession` in memory. Disk formats are import/export only.

## `Client`

Subclass of `telethon.TelegramClient`. All Telethon messaging APIs work unchanged.

### Constructors

| Method | Source |
|--------|--------|
| `Client(session, api_id, api_hash, **kwargs)` | `None` / `StringSession` / telethon or pyrogram string / Telethon `.session` path |
| `await Client.create(...)` | exactly one of `tdata`, `session_file`, `session_string`, `pyrogram_session`, `pyrogram_string` |
| `await Client.from_string(...)` | Telethon or Pyrogram session string (auto-detect) |
| `await Client.from_session_file(...)` | Telethon SQLite `.session` |
| `await Client.from_pyrogram_string(...)` | Pyrogram session string |
| `await Client.from_pyrogram_file(...)` | Pyrogram SQLite `.session` |
| `await Client.from_tdata(..., use_current=True)` | Desktop `tdata` (`UseCurrentSession` / `CreateNewSession` via `use_current=False`) |

### Session export

| Method | Output |
|--------|--------|
| `session_string` / `export_session_string()` | Telethon StringSession |
| `await export_pyrogram_string()` | Pyrogram session string (needs connected authorized user) |
| `to_session_file(path)` | Telethon `.session` |
| `await to_pyrogram_file(path)` | Pyrogram `.session` |
| `await to_tdata(path, use_current=..., flag via use_current)` | Desktop tdata |

---

## Telethon session layer (`convert`)

| Function | Role |
|----------|------|
| `StringSession` / `SQLiteSession` / `MemorySession` | re-exported Telethon sessions |
| `AuthParts` | dataclass: `dc_id`, `auth_key`, address/port, pyro fields |
| `detect_string_kind(s)` | `"telethon"` / `"pyrogram"` / `"unknown"` |
| `dc_address(dc_id, test_mode=False)` | `(ip, 443)` |
| `memory_from_parts(...)` | build `StringSession` from dc/auth |
| `session_to_string(session)` | any Telethon session → string |
| `string_to_session(s)` | telethon/pyrogram string → `StringSession` |
| `session_file_to_string(path)` | Telethon file → string (close-safe) |
| `string_to_session_file(s, path)` | string → Telethon `.session` |
| `list_telethon_sessions()` | `SQLiteSession.list_sessions()` |
| `auth_parts_from_telethon_string` / `telethon_string_from_parts` | pack/unpack |
| `await tdata_to_string(...)` / `await string_to_tdata(...)` | Desktop bridge |

---

## Pyrogram session layer (`pyro_session`)

| Function | Role |
|----------|------|
| `looks_like_pyrogram_string` | format probe |
| `unpack_pyrogram_string` / `pack_pyrogram_string` | ↔ `AuthParts` |
| `pyrogram_string_to_telethon_string` | pyro → telethon string |
| `telethon_string_to_pyrogram_string(..., api_id, user_id)` | reverse (needs `user_id`) |
| `pyrogram_file_to_parts` / `pyrogram_file_to_string` / `pyrogram_file_to_pyrogram_string` | SQLite read |
| `string_to_pyrogram_file(...)` | write Pyrogram `.session` |
| `await open_pyrogram(api_id, api_hash, *, session_string\|session_file\|tdata\|telethon_string, user_id=...)` | real `pyrogram.Client` on in-memory storage |

Pyrogram method style stays on `pyrogram.Client` from `open_pyrogram` — not merged onto `seshforge.Client`.

---

## Desktop / opentele (`desktop`, `api`)

| Symbol | Role |
|--------|------|
| `API`, `APIData`, `UseCurrentSession`, `CreateNewSession`, `LoginFlag` | re-exports from opentele |
| `load_tdata` / `save_tdata` | `TDesktop` load/save |
| `list_accounts` / `main_account` / `accounts_count` | multi-account |
| `await tdata_to_telethon_string(...)` | tdata → StringSession |
| `await telethon_to_tdata(...)` | StringSession → tdata |

Supports `account_index`, `passcode`, `key_file`, `password`, and API presets (`API.TelegramDesktop`, `API.TelegramAndroid`, … / `Generate()`).

---

## Patterns

### Multi-worker (Telethon)

```python
from seshforge import Client

client = await Client.from_string(SESSION, API_ID, API_HASH)
await client.send_message("me", "hi")
```

### Pyrogram runtime

```python
from seshforge import open_pyrogram

app = await open_pyrogram(API_ID, API_HASH, session_string=PYRO_STRING)
await app.start()
```

### Convert matrix without live connect

```python
from seshforge import (
    telethon_string_to_pyrogram_string,
    pyrogram_string_to_telethon_string,
    string_to_session_file,
)

pyro = telethon_string_to_pyrogram_string(tl, api_id=API_ID, user_id=123)
tl2 = pyrogram_string_to_telethon_string(pyro)
string_to_session_file(tl2, "out.session")
```

---

## Errors

| Error | Cause |
|-------|-------|
| `ValueError: pass exactly one of...` | multiple sources |
| `ValueError: user_id required...` | pyro pack without user id |
| `ValueError: no accounts in tdata` | empty / wrong tdata |
| `FileNotFoundError` | missing session file |
| `ValueError: no auth_key` | corrupt / logged-out session |
