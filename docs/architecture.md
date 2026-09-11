# Architecture

```
tdata ──opentele──┐
telethon .session─┤
telethon string───┼──► StringSession (memory) ──► seshforge.Client (Telethon)
pyrogram file─────┤
pyrogram string───┘
                         │
                         ├── export → telethon / pyrogram / tdata
                         └── open_pyrogram → pyrogram.Client (MemoryStorage)
```

## Layers

1. **convert** — Telethon auth parts, string/file, format detection
2. **pyro_session** — Pyrogram pack/unpack + `open_pyrogram`
3. **desktop / api** — opentele `TDesktop`, `API`, login flags
4. **client** — Telethon subclass; session I/O only (no Pyrogram method merge)
5. **CLI** — convert + connect + optional exports

## Why not keep `.session` open?

SQLite session files serialize writers. Multi-process bots collide (`database is locked`). A string is immutable auth material.

## Trust boundary

`UseCurrentSession` reuses Desktop auth keys on the machine you control. Treat exported strings like passwords.
