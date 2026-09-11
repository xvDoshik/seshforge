# Быстрый старт

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
python -m seshforge --session ./acc.session
```

```python
from seshforge import Client

client = await Client.create(API_ID, API_HASH, tdata="/path/to/tdata")
print(client.session_string)
await client.disconnect()
```
