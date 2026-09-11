# Architecture

```
tdata ──opentele──┐
                  ├──► StringSession (memory) ──► Telethon Client
.session ─read────┘
string ───────────┘
```

## Layers

1. **Convert** (`seshforge.convert`) - tdata / SQLite → string
2. **Client** (`seshforge.client`) - Telethon subclass that only boots from `StringSession`
3. **CLI** (`python -m seshforge`) - thin wrapper around convert + connect + print

## Why not keep `.session` open?

SQLite session files serialize writers. Multi-process bots, web workers, and parallel scripts collide (`database is locked`). A string is immutable auth material: each process rebuilds an in-memory session independently.

## Trust boundary

`UseCurrentSession` reuses Desktop auth keys on the machine you control. Treat exported strings like passwords; revoke via Telegram active sessions if leaked.
