EN | [RU](docs/README_RU.md) · [Docs site](https://xvdoshik.github.io/seshforge/)

## seshforge ⚡

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-0088CC?style=flat-square&logo=telegram&logoColor=white)
![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-222?style=flat-square)

Forge a **Telethon StringSession** from Telegram Desktop **tdata** or a `.session` file, then run the full Telethon API without SQLite locks.

Phone login only? Use [tg-session](https://github.com/xvDoshik/tg-session).

**seshforge** = **sesh**ion **forge**

```
seshforge/
├── seshforge/       # Client + converters
├── docs/            # MkDocs (EN/RU)
├── mkdocs.yml
├── requirements.txt
└── .env.example
```

---

## ✨ Features

- **Lock-free runtime** 🔓 - always `StringSession` in memory, no `database is locked`.
- **tdata in** 🖥️ - Telegram Desktop / AyuGram / Kotatogram via opentele.
- **`.session` in** 💾 - one-shot SQLite read, then drop the file handle.
- **Full MTProto API** 📡 - `Client` subclasses Telethon `TelegramClient`.
- **One factory** 🏭 - `Client.create(...)` with exactly one source.

---

## 🚀 Quick start

### Install

```bash
git clone https://github.com/xvDoshik/seshforge.git
cd seshforge
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

### CLI

```bash
python -m seshforge --tdata "~/Library/Application Support/Telegram Desktop/tdata"
python -m seshforge --session ./acc.session
python -m seshforge --string '1...'
```

### Library

```python
from seshforge import Client

client = await Client.create(API_ID, API_HASH, tdata="/path/to/tdata")
print(client.session_string)
await client.send_message("me", "hi")
await client.disconnect()
```

Full guide: [docs site](https://xvdoshik.github.io/seshforge/) · [API](docs/api.md)

---

## 📋 Commands

| Command | What it does |
|---------|----------------|
| `python -m seshforge --tdata PATH` | tdata → StringSession |
| `python -m seshforge --session PATH` | `.session` → StringSession |
| `python -m seshforge --string STR` | verify / reprint string |
| `--account N` | account index inside tdata |

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_ID` | `2040` | Telegram API id ([my.telegram.org](https://my.telegram.org)) |
| `API_HASH` | Telegram Desktop | API hash |

---

## 🔒 Security

- A session string is full account access - treat it like a password.
- Never commit `.env` or session strings.

---

## 📄 License

MIT - see [LICENSE](LICENSE).

---

Thank you for reading! 🐾

**xvDosha** · [github.com/xvDoshik](https://github.com/xvDoshik) · [dosha.pw](https://dosha.pw)
