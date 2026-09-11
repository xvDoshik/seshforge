# API

`Client` - наследник `telethon.TelegramClient`.

```python
from seshforge import Client, tdata_to_string, session_file_to_string

client = await Client.create(API_ID, API_HASH, tdata="...")
client = await Client.create(API_ID, API_HASH, session_file="acc.session")
client = await Client.create(API_ID, API_HASH, session_string="1...")

s = client.session_string
s = await tdata_to_string("/path/tdata")
s = session_file_to_string("acc.session")
```

Полная EN-версия: [API](../api.md).
