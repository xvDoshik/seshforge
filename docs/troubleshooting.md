# Troubleshooting

| Symptom | Fix |
|---------|-----|
| `no accounts in tdata` | Path must be the `tdata` folder; Desktop must be logged in |
| `database is locked` | Something still opens a `.session` path - switch fully to string |
| `FileNotFoundError` | Wrong `.session` path / missing `acc.session` |
| flood / auth errors | Use your own `API_ID`/`API_HASH`, slow down, don't share strings |
| PyQt / opentele install fails | Install `PyQt5` wheels; on servers avoid headless display issues |

## Phone login

seshforge does not do interactive phone login. Use [tg-session](https://github.com/xvDoshik/tg-session), then:

```bash
python -m seshforge --string "$SESSION_STRING"
```

## Multi-account tdata

```bash
python -m seshforge --tdata /path/to/tdata --account 1
```
