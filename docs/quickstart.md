# Quick start

## Install

```bash
git clone https://github.com/xvDoshik/seshforge.git
cd seshforge
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

## Forge a string

=== "tdata"

    ```bash
    python -m seshforge --tdata "~/Library/Application Support/Telegram Desktop/tdata"
    ```

=== ".session"

    ```bash
    python -m seshforge --session ./acc.session
    ```

=== "string"

    ```bash
    python -m seshforge --string '1...'
    ```

Copy `SESSION_STRING` from stdout into your secret store.

## Use as a library

```python
import asyncio
from seshforge import Client

API_ID = 2040
API_HASH = "..."

async def main():
    client = await Client.create(API_ID, API_HASH, tdata="/path/to/tdata")
    me = await client.get_me()
    print(me.username, client.session_string[:32], "...")
    await client.send_message("me", "seshforge ok")
    await client.disconnect()

asyncio.run(main())
```

## After forge

```python
client = await Client.from_string(os.environ["SESSION_STRING"], API_ID, API_HASH)
```

Each worker process gets its own memory session - no file locks.
