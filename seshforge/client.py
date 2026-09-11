from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Self

from telethon import TelegramClient as TelethonClient
from telethon.sessions import StringSession

from seshforge.convert import session_file_to_string, session_to_string, tdata_to_string


def _looks_like_string_session(value: str) -> bool:
    if len(value) < 50 or value[0] != "1":
        return False
    return "/" not in value and "\\" not in value and not value.endswith(".session")


def _resolve_session(session: str | StringSession | None) -> StringSession:
    if session is None:
        return StringSession()
    if isinstance(session, StringSession):
        return session
    raw = session.strip()
    if _looks_like_string_session(raw):
        return StringSession(raw)
    path = Path(raw).expanduser()
    candidates = [path]
    if path.suffix != ".session":
        candidates.append(Path(str(path) + ".session"))
    for cand in candidates:
        if cand.exists() and cand.is_file():
            return StringSession(session_file_to_string(cand))
        stem = cand.with_suffix("") if cand.suffix == ".session" else cand
        if Path(str(stem) + ".session").exists():
            return StringSession(session_file_to_string(stem))
    if raw.startswith("1") and len(raw) > 50:
        return StringSession(raw)
    raise FileNotFoundError(f"session not found and not a StringSession: {session!r}")


class Client(TelethonClient):
    def __init__(
        self,
        session: str | StringSession | None = None,
        api_id: int | None = None,
        api_hash: str | None = None,
        **kwargs: Any,
    ) -> None:
        if api_id is None or api_hash is None:
            raise ValueError("api_id and api_hash are required")
        super().__init__(_resolve_session(session), api_id, api_hash, **kwargs)

    @property
    def session_string(self) -> str:
        return session_to_string(self.session)

    def export_session_string(self) -> str:
        return self.session_string

    @classmethod
    async def from_string(
        cls,
        session_string: str,
        api_id: int,
        api_hash: str,
        *,
        connect: bool = True,
        **kwargs: Any,
    ) -> Self:
        client = cls(StringSession(session_string), api_id, api_hash, **kwargs)
        if connect:
            await client.connect()
        return client

    @classmethod
    async def from_session_file(
        cls,
        path: str | Path,
        api_id: int,
        api_hash: str,
        *,
        connect: bool = True,
        **kwargs: Any,
    ) -> Self:
        string = await asyncio.to_thread(session_file_to_string, path)
        return await cls.from_string(string, api_id, api_hash, connect=connect, **kwargs)

    @classmethod
    async def from_tdata(
        cls,
        tdata_path: str | Path,
        api_id: int,
        api_hash: str,
        *,
        account_index: int = 0,
        use_current: bool = True,
        connect: bool = True,
        **kwargs: Any,
    ) -> Self:
        string = await tdata_to_string(
            tdata_path,
            account_index=account_index,
            use_current=use_current,
        )
        return await cls.from_string(string, api_id, api_hash, connect=connect, **kwargs)

    @classmethod
    async def create(
        cls,
        api_id: int,
        api_hash: str,
        *,
        tdata: str | Path | None = None,
        session_file: str | Path | None = None,
        session_string: str | None = None,
        account_index: int = 0,
        connect: bool = True,
        **kwargs: Any,
    ) -> Self:
        sources = [tdata, session_file, session_string]
        if sum(x is not None for x in sources) != 1:
            raise ValueError("pass exactly one of: tdata, session_file, session_string")
        if tdata is not None:
            return await cls.from_tdata(
                tdata,
                api_id,
                api_hash,
                account_index=account_index,
                connect=connect,
                **kwargs,
            )
        if session_file is not None:
            return await cls.from_session_file(
                session_file,
                api_id,
                api_hash,
                connect=connect,
                **kwargs,
            )
        assert session_string is not None
        return await cls.from_string(
            session_string,
            api_id,
            api_hash,
            connect=connect,
            **kwargs,
        )
