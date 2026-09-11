# CLI

```bash
python -m seshforge --help
```

## Inputs (exactly one)

| Flag | Description |
|------|-------------|
| `--tdata PATH` | Telegram Desktop `tdata` directory |
| `--session PATH` | Telethon `.session` file |
| `--string STR` | Telethon StringSession |
| `--pyrogram-session PATH` | Pyrogram `.session` SQLite |
| `--pyrogram-string STR` | Pyrogram session string |

## Options / exports

| Flag | Description |
|------|-------------|
| `--account N` | tdata account index (default `0`) |
| `--qr` | `CreateNewSession` instead of `UseCurrentSession` |
| `--to-tdata OUT` | write Desktop tdata |
| `--to-session OUT` | write Telethon `.session` |
| `--to-pyrogram-session OUT` | write Pyrogram `.session` |
| `--to-pyrogram-string` | also print Pyrogram session string |

## Output

```
ok
account: Name (@user) id=123

SESSION_STRING=
1BVtsO...
```

## Env

| Variable | Default |
|----------|---------|
| `API_ID` | `2040` |
| `API_HASH` | Telegram Desktop hash |
