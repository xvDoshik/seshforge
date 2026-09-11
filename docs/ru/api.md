# API

Полный публичный API **seshforge 0.2**. Рантайм — всегда Telethon `StringSession` в памяти.

## `Client`

Наследник `telethon.TelegramClient`. Методы Telethon без изменений.

| Метод | Источник |
|-------|----------|
| `Client.create(...)` | ровно один из `tdata` / `session_file` / `session_string` / `pyrogram_session` / `pyrogram_string` |
| `from_tdata` / `from_session_file` / `from_string` | Desktop / Telethon file / string |
| `from_pyrogram_string` / `from_pyrogram_file` | форматы Pyrogram |
| `export_pyrogram_string` / `to_tdata` / `to_session_file` / `to_pyrogram_file` | экспорт |

## Слои

- **Telethon** — `convert`: `session_*`, `string_*`, `detect_string_kind`, `AuthParts`
- **Pyrogram** — `pyro_session`: pack/unpack, file I/O, `open_pyrogram`
- **Desktop** — `desktop` + `api`: `load_tdata`, `tdata_to_telethon_string`, `API`, `UseCurrentSession`, `CreateNewSession`

```python
from seshforge import Client, open_pyrogram, pyrogram_string_to_telethon_string

client = await Client.create(API_ID, API_HASH, pyrogram_string=PYRO)
app = await open_pyrogram(API_ID, API_HASH, session_string=PYRO)
```

Полный inventory: [EN API](../api.md).
