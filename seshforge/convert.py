from __future__ import annotations

from pathlib import Path
from typing import Any

from telethon.crypto import AuthKey
from telethon.sessions import SQLiteSession, StringSession


def session_to_string(session: Any) -> str:
    if isinstance(session, StringSession):
        return session.save() or ""
    if not getattr(session, "auth_key", None):
        raise ValueError("session has no auth_key")
    out = StringSession()
    out.set_dc(session.dc_id, session.server_address, session.port)
    out.auth_key = session.auth_key
    return out.save() or ""


def session_file_to_string(path: str | Path) -> str:
    path = Path(path).expanduser().resolve()
    if path.suffix == ".session":
        stem = str(path.with_suffix(""))
    elif Path(str(path) + ".session").exists():
        stem = str(path)
    elif path.exists() and path.is_file():
        stem = str(path.with_suffix("")) if path.suffix == ".session" else str(path)
    else:
        raise FileNotFoundError(path)
    sqlite = SQLiteSession(stem)
    try:
        if not sqlite.auth_key:
            raise ValueError(f"no auth_key in session file: {path}")
        return session_to_string(sqlite)
    finally:
        close = getattr(sqlite, "close", None)
        if callable(close):
            close()


async def tdata_to_string(
    tdata_path: str | Path,
    *,
    account_index: int = 0,
    use_current: bool = True,
) -> str:
    from opentele.api import API, CreateNewSession, UseCurrentSession
    from opentele.td import TDesktop
    from opentele.tl import TelegramClient

    tdata_path = Path(tdata_path).expanduser().resolve()
    tdesk = TDesktop(str(tdata_path), api=API.TelegramDesktop)
    if not tdesk.isLoaded() or tdesk.accountsCount < 1:
        raise ValueError(f"no accounts in tdata: {tdata_path}")

    account = tdesk.accounts[account_index]
    flag = UseCurrentSession if use_current else CreateNewSession
    ss = StringSession()
    client = await TelegramClient.FromTDesktop(
        account,
        session=ss,
        flag=flag,
        api=API.TelegramDesktop,
    )
    try:
        if not client.is_connected():
            await client.connect()
        saved = client.session.save()
        if not saved:
            raise ValueError("failed to export StringSession from tdata")
        return saved
    finally:
        await client.disconnect()


def memory_from_parts(dc_id: int, address: str, port: int, auth_key: bytes) -> StringSession:
    ss = StringSession()
    ss.set_dc(dc_id, address, port)
    ss.auth_key = AuthKey(auth_key)
    return ss
