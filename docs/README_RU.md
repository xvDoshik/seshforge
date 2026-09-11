[EN](../README.md) | RU · [Docs](https://xvdoshik.github.io/seshforge/ru/)

## seshforge ⚡

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-0088CC?style=flat-square&logo=telegram&logoColor=white)

Собирает **Telethon StringSession** из **tdata** или `.session`, дальше полный Telethon API без SQLite lock.

Логин по номеру: [tg-session](https://github.com/xvDoshik/tg-session).

**seshforge** = **sesh**ion **forge**

---

## ✨ Фичи

- **Без lock** 🔓 - в рантайме только `StringSession`.
- **tdata** 🖥️ - Desktop / AyuGram / Kotatogram.
- **`.session`** 💾 - один раз прочитали SQLite и забыли.
- **Полный MTProto** 📡 - `Client` = наследник Telethon.
- **Один вход** 🏭 - `Client.create(...)` с одним источником.

---

## 🚀 Быстрый старт

```bash
git clone https://github.com/xvDoshik/seshforge.git
cd seshforge
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

```bash
python -m seshforge --tdata "~/Library/Application Support/Telegram Desktop/tdata"
```

```python
from seshforge import Client

client = await Client.create(API_ID, API_HASH, tdata="/path/to/tdata")
print(client.session_string)
```

Доки: [сайт](https://xvdoshik.github.io/seshforge/ru/)

---

## ⚙️ Конфиг

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `API_ID` | `2040` | API id ([my.telegram.org](https://my.telegram.org)) |
| `API_HASH` | Telegram Desktop | API hash |

---

## 🔒 Безопасность

Session string = полный доступ. Не коммить и не скидывать.

---

## 📄 Лицензия

MIT - см. [LICENSE](../LICENSE).

---

Спасибо за прочтение! 🐾

**xvDosha** · [github.com/xvDoshik](https://github.com/xvDoshik) · [dosha.pw](https://dosha.pw)
