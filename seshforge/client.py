from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Self

from telethon import TelegramClient as TelethonClient
from telethon.sessions import StringSession

from seshforge.convert import (
    detect_string_kind,
    session_file_to_string,
    session_to_string,
    string_to_session,
    string_to_session_file,
    tdata_to_string,
)


def _resolve_session(session: str | StringSession | None) -> StringSession:
    if session is None:
        return StringSession()
    if isinstance(session, StringSession):
        return session
    raw = session.strip()
    kind = detect_string_kind(raw)
    if kind in ("telethon", "pyrogram"):
        return string_to_session(raw)
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

    async def export_pyrogram_string(self, *, is_bot: bool | None = None) -> str:
        from seshforge.pyro_session import telethon_string_to_pyrogram_string

        me = await self.get_me()
        if me is None:
            raise ValueError("not authorized; connect and login first")
        bot = bool(me.bot) if is_bot is None else bool(is_bot)
        return telethon_string_to_pyrogram_string(
            self.session_string,
            api_id=int(self.api_id),
            user_id=int(me.id),
            is_bot=bot,
        )

    async def to_tdata(
        self,
        out_path: str | Path,
        *,
        use_current: bool = True,
        password: str | None = None,
        api: Any = None,
        passcode: str | None = None,
        key_file: str | None = None,
    ) -> Path:
        from seshforge.desktop import telethon_to_tdata

        return await telethon_to_tdata(
            self.session_string,
            out_path,
            api_id=int(self.api_id),
            api_hash=str(self.api_hash),
            use_current=use_current,
            password=password,
            api=api,
            passcode=passcode,
            key_file=key_file,
        )

    def to_session_file(self, path: str | Path) -> Path:
        return string_to_session_file(self.session_string, path)

    async def to_pyrogram_file(
        self,
        path: str | Path,
        *,
        is_bot: bool | None = None,
        name: str | None = None,
    ) -> Path:
        from seshforge.pyro_session import string_to_pyrogram_file

        me = await self.get_me()
        if me is None:
            raise ValueError("not authorized; connect and login first")
        bot = bool(me.bot) if is_bot is None else bool(is_bot)
        return string_to_pyrogram_file(
            self.session_string,
            path,
            api_id=int(self.api_id),
            user_id=int(me.id),
            is_bot=bot,
            name=name,
        )

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
        client = cls(string_to_session(session_string), api_id, api_hash, **kwargs)
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
    async def from_pyrogram_string(
        cls,
        session_string: str,
        api_id: int,
        api_hash: str,
        *,
        connect: bool = True,
        **kwargs: Any,
    ) -> Self:
        from seshforge.pyro_session import pyrogram_string_to_telethon_string

        return await cls.from_string(
            pyrogram_string_to_telethon_string(session_string),
            api_id,
            api_hash,
            connect=connect,
            **kwargs,
        )

    @classmethod
    async def from_pyrogram_file(
        cls,
        path: str | Path,
        api_id: int,
        api_hash: str,
        *,
        connect: bool = True,
        **kwargs: Any,
    ) -> Self:
        from seshforge.pyro_session import pyrogram_file_to_string

        string = await asyncio.to_thread(pyrogram_file_to_string, path)
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
        passcode: str | None = None,
        key_file: str | None = None,
        api: Any = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> Self:
        string = await tdata_to_string(
            tdata_path,
            account_index=account_index,
            use_current=use_current,
            passcode=passcode,
            key_file=key_file,
            api=api,
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
        pyrogram_session: str | Path | None = None,
        pyrogram_string: str | None = None,
        account_index: int = 0,
        use_current: bool = True,
        connect: bool = True,
        **kwargs: Any,
    ) -> Self:
        sources = [tdata, session_file, session_string, pyrogram_session, pyrogram_string]
        if sum(x is not None for x in sources) != 1:
            raise ValueError(
                "pass exactly one of: tdata, session_file, session_string, "
                "pyrogram_session, pyrogram_string"
            )
        if tdata is not None:
            return await cls.from_tdata(
                tdata,
                api_id,
                api_hash,
                account_index=account_index,
                use_current=use_current,
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
        if pyrogram_session is not None:
            return await cls.from_pyrogram_file(
                pyrogram_session,
                api_id,
                api_hash,
                connect=connect,
                **kwargs,
            )
        if pyrogram_string is not None:
            return await cls.from_pyrogram_string(
                pyrogram_string,
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
