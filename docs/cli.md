# CLI

```bash
python -m seshforge --help
```

| Flag | Required | Description |
|------|----------|-------------|
| `--tdata PATH` | one of | Telegram Desktop `tdata` directory |
| `--session PATH` | one of | Telethon `.session` file |
| `--string STR` | one of | existing StringSession |
| `--account N` | no | tdata account index (default `0`) |

## Output

```
ok
account: Name (@user) id=123

SESSION_STRING=
1BVtsO...
```

Nothing is written to disk unless you redirect stdout yourself.

## Env

Loaded from `.env` next to the project (or process env):

| Variable | Default |
|----------|---------|
| `API_ID` | `2040` |
| `API_HASH` | Telegram Desktop hash |
