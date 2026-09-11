from __future__ import annotations

from pathlib import Path
from typing import Any

from telethon.sessions import StringSession


def load_tdata(
    tdata_path: str | Path,
    *,
    api: Any = None,
    passcode: str | None = None,
    key_file: str | None = None,
):
    from opentele.td import TDesktop

    from seshforge.api import API

    path = Path(tdata_path).expanduser().resolve()
    return TDesktop(
        str(path),
        api=api or API.TelegramDesktop,
        passcode=passcode,
        keyFile=key_file,
    )


def save_tdata(
    tdesk,
    out_path: str | Path | None = None,
    *,
    passcode: str | None = None,
    key_file: str | None = None,
) -> bool:
    path = str(Path(out_path).expanduser().resolve()) if out_path else None
    return bool(tdesk.SaveTData(basePath=path, passcode=passcode, keyFile=key_file))


def list_accounts(tdesk) -> list:
    return list(tdesk.accounts)


def main_account(tdesk):
    return tdesk.mainAccount


def accounts_count(tdesk) -> int:
    return int(tdesk.accountsCount)


async def tdata_to_telethon_string(
    tdata_path: str | Path,
    *,
    account_index: int = 0,
    use_current: bool = True,
    passcode: str | None = None,
    key_file: str | None = None,
    api: Any = None,
    password: str | None = None,
) -> str:
    from opentele.tl import TelegramClient

    from seshforge.api import API, CreateNewSession, UseCurrentSession

    tdesk = load_tdata(tdata_path, api=api, passcode=passcode, key_file=key_file)
    if not tdesk.isLoaded() or tdesk.accountsCount < 1:
        raise ValueError(f"no accounts in tdata: {tdata_path}")
    if account_index < 0 or account_index >= tdesk.accountsCount:
        raise IndexError(f"account_index {account_index} out of range 0..{tdesk.accountsCount - 1}")

    account = tdesk.accounts[account_index]
    flag = UseCurrentSession if use_current else CreateNewSession
    ss = StringSession()
    client = await TelegramClient.FromTDesktop(
        account,
        session=ss,
        flag=flag,
        api=api or API.TelegramDesktop,
        password=password,
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


async def telethon_to_tdata(
    session_string: str,
    out_path: str | Path,
    *,
    api_id: int,
    api_hash: str,
    use_current: bool = True,
    password: str | None = None,
    api: Any = None,
    passcode: str | None = None,
    key_file: str | None = None,
) -> Path:
    from opentele.td import TDesktop
    from opentele.tl import TelegramClient

    from seshforge.api import API, CreateNewSession, UseCurrentSession

    out = Path(out_path).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    flag = UseCurrentSession if use_current else CreateNewSession
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    await client.connect()
    try:
        tdesk = await TDesktop.FromTelethon(
            client,
            flag=flag,
            api=api or API.TelegramDesktop,
            password=password,
        )
        ok = tdesk.SaveTData(basePath=str(out), passcode=passcode, keyFile=key_file)
        if not ok:
            raise ValueError(f"SaveTData failed for {out}")
        return out
    finally:
        await client.disconnect()


__all__ = [
    "accounts_count",
    "list_accounts",
    "load_tdata",
    "main_account",
    "save_tdata",
    "tdata_to_telethon_string",
    "telethon_to_tdata",
]
